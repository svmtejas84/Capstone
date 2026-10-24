"""Diagnostic legacy checkpoint replay on data_v2 observed test hours.

Uses explicit 13->16 feature and station-graph adapters. The checkpoint was
trained with different full-period scaling and 64 city partitions; these
numbers are protocol diagnostics, not like-for-like retrained model scores.
"""
from __future__ import annotations

import datetime as dt
import json
import subprocess
import time

import numpy as np
import pandas as pd
import torch
import yaml

from gnn.checkpoint import load_stpignn_checkpoint
from src.stpignn.evaluation import evaluate_arrays
from src.stpignn.paths import REPO_ROOT
from src.stpignn.station_graph import directed_knn_graph

RAW_MASTER = ["pm2_5", "pm10", "nitrogen_dioxide", "sulphur_dioxide", "carbon_monoxide",
              "wind_speed_10m", "wind_direction_10m", "wind_gusts_10m", "temperature_2m",
              "relative_humidity_2m", "surface_pressure"]
NEW_INDEX = [0, 1, 2, 3, 4, 5, None, 6, 7, 8, 9]


def main():
    began = time.perf_counter()
    cfg = yaml.safe_load((REPO_ROOT / "configs/data_v2.yaml").read_text())
    gate = yaml.safe_load((REPO_ROOT / "configs/gate_v2.yaml").read_text())
    z = np.load(REPO_ROOT / "results/data_v2_arrays.npz")
    fit = json.loads((REPO_ROOT / "results/data_v2_fit.json").read_text())["fit"]
    times = pd.DatetimeIndex(pd.to_datetime(z["times_ns"], utc=True))
    test = np.asarray((times >= pd.Timestamp(cfg["test_start_utc"])) &
                      (times <= pd.Timestamp(cfg["test_end_utc"])) & z["observed_mask"].any(axis=1))
    history = int(cfg["history_hours"])
    horizon = int(gate["horizon_hours"])
    test[:history - 1 + horizon] = False
    target_hours = np.flatnonzero(test)
    master_columns = RAW_MASTER + [name + "_scaled" for name in RAW_MASTER]
    master = pd.read_parquet(REPO_ROOT / "data/processed/graph/master_scaled_checkpoint.parquet",
                             columns=master_columns)
    linear_map = {}
    for raw in RAW_MASTER:
        pair = master[[raw, raw + "_scaled"]].dropna().drop_duplicates()
        slope, intercept = np.polyfit(pair[raw].to_numpy(float), pair[raw + "_scaled"].to_numpy(float), 1)
        linear_map[raw] = {"slope": float(slope), "intercept": float(intercept)}
    del master
    rawfilled = z["features"] * np.asarray(fit["feature_stds"], dtype=np.float32) + np.asarray(fit["feature_means"], dtype=np.float32)
    channels = []
    for name, index in zip(RAW_MASTER, NEW_INDEX):
        value = z["raw_wind_degrees"][:, None].repeat(len(z["station_ids"]), axis=1) if index is None else rawfilled[:, :, index]
        channels.append((value * linear_map[name]["slope"] + linear_map[name]["intercept"]).astype(np.float32))
    feature11 = np.stack(channels, axis=-1)
    legacy16 = np.concatenate([feature11, feature11[:, :, [2, 3, 0, 1, 4]]], axis=-1)
    edge_index, length = directed_knn_graph(z["coordinates"], int(gate["station_graph_neighbours"]))
    edge_attr = torch.zeros(len(length), 16, dtype=torch.float32)
    edge_attr[:, 0] = length[:, 0]
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model, info = load_stpignn_checkpoint(REPO_ROOT / "citywide_stpignn_best.pt", device=device, eval_mode=True)
    edge_index, edge_attr = edge_index.to(device), edge_attr.to(device)
    pred_rows = []
    with torch.no_grad():
        for start in range(0, len(target_hours), 128):
            ids = target_hours[start:start + 128]
            cutoff = ids - horizon
            indices = cutoff[:, None] - np.arange(history - 1, -1, -1)[None, :]
            if np.any(indices > cutoff[:, None]):
                raise AssertionError("Legacy adapter used future input")
            x = torch.as_tensor(legacy16[indices].copy(), device=device)
            prediction = (model(x, edge_index, edge_attr) * 342.9356).cpu().numpy()
            mask = z["observed_mask"][ids]
            row, col = np.where(mask)
            pred_rows.append(pd.DataFrame({"target_time_utc": times[ids[row]].astype(str),
                                           "station_id": z["station_ids"][col],
                                           "target_ug_m3": z["observed_target"][ids[row], col],
                                           "prediction_ug_m3": prediction[row, col]}))
    frame = pd.concat(pred_rows, ignore_index=True)
    frame.to_parquet(REPO_ROOT / "results/legacy_checkpoint_v2_predictions.parquet", index=False)
    rows = []
    for station_id, group in [(None, frame)] + list(frame.groupby("station_id")):
        metrics = evaluate_arrays(group.prediction_ug_m3, group.target_ug_m3,
                                  np.ones(len(group), dtype=bool))
        rows.append({"scope": "pooled" if station_id is None else "station",
                     "station_id": station_id, **metrics})
    pd.DataFrame(rows).to_csv(REPO_ROOT / "results/legacy_checkpoint_v2_metrics.csv", index=False)
    report = {"timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
              "script": "scripts/evaluate_legacy_checkpoint_v2.py", "config": "configs/data_v2.yaml",
              "gate_config": "configs/gate_v2.yaml", "seed": cfg["seed"],
              "source_git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True).strip(),
              "checkpoint": "citywide_stpignn_best.pt", "checkpoint_epoch": info.epoch,
              "adapter": "13 train-only-scaled station channels -> legacy 16 full-period-scaled slots; 15-node kNN graph with length and zero road flags; strictly lagged input",
              "feature_linear_maps": linear_map, "test_pairs": len(frame),
              "runtime_seconds": time.perf_counter() - began}
    (REPO_ROOT / "results/legacy_checkpoint_v2_run.json").write_text(json.dumps(report, indent=2) + "\n")
    print(pd.DataFrame(rows).iloc[0].to_dict())
    print(json.dumps({k: v for k, v in report.items() if k != "feature_linear_maps"}, indent=2))


if __name__ == "__main__":
    main()
