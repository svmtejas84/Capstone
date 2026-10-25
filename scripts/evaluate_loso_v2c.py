"""S4: fold-isolated LOSO with the predeclared causal residual formulation."""
from __future__ import annotations

import os
os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")

import datetime as dt
import json
import subprocess
import time
import warnings

import numpy as np
import pandas as pd
import torch
from scipy.stats import wilcoxon
import yaml

from scripts.evaluate_loso_v2 import (METHODS, INFO as ORIGINAL_INFO, available_hours,
                                      batches, paired_ci, spatial_baselines)
from scripts.train_gate_v2 import aligned_mask_arrays, inverse_y, normalize_y, seed_all
from src.stpignn.data_v2 import build
from src.stpignn.evaluation import evaluate_arrays
from src.stpignn.models_v2 import make_model
from src.stpignn.paths import REPO_ROOT
from src.stpignn.physics_v2 import batched_penalty
from src.stpignn.station_graph import directed_knn_graph

CFG = yaml.safe_load((REPO_ROOT / "configs/loso_v2.yaml").read_text())
INFO = dict(ORIGINAL_INFO)
INFO["stpignn_known"] = "known-station pollutant history; hidden station's own readings suppressed; nearest-known-station causal persistence as hidden residual anchor"
INFO["stpignn_weather_static"] = "weather/static only; fixed known-station training mean as residual anchor"
INFO["gru_only"] = "held-out weather/static only; fixed known-station training mean as residual anchor"


def residual_anchors(data, hidden):
    readings = data.observed_target.copy()
    readings[:, hidden] = np.nan
    train = readings[data.split_masks["train"]]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        station_mean = np.nanmean(train, axis=0)
        global_mean = float(np.nanmean(train))
    if not np.isfinite(global_mean):
        raise ValueError("No known-station training PM2.5 for LOSO anchor")
    station_mean = np.where(np.isfinite(station_mean), station_mean, global_mean)
    last = pd.DataFrame(readings).ffill().to_numpy(dtype=np.float32)
    own = np.where(np.isfinite(last), last, station_mean[None, :]).astype(np.float32)
    distance = np.linalg.norm(data.coordinates.astype(float) - data.coordinates[hidden].astype(float), axis=1)
    distance[hidden] = np.inf
    order = np.argsort(distance)
    nearest = np.full(len(data.times), global_mean, dtype=np.float32)
    for hour in range(len(data.times)):
        current = readings[hour, order]
        available = np.flatnonzero(np.isfinite(current))
        if len(available):
            nearest[hour] = current[available[0]]
            continue
        prior = last[hour, order]
        available = np.flatnonzero(np.isfinite(prior))
        if len(available):
            nearest[hour] = prior[available[0]]
    own[:, hidden] = nearest
    data.features = data.features.copy()
    data.features[:, :, 0] = ((np.log1p(own) - data.fit["target_log1p_mean"]) /
                               data.fit["target_log1p_std"]).astype(np.float32)
    return own, nearest, global_mean


def neural_fold(data, hidden, method, seed, edge, edge_attr, corrected_mask, device,
                own_anchor, nearest_anchor, global_anchor):
    seed_all(seed)
    horizon = int(CFG["horizon_hours"])
    known = np.ones(len(data.station_ids), dtype=bool)
    known[hidden] = False
    heldout = ~known
    train_hours = available_hours(data, "train", known, horizon)
    val_hours = available_hours(data, "validation", known, horizon)
    test_hours = available_hours(data, "test", heldout, horizon)
    name = "gru_only" if method == "gru_only" else "stpignn_corrected"
    model = make_model(name, data.features.shape[-1], int(CFG["hidden_dim"]), edge_attr.shape[1]).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=float(CFG["learning_rate"]),
                                  weight_decay=float(CFG["weight_decay"]))
    mean = float(data.fit["target_log1p_mean"])
    std = float(data.fit["target_log1p_std"])
    phys_scale = float(data.fit["target_standard_std"])
    best_val, best_epoch, best_state, bad = float("inf"), 0, None, 0
    curves = []

    def input_and_anchor(x, idx):
        cutoff = idx - horizon
        if method == "stpignn_known":
            anchor = own_anchor[cutoff].copy()
        else:
            x = x.clone()
            x[..., :5] = 0.0
            anchor = np.full((len(idx), len(data.station_ids)), global_anchor, dtype=np.float32)
        anchor_t = torch.as_tensor(anchor, dtype=torch.float32, device=device)
        return x, normalize_y(anchor_t, "log1p", mean, std)

    def score(hours, station_mask, collect=False):
        model.eval()
        pred, truth, stamps = [], [], []
        with torch.no_grad():
            for idx, x, y, mask in batches(data, hours, station_mask, device,
                                            int(CFG["batch_size"]), horizon):
                x, anchor_norm = input_and_anchor(x, idx)
                out = model(x, edge, edge_attr) + anchor_norm
                physical = inverse_y(out, "log1p", mean, std).cpu().numpy()
                selected = mask.cpu().numpy()
                row, col = np.where(selected)
                pred.append(physical[row, col])
                truth.append(y.cpu().numpy()[row, col])
                if collect:
                    stamps.extend(data.times[idx[row]].astype(str).tolist())
        p, y = np.concatenate(pred), np.concatenate(truth)
        return evaluate_arrays(p, y, np.ones(len(y), bool)), p, y, stamps

    for epoch in range(1, int(CFG["max_epochs"]) + 1):
        model.train()
        losses = []
        for idx, x, y, mask in batches(data, train_hours, known, device,
                                       int(CFG["batch_size"]), horizon, seed * 1000 + epoch):
            optimizer.zero_grad(set_to_none=True)
            x, anchor_norm = input_and_anchor(x, idx)
            total_norm = model(x, edge, edge_attr) + anchor_norm
            target_norm = normalize_y(y, "log1p", mean, std)
            data_loss = (((total_norm - target_norm) ** 2) * mask).sum() / mask.sum().clamp(min=1)
            loss = data_loss
            lam = float(CFG["physics_weight"]) * min(1.0, epoch / 25.0)
            if method.startswith("stpignn"):
                physical_norm = inverse_y(total_norm, "log1p", mean, std) / phys_scale
                wind = torch.as_tensor(corrected_mask[idx - horizon].copy(), dtype=torch.bool, device=device)
                loss = loss + lam * batched_penalty(physical_norm, edge, wind, edge_attr, "corrected_mask")
            if not torch.isfinite(loss):
                raise FloatingPointError(f"Nonfinite S4 loss station={data.station_ids[hidden]} method={method} seed={seed}")
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 0.3)
            optimizer.step()
            losses.append(float(loss.detach()))
        val = score(val_hours, known)[0]
        curves.append({"station_id": int(data.station_ids[hidden]), "method": method, "seed": seed,
                       "epoch": epoch, "train_loss": float(np.mean(losses)), "validation_mae": val["mae"]})
        if val["mae"] < best_val:
            best_val, best_epoch, bad = val["mae"], epoch, 0
            best_state = {key: value.detach().cpu().clone() for key, value in model.state_dict().items()}
        else:
            bad += 1
            if bad >= int(CFG["patience"]):
                break
    model.load_state_dict(best_state)
    _, p, y, stamps = score(test_hours, heldout, True)
    result = pd.DataFrame({"station_id": int(data.station_ids[hidden]), "method": method,
                           "seed": seed, "target_time_utc": stamps, "target": y, "prediction": p,
                           "best_epoch": best_epoch, "validation_mae": best_val})
    return result, curves


def main():
    started = time.perf_counter()
    source_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True).strip()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    predictions, curves, fallback_rows, unscored = [], [], [], []
    stations = pd.read_csv(REPO_ROOT / "results/stations_v2.csv").station_id.astype(int).tolist()
    for fold, station_id in enumerate(stations):
        data, _ = build(REPO_ROOT / "configs/data_v2.yaml", excluded_station_id=station_id)
        hidden = int(np.flatnonzero(data.station_ids == station_id)[0])
        assert station_id not in data.fit["fitted_station_ids"]
        if not data.observed_mask[data.split_masks["test"], hidden].any():
            unscored.append({"station_id": station_id, "reason": "zero observed PM2.5 targets in test interval"})
            print(f"fold={fold + 1}/15 station={station_id} unscored", flush=True)
            continue
        own, nearest, global_mean = residual_anchors(data, hidden)
        edge, edge_attr = directed_knn_graph(data.coordinates, int(CFG["station_graph_neighbours"]))
        corrected, _ = aligned_mask_arrays(data.raw_wind_degrees, data.coordinates, edge, 1.0, 0.0)
        edge, edge_attr = edge.to(device), edge_attr.to(device)
        for method in METHODS[:3]:
            for seed in CFG["seeds"]:
                part, track = neural_fold(data, hidden, method, int(seed), edge, edge_attr,
                                          corrected, device, own, nearest, global_mean)
                predictions.append(part)
                curves.extend(track)
                print(f"fold={fold + 1}/15 station={station_id} method={method} seed={seed} n={len(part)} mae={np.mean(np.abs(part.prediction - part.target)):.6f}", flush=True)
        base, fallback = spatial_baselines(data, hidden)
        predictions.append(base)
        fallback_rows.append({"station_id": station_id, **fallback})
        print(f"fold={fold + 1}/15 baselines done", flush=True)
    raw = pd.concat(predictions, ignore_index=True)
    raw["information_set"] = raw.method.map(INFO)
    neural = raw.loc[raw.seed >= 0]
    pooled_neural = neural.groupby(["station_id", "method", "target_time_utc", "target", "information_set"], as_index=False).prediction.mean()
    pooled_neural["seed"] = -2
    scored = pd.concat([raw.loc[raw.seed == -1], pooled_neural], ignore_index=True)
    per_station, summary = [], []
    for (station_id, method), part in scored.groupby(["station_id", "method"]):
        per_station.append({"station_id": station_id, "method": method, "information_set": INFO[method],
                            **evaluate_arrays(part.prediction, part.target, np.ones(len(part), bool))})
    for method, part in scored.groupby("method"):
        summary.append({"method": method, "information_set": INFO[method],
                        **evaluate_arrays(part.prediction, part.target, np.ones(len(part), bool))})
    per_station, summary = pd.DataFrame(per_station), pd.DataFrame(summary)
    if len(summary) != len(METHODS) or not (summary.n == summary.n.iloc[0]).all():
        raise AssertionError("S4 methods do not share identical observed test pairs")
    spatial = summary.set_index("method").loc[["idw", "gp_rbf", "ordinary_kriging"]]
    best = str(spatial.mae.idxmin())
    a = scored.loc[scored.method.eq("stpignn_known")]
    b = scored.loc[scored.method.eq(best)]
    ci = paired_ci(a, b, int(CFG["bootstrap_seed"]), int(CFG["bootstrap_replicates"]))
    known = summary.set_index("method").loc["stpignn_known"]
    competitor = summary.set_index("method").loc[best]
    if ci[0][0] <= 0 <= ci[1][0]:
        verdict = "TIE"
    elif known.mae < competitor.mae and known.r2 > competitor.r2 and ci[1][0] < 0:
        verdict = "WIN"
    else:
        verdict = "LOSS"
    station_mae = per_station.set_index(["station_id", "method"]).mae
    paired = station_mae.xs("stpignn_known", level="method") - station_mae.xs(best, level="method")
    p_value = float(wilcoxon(paired.to_numpy(), zero_method="wilcox", alternative="two-sided").pvalue)
    out = REPO_ROOT / "results"
    raw.to_parquet(out / "loso_predictions_v2c.parquet", index=False)
    pd.DataFrame(curves).to_csv(out / "loso_curves_v2c.csv", index=False)
    pd.DataFrame(fallback_rows).to_csv(out / "loso_fallbacks_v2c.csv", index=False)
    pd.DataFrame(unscored).to_csv(out / "loso_unscored_folds_v2c.csv", index=False)
    per_station.to_csv(out / "loso_per_station_v2c.csv", index=False)
    summary.to_csv(out / "loso_summary_v2c.csv", index=False)
    details = {"timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
               "source_git_commit": source_commit, "script": "scripts/evaluate_loso_v2c.py",
               "config": "configs/loso_v2.yaml", "data_config": "configs/data_v2.yaml",
               "seeds": CFG["seeds"], "folds_considered": len(stations),
               "folds_scored": len(stations) - len(unscored),
               "unscored_station_ids": [int(row["station_id"]) for row in unscored],
               "n_scored_pairs_per_method": int(len(a)), "best_spatial_baseline": best,
               "paired_utc_day_bootstrap_replicates": int(CFG["bootstrap_replicates"]),
               "mae_difference_stpignn_minus_best": float(known.mae - competitor.mae),
               "r2_difference_stpignn_minus_best": float(known.r2 - competitor.r2),
               "mae_difference_ci": [ci[0][0], ci[1][0]],
               "r2_difference_ci": [ci[0][1], ci[1][1]],
               "wilcoxon_p_over_stations": p_value, "verdict": verdict,
               "runtime_seconds": time.perf_counter() - started, "hardware": str(device)}
    (out / "loso_decision_v2c.json").write_text(json.dumps(details, indent=2) + "\n")
    print(json.dumps(details, indent=2), flush=True)


if __name__ == "__main__":
    main()
