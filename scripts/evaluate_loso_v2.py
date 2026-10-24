"""Leak-isolated, observed-only 15-fold station holdout on data_v2."""
from __future__ import annotations

import os
os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")

import datetime as dt
import json
import random
import subprocess
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import yaml
from scipy.stats import wilcoxon
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import ConstantKernel, RBF, WhiteKernel
from sklearn.linear_model import Ridge
from pykrige.ok import OrdinaryKriging

from src.stpignn.data_v2 import build
from src.stpignn.evaluation import evaluate_arrays
from src.stpignn.models_v2 import make_model
from src.stpignn.paths import REPO_ROOT
from src.stpignn.physics_v2 import batched_penalty
from src.stpignn.station_graph import directed_knn_graph
from scripts.train_gate_v2 import aligned_mask_arrays, inverse_y, normalize_y, seed_all

CFG_PATH = REPO_ROOT / "configs/loso_v2.yaml"
CFG = yaml.safe_load(CFG_PATH.read_text())
METHODS = ("stpignn_known", "stpignn_weather_static", "gru_only", "idw", "gp_rbf",
           "ordinary_kriging", "nearest_station_persistence", "station_train_mean", "ridge_weather_static")
INFO = {
    "stpignn_known": "known-station lagged pollutant history and all-station weather/static; held-out pollutant history suppressed",
    "stpignn_weather_static": "all-station weather/static only; all pollutant history suppressed",
    "gru_only": "held-out weather/static only; held-out pollutant history suppressed",
    "idw": "known-station observed PM2.5 at forecast cutoff; training-known global mean fallback",
    "gp_rbf": "known-station observed PM2.5 at forecast cutoff; fixed RBF GP hyperparameters; training-known global mean fallback",
    "ordinary_kriging": "known-station observed PM2.5 at forecast cutoff; per-hour fitted spherical variogram; training-known global mean fallback",
    "nearest_station_persistence": "nearest known station observed PM2.5 at forecast cutoff, or its last earlier reading; training-known global mean fallback",
    "station_train_mean": "pooled known-station PM2.5 mean fit on training period",
    "ridge_weather_static": "weather/static features fitted on known-station training observations only",
}


def available_hours(data, split, station_mask, horizon):
    eligible = data.split_masks[split] & data.observed_mask[:, station_mask].any(axis=1)
    eligible[:int(data.config["history_hours"]) - 1 + horizon] = False
    return np.flatnonzero(eligible)


def batches(data, hours, station_mask, device, size, horizon, seed=None):
    hours = hours.copy()
    if seed is not None:
        np.random.default_rng(seed).shuffle(hours)
    history = int(data.config["history_hours"])
    for start in range(0, len(hours), size):
        idx = hours[start:start + size]
        cutoff = idx - horizon
        win = cutoff[:, None] - np.arange(history - 1, -1, -1)[None, :]
        assert win.min() >= 0 and np.all(win <= cutoff[:, None])
        x = torch.as_tensor(data.features[win].copy(), dtype=torch.float32, device=device)
        # Even the imputed hidden pollutant channels are withheld from the network.
        x[:, :, ~station_mask, :5] = 0.0
        y = torch.as_tensor(np.nan_to_num(data.observed_target[idx], nan=0.0).copy(), dtype=torch.float32, device=device)
        mask = torch.as_tensor((data.observed_mask[idx] & station_mask[None, :]).copy(), dtype=torch.bool, device=device)
        yield idx, x, y, mask


def neural_fold(data, hidden, method, seed, edge, edge_attr, wind_mask, device):
    seed_all(seed)
    horizon = int(CFG["horizon_hours"])
    known = np.ones(len(data.station_ids), dtype=bool)
    known[hidden] = False
    heldout = ~known
    train_hours = available_hours(data, "train", known, horizon)
    val_hours = available_hours(data, "validation", known, horizon)
    test_hours = available_hours(data, "test", heldout, horizon)
    if not len(train_hours) or not len(val_hours) or not len(test_hours):
        raise ValueError("LOSO fold has no observed train, validation or test hours")
    name = "gru_only" if method == "gru_only" else "stpignn_corrected"
    model = make_model(name, data.features.shape[-1], int(CFG["hidden_dim"]), edge_attr.shape[1]).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=float(CFG["learning_rate"]), weight_decay=float(CFG["weight_decay"]))
    mean = float(data.fit["target_log1p_mean"])
    std = float(data.fit["target_log1p_std"])
    phys_scale = float(data.fit["target_standard_std"])
    best_val, best_epoch, best_state, bad = float("inf"), 0, None, 0
    curves = []

    def model_x(x):
        if method == "stpignn_weather_static":
            x = x.clone()
            x[..., :5] = 0.0
        elif method == "gru_only":
            x = x.clone()
            x[..., :5] = 0.0
        return x

    def score(hours, station_mask, collect=False):
        model.eval()
        pred, truth, times = [], [], []
        with torch.no_grad():
            for idx, x, y, mask in batches(data, hours, station_mask, device, int(CFG["batch_size"]), horizon):
                p = inverse_y(model(model_x(x), edge, edge_attr), "log1p", mean, std).cpu().numpy()
                m = mask.cpu().numpy()
                rows, cols = np.where(m)
                pred.append(p[rows, cols])
                truth.append(y.cpu().numpy()[rows, cols])
                if collect:
                    times.extend(data.times[idx[rows]].astype(str).tolist())
        p = np.concatenate(pred)
        y = np.concatenate(truth)
        return (evaluate_arrays(p, y, np.ones(len(y), bool)), p, y, times)

    for epoch in range(1, int(CFG["max_epochs"]) + 1):
        model.train()
        train_loss = []
        for idx, x, y, mask in batches(data, train_hours, known, device, int(CFG["batch_size"]), horizon, seed * 1000 + epoch):
            opt.zero_grad(set_to_none=True)
            pred = model(model_x(x), edge, edge_attr)
            target = normalize_y(y, "log1p", mean, std)
            data_loss = (((pred - target) ** 2) * mask).sum() / mask.sum().clamp(min=1)
            loss = data_loss
            lam = float(CFG["physics_weight"]) * min(1.0, epoch / 25.0)
            if method.startswith("stpignn"):
                physical = inverse_y(pred, "log1p", mean, std) / phys_scale
                cmask = torch.as_tensor(wind_mask[idx - horizon].copy(), dtype=torch.bool, device=device)
                loss = loss + lam * batched_penalty(physical, edge, cmask, edge_attr, "corrected_mask")
            if not torch.isfinite(loss):
                raise FloatingPointError(f"non-finite LOSO loss fold={hidden} method={method} seed={seed}")
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 0.3)
            opt.step()
            train_loss.append(float(loss.detach()))
        val = score(val_hours, known)[0]
        curves.append({"station_id": int(data.station_ids[hidden]), "method": method, "seed": seed,
                       "epoch": epoch, "train_loss": float(np.mean(train_loss)), "validation_mae": val["mae"]})
        if val["mae"] < best_val:
            best_val, best_epoch, bad = val["mae"], epoch, 0
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
        else:
            bad += 1
            if bad >= int(CFG["patience"]):
                break
    model.load_state_dict(best_state)
    _, p, y, times = score(test_hours, heldout, True)
    result = pd.DataFrame({"station_id": int(data.station_ids[hidden]), "method": method,
                           "seed": seed, "target_time_utc": times, "target": y, "prediction": p})
    result["best_epoch"] = best_epoch
    result["validation_mae"] = best_val
    return result, curves


def spatial_baselines(data, hidden):
    horizon = int(CFG["horizon_hours"])
    known = np.ones(len(data.station_ids), bool)
    known[hidden] = False
    hours = available_hours(data, "test", ~known, horizon)
    target = data.observed_target[hours, hidden]
    keep = np.isfinite(target)
    hours, target = hours[keep], target[keep]
    xy = data.coordinates.astype(float)
    distance = np.linalg.norm(xy[known] - xy[hidden], axis=1)
    train_known = data.observed_target[data.split_masks["train"]][:, known]
    global_mean = float(np.nanmean(train_known))
    train_station_means = np.nanmean(train_known, axis=0)
    if not np.isfinite(global_mean):
        raise ValueError("LOSO train mean absent")
    known_ids = np.flatnonzero(known)
    p = {method: np.full(len(hours), global_mean, np.float64) for method in METHODS[3:]}
    fallback = {method: 0 for method in METHODS[3:]}
    # Ridge features are weather and elevation channels only; fit with known observed targets.
    rr, cc = np.where(data.observed_mask & data.split_masks["train"][:, None] & known[None, :])
    valid = rr >= horizon + int(data.config["history_hours"]) - 1
    rr, cc = rr[valid], cc[valid]
    ridge = Ridge(alpha=1.0)
    ridge.fit(data.features[rr - horizon, cc, 5:13], data.observed_target[rr, cc])
    p["ridge_weather_static"] = ridge.predict(data.features[hours - horizon, hidden, 5:13])
    # Fixed GP kernel constants avoid fitting any parameter on held-out observations.
    kernel = ConstantKernel(1.0, constant_value_bounds="fixed") * RBF(float(CFG["gp_length_scale_m"]), length_scale_bounds="fixed") + WhiteKernel(float(CFG["gp_noise_variance"]), noise_level_bounds="fixed")
    for k, hour in enumerate(hours):
        cutoff = hour - horizon
        values = data.observed_target[cutoff, known]
        finite = np.isfinite(values)
        d = distance[finite]
        v = values[finite]
        if len(v):
            weights = 1.0 / np.maximum(d, 1.0) ** float(CFG["idw_power"])
            p["idw"][k] = float(np.dot(weights, v) / weights.sum())
            nearest = np.argmin(d)
            p["nearest_station_persistence"][k] = v[nearest]
        else:
            fallback["idw"] += 1
            # Last earlier known observation, station by station, before cutoff.
            latest = []
            for j in known_ids:
                prior = np.flatnonzero(np.isfinite(data.observed_target[:cutoff + 1, j]))
                if len(prior):
                    latest.append((np.linalg.norm(xy[j] - xy[hidden]), data.observed_target[prior[-1], j]))
            if latest:
                p["nearest_station_persistence"][k] = min(latest)[1]
            else:
                fallback["nearest_station_persistence"] += 1
        if len(v) >= 2:
            try:
                gp = GaussianProcessRegressor(kernel=kernel, optimizer=None, normalize_y=True, alpha=1e-6)
                gp.fit(xy[known][finite], v)
                p["gp_rbf"][k] = float(gp.predict(xy[hidden:hidden + 1])[0])
            except (ValueError, np.linalg.LinAlgError):
                fallback["gp_rbf"] += 1
        else:
            fallback["gp_rbf"] += 1
        if len(v) >= 4:
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    ok = OrdinaryKriging(xy[known][finite, 0], xy[known][finite, 1], v,
                                         variogram_model=CFG["kriging_variogram_model"],
                                         variogram_parameters=None, enable_plotting=False,
                                         verbose=False, exact_values=False)
                    estimate, _ = ok.execute("points", [xy[hidden, 0]], [xy[hidden, 1]])
                p["ordinary_kriging"][k] = float(estimate[0])
            except (ValueError, RuntimeError, np.linalg.LinAlgError, ZeroDivisionError):
                fallback["ordinary_kriging"] += 1
        else:
            fallback["ordinary_kriging"] += 1
    frames = []
    for method in METHODS[3:]:
        frames.append(pd.DataFrame({"station_id": int(data.station_ids[hidden]), "method": method,
                                    "seed": -1, "target_time_utc": data.times[hours].astype(str),
                                    "target": target, "prediction": p[method]}))
    return pd.concat(frames, ignore_index=True), fallback


def paired_ci(frame_a, frame_b, seed, replicates):
    keys = ["station_id", "target_time_utc"]
    joined = frame_a.merge(frame_b[keys + ["prediction"]], on=keys, suffixes=("_a", "_b"), validate="one_to_one")
    if len(joined) != len(frame_a):
        raise AssertionError("Paired LOSO methods lack identical scored pairs")
    days = pd.to_datetime(joined.target_time_utc, utc=True).dt.floor("D")
    groups = [np.flatnonzero(days == day) for day in days.unique()]
    rng = np.random.default_rng(seed)
    diffs = []
    for _ in range(replicates):
        chosen = rng.integers(0, len(groups), len(groups))
        idx = np.concatenate([groups[j] for j in chosen])
        a = evaluate_arrays(joined.prediction_a.to_numpy()[idx], joined.target.to_numpy()[idx], np.ones(len(idx), bool))
        b = evaluate_arrays(joined.prediction_b.to_numpy()[idx], joined.target.to_numpy()[idx], np.ones(len(idx), bool))
        diffs.append((a["mae"] - b["mae"], a["r2"] - b["r2"]))
    return np.quantile(np.asarray(diffs), [0.025, 0.975], axis=0).tolist()


def main():
    started = time.perf_counter()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config_path = REPO_ROOT / CFG["data_config"]
    source_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True).strip()
    predictions, curves, fallback_rows, unscored = [], [], [], []
    reference_ids = None
    for fold, station_id in enumerate(pd.read_csv(REPO_ROOT / "results/stations_v2.csv").station_id.astype(int)):
        data, _ = build(config_path, excluded_station_id=station_id)
        if reference_ids is None:
            reference_ids = data.station_ids.astype(int).tolist()
        hidden = int(np.flatnonzero(data.station_ids == station_id)[0])
        fit_ids = set(data.fit["fitted_station_ids"])
        assert station_id not in fit_ids and len(fit_ids) == len(data.station_ids) - 1
        if not data.observed_mask[data.split_masks["test"], hidden].any():
            unscored.append({"station_id": station_id, "reason": "zero observed PM2.5 targets in test interval"})
            print(f"fold={fold + 1}/15 station={station_id} unscored: zero observed test targets", flush=True)
            continue
        edge, edge_attr = directed_knn_graph(data.coordinates, int(CFG["station_graph_neighbours"]))
        edge, edge_attr = edge.to(device), edge_attr.to(device)
        # Legacy slope only fills the unused legacy mask return.
        corrected, _ = aligned_mask_arrays(data.raw_wind_degrees, data.coordinates, edge.cpu(), 1.0, 0.0)
        for method in METHODS[:3]:
            for seed in CFG["seeds"]:
                result, c = neural_fold(data, hidden, method, int(seed), edge, edge_attr, corrected, device)
                predictions.append(result)
                curves.extend(c)
                print(f"fold={fold + 1}/15 station={station_id} method={method} seed={seed} n={len(result)} mae={np.mean(np.abs(result.prediction - result.target)):.6f}", flush=True)
        base, fallback = spatial_baselines(data, hidden)
        predictions.append(base)
        fallback_rows.append({"station_id": station_id, **fallback})
        print(f"fold={fold + 1}/15 baselines done", flush=True)
    all_pred = pd.concat(predictions, ignore_index=True)
    all_pred["information_set"] = all_pred.method.map(INFO)
    # A pooled neural prediction is the equal mean over predetermined seeds per pair.
    neural = all_pred.loc[all_pred.seed >= 0]
    pooled_neural = neural.groupby(["station_id", "method", "target_time_utc", "target", "information_set"], as_index=False).prediction.mean()
    pooled_neural["seed"] = -2
    scored = pd.concat([all_pred.loc[all_pred.seed == -1], pooled_neural], ignore_index=True)
    per_station, summary = [], []
    for (station_id, method), part in scored.groupby(["station_id", "method"]):
        metric = evaluate_arrays(part.prediction, part.target, np.ones(len(part), bool))
        per_station.append({"station_id": station_id, "method": method, "information_set": INFO[method], **metric})
    for method, part in scored.groupby("method"):
        metric = evaluate_arrays(part.prediction, part.target, np.ones(len(part), bool))
        summary.append({"method": method, "information_set": INFO[method], **metric})
    per_station = pd.DataFrame(per_station)
    summary = pd.DataFrame(summary)
    baselines = summary.set_index("method").loc[["idw", "gp_rbf", "ordinary_kriging"]]
    best = str(baselines.mae.idxmin())
    a = scored.loc[scored.method == "stpignn_known"]
    b = scored.loc[scored.method == best]
    ci = paired_ci(a, b, int(CFG["bootstrap_seed"]), int(CFG["bootstrap_replicates"]))
    known = summary.set_index("method").loc["stpignn_known"]
    competitor = summary.set_index("method").loc[best]
    if ci[0][0] <= 0 <= ci[1][0]:
        verdict = "TIE"
    elif known.mae < competitor.mae and known.r2 > competitor.r2 and ci[1][0] < 0:
        verdict = "WIN"
    else:
        verdict = "LOSS"
    station_a = per_station.set_index(["station_id", "method"]).xs("stpignn_known", level="method").mae
    station_b = per_station.set_index(["station_id", "method"]).xs(best, level="method").mae
    paired_station = station_a - station_b
    wilcoxon_result = wilcoxon(paired_station.to_numpy(), zero_method="wilcox", alternative="two-sided")
    out = REPO_ROOT / "results"
    all_pred.to_parquet(out / "loso_predictions_v2.parquet", index=False)
    pd.DataFrame(curves).to_csv(out / "loso_curves_v2.csv", index=False)
    pd.DataFrame(fallback_rows).to_csv(out / "loso_fallbacks_v2.csv", index=False)
    pd.DataFrame(unscored).to_csv(out / "loso_unscored_folds_v2.csv", index=False)
    per_station.to_csv(out / "loso_per_station_v2.csv", index=False)
    summary.to_csv(out / "loso_summary_v2.csv", index=False)
    details = {"timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat(), "source_git_commit": source_commit,
               "script": "scripts/evaluate_loso_v2.py", "config": "configs/loso_v2.yaml", "seeds": CFG["seeds"],
               "folds_considered": len(reference_ids), "folds_scored": len(reference_ids) - len(unscored),
               "unscored_station_ids": [int(row["station_id"]) for row in unscored],
               "n_scored_pairs_per_method": int(len(a)), "best_spatial_baseline": best,
               "paired_utc_day_bootstrap_replicates": int(CFG["bootstrap_replicates"]),
               "mae_difference_stpignn_minus_best": float(known.mae - competitor.mae),
               "r2_difference_stpignn_minus_best": float(known.r2 - competitor.r2),
               "mae_difference_ci": [ci[0][0], ci[1][0]], "r2_difference_ci": [ci[0][1], ci[1][1]],
               "wilcoxon_p_over_stations": float(wilcoxon_result.pvalue), "verdict": verdict,
               "runtime_seconds": time.perf_counter() - started, "hardware": str(device)}
    (out / "loso_decision_v2.json").write_text(json.dumps(details, indent=2))
    print(json.dumps(details, indent=2), flush=True)


if __name__ == "__main__":
    main()
