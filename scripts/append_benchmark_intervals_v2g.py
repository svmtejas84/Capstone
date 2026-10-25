"""Append saved-prediction paired intervals to the existing v2g benchmark report."""
from __future__ import annotations

import datetime as dt
import glob
import subprocess

import numpy as np
import pandas as pd

from scripts.summarize_benchmark_v2g import paired_ci
from src.stpignn.paths import REPO_ROOT

HORIZONS = (1, 3, 6, 12, 24)
MODELS = ("stpignn_original", "gine_gru_wind", "adaptive_graph_st", "stpignn_v2",
          "stpignn_lambda0", "stpignn_laplacian")
BASELINES = ("persistence", "same_hour_yesterday")
MARKER = "## Step 4g-2: paired reference intervals"


def main():
    report_path = REPO_ROOT / "results/benchmark_v2g.md"
    old = report_path.read_text()
    if MARKER in old:
        raise RuntimeError("Intervals already appended; preserve the previous report")
    rows = []
    for horizon in HORIZONS:
        paths = glob.glob(str(REPO_ROOT / f"results/benchmark_predictions_h{horizon}_*_v2g.parquet"))
        paths = [path for path in paths if "_provisional_v2g.parquet" not in path]
        data = pd.concat([pd.read_parquet(path) for path in paths], ignore_index=True)
        data = data[data.model.isin(MODELS + BASELINES)]
        key = ["model", "target_time_utc", "station_id"]
        counts = data.groupby(key, sort=False).seed.nunique().groupby(level=0).min()
        for model in MODELS:
            if counts[model] != 5:
                raise AssertionError(f"Missing seeds h={horizon} {model}")
        pooled = data.groupby(key, as_index=False).agg(target_ug_m3=("target_ug_m3", "first"),
                                                        prediction_ug_m3=("prediction_ug_m3", "mean"))
        pivot = pooled.pivot(index=["target_time_utc", "station_id", "target_ug_m3"],
                             columns="model", values="prediction_ug_m3")
        if pivot.isna().any().any():
            raise AssertionError(f"Unequal test masks h={horizon}")
        y = pivot.index.get_level_values("target_ug_m3").to_numpy(float)
        dates = pd.to_datetime(pivot.index.get_level_values("target_time_utc"), utc=True).date
        for model in MODELS:
            for baseline in BASELINES:
                dmae, ci, _, _ = paired_ci(pivot[model].to_numpy(float),
                    pivot[baseline].to_numpy(float), y, dates, 4303 + horizon, 2000)
                rows.append({"horizon_hours": horizon, "model": model, "reference": baseline,
                             "delta_mae_ug_m3": dmae, "ci_low": ci[0], "ci_high": ci[1],
                             "ci_width_ug_m3": ci[1] - ci[0]})
    lines = [old.rstrip(), "", MARKER, "",
             f"Source `scripts/append_benchmark_intervals_v2g.py`, saved W2 predictions, "
             f"config `configs/benchmark_v2g.yaml`, seeds [11,23,37,51,79], "
             f"commit `{subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO_ROOT,text=True).strip()}`, "
             f"{dt.datetime.now(dt.timezone.utc).isoformat()}.", "",
             "ΔMAE is model minus reference in µg/m³; negative favors the model. "
             "Intervals resample paired UTC days 2,000 times.", "",
             "| Horizon (h) | Model | Reference | ΔMAE (µg/m³) | 95% CI (µg/m³) | CI width (µg/m³) |",
             "|---:|---|---|---:|---:|---:|"]
    for row in rows:
        lines.append(f"| {row['horizon_hours']} | {row['model']} | {row['reference']} | "
                     f"{row['delta_mae_ug_m3']:+.6f} | [{row['ci_low']:+.6f}, {row['ci_high']:+.6f}] | "
                     f"{row['ci_width_ug_m3']:.6f} |")
    lines += ["", f"Multiplicity note: {len(rows)} model-horizon-reference comparisons were made "
              f"({len(MODELS)} models × {len(HORIZONS)} horizons × {len(BASELINES)} references). "
              "These are nominal 95% intervals; no familywise or false-discovery adjustment was applied.", ""]
    report_path.write_text("\n".join(lines))
    print(f"Appended {len(rows)} comparisons to {report_path}")


if __name__ == "__main__":
    main()
