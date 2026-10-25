"""W7 fixed lambda sweep with validation LR selection and paired UTC-day CIs."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess

import numpy as np
import pandas as pd
import torch
import yaml

from scripts.benchmark_v2g import Context, fit
from scripts.summarize_benchmark_v2g import paired_ci
from src.stpignn.paths import REPO_ROOT

HORIZONS = (1, 3, 6, 12, 24)
LAMBDAS = (0.0, 0.06, 0.3, 1.0, 3.0, 10.0)
THRESHOLDS = (0.0, 0.01, 0.05, 0.1)
MODELS = ("stpignn_original", "stpignn_laplacian")
SELECTION_PATH = REPO_ROOT / "results/lambda_selection_v2g.csv"
SEED_PATH = REPO_ROOT / "results/lambda_seed_runs_v2g.csv"
OUTPUT_PATH = REPO_ROOT / "results/lambda_sweep_v2g.csv"
PREDICTION_DIR = REPO_ROOT / "results/lambda_predictions_v2g"


def physics_stats(ctx, model, name):
    counts = np.zeros(len(THRESHOLDS), float)
    violations = np.zeros(len(THRESHOLDS), float)
    abs_sum = 0.0
    edges = 0
    source, dest = ctx.edge_index
    model.eval()
    with torch.no_grad():
        for index, x, _, _, anchor, wind in ctx.batches("test"):
            z = ctx.forward(model, name, x, anchor, wind)
            physical = torch.expm1(z * ctx.sd + ctx.mu)
            diff = (physical[:, dest] - physical[:, source]) / ctx.physical_scale
            wind_mask = torch.as_tensor(ctx.corrected_wind_mask[index - ctx.horizon].copy(), device=ctx.device)
            active = diff[wind_mask]
            for k, threshold in enumerate(THRESHOLDS):
                counts[k] += active.numel()
                violations[k] += (active > threshold).sum().item()
            abs_sum += torch.abs(physical[:, dest] - physical[:, source]).sum().item()
            edges += diff.numel()
    return {**{f"pvr_{threshold:g}_percent": float(100 * violations[k] / counts[k]) if counts[k] else np.nan
               for k, threshold in enumerate(THRESHOLDS)},
            "mean_abs_edge_difference_ug_m3": abs_sum / edges,
            "active_edges": int(counts[0])}


def prediction_path(horizon, name, lam, seed):
    label = str(lam).replace(".", "p")
    return PREDICTION_DIR / f"h{horizon}_{name}_lambda{label}_seed{seed}_v2g.parquet"


def complete_selection(frame, horizon, name, lam, lr_grid):
    if frame.empty:
        return False
    part = frame[(frame.horizon_hours == horizon) & (frame.model == name) & np.isclose(frame["lambda"], lam)]
    return len(part) == len(lr_grid) and all(np.isclose(part.lr, lr).any() for lr in lr_grid)


def run_horizon(horizon, cfg, selection, seeds):
    for name in MODELS:
        for lam in LAMBDAS:
            local = dict(cfg, lambda_original=lam)
            ctx = Context(horizon, local)
            if not complete_selection(selection, horizon, name, lam, cfg["neural_lr_grid"]):
                for lr in cfg["neural_lr_grid"]:
                    exists = (not selection.empty and
                              ((selection.horizon_hours == horizon) & (selection.model == name) &
                               np.isclose(selection["lambda"], lam) & np.isclose(selection.lr, lr)).any())
                    if exists:
                        continue
                    result, _ = fit(ctx, name, lr, cfg["neural_seeds"][0], evaluate_test=False)
                    row = {"horizon_hours": horizon, "model": name, "lambda": lam, "lr": lr,
                           "selection_seed": cfg["neural_seeds"][0], "validation_mae": result["validation_mae"],
                           "best_epoch": result["best_epoch"], "epochs_run": result["epochs_run"],
                           "train_seconds": result["train_seconds"], "parameter_count": result["parameter_count"]}
                    selection = pd.concat([selection, pd.DataFrame([row])], ignore_index=True)
                    selection.to_csv(SELECTION_PATH, index=False)
                    print("SELECT", horizon, name, lam, lr, row["validation_mae"], flush=True)
            part = selection[(selection.horizon_hours == horizon) & (selection.model == name) &
                             np.isclose(selection["lambda"], lam)].sort_values("validation_mae")
            lr = float(part.iloc[0].lr)
            for seed in cfg["neural_seeds"]:
                path = prediction_path(horizon, name, lam, seed)
                done = (not seeds.empty and
                        ((seeds.horizon_hours == horizon) & (seeds.model == name) &
                         np.isclose(seeds["lambda"], lam) & (seeds.seed == seed)).any())
                if done and path.exists():
                    continue
                result, tested, model = fit(ctx, name, lr, seed, evaluate_test=True, return_model=True)
                pred = pd.DataFrame({"target_time_utc": ctx.times[tested["time_index"]].astype(str),
                                     "station_id": ctx.station_ids[tested["station_index"]],
                                     "target_ug_m3": tested["truth"], "prediction_ug_m3": tested["pred"]})
                PREDICTION_DIR.mkdir(exist_ok=True)
                pred.to_parquet(path, index=False)
                row = {"horizon_hours": horizon, "model": name, "lambda": lam, "seed": seed, "lr": lr,
                       "best_epoch": result["best_epoch"], "validation_mae": result["validation_mae"],
                       "test_n": result["test_n"], "test_mae_ug_m3": result["test_mae"],
                       "test_r2": result["test_r2"], "parameter_count": result["parameter_count"],
                       "train_seconds": result["train_seconds"], **physics_stats(ctx, model, name)}
                seeds = seeds[~((seeds.horizon_hours == horizon) & (seeds.model == name) &
                                np.isclose(seeds["lambda"], lam) & (seeds.seed == seed))] if not seeds.empty else seeds
                seeds = pd.concat([seeds, pd.DataFrame([row])], ignore_index=True)
                seeds.to_csv(SEED_PATH, index=False)
                print("LAMBDA", horizon, name, lam, seed, row["test_mae_ug_m3"], flush=True)
    return selection, seeds


def summarize(horizons, cfg, seeds):
    rows = []
    verdict = {}
    for horizon in horizons:
        verdict[horizon] = {}
        for name in MODELS:
            part = seeds[(seeds.horizon_hours == horizon) & (seeds.model == name)]
            expected = len(LAMBDAS) * len(cfg["neural_seeds"])
            if len(part) != expected:
                raise AssertionError(f"Incomplete W7 h={horizon} {name}: {len(part)}/{expected}")
            pooled = {}
            for lam in LAMBDAS:
                frames = [pd.read_parquet(prediction_path(horizon, name, lam, seed)).assign(seed=seed)
                          for seed in cfg["neural_seeds"]]
                full = pd.concat(frames, ignore_index=True)
                key = ["target_time_utc", "station_id"]
                if full.groupby(key).seed.nunique().min() != len(cfg["neural_seeds"]):
                    raise AssertionError(f"Unequal seed coverage h={horizon} {name} lambda={lam}")
                pooled[lam] = full.groupby(key, as_index=False).agg(target_ug_m3=("target_ug_m3", "first"),
                                                                      prediction_ug_m3=("prediction_ug_m3", "mean"))
            for lam in LAMBDAS:
                other = pooled[lam]
                zero = pooled[0.0]
                key = ["target_time_utc", "station_id"]
                joined = other.merge(zero[key + ["prediction_ug_m3"]], on=key,
                                     suffixes=("_lambda", "_zero"), validate="one_to_one")
                if len(joined) != len(other) or len(joined) != len(zero):
                    raise AssertionError("Unequal lambda test masks")
                y = joined.target_ug_m3.to_numpy(float)
                a = joined.prediction_ug_m3_lambda.to_numpy(float)
                b = joined.prediction_ug_m3_zero.to_numpy(float)
                dates = pd.to_datetime(joined.target_time_utc, utc=True).dt.date.to_numpy()
                dmae, ci, dr2, r2ci = paired_ci(a, b, y, dates, 4700 + horizon, 2000)
                from src.stpignn.evaluation import evaluate_arrays
                metrics = evaluate_arrays(a, y, np.ones(len(y), bool))
                runs = part[np.isclose(part["lambda"], lam)]
                row = {"horizon_hours": horizon, "model": name, "lambda": lam,
                       "seeds_completed": len(runs), "test_n": len(y), "test_mae_ug_m3": metrics["mae"],
                       "test_r2": metrics["r2"], "delta_mae_vs_zero_ug_m3": dmae,
                       "mae_ci_low": ci[0], "mae_ci_high": ci[1],
                       "delta_r2_vs_zero": dr2, "r2_ci_low": r2ci[0], "r2_ci_high": r2ci[1],
                       "pvr_0_percent": runs["pvr_0_percent"].mean(),
                       "pvr_0.01_percent": runs["pvr_0.01_percent"].mean(),
                       "pvr_0.05_percent": runs["pvr_0.05_percent"].mean(),
                       "pvr_0.1_percent": runs["pvr_0.1_percent"].mean(),
                       "mean_abs_edge_difference_ug_m3": runs.mean_abs_edge_difference_ug_m3.mean(),
                       "mean_validation_mae": runs.validation_mae.mean(),
                       "lr": runs.lr.iloc[0], "parameter_count": runs.parameter_count.iloc[0],
                       "total_train_seconds": runs.train_seconds.sum(),
                       "physics_helps_at_horizon": bool(lam > 0 and ci[1] < 0)}
                rows.append(row)
                print("COMPARE", horizon, name, lam, dmae, ci, flush=True)
            better = [row for row in rows if row["horizon_hours"] == horizon and row["model"] == name and
                      row["lambda"] > 0 and row["physics_helps_at_horizon"]]
            verdict[horizon][name] = {"met": bool(better), "qualifying_lambdas": [row["lambda"] for row in better]}
    pd.DataFrame(rows).to_csv(OUTPUT_PATH, index=False)
    (REPO_ROOT / "results/lambda_verdict_v2g.json").write_text(json.dumps({
        "criterion": "some lambda>0 has paired UTC-day bootstrap MAE CI strictly below zero vs lambda=0",
        "verdict_by_horizon": verdict,
        "overall_met": any(item["met"] for methods in verdict.values() for item in methods.values()),
        "script": "scripts/lambda_sweep_v2g.py", "config": "configs/benchmark_v2g.yaml",
        "seeds": cfg["neural_seeds"],
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True).strip(),
        "timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat()}, indent=2) + "\n")
    print(json.dumps(verdict, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--horizons", nargs="*", type=int, default=list(HORIZONS))
    args = parser.parse_args()
    if not set(args.horizons) <= set(HORIZONS):
        raise ValueError("Unexpected horizon")
    cfg = yaml.safe_load((REPO_ROOT / "configs/benchmark_v2g.yaml").read_text())
    selection = pd.read_csv(SELECTION_PATH) if SELECTION_PATH.exists() else pd.DataFrame()
    seeds = pd.read_csv(SEED_PATH) if SEED_PATH.exists() else pd.DataFrame()
    for horizon in args.horizons:
        selection, seeds = run_horizon(horizon, cfg, selection, seeds)
    summarize(args.horizons, cfg, seeds)


if __name__ == "__main__":
    main()
