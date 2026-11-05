"""Build corrected-weather arrays with the unchanged v2g input transformation."""
from __future__ import annotations

import datetime as dt
import json
import subprocess

import numpy as np
import pandas as pd

from src.stpignn.data_v2 import build
from src.stpignn.paths import REPO_ROOT


def main():
    data, extra = build(REPO_ROOT / "configs/data_v2.yaml", weather_half_hour_rule=True)
    temperature = data.raw_values[:, 0, 7]
    profile = pd.Series(temperature).groupby(data.times.hour).mean()
    peak = int(profile.idxmax())
    if peak not in (8, 9, 10):
        raise RuntimeError(f"Corrected 2 m temperature peaks at {peak:02d}:00 UTC; stop")

    times = data.times
    train = data.split_masks["train"]
    features = data.features.copy()
    pm25 = np.clip(data.imputed_target, 0, 500)
    pm10 = np.clip(features[:, :, 1] * data.fit["feature_stds"][1] +
                   data.fit["feature_means"][1], 0, 500)
    y_train = data.observed_target[train]
    y_log_train = np.log1p(y_train[np.isfinite(y_train)])
    mean25, sd25 = float(y_log_train.mean()), float(y_log_train.std())
    log10 = np.log1p(pm10[train])
    mean10, sd10 = float(log10.mean()), float(log10.std())
    features[:, :, 0] = (np.log1p(pm25) - mean25) / sd25
    features[:, :, 1] = (np.log1p(pm10) - mean10) / sd10
    out = REPO_ROOT / "results"
    np.savez_compressed(out / "data_v2j_arrays.npz",
                        times_ns=times.asi8, station_ids=data.station_ids,
                        node_indices=data.node_indices, coordinates=data.coordinates,
                        elevation_m=data.elevation_m, features=features,
                        raw_wind_degrees=data.raw_wind_degrees,
                        observed_target=data.observed_target,
                        observed_mask=data.observed_mask,
                        imputed_target=pm25, imputation_tier=data.imputation_tier)
    report = {
        "timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True).strip(),
        "script": "scripts/build_data_v2j.py", "config": "configs/data_v2.yaml", "seed": data.config["seed"],
        "weather_half_hour_rule": True, "temperature_peak_utc_hour": peak,
        "temperature_profile_c": {str(k): float(v) for k, v in profile.items()},
        "edge_hours": {
            "first_raw_local": "2022-01-01 00:00 Asia/Kolkata",
            "first_corrected_record_utc": "2021-12-31 18:30 UTC",
            "first_complete_utc_hour": "2021-12-31 19:00 UTC",
            "first_model_hour": str(times[0]),
            "first_model_hour_records_utc": ["2021-12-31 23:30 UTC", "2022-01-01 00:30 UTC"],
            "last_model_hours_missing_pair": "2026-03-28 18:00–23:00 UTC; existing bounded forward-fill then train-median fallback",
        },
        "target_log1p_mean": mean25, "target_log1p_sd": sd25,
        "pm10_log1p_mean": mean10, "pm10_log1p_sd": sd10,
        "fit": data.fit, "provenance": extra["provenance"],
    }
    (out / "data_v2j_fit.json").write_text(json.dumps(report, indent=2, default=str) + "\n")
    print(json.dumps({"temperature_peak_utc_hour": peak, "output": "results/data_v2j_arrays.npz"}))


if __name__ == "__main__":
    main()
