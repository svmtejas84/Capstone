"""Compare cleaned v2 observed targets with saved old y_clean on matching keys."""
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
    old = pd.read_csv(REPO_ROOT / "results/old_vs_raw_pm25.csv", parse_dates=["time_utc"])
    z = np.load(REPO_ROOT / cfg["output_npz"])
    times = pd.DatetimeIndex(pd.to_datetime(z["times_ns"], utc=True))
    station = z["station_ids"]
    lookup = pd.MultiIndex.from_product([times, station], names=["time_utc", "station_id"])
    new = pd.DataFrame({"new_observed": z["observed_target"].reshape(-1)}, index=lookup).reset_index()
    overlap = old.merge(new, on=["station_id", "time_utc"], how="inner", validate="one_to_one")
    old_present = overlap.old_y_clean.notna()
    new_present = overlap.new_observed.notna()
    both = old_present & new_present
    disagree = old_present & (~new_present | ~np.isclose(overlap.old_y_clean.fillna(-1),
                                                          overlap.new_observed.fillna(-1),
                                                          rtol=1e-5, atol=1e-5))
    old_observed = overlap.old_status.eq("observed_tier")
    train = overlap.time_utc.between(pd.Timestamp(cfg["train_start_utc"]), pd.Timestamp(cfg["train_end_utc"]))
    train_values = z["observed_target"][(times >= pd.Timestamp(cfg["train_start_utc"])) &
                                         (times <= pd.Timestamp(cfg["train_end_utc"]))]
    valid = train_values[np.isfinite(train_values)]
    counts = pd.read_csv(REPO_ROOT / "results/cleaning_counts_v2.csv")
    report = {"script": "scripts/summarize_cleaning_v2.py", "config": "configs/data_v2.yaml",
              "seed": cfg["seed"], "timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
              "source_git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True).strip(),
              "overlap_raw_station_hours": len(overlap),
              "old_y_clean_present": int(old_present.sum()), "v2_observed_present_on_overlap": int(new_present.sum()),
              "both_present": int(both.sum()), "old_y_clean_vs_v2_observed_disagreements": int(disagree.sum()),
              "old_observed_tier_vs_v2_disagreements": int((disagree & old_observed).sum()),
              "train_old_y_clean_vs_v2_disagreements": int((disagree & train).sum()),
              "train_observed_mean_ug_m3": float(valid.mean()),
              "train_observed_sd_ug_m3": float(valid.std()),
              "train_observed_max_ug_m3": float(valid.max()),
              "train_pm25_rows_rejected_above_500": int(counts.loc[(counts.source == "station") &
                 (counts.parameter == "pm25") & (counts.split == "train") &
                 (counts.reason == "pm25_above_old_graph_cap"), "rows"].sum())}
    (REPO_ROOT / "results/cleaning_compare_v2.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
