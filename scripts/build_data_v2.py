"""Build UTC-aligned, train-fitted, observed-target station tensors."""
from __future__ import annotations

import datetime as dt
import json
import subprocess
import time
import math
from pathlib import Path

import numpy as np
import pandas as pd

from src.stpignn.data_v2 import build
from src.stpignn.paths import REPO_ROOT


def json_safe(value):
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(v) for v in value]
    if isinstance(value, (float, np.floating)) and not math.isfinite(float(value)):
        return None
    if isinstance(value, np.generic):
        return value.item()
    return value


def main():
    start = time.perf_counter()
    config = REPO_ROOT / "configs/data_v2.yaml"
    data, extra = build(config)
    out = REPO_ROOT / "results"
    out.mkdir(exist_ok=True)
    meta = {"timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
            "source_git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True).strip(),
            "script": "scripts/build_data_v2.py", "config": "configs/data_v2.yaml", "seed": data.config["seed"]}
    split_report = dict(meta)
    split_report["requested_boundaries"] = {k: v for k, v in data.config.items() if k.endswith("_utc")}
    split_report["horizons"] = {}
    for horizon in data.config["horizons_hours"]:
        by_split = {}
        for name in data.split_masks:
            idx = data.target_indices(name, int(horizon))
            mask = data.observed_mask[idx]
            scored_times = data.times[idx]
            by_split[name] = {"scored_target_hours": len(idx), "scored_pairs": int(mask.sum()),
                              "first_scored_utc": scored_times.min().isoformat() if len(idx) else None,
                              "last_scored_utc": scored_times.max().isoformat() if len(idx) else None}
        split_report["horizons"][str(horizon)] = by_split
    split_report["gap_hours"] = {
        "train_to_validation": (pd.Timestamp(data.config["validation_start_utc"]) - pd.Timestamp(data.config["train_end_utc"])).total_seconds() / 3600 - 1,
        "validation_to_test": (pd.Timestamp(data.config["test_start_utc"]) - pd.Timestamp(data.config["validation_end_utc"])).total_seconds() / 3600 - 1}
    (out / "splits_v2.json").write_text(json.dumps(split_report, indent=2) + "\n")
    registry = dict(meta, channels=data.feature_registry,
                    physical_wind_tensor={"source": "raw weather wind_direction_10m", "units": "degrees FROM north, clockwise",
                                          "shape": list(data.raw_wind_degrees.shape)})
    (out / "feature_registry.json").write_text(json.dumps(registry, indent=2) + "\n")

    station = extra["station_table"].copy()
    prior = out / "stations.csv"
    if prior.exists():
        historical_clusters = pd.read_csv(prior)[["station_id", "cluster"]]
        station = station.merge(historical_clusters, on="station_id", how="left")
    else:
        station["cluster"] = pd.NA
    for name, time_mask in data.split_masks.items():
        station[f"observed_{name}_hours"] = data.observed_mask[time_mask].sum(axis=0)
    station = station.rename(columns={"lat": "latitude", "lon": "longitude", "elevation_true": "srtm_elevation_m"})
    station[["station_id", "latitude", "longitude", "node_index", "cluster", "srtm_elevation_m",
             "observed_train_hours", "observed_validation_hours", "observed_test_hours"]].to_csv(out / "stations_v2.csv", index=False)

    breakdown = []
    years = data.times.year.to_numpy()
    for name, time_mask in data.split_masks.items():
        for year in np.unique(years[time_mask]):
            ym = time_mask & (years == year)
            for j, station_id in enumerate(data.station_ids):
                for tier in ("O", "R", "I", "C", "D"):
                    count = int(np.sum(data.imputation_tier[ym, j] == tier))
                    if count:
                        breakdown.append({"split": name, "year": int(year), "station_id": int(station_id),
                                          "tier": tier, "hours": count,
                                          "train_nonobserved_fraction": float(np.mean(data.imputation_tier[data.split_masks["train"], j] != "O"))})
    pd.DataFrame(breakdown).to_csv(out / "imputation_breakdown_v2.csv", index=False)
    fit_report = dict(meta, fit=data.fit, provenance=extra["provenance"])
    fit_report["runtime_seconds"] = time.perf_counter() - start
    (out / "data_v2_fit.json").write_text(json.dumps(json_safe(fit_report), indent=2, allow_nan=False) + "\n")
    np.savez_compressed(REPO_ROOT / data.config["output_npz"],
                        times_ns=data.times.asi8, station_ids=data.station_ids,
                        node_indices=data.node_indices, coordinates=data.coordinates,
                        elevation_m=data.elevation_m, features=data.features,
                        raw_wind_degrees=data.raw_wind_degrees,
                        observed_target=data.observed_target,
                        observed_mask=data.observed_mask,
                        imputed_target=data.imputed_target,
                        imputation_tier=data.imputation_tier)
    print(json.dumps({"split_report": split_report, "provenance": extra["provenance"],
                      "target_fit": {k: v for k, v in data.fit.items() if k.startswith("target_") or k.startswith("legacy_")}}, indent=2))


if __name__ == "__main__":
    main()
