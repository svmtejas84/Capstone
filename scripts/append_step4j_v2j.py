"""Append the fixed corrected-weather Step 4j result tables once."""
from __future__ import annotations

import datetime as dt
import json
import subprocess

import pandas as pd

from src.stpignn.paths import REPO_ROOT


def fmt(value, digits=3):
    return f"{value:.{digits}f}"


def main():
    paper = REPO_ROOT / "claude_paper.md"
    existing = paper.read_text()
    if "## Step 4j — corrected weather timestamps" in existing:
        raise RuntimeError("Step 4j already appended")
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True).strip()
    fit = json.loads((REPO_ROOT / "results/data_v2j_fit.json").read_text())
    benchmark = pd.read_csv(REPO_ROOT / "results/benchmark_v2j.csv")
    comparison = pd.read_csv(REPO_ROOT / "results/weather_fix_comparison_v2j.csv")
    loso = pd.read_csv(REPO_ROOT / "results/loso_summary_v2j.csv")
    lamb = pd.read_csv(REPO_ROOT / "results/lambda_check_v2j.csv")
    dem = pd.read_csv(REPO_ROOT / "results/dem_study_v2j.csv")
    lines = [
        "## Step 4j — corrected weather timestamps", "",
        "All earlier weather-dependent scores remain labelled **shifted weather**. The v2j scores use the confirmed Asia/Kolkata timestamp correction and the fixed half-hour rule: subtract 5 h 30 min from each raw local timestamp, then average the records at UTC h−1:30 and h:30 to represent hour h. The first raw local record (2022-01-01 00:00) becomes 2021-12-31 18:30 UTC; the first complete UTC hour is 19:00. The first model hour (2022-01-01 00:00 UTC) averages 2021-12-31 23:30 and 2022-01-01 00:30. The last six model hours lack a complete pair and use the existing bounded forward fill and train-only fallback. The mean 2 m temperature peaks at **" + f"{fit['temperature_peak_utc_hour']:02d}:00 UTC" + "**.",
        "",
        f"Source: `src/stpignn/data_v2.py`, `scripts/build_data_v2j.py`, `tests/test_weather_half_hour_v2j.py`; config `configs/data_v2.yaml`, data seed 42; source commit `{commit}`; generated {now}.",
        "",
        "### Fixed horizon benchmark", "",
        "The same cleaning bounds (0–500 µg/m³), splits, train-only fitting, imputed-lag indicator, same-space log1p channels, residual output, model families, learning-rate grid, and five seeds were retained. A win requires a lower point test MAE than both persistence and same-hour-yesterday and a paired UTC-day 2,000-replicate MAE CI below zero against each.",
        "",
        "| h | Model | Shifted MAE | Shifted R² | Corrected MAE | Corrected R² | Win shifted → corrected |",
        "|---:|---|---:|---:|---:|---:|---|",
    ]
    chosen = ["persistence", "same_hour_yesterday", "ridge_lag_calendar_weather",
              "stpignn_original", "gine_gru_wind", "adaptive_graph_st", "stpignn_v2"]
    names = {"ridge_lag_calendar_weather": "Ridge", "stpignn_original": "ST-PIGNN original",
             "gine_gru_wind": "A", "adaptive_graph_st": "B", "stpignn_v2": "C"}
    cells = comparison[comparison.comparison_type.eq("benchmark")]
    for horizon in (1, 3, 6, 12, 24):
        for model in chosen:
            row = cells[(cells.horizon_hours.eq(horizon)) & (cells.model.eq(model))].iloc[0]
            lines.append(f"| {horizon} | {names.get(model, model)} | {fmt(row.old_mae)} | {fmt(row.old_r2)} | {fmt(row.new_mae)} | {fmt(row.new_r2)} | {int(row.old_verdict)} → {int(row.new_verdict)} |")
    lines += ["", "| h | Corrected qualifying models | Any-model win |", "|---:|---|---|"]
    for horizon in (1, 3, 6, 12, 24):
        part = cells[cells.horizon_hours.eq(horizon)]
        winners = part[pd.to_numeric(part.new_verdict, errors="coerce").eq(1)].model.tolist()
        lines.append(f"| {horizon} | {', '.join(winners) if winners else 'none'} | {'MET' if winners else 'NOT MET'} |")
    lines += ["", f"Source: `scripts/benchmark_v2j.py`, `scripts/summarize_benchmark_v2j.py`, `scripts/weather_fix_comparison_v2j.py`; config `configs/benchmark_v2g.yaml`; seeds [11,23,37,51,79], bootstrap seed 4303, 2,000 UTC-day draws; source commit `{commit}`; generated {now}. All 85 model/horizon pairs are in `results/weather_fix_comparison_v2j.csv`.", "",
              "### Leave-one-station-out transfer", "",
              "All 15 fixed folds were retained; four have zero observed test targets and are reported without a score. Both W6 anchors were evaluated. The fixed W6 WIN/TIE/LOSS rule compares each neural method with the best fixed spatial baseline on paired UTC days.", "",
              "| Anchor | Neural method | Raw MAE | Raw verdict | Bias-adjusted MAE | Bias-adjusted verdict |",
              "|---|---|---:|---|---:|---|"]
    neural = loso[loso.anchor.ne("baseline")]
    for (anchor, method), part in neural.groupby(["anchor", "method"], sort=True):
        raw = part[part.seasonal_bias_corrected.eq(False)].iloc[0]
        adjusted = part[part.seasonal_bias_corrected.eq(True)].iloc[0]
        lines.append(f"| {anchor} | {method} | {fmt(raw.mae)} | {raw.verdict} | {fmt(adjusted.mae)} | {adjusted.verdict} |")
    lines += ["", f"Source: `scripts/evaluate_loso_v2j.py`; configs `configs/data_v2.yaml`, `configs/benchmark_v2g.yaml`, `configs/loso_v2.yaml`; seeds [11,23,37], bootstrap seed 4303, 2,000 UTC-day draws; source commit `{commit}`; generated {now}. Unscored stations: 5547, 5548, 6975, 2498781. No neural WIN.", "",
              "### Fixed lambda check and DEM control", "",
              "Physics helps only when lambda>0 has lower point test MAE than lambda=0 and the paired UTC-day MAE CI excludes zero. The full lambda sweep was not repeated.", "",
              "| h | Original ST-PIGNN lambda | Test MAE | ΔMAE vs 0 | 95% CI | Helps |",
              "|---:|---:|---:|---:|---|---|"]
    for row in lamb[lamb.model.eq("stpignn_original")].sort_values(["horizon_hours", "lambda"]).itertuples():
        lines.append(f"| {row.horizon_hours} | {row._3:.2f} | {fmt(row.test_mae_ug_m3)} | {fmt(row.delta_mae_vs_zero_ug_m3)} | [{fmt(row.mae_ci_low)}, {fmt(row.mae_ci_high)}] | {'MET' if row.physics_helps_at_horizon else 'NOT MET'} |")
    lines += ["", "The original physics criterion is MET at h=1 for lambda=0.06 and NOT MET at h=24. The Laplacian control has no qualifying positive-lambda cell at either checked horizon.",
              "", "| h | Validation-best A/B/C model | SRTM − no terrain ΔMAE | 95% CI | All-control DEM verdict shifted → corrected |",
              "|---:|---|---:|---|---|"]
    for horizon in (1, 24):
        part = dem[(dem.horizon_hours.eq(horizon)) & dem.record_type.eq("paired_bootstrap")]
        selected = part.best_validation_model.iloc[0]
        row = part[(part.model.eq(selected)) & part.comparison.eq("srtm_minus_none")].iloc[0]
        verdict = comparison[(comparison.comparison_type.eq("dem_criterion")) & comparison.horizon_hours.eq(horizon)].iloc[0]
        lines.append(f"| {horizon} | {selected} | {fmt(row.delta_mae_ug_m3)} | [{fmt(row.mae_ci_low)}, {fmt(row.mae_ci_high)}] | {int(verdict.old_verdict)} → {int(verdict.new_verdict)} |")
    lines += ["", "Both corrected-weather DEM horizons fail the predeclared all-control criterion because the fixed `shuffle_2` control CI includes zero. The earlier shifted-weather h=1 DEM verdict was MET; its h=24 verdict was NOT MET.",
              "", f"Source: `scripts/lambda_check_v2j.py`, `scripts/dem_study_v2j.py`, `scripts/weather_fix_comparison_v2j.py`; config `configs/benchmark_v2g.yaml`; seeds [11,23,37,51,79], fixed lambda grid [0,0.06,0.3,1], shuffle seeds [4201..4205], 2,000 UTC-day draws; source commit `{commit}`; generated {now}.", ""]
    paper.write_text(existing.rstrip() + "\n\n" + "\n".join(lines))
    print(f"Appended Step 4j: {len(lines)} lines")


if __name__ == "__main__":
    main()
