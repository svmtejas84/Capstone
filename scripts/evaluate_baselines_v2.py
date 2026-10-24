"""Observed-only, common-mask non-neural forecast baselines for persistence gate."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import time

import numpy as np
import pandas as pd
import yaml
from sklearn.linear_model import Ridge

from src.stpignn.evaluation import evaluate_arrays
from src.stpignn.paths import REPO_ROOT


def _train_climatology(target, times, train_mask):
    n = target.shape[1]
    table = np.full((168, n), np.nan, dtype=np.float64)
    keys = times.hour.to_numpy() * 7 + times.dayofweek.to_numpy()
    for key in range(168):
        arr = target[train_mask & (keys == key)]
        if len(arr):
            with np.errstate(all="ignore"):
                table[key] = np.nanmedian(arr, axis=0)
    station_means = np.nanmean(target[train_mask], axis=0)
    global_mean = float(np.nanmean(target[train_mask]))
    station_means = np.where(np.isfinite(station_means), station_means, global_mean)
    return table, station_means, global_mean


def _pairs(target, mask, time_mask, history, horizon):
    eligible = time_mask.copy()
    eligible[:history - 1 + horizon] = False
    return np.where(mask & eligible[:, None])


def main():
    started = time.perf_counter()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/gate_v2.yaml")
    parser.add_argument("--output-prefix", default="v2")
    args = parser.parse_args()
    cfg = yaml.safe_load((REPO_ROOT / args.config).read_text())
    data_cfg = yaml.safe_load((REPO_ROOT / "configs/data_v2.yaml").read_text())
    z = np.load(REPO_ROOT / "results/data_v2_arrays.npz")
    times = pd.DatetimeIndex(pd.to_datetime(z["times_ns"], utc=True))
    target = z["observed_target"]
    observed = z["observed_mask"]
    features = z["features"]
    station_ids = z["station_ids"]
    horizon = int(cfg["horizon_hours"])
    history = int(data_cfg["history_hours"])
    train_mask = np.asarray((times >= pd.Timestamp(data_cfg["train_start_utc"])) &
                            (times <= pd.Timestamp(data_cfg["train_end_utc"])))
    test_mask = np.asarray((times >= pd.Timestamp(data_cfg["test_start_utc"])) &
                           (times <= pd.Timestamp(data_cfg["test_end_utc"])))
    table, station_means, global_mean = _train_climatology(target, times, train_mask)
    train_i, train_j = _pairs(target, observed, train_mask, history, horizon)
    test_i, test_j = _pairs(target, observed, test_mask, history, horizon)
    y_train = target[train_i, train_j]
    regression_first_feature = 5 if cfg.get("ridge_weather_static_only", False) else 1
    x_train = features[train_i - horizon, train_j, regression_first_feature:]
    regression = Ridge(alpha=float(cfg["non_neural_regression_alpha"]))
    regression.fit(x_train, y_train)
    x_test = features[test_i - horizon, test_j, regression_first_feature:]
    regression_pred = regression.predict(x_test)

    cutoff = test_i - horizon
    history_frame = pd.DataFrame(target).ffill().to_numpy(dtype=np.float32)
    last_value = history_frame[cutoff, test_j]
    persistence_fallback = ~np.isfinite(last_value)
    persistence = np.where(persistence_fallback, station_means[test_j], last_value)

    key = times[test_i].hour.to_numpy() * 7 + times[test_i].dayofweek.to_numpy()
    climatology = table[key, test_j]
    climatology = np.where(np.isfinite(climatology), climatology, station_means[test_j])
    station_mean = station_means[test_j]

    xy = z["coordinates"].astype(float)
    distance = np.linalg.norm(xy[:, None, :] - xy[None, :, :], axis=-1)
    weights = 1.0 / np.maximum(distance, 1.0) ** float(cfg["idw_power"])
    np.fill_diagonal(weights, 0.0)
    readings = target[cutoff]
    known = np.isfinite(readings)
    w = weights[test_j] * known
    numerator = (w * np.nan_to_num(readings, nan=0.0)).sum(axis=1)
    denominator = w.sum(axis=1)
    idw_fallback = denominator <= 0
    idw = np.divide(numerator, denominator, out=station_mean.copy(), where=denominator > 0)

    pred = {"persistence": persistence, "climatology_hod_dow": climatology,
            "station_train_mean": station_mean, "idw_known_at_t": idw,
            "ridge_meteorology_static": regression_pred}
    truth = target[test_i, test_j]
    frame = pd.DataFrame({"target_time_utc": times[test_i].astype(str),
                          "input_cutoff_utc": times[cutoff].astype(str),
                          "station_id": station_ids[test_j], "node_index": z["node_indices"][test_j],
                          "target_ug_m3": truth})
    for method, values in pred.items():
        frame[method + "_ug_m3"] = values
    frame.to_parquet(REPO_ROOT / f"results/baselines_{args.output_prefix}_predictions.parquet", index=False)

    rows = []
    for method, values in pred.items():
        pooled = evaluate_arrays(values, truth, np.ones_like(truth, dtype=bool))
        rows.append({"method": method, "scope": "pooled", "station_id": None, **pooled})
        for j, station_id in enumerate(station_ids):
            selected = test_j == j
            if selected.any():
                metric = evaluate_arrays(values[selected], truth[selected], np.ones(selected.sum(), dtype=bool))
                rows.append({"method": method, "scope": "station", "station_id": int(station_id), **metric})
    pd.DataFrame(rows).to_csv(REPO_ROOT / f"results/baselines_{args.output_prefix}_metrics.csv", index=False)
    report = {"timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
              "script": "scripts/evaluate_baselines_v2.py", "config": args.config,
              "data_config": "configs/data_v2.yaml", "seed": cfg["seed"],
              "source_git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True).strip(),
              "horizon_hours": horizon, "test_pairs": len(truth),
              "train_pairs_for_regression": len(y_train),
              "persistence_fallback_pairs": int(persistence_fallback.sum()),
              "idw_fallback_pairs": int(idw_fallback.sum()),
              "train_target_mean": float(np.mean(y_train)),
              "regression_feature_indices": list(range(regression_first_feature, features.shape[-1])),
              "regression_coefficients": regression.coef_.tolist(),
              "runtime_seconds": time.perf_counter() - started}
    (REPO_ROOT / f"results/baselines_{args.output_prefix}_run.json").write_text(json.dumps(report, indent=2) + "\n")
    print(pd.DataFrame(rows).query('scope == "pooled"').to_string(index=False))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
