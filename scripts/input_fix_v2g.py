"""W1: cap pollutant inputs, align PM2.5 lag/target scaling, and audit AR."""
from __future__ import annotations

import datetime as dt
import json
import subprocess

import numpy as np
import pandas as pd
import yaml
from sklearn.linear_model import LinearRegression

from src.stpignn.evaluation import evaluate_arrays
from src.stpignn.paths import REPO_ROOT


def main():
    cfg = yaml.safe_load((REPO_ROOT / "configs/data_v2.yaml").read_text())
    z = np.load(REPO_ROOT / "results/data_v2_arrays.npz")
    old_fit = json.loads((REPO_ROOT / "results/data_v2_fit.json").read_text())["fit"]
    times = pd.DatetimeIndex(pd.to_datetime(z["times_ns"], utc=True))
    train = np.asarray((times >= pd.Timestamp(cfg["train_start_utc"])) &
                       (times <= pd.Timestamp(cfg["train_end_utc"])))
    test = np.asarray((times >= pd.Timestamp(cfg["test_start_utc"])) &
                      (times <= pd.Timestamp(cfg["test_end_utc"])))
    features = z["features"].copy()
    pm25 = np.clip(z["imputed_target"], 0, 500)
    pm10 = np.clip(features[:, :, 1] * old_fit["feature_stds"][1] +
                   old_fit["feature_means"][1], 0, 500)
    y = z["observed_target"]
    y_log_train = np.log1p(y[train][np.isfinite(y[train])])
    mean25, sd25 = float(y_log_train.mean()), float(y_log_train.std())
    mean10, sd10 = float(np.log1p(pm10[train]).mean()), float(np.log1p(pm10[train]).std())
    features[:, :, 0] = (np.log1p(pm25) - mean25) / sd25
    features[:, :, 1] = (np.log1p(pm10) - mean10) / sd10
    out = REPO_ROOT / "results"
    np.savez_compressed(out / "data_v2g_arrays.npz", **{k: z[k] for k in z.files if k not in
                        ("features", "imputed_target")}, features=features,
                        imputed_target=pm25)
    channel_stats = []
    for channel, values, mean, sd in (("pm25_lag", pm25, mean25, sd25),
                                      ("pm10_lag", pm10, mean10, sd10)):
        channel_stats.append({"channel": channel, "train_mean_ug_m3": float(values[train].mean()),
                              "train_sd_ug_m3": float(values[train].std()),
                              "train_max_ug_m3": float(values[train].max()),
                              "log1p_mean": mean, "log1p_sd": sd,
                              "train_above_500": int((values[train] > 500).sum())})
    pd.DataFrame(channel_stats).to_csv(out / "input_channels_v2g.csv", index=False)
    mask = z["observed_mask"]
    history = int(cfg["history_hours"])
    train[:history] = False
    test[:history] = False
    i_train, j_train = np.where(mask & train[:, None])
    i_test, j_test = np.where(mask & test[:, None])
    x_train = features[i_train - 1, j_train, 0]
    x_test = features[i_test - 1, j_test, 0]
    ar = LinearRegression().fit(x_train[:, None], y[i_train, j_train])
    pred = ar.predict(x_test[:, None])
    ar_score = evaluate_arrays(pred, y[i_test, j_test], np.ones(len(pred), bool))
    observed_lag = pd.DataFrame(y).ffill().to_numpy(dtype=np.float32)[i_test - 1, j_test]
    station_mean = np.nanmean(y[train], axis=0)
    station_mean = np.where(np.isfinite(station_mean), station_mean, np.nanmean(y[train]))
    persistence = np.where(np.isfinite(observed_lag), observed_lag, station_mean[j_test])
    pers_score = evaluate_arrays(persistence, y[i_test, j_test], np.ones(len(pred), bool))
    ratio = ar_score["mae"] / pers_score["mae"]
    report = {"timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
              "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True).strip(),
              "script": "scripts/input_fix_v2g.py", "config": "configs/data_v2.yaml",
              "seed": 42, "horizon_hours": 1, "train_pairs": len(i_train), "test_pairs": len(i_test),
              "cap_ug_m3": 500, "channels": channel_stats,
              "ar_with_lag": ar_score, "persistence": pers_score,
              "ar_to_persistence_mae_ratio": ratio,
              "alignment_bug_possible": bool(ratio > 1.25)}
    (out / "input_fix_v2g.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
