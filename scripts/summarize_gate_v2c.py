"""Summarize fixed residual gate and predeclared UTC-day paired comparisons."""
from __future__ import annotations

import datetime as dt
import json
import subprocess

import numpy as np
import pandas as pd
import yaml
from sklearn.linear_model import Ridge

from scripts.evaluate_baselines_v2 import _pairs, _train_climatology
from scripts.summarize_gate_v2 import bootstrap_day_difference
from src.stpignn.evaluation import evaluate_arrays
from src.stpignn.paths import REPO_ROOT


def classical_validation():
    cfg = yaml.safe_load((REPO_ROOT / "configs/data_v2.yaml").read_text())
    z = np.load(REPO_ROOT / "results/data_v2_arrays.npz")
    times = pd.DatetimeIndex(pd.to_datetime(z["times_ns"], utc=True))
    target, observed, features = z["observed_target"], z["observed_mask"], z["features"]
    train = np.asarray((times >= pd.Timestamp(cfg["train_start_utc"])) & (times <= pd.Timestamp(cfg["train_end_utc"])))
    val = np.asarray((times >= pd.Timestamp(cfg["validation_start_utc"])) & (times <= pd.Timestamp(cfg["validation_end_utc"])))
    ti, tj = _pairs(target, observed, train, int(cfg["history_hours"]), 1)
    vi, vj = _pairs(target, observed, val, int(cfg["history_hours"]), 1)
    y = target[vi, vj]
    table, station_means, _ = _train_climatology(target, times, train)
    key = times[vi].hour.to_numpy() * 7 + times[vi].dayofweek.to_numpy()
    climat = table[key, vj]
    climat = np.where(np.isfinite(climat), climat, station_means[vj])
    xy = z["coordinates"].astype(float)
    distance = np.linalg.norm(xy[:, None, :] - xy[None, :, :], axis=-1)
    weight = 1.0 / np.maximum(distance, 1.0) ** 2
    np.fill_diagonal(weight, 0.0)
    readings = target[vi - 1]
    available = np.isfinite(readings)
    w = weight[vj] * available
    denominator = w.sum(axis=1)
    idw = np.divide((w * np.nan_to_num(readings, nan=0.0)).sum(axis=1), denominator,
                    out=station_means[vj].copy(), where=denominator > 0)
    ridge = Ridge(alpha=1.0).fit(features[ti - 1, tj, 5:13], target[ti, tj])
    rpred = ridge.predict(features[vi - 1, vj, 5:13])
    pred = {"climatology_hod_dow": climat, "idw_known_at_t": idw, "ridge_meteorology_static": rpred}
    rows = []
    for method, value in pred.items():
        result = evaluate_arrays(value, y, np.ones(len(y), bool))
        rows.append({"method": method, "validation_pairs": len(y), "validation_mae": result["mae"],
                     "validation_r2": result["r2"]})
    out = pd.DataFrame(rows).sort_values("validation_mae")
    out.to_csv(REPO_ROOT / "results/classical_validation_v2c.csv", index=False)
    return out


def main():
    results = REPO_ROOT / "results"
    cfg = yaml.safe_load((REPO_ROOT / "configs/gate_v2c.yaml").read_text())
    classic = classical_validation()
    chosen_classic = str(classic.iloc[0].method)
    base = pd.read_parquet(results / "baselines_v2b_predictions.parquet")
    base_metric = pd.read_csv(results / "baselines_v2b_metrics.csv")
    rows = []
    for row in base_metric.loc[base_metric.scope.eq("pooled")].itertuples(index=False):
        rows.append({"method": row.method, "selection": "classical", "seeds": 0, "n": row.n,
                     "mae_mean": row.mae, "mae_sd": np.nan, "r2_mean": row.r2, "r2_sd": np.nan,
                     "rmse_mean": row.rmse, "rmse_sd": np.nan})
    choices = {}
    for selection, metric_file, pred_file in (
        ("validation", "neural_final_v2c.csv", "neural_predictions_v2c.parquet"),
        ("train_tail", "neural_train_tail_v2c.csv", "neural_train_tail_predictions_v2c.parquet")):
        frame = pd.read_csv(results / metric_file)
        predictions = pd.read_parquet(results / pred_file)
        for model, group in frame.groupby("model"):
            if group.seed.nunique() != len(cfg["neural_seeds"]) or not (group.n == len(base)).all():
                raise AssertionError(f"Incomplete or mismatched five-seed {selection}/{model}")
            rows.append({"method": model, "selection": selection, "seeds": len(group), "n": int(group.n.iloc[0]),
                         "mae_mean": float(group.mae.mean()), "mae_sd": float(group.mae.std()),
                         "r2_mean": float(group.r2.mean()), "r2_sd": float(group.r2.std()),
                         "rmse_mean": float(group.rmse.mean()), "rmse_sd": float(group.rmse.std())})
        st = frame.loc[frame.model.eq("stpignn_corrected")]
        selected = st.sort_values("best_val_mae_ug_m3").iloc[0] if selection == "validation" else st.loc[st.seed.eq(cfg["neural_seeds"][0])].iloc[0]
        selection_mae = float(selected.best_val_mae_ug_m3)
        if selection == "train_tail":
            tail_grid = pd.read_csv(results / "neural_selection_train_tail_v2c.csv")
            matched = tail_grid.loc[(tail_grid.model.eq("stpignn_corrected")) &
                                    (tail_grid.lr.eq(float(selected.lr)))].iloc[0]
            selection_mae = float(matched.best_val_mae_ug_m3)
        choice = predictions.loc[(predictions.model == "stpignn_corrected") & (predictions.seed == selected.seed)]
        merged = base.merge(choice[["station_id", "target_time_utc", "target_ug_m3", "prediction_ug_m3"]],
                            on=["station_id", "target_time_utc"], suffixes=("_base", "_neural"), validate="one_to_one")
        if len(merged) != len(base) or not np.allclose(merged.target_ug_m3_base, merged.target_ug_m3_neural):
            raise AssertionError("S2 residual and Gate B baseline targets/masks differ")
        merged = merged.rename(columns={"target_ug_m3_base": "target_ug_m3", "prediction_ug_m3": "stpignn_ug_m3"})
        merged = merged.drop(columns="target_ug_m3_neural")
        comparisons = {}
        if selection == "validation":
            for method, column in (("persistence", "persistence_ug_m3"), (chosen_classic, chosen_classic + "_ug_m3")):
                comparisons[method] = bootstrap_day_difference(merged, "stpignn_ug_m3", column,
                                                              int(cfg["bootstrap_replicates"]), int(cfg["bootstrap_seed"]))
        choices[selection] = {"seed": int(selected.seed), "lr": float(selected.lr),
                              "test_mae": float(selected.mae), "test_r2": float(selected.r2),
                              "selection_mae": selection_mae,
                              "external_validation_diagnostic_mae": float(selected.best_val_mae_ug_m3) if selection == "train_tail" else None,
                              "comparisons": comparisons}
    table = pd.DataFrame(rows)
    table.to_csv(results / "gate_v2c.csv", index=False)
    primary = choices["validation"]["comparisons"]["persistence"]
    beats = bool(primary["mae_difference_ug_m3"] < 0 and primary["mae_ci95"][1] < 0)
    report = {"timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
              "script": "scripts/summarize_gate_v2c.py", "config": "configs/gate_v2c.yaml",
              "data_config": "configs/data_v2.yaml", "seed": 42, "neural_seeds": cfg["neural_seeds"],
              "bootstrap_seed": cfg["bootstrap_seed"], "source_git_commit": subprocess.check_output(
                  ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True).strip(),
              "test_pairs": len(base), "classical_selected_on_validation": chosen_classic,
              "choices": choices, "stpignn_beats_persistence_mae_with_ci": beats}
    (results / "gate_v2c_bootstrap.json").write_text(json.dumps(report, indent=2) + "\n")
    lines = ["# Residual h=1 gate", "",
             f"Source: `scripts/summarize_gate_v2c.py`, `configs/gate_v2c.yaml`, seeds {cfg['neural_seeds']}, commit `{report['source_git_commit']}`, {report['timestamp_utc']}. All test rows use the same {len(base)} observed station-hour pairs.", "",
             "| Method | Selection | Seeds | MAE mean±SD (µg/m³) | R² mean±SD |",
             "|---|---|---:|---:|---:|"]
    for row in table.itertuples(index=False):
        mae = f"{row.mae_mean:.6f}" if np.isnan(row.mae_sd) else f"{row.mae_mean:.6f}±{row.mae_sd:.6f}"
        r2 = f"{row.r2_mean:.6f}" if np.isnan(row.r2_sd) else f"{row.r2_mean:.6f}±{row.r2_sd:.6f}"
        lines.append(f"| {row.method} | {row.selection} | {row.seeds} | {mae} | {r2} |")
    lines += ["", "Classical validation selection (not test selection):", "",
              "| Method | Validation pairs | MAE | R² |", "|---|---:|---:|---:|"]
    for row in classic.itertuples(index=False):
        lines.append(f"| {row.method} | {row.validation_pairs} | {row.validation_mae:.6f} | {row.validation_r2:.6f} |")
    for name, choice in choices.items():
        description = f"Corrected ST-PIGNN selected by {name}: seed {choice['seed']}, LR {choice['lr']}, selection MAE {choice['selection_mae']:.6f}, test MAE {choice['test_mae']:.6f}, R² {choice['test_r2']:.6f}."
        if choice["external_validation_diagnostic_mae"] is not None:
            description += f" Original July–September validation MAE (diagnostic only): {choice['external_validation_diagnostic_mae']:.6f}."
        lines += ["", description]
        if choice["comparisons"]:
            lines += ["", "| ST-PIGNN minus reference | MAE difference [95% UTC-day CI] | R² difference [95% UTC-day CI] |",
                      "|---|---:|---:|"]
            for method, item in choice["comparisons"].items():
                lines.append(f"| {method} | {item['mae_difference_ug_m3']:.6f} [{item['mae_ci95'][0]:.6f}, {item['mae_ci95'][1]:.6f}] | {item['r2_difference']:.6f} [{item['r2_ci95'][0]:.6f}, {item['r2_ci95'][1]:.6f}] |")
    lines += ["", f"Validation-selected residual ST-PIGNN beats persistence on test MAE with paired CI excluding zero: {'YES' if beats else 'NO'}.",
              "source: results/gate_v2c.csv, results/gate_v2c_bootstrap.json, results/classical_validation_v2c.csv; produced by scripts/summarize_gate_v2c.py.", ""]
    (results / "gate_v2c.md").write_text("\n".join(lines))
    print("\n".join(lines), flush=True)


if __name__ == "__main__":
    main()
