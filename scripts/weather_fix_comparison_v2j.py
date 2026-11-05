"""Numerical old shifted-weather versus corrected-weather comparison."""
from __future__ import annotations

import glob
import numpy as np
import pandas as pd

from scripts.benchmark_v2j import NAMES
from scripts.summarize_benchmark_v2j import paired_ci
from src.stpignn.paths import REPO_ROOT


def predictions(horizon, suffix):
    paths = glob.glob(str(REPO_ROOT / f"results/benchmark_predictions_h{horizon}_*_{suffix}.parquet"))
    frames = [pd.read_parquet(path) for path in paths if "provisional" not in path]
    if not frames:
        raise RuntimeError(f"No {suffix} predictions h={horizon}")
    raw = pd.concat(frames, ignore_index=True)
    count = raw.groupby(["model", "target_time_utc", "station_id"]).seed.nunique()
    expected = raw.groupby("model").seed.nunique()
    if not (count.groupby(level=0).min() == expected).all():
        raise AssertionError(f"Incomplete seed coverage {suffix} h={horizon}")
    if any(expected.get(name, 0) != 5 for name in NAMES):
        raise AssertionError(f"Missing neural seeds {suffix} h={horizon}")
    mean = raw.groupby(["model", "target_time_utc", "station_id"], as_index=False).agg(
        target_ug_m3=("target_ug_m3", "first"), prediction_ug_m3=("prediction_ug_m3", "mean"))
    pivot = mean.pivot(index=["target_time_utc", "station_id", "target_ug_m3"],
                       columns="model", values="prediction_ug_m3").sort_index()
    if pivot.isna().any().any():
        raise AssertionError(f"Unequal scored pairs {suffix} h={horizon}")
    return pivot


def win(pivot, model, horizon):
    if model in ("persistence", "same_hour_yesterday"):
        return 0
    y = pivot.index.get_level_values("target_ug_m3").to_numpy(float)
    dates = pd.to_datetime(pivot.index.get_level_values("target_time_utc"), utc=True).date
    return int(all(paired_ci(pivot[model].to_numpy(), pivot[base].to_numpy(), y,
                             dates, 4303+horizon, 2000)[1][1] < 0
                   for base in ("persistence", "same_hour_yesterday")))


def main():
    rows = []
    old = pd.read_csv(REPO_ROOT / "results/benchmark_v2g.csv")
    new = pd.read_csv(REPO_ROOT / "results/benchmark_v2j.csv")
    keys = ["horizon_hours", "model"]
    joined = old.merge(new, on=keys, suffixes=("_shifted", "_corrected"), validate="one_to_one")
    if len(joined) != len(old) or len(joined) != len(new):
        raise AssertionError("Old/new benchmark model-horizon coverage differs")
    pivots = {}
    for horizon in (1, 3, 6, 12, 24):
        a, b = predictions(horizon, "v2g"), predictions(horizon, "v2j")
        if not a.index.equals(b.index) or set(a.columns) != set(b.columns):
            raise AssertionError(f"Old/new test population differs h={horizon}")
        pivots[horizon] = a, b
    for row in joined.itertuples(index=False):
        a, b = pivots[row.horizon_hours]
        rows.append(dict(comparison_type="benchmark", horizon_hours=row.horizon_hours, model=row.model,
                         old_mae=row.test_mae_ug_m3_shifted, old_r2=row.test_r2_shifted,
                         new_mae=row.test_mae_ug_m3_corrected, new_r2=row.test_r2_corrected,
                         old_verdict=win(a, row.model, row.horizon_hours),
                         new_verdict=win(b, row.model, row.horizon_hours)))
    for category, old_name, new_name, keys, mae, r2, verdict in (
        ("lambda", "lambda_sweep_v2g.csv", "lambda_check_v2j.csv",
         ["horizon_hours", "model", "lambda"], "test_mae_ug_m3", "test_r2", "physics_helps_at_horizon"),
        ("loso", "loso_summary_v2g.csv", "loso_summary_v2j.csv",
         ["anchor", "method", "seasonal_bias_corrected"], "mae", "r2", "verdict"),
        ("dem", "dem_study_v2h.csv", "dem_study_v2j.csv",
         ["horizon_hours", "model", "variant", "record_type"], "test_mae_ug_m3", "test_r2", "met"),
    ):
        left = pd.read_csv(REPO_ROOT / "results" / old_name)
        right = pd.read_csv(REPO_ROOT / "results" / new_name)
        if category == "lambda":
            left = left[left.horizon_hours.isin([1, 24]) & left["lambda"].isin([0, .06, .3, 1])]
        if category == "dem":
            left = left[left.record_type.eq("paired_bootstrap")]
            right = right[right.record_type.eq("paired_bootstrap")]
        matched = left.merge(right, on=keys, how="outer", suffixes=("_shifted", "_corrected"), validate="one_to_one")
        if category == "lambda" and (len(matched) != len(left) or len(matched) != len(right)):
            raise AssertionError(f"Old/new {category} coverage differs")
        for item in matched.to_dict("records"):
            entry = {"comparison_type": category}
            entry.update({key: item[key] for key in keys})
            entry.update(old_mae=item.get(mae+"_shifted"), old_r2=item.get(r2+"_shifted"),
                         new_mae=item.get(mae+"_corrected"), new_r2=item.get(r2+"_corrected"),
                         old_verdict=item.get(verdict+"_shifted"),
                         new_verdict=item.get(verdict+"_corrected"))
            rows.append(entry)
        if category == "dem":
            for horizon in (1, 24):
                verdicts = []
                for frame in (left, right):
                    chosen = frame.loc[frame.horizon_hours.eq(horizon), "best_validation_model"].iloc[0]
                    cells = frame[frame.horizon_hours.eq(horizon) & frame.model.eq(chosen)]
                    verdicts.append(int(bool(cells.met.astype(bool).all())))
                rows.append(dict(comparison_type="dem_criterion", horizon_hours=horizon,
                                 old_verdict=verdicts[0], new_verdict=verdicts[1]))
    pd.DataFrame(rows).to_csv(REPO_ROOT / "results/weather_fix_comparison_v2j.csv", index=False)


if __name__ == "__main__":
    main()
