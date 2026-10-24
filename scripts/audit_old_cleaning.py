"""Join raw PM2.5 hours to the old master and audit available cleaning code."""
from __future__ import annotations

import datetime as dt
import json
import subprocess

import numpy as np
import pandas as pd
import yaml

from src.stpignn.paths import REPO_ROOT


def main():
    cfg = yaml.safe_load((REPO_ROOT / "configs/data_v2.yaml").read_text())
    parts = []
    for path in sorted(REPO_ROOT.glob(cfg["raw_stations_glob"])):
        if path.name == "meta.parquet":
            continue
        frame = pd.read_parquet(path)
        frame = frame.loc[frame.parameter.eq("pm25"), ["station_id", "value"]].reset_index()
        frame["time_utc"] = pd.DatetimeIndex(pd.to_datetime(frame.time)).tz_convert("UTC").floor("h")
        parts.append(frame[["station_id", "time_utc", "value"]])
    raw = pd.concat(parts, ignore_index=True)
    raw["value"] = pd.to_numeric(raw.value, errors="coerce")
    raw = raw.dropna(subset=["station_id", "time_utc", "value"])
    raw = raw.groupby(["station_id", "time_utc"], observed=True).agg(
        raw_value=("value", "mean"), raw_rows=("value", "size")).reset_index()
    columns = ["time", "station_id", "parameter", "value", "observed_value", "y_clean",
               "is_imputed", "impute_tier"]
    old = pd.read_parquet(REPO_ROOT / "data/processed/graph/master_scaled_checkpoint.parquet", columns=columns)
    old = old.loc[old.parameter.eq("pm25"), columns].copy()
    old["time_utc"] = pd.DatetimeIndex(pd.to_datetime(old.time)).tz_localize("Asia/Kolkata").tz_convert("UTC").floor("h")
    old = old.rename(columns={"value": "old_value", "observed_value": "old_observed_value",
                              "y_clean": "old_y_clean", "is_imputed": "old_is_imputed",
                              "impute_tier": "old_impute_tier"})
    old = old.drop(columns=["time", "parameter"])
    old = old.drop_duplicates(["station_id", "time_utc"])
    joined = raw.merge(old, on=["station_id", "time_utc"], how="left", indicator=True, validate="one_to_one")
    joined["old_status"] = np.select(
        [joined._merge.eq("left_only"), joined.old_is_imputed.fillna(False).astype(bool),
         joined.old_observed_value.isna()],
        ["absent_from_master", "imputed_tier", "observed_value_missing"], default="observed_tier")
    joined["raw_differs_from_old_observed"] = (~np.isclose(joined.raw_value, joined.old_observed_value,
                                                           equal_nan=False, rtol=1e-5, atol=1e-5))
    joined = joined.drop(columns="_merge")
    out = REPO_ROOT / "results"
    joined.to_csv(out / "old_vs_raw_pm25.csv", index=False)
    ranges = joined.groupby("old_status").agg(rows=("raw_value", "size"),
        raw_min=("raw_value", "min"), raw_max=("raw_value", "max")).reset_index()
    train_end = pd.Timestamp(cfg["train_end_utc"])
    train_start = pd.Timestamp(cfg["train_start_utc"])
    train = joined.loc[joined.time_utc.between(train_start, train_end)]
    extreme = train.loc[train.raw_value > 10000]
    metadata = {"script": "scripts/audit_old_cleaning.py", "config": "configs/data_v2.yaml",
                "seed": cfg["seed"], "timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
                "source_git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True).strip(),
                "raw_hour_pairs": len(joined), "raw_train_gt_10000_pairs": len(extreme),
                "raw_train_gt_10000_old_observed": int(extreme.old_status.eq("observed_tier").sum()),
                "raw_train_gt_10000_old_absent": int(extreme.old_status.eq("absent_from_master").sum()),
                "raw_train_gt_10000_old_imputed": int(extreme.old_status.eq("imputed_tier").sum()),
                "raw_train_gt_10000_old_y_clean_max": float(extreme.old_y_clean.max()) if len(extreme) else None}
    (out / "old_filtering_audit.json").write_text(json.dumps(metadata, indent=2) + "\n")
    lines = ["# Old filtering audit", "", f"Source: `{metadata['script']}`, config `{metadata['config']}`, seed {metadata['seed']}, source commit `{metadata['source_git_commit']}`, {metadata['timestamp_utc']}.", "",
             "| Rule | File:line | Type | Parameters | Rows affected |", "|---|---|---|---|---:|",
             "| Non-null station ID, parameter, value; numeric conversion; hourly mean | `scripts/build_gapfill_derived_layer.py:73-100` | per-row/aggregation | no outlier ceiling | see joined counts below |",
             "| Gap-fill linear interpolation | `scripts/build_gapfill_derived_layer.py:246-253` | fitted across full timeline | limit 24, both directions | see old report: PM2.5 temporal-linear 9,609 |",
             "| Climatology and median gap fill | `scripts/build_gapfill_derived_layer.py:279-315` | fitted across full timeline | hour×day medians; station median | see old report: PM2.5 climatology 239,734 |",
             "| PM2.5 graph-node feature sanitation | `scripts/build_graph_tensors.py:154-165,178-195` | per-row after data-dependent kg/m³ inference | clip to [0,500], nonfinite/zero replaced by full-data median | not applied to canonical station target; count in this join N/A |",
             "| Humidity / temperature graph-node sanitation | `scripts/build_graph_tensors.py:183-185` | per-row | humidity [0,100]%, temperature [10,50]°C | not applied to canonical station target; count N/A |",
             "| Station feature interpolation and global medians | `scripts/sync_on_entry.py:335-363` | fitted across full timeline | bidirectional interpolation, ffill/bfill, column median | count N/A: separate master writer |",
             "| `y_clean` in saved master | source writer absent from permitted scripts | UNKNOWN | empirical range [0,250], transformation not inferable from these files | see `old_vs_raw_pm25.csv` |", "",
             "## Raw-to-master join by station and UTC hour", "",
             "| Old status | Raw hourly pairs | Raw min | Raw max |", "|---|---:|---:|---:|"]
    for row in ranges.itertuples(index=False):
        lines.append(f"| {row.old_status} | {row.rows} | {row.raw_min:.6f} | {row.raw_max:.6f} |")
    lines += ["", f"Among {len(extreme)} raw train station-hours above 10,000 µg/m³, {metadata['raw_train_gt_10000_old_observed']} remain old observed-tier rows, {metadata['raw_train_gt_10000_old_imputed']} are old imputed-tier rows, and {metadata['raw_train_gt_10000_old_absent']} are absent. The old saved `y_clean` reaches {metadata['raw_train_gt_10000_old_y_clean_max']} on these rows. This does not establish the undocumented `y_clean` rule.", ""]
    (out / "old_filtering_audit.md").write_text("\n".join(lines))
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
