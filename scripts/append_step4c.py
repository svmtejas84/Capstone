"""Append factual Step 4c tables from committed S1-S4 result files once."""
from __future__ import annotations

import datetime as dt
import json
import subprocess

import pandas as pd

from src.stpignn.paths import REPO_ROOT


def source_line(label, meta, files):
    return (f"source: {files}; produced by `{meta['script']}`; config "
            f"`{meta.get('config', meta.get('data_config'))}`, seeds "
            f"{meta.get('seeds', meta.get('neural_seeds', meta.get('checkpoint_seeds', meta.get('seed'))))}, "
            f"source commit `{meta['source_git_commit']}`, UTC timestamp {meta['timestamp_utc']}.")


def main():
    results = REPO_ROOT / "results"
    s1 = json.loads((results / "diagnosis_v2c.json").read_text())
    s2 = json.loads((results / "gate_v2c_bootstrap.json").read_text())
    s3 = json.loads((results / "physics_controls_v2c.json").read_text())
    s4 = json.loads((results / "loso_decision_v2c.json").read_text())
    split = pd.read_csv(results / "diagnosis_splits_v2c.csv")
    gate = pd.read_csv(results / "gate_v2c.csv")
    physics = pd.read_csv(results / "physics_controls_v2c.csv")
    loso = pd.read_csv(results / "loso_summary_v2c.csv")
    lines = ["", "### Step 4c: S1–S4 revised residual diagnostics and comparisons", "",
             "S1 lag and observed-target diagnosis:", "",
             "| Split | Observed pairs | Lag–target Pearson r | Lag values above 500 µg/m³ | Persistence MAE (µg/m³) | Persistence R² |",
             "|---|---:|---:|---:|---:|---:|"]
    for row in split.itertuples(index=False):
        lines.append(f"| {row.split} | {row.n} | {row.lag_target_correlation} | {row.lag_above_cleaning_cap_pairs} | {row.persistence_mae} | {row.persistence_r2} |")
    lines += [source_line("S1", s1, "`results/diagnosis_splits_v2c.csv`, `results/diagnosis_v2c.json`"), "",
              "S1 found an imputed-lag/scaling defect; no timestamp shift was identified. The train-only AR and Ridge test metrics and checkpoint-lag correlations are in `results/diagnosis_v2c.md`.", "",
              "S2 same-mask h=1 test comparison (five neural seeds per selection):", "",
              "| Method | Selection | Seeds | MAE mean (µg/m³) | MAE SD | R² mean | R² SD |",
              "|---|---|---:|---:|---:|---:|---:|"]
    for row in gate.itertuples(index=False):
        lines.append(f"| {row.method} | {row.selection} | {row.seeds} | {row.mae_mean} | {row.mae_sd} | {row.r2_mean} | {row.r2_sd} |")
    lines += [source_line("S2", s2, "`results/gate_v2c.csv`, `results/gate_v2c_bootstrap.json`"), ""]
    primary = s2["choices"]["validation"]
    comparison = primary["comparisons"]["persistence"]
    lines += [f"Validation-selected corrected ST-PIGNN seed {primary['seed']}: test MAE {primary['test_mae']} µg/m³, R² {primary['test_r2']}. ST-PIGNN minus persistence paired UTC-day MAE difference {comparison['mae_difference_ug_m3']} µg/m³, 95% CI {comparison['mae_ci95']}; beats persistence on test MAE with CI excluding zero: {s2['stpignn_beats_persistence_mae_with_ci']}.",
              source_line("S2", s2, "`results/gate_v2c_bootstrap.json`"), "",
              "S3 matched residual physics controls (PVR at normalized threshold zero):", "",
              "| Model | Five-seed mean MAE (µg/m³) | MAE SD | Mean PVR (%) | PVR SD | Mean absolute edge difference (µg/m³) | Mean Dirichlet energy (µg²/m⁶) |",
              "|---|---:|---:|---:|---:|---:|---:|"]
    for model, group in physics.loc[physics.threshold_normalized.eq(0)].groupby("model"):
        lines.append(f"| {model} | {group.test_mae_ug_m3.mean()} | {group.test_mae_ug_m3.std()} | {group.pvr_percent.mean()} | {group.pvr_percent.std()} | {group.mean_abs_edge_difference_ug_m3.mean()} | {group.dirichlet_energy_mean_squared_ug_m6.mean()} |")
    lines += [source_line("S3", s3, "`results/physics_controls_v2c.csv`, `results/physics_controls_v2c.json`"),
              f"The predeclared paired five-seed rule detected a MAE or PVR(0) change beyond seed noise: {s3['change_beyond_seed_noise_at_mae_or_pvr_zero']}. Q was unavailable because measured traffic index was absent.",
              source_line("S3", s3, "`results/physics_controls_v2c.json`"), "",
              "S4 cleaned residual LOSO pooled observed-target scores:", "",
              "| Method | Scored station-hour pairs | MAE (µg/m³) | RMSE (µg/m³) | R² |",
              "|---|---:|---:|---:|---:|"]
    for row in loso.itertuples(index=False):
        lines.append(f"| {row.method} | {row.n} | {row.mae} | {row.rmse} | {row.r2} |")
    lines += [source_line("S4", s4, "`results/loso_summary_v2c.csv`, `results/loso_decision_v2c.json`"),
              f"S4 predeclared verdict: {s4['verdict']}; known-station ST-PIGNN minus best spatial baseline ({s4['best_spatial_baseline']}) pooled MAE difference {s4['mae_difference_stpignn_minus_best']} µg/m³, paired UTC-day 95% CI {s4['mae_difference_ci']}; R² difference {s4['r2_difference_stpignn_minus_best']}, CI {s4['r2_difference_ci']}. Folds considered/scored: {s4['folds_considered']}/{s4['folds_scored']}; unscored station IDs {s4['unscored_station_ids']}.",
              source_line("S4", s4, "`results/loso_decision_v2c.json`"), ""]
    append_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True).strip()
    lines.append(f"Step 4c aggregation script: `scripts/append_step4c.py`, source commit `{append_commit}`, UTC timestamp {dt.datetime.now(dt.timezone.utc).isoformat()}.")
    with (REPO_ROOT / "claude_paper.md").open("a") as stream:
        stream.write("\n".join(lines) + "\n")
    print("Appended factual Step 4c from S1-S4 results", flush=True)


if __name__ == "__main__":
    main()
