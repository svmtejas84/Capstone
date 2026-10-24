"""Generate factual persistence gate and paired day-bootstrap intervals."""
from __future__ import annotations

import datetime as dt
import json
import subprocess

import numpy as np
import pandas as pd
import yaml

from src.stpignn.evaluation import evaluate_arrays
from src.stpignn.paths import REPO_ROOT


def _r2(pred, target):
    den = np.sum((target - np.mean(target)) ** 2)
    return 1 - np.sum((pred - target) ** 2) / den if den > 0 else np.nan


def bootstrap_day_difference(frame, challenger_col, reference_col, replicates, seed):
    day = pd.to_datetime(frame.target_time_utc, utc=True).dt.floor("D")
    groups = list(frame.groupby(day, sort=True).indices.values())
    random = np.random.default_rng(seed)
    y = frame.target_ug_m3.to_numpy(float)
    challenger = frame[challenger_col].to_numpy(float)
    reference = frame[reference_col].to_numpy(float)
    mae_diffs, r2_diffs = np.empty(replicates), np.empty(replicates)
    for index in range(replicates):
        sampled = random.integers(0, len(groups), size=len(groups))
        rows = np.concatenate([groups[i] for i in sampled])
        mae_diffs[index] = np.mean(np.abs(challenger[rows] - y[rows])) - np.mean(np.abs(reference[rows] - y[rows]))
        r2_diffs[index] = _r2(challenger[rows], y[rows]) - _r2(reference[rows], y[rows])
    return {"mae_difference_ug_m3": float(np.mean(np.abs(challenger - y)) - np.mean(np.abs(reference - y))),
            "mae_ci95": np.quantile(mae_diffs, [.025, .975]).tolist(),
            "r2_difference": float(_r2(challenger, y) - _r2(reference, y)),
            "r2_ci95": np.quantile(r2_diffs, [.025, .975]).tolist(),
            "bootstrap_unit": "UTC calendar day", "distinct_days": len(groups),
            "replicates": replicates, "seed": seed}


def main():
    cfg = yaml.safe_load((REPO_ROOT / "configs/gate_v2.yaml").read_text())
    final = pd.read_csv(REPO_ROOT / "results/neural_final_v2.csv")
    neural = pd.read_parquet(REPO_ROOT / "results/neural_predictions_v2.parquet")
    baselines = pd.read_parquet(REPO_ROOT / "results/baselines_v2_predictions.parquet")
    baseline_metrics = pd.read_csv(REPO_ROOT / "results/baselines_v2_metrics.csv")
    st = final[final.model.str.startswith("stpignn_")]
    if st.empty:
        raise ValueError("No trained ST-PIGNN predictions")
    selected = st.sort_values("best_val_mae_ug_m3").iloc[0]
    challenger = neural[(neural.model == selected.model) & (neural.seed == selected.seed)]
    if len(challenger) != len(baselines):
        raise AssertionError("Neural and baseline target masks differ")
    merged = baselines.merge(challenger[["target_time_utc", "station_id", "target_ug_m3", "prediction_ug_m3"]],
                             on=["target_time_utc", "station_id"], suffixes=("_baseline", "_neural"),
                             validate="one_to_one")
    if len(merged) != len(baselines) or not np.allclose(merged.target_ug_m3_baseline, merged.target_ug_m3_neural):
        raise AssertionError("Neural and baseline truth arrays disagree")
    merged = merged.rename(columns={"target_ug_m3_baseline": "target_ug_m3",
                                    "prediction_ug_m3": "stpignn_ug_m3"})
    merged = merged.drop(columns=["target_ug_m3_neural"])
    intervals = {}
    for name in ("persistence", "climatology_hod_dow"):
        intervals[name] = bootstrap_day_difference(merged, "stpignn_ug_m3", name + "_ug_m3",
                                                    int(cfg["bootstrap_replicates"]), int(cfg["bootstrap_seed"]))
    by_model = final.groupby("model").agg(seeds=("seed", "nunique"),
                                           mae_mean=("mae", "mean"), mae_std=("mae", "std"),
                                           rmse_mean=("rmse", "mean"), rmse_std=("rmse", "std"),
                                           r2_mean=("r2", "mean"), r2_std=("r2", "std"),
                                           bias_mean=("bias", "mean"), nmae_mean=("nmae", "mean")).reset_index()
    by_model.to_csv(REPO_ROOT / "results/neural_summary_v2.csv", index=False)
    station_rows = []
    for (name, seed, station), group in neural.groupby(["model", "seed", "station_id"]):
        result = evaluate_arrays(group.prediction_ug_m3, group.target_ug_m3, np.ones(len(group), dtype=bool))
        station_rows.append({"model": name, "seed": seed, "station_id": station, **result})
    pd.DataFrame(station_rows).to_csv(REPO_ROOT / "results/neural_per_station_v2.csv", index=False)
    persistence = baseline_metrics[(baseline_metrics.method == "persistence") & (baseline_metrics.scope == "pooled")].iloc[0]
    climatology = baseline_metrics[(baseline_metrics.method == "climatology_hod_dow") & (baseline_metrics.scope == "pooled")].iloc[0]
    point_gate = (selected.mae < persistence.mae and selected.mae < climatology.mae and
                  selected.r2 > persistence.r2 and selected.r2 > climatology.r2)
    ci_gate = all(intervals[name]["mae_ci95"][1] < 0 and intervals[name]["r2_ci95"][0] > 0
                  for name in intervals)
    report = {"timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
              "script": "scripts/summarize_gate_v2.py", "config": "configs/gate_v2.yaml",
              "data_config": "configs/data_v2.yaml", "seed": cfg["seed"],
              "source_git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True).strip(),
              "selected_by_validation": {"model": selected.model, "seed": int(selected.seed),
                                         "scaler": selected.scaler, "lr": float(selected.lr),
                                         "best_val_mae_ug_m3": float(selected.best_val_mae_ug_m3)},
              "intervals": intervals, "point_gate_pass": bool(point_gate),
              "ci_gate_pass": bool(ci_gate), "test_pairs": len(merged),
              "q_variant_status": "BLOCKED: no measured traffic index"}
    (REPO_ROOT / "results/gate_bootstrap_v2.json").write_text(json.dumps(report, indent=2) + "\n")
    table = ["# Persistence gate", "",
             "All methods use raw observed PM2.5 at the same test station-hour pairs. ST-PIGNN row is the variant and seed selected by validation MAE.", "",
             "| Method | Test pairs | MAE (µg/m³) | RMSE (µg/m³) | R² |", "|---|---:|---:|---:|---:|"]
    for label, row in (("Persistence", persistence), ("Hour/day climatology", climatology),
                       (f"ST-PIGNN {selected.model}, seed {int(selected.seed)}", selected)):
        table.append(f"| {label} | {int(row.n)} | {row.mae:.6f} | {row.rmse:.6f} | {row.r2:.6f} |")
    table += ["", "| Paired difference: ST-PIGNN minus baseline | MAE difference and 95% day-bootstrap CI (µg/m³) | R² difference and 95% CI |",
              "|---|---:|---:|"]
    for name, label in (("persistence", "Persistence"), ("climatology_hod_dow", "Hour/day climatology")):
        val = intervals[name]
        table.append(f"| {label} | {val['mae_difference_ug_m3']:.6f} [{val['mae_ci95'][0]:.6f}, {val['mae_ci95'][1]:.6f}] | {val['r2_difference']:.6f} [{val['r2_ci95'][0]:.6f}, {val['r2_ci95'][1]:.6f}] |")
    table += ["", f"Point-metric gate: {'PASS' if point_gate else 'FAIL'}. CI-supported gate: {'PASS' if ci_gate else 'FAIL'}.", "",
              "source: results/gate_bootstrap_v2.json, results/neural_final_v2.csv, results/neural_predictions_v2.parquet, results/baselines_v2_metrics.csv; produced by scripts/summarize_gate_v2.py; configs/gate_v2.yaml and data_v2.yaml; seed and git commit and UTC timestamp in gate_bootstrap_v2.json.", ""]
    (REPO_ROOT / "results/gate_persistence.md").write_text("\n".join(table))
    print("\n".join(table))


if __name__ == "__main__":
    main()
