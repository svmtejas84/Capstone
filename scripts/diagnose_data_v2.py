"""Describe raw observed-target tails and year coverage without data edits."""
import datetime as dt
import json
import subprocess
import pyarrow.parquet as pq

import numpy as np
import pandas as pd

from src.stpignn.paths import REPO_ROOT


def main():
    array = np.load(REPO_ROOT / "results/data_v2_arrays.npz")
    split = json.loads((REPO_ROOT / "results/splits_v2.json").read_text())
    times = pd.DatetimeIndex(pd.to_datetime(array["times_ns"], utc=True))
    observed = array["observed_target"]
    mask = array["observed_mask"]
    report = {"timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
              "script": "scripts/diagnose_data_v2.py", "config": "configs/data_v2.yaml", "seed": 42,
              "source_git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True).strip(),
              "year_counts": {}, "split_tails": {}}
    report["raw_station_source_rows"] = {
        path.name: pq.ParquetFile(path).metadata.num_rows
        for path in sorted((REPO_ROOT / "data/raw/stations").glob("*.parquet"))
        if path.name != "meta.parquet"
    }
    for year in np.unique(times.year):
        report["year_counts"][str(year)] = int(mask[times.year == year].sum())
    for name in ("train", "validation", "test"):
        a = pd.Timestamp(split["requested_boundaries"][f"{name}_start_utc"])
        b = pd.Timestamp(split["requested_boundaries"][f"{name}_end_utc"])
        values = observed[np.asarray((times >= a) & (times <= b))]
        values = values[np.isfinite(values)]
        report["split_tails"][name] = {"n": int(len(values)), "mean": float(np.mean(values)),
                                       "std": float(np.std(values)), "median": float(np.median(values)),
                                       "p95": float(np.quantile(values, .95)),
                                       "p99": float(np.quantile(values, .99)),
                                       "max": float(np.max(values)),
                                       "over_1000": int(np.sum(values > 1000)),
                                       "over_10000": int(np.sum(values > 10000))}
    (REPO_ROOT / "results/data_v2_diagnostics.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
