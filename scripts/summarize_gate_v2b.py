"""Summarize the cleaned h=1 gate with paired UTC-day bootstrap intervals."""
from __future__ import annotations

import datetime as dt
import json
import subprocess

import numpy as np
import pandas as pd
import yaml

from scripts.summarize_gate_v2 import bootstrap_day_difference
from src.stpignn.paths import REPO_ROOT


def main():
    cfg = yaml.safe_load((REPO_ROOT / "configs/gate_v2b.yaml").read_text())
    results = REPO_ROOT / "results"
    baseline = pd.read_csv(results / "baselines_v2b_metrics.csv")
    base_predictions = pd.read_parquet(results / "baselines_v2b_predictions.parquet")
    short = pd.read_csv(results / "neural_final_v2b.csv")
    long = pd.read_csv(results / "neural_longer_v2b.csv")
    neural_predictions = pd.read_parquet(results / "neural_predictions_v2b.parquet")
    long_predictions = pd.read_parquet(results / "neural_longer_predictions_v2b.parquet")
    expected = 14583
    if len(base_predictions) != expected:
        raise AssertionError(f"Cleaned test mask has {len(base_predictions)} pairs, expected {expected}")
    rows = []
    for row in baseline.loc[baseline.scope.eq("pooled")].itertuples(index=False):
        if row.method == "station_train_mean":
            continue
        rows.append({"method": row.method, "budget": "baseline", "seeds": 0, "n": row.n,
                     "mae_mean": row.mae, "mae_sd": np.nan, "rmse_mean": row.rmse,
                     "rmse_sd": np.nan, "r2_mean": row.r2, "r2_sd": np.nan,
                     "bias_mean": row.bias, "nmae_mean": row.nmae})
    for budget, frame in (("short", short), ("longer", long)):
        for name, group in frame.groupby("model"):
            if group.seed.nunique() != len(cfg["neural_seeds"]):
                raise AssertionError(f"Expected five seeds for {budget}/{name}")
            rows.append({"method": name, "budget": budget, "seeds": group.seed.nunique(),
                         "n": int(group.n.iloc[0]), "mae_mean": group.mae.mean(),
                         "mae_sd": group.mae.std(), "rmse_mean": group.rmse.mean(),
                         "rmse_sd": group.rmse.std(), "r2_mean": group.r2.mean(),
                         "r2_sd": group.r2.std(), "bias_mean": group.bias.mean(),
                         "nmae_mean": group.nmae.mean()})
    table = pd.DataFrame(rows)
    table.to_csv(results / "gate_v2b.csv", index=False)

    selections = {}
    for budget, frame, predictions in (("short", short, neural_predictions),
                                        ("longer", long, long_predictions)):
        candidate = frame.loc[frame.model.eq("stpignn_corrected")].sort_values("best_val_mae_ug_m3").iloc[0]
        selected = predictions.loc[(predictions.model == candidate.model) &
                                   (predictions.seed == candidate.seed)].copy()
        if len(selected) != len(base_predictions):
            raise AssertionError(f"{budget} selected prediction count differs")
        joined = base_predictions.merge(selected[["station_id", "target_time_utc", "target_ug_m3",
                                                  "prediction_ug_m3"]],
                                        on=["station_id", "target_time_utc"],
                                        suffixes=("_baseline", "_neural"), validate="one_to_one")
        if len(joined) != len(base_predictions) or not np.allclose(
                joined.target_ug_m3_baseline, joined.target_ug_m3_neural):
            raise AssertionError("Baseline and neural masks/truth disagree")
        joined = joined.rename(columns={"target_ug_m3_baseline": "target_ug_m3",
                                        "prediction_ug_m3": "stpignn_prediction"})
        comparisons = {}
        for method, column in (("persistence", "persistence_ug_m3"),
                               ("idw_known_at_t", "idw_known_at_t_ug_m3")):
            comparisons[method] = bootstrap_day_difference(
                joined, "stpignn_prediction", column,
                int(cfg["bootstrap_replicates"]), int(cfg["bootstrap_seed"]))
        selections[budget] = {"model": candidate.model, "seed": int(candidate.seed),
                              "lr": float(candidate.lr), "scaler": candidate.scaler,
                              "best_val_mae_ug_m3": float(candidate.best_val_mae_ug_m3),
                              "test_mae_ug_m3": float(candidate.mae), "test_r2": float(candidate.r2),
                              "comparisons": comparisons}
    primary = selections["short"]["comparisons"]
    pass_point = all(v["mae_difference_ug_m3"] < 0 and v["r2_difference"] > 0 for v in primary.values())
    pass_ci = all(v["mae_ci95"][1] < 0 and v["r2_ci95"][0] > 0 for v in primary.values())
    meta = {"script": "scripts/summarize_gate_v2b.py", "config": "configs/gate_v2b.yaml",
            "data_config": "configs/data_v2.yaml", "seed": cfg["seed"],
            "neural_seeds": cfg["neural_seeds"], "bootstrap_seed": cfg["bootstrap_seed"],
            "timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
            "source_git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True).strip(),
            "test_pairs": expected, "selections": selections,
            "primary_point_gate_pass": bool(pass_point), "primary_ci_gate_pass": bool(pass_ci)}
    (results / "gate_v2b_bootstrap.json").write_text(json.dumps(meta, indent=2) + "\n")
    lines = ["# Cleaned h=1 gate", "",
             "All rows use the same observed test station-hours. Neural entries are five-seed means and sample SDs; the 20-epoch entries are separate budget diagnostics.", "",
             "| Method | Budget | Seeds | Pairs | MAE mean±SD (µg/m³) | RMSE mean±SD (µg/m³) | R² mean±SD |",
             "|---|---|---:|---:|---:|---:|---:|"]
    for row in table.itertuples(index=False):
        fmt = lambda mean, sd: f"{mean:.6f}" if pd.isna(sd) else f"{mean:.6f}±{sd:.6f}"
        lines.append(f"| {row.method} | {row.budget} | {row.seeds} | {row.n} | {fmt(row.mae_mean,row.mae_sd)} | {fmt(row.rmse_mean,row.rmse_sd)} | {fmt(row.r2_mean,row.r2_sd)} |")
    for budget, item in selections.items():
        lines += ["", f"Validation-selected corrected ST-PIGNN ({budget}): seed {item['seed']}, LR {item['lr']}, scaler {item['scaler']}, validation MAE {item['best_val_mae_ug_m3']:.6f} µg/m³; test MAE {item['test_mae_ug_m3']:.6f} µg/m³, R² {item['test_r2']:.6f}.", "",
                  "| Paired ST-PIGNN minus baseline | MAE difference [95% UTC-day CI], µg/m³ | R² difference [95% UTC-day CI] |",
                  "|---|---:|---:|"]
        for name, val in item["comparisons"].items():
            lines.append(f"| {name} | {val['mae_difference_ug_m3']:.6f} [{val['mae_ci95'][0]:.6f}, {val['mae_ci95'][1]:.6f}] | {val['r2_difference']:.6f} [{val['r2_ci95'][0]:.6f}, {val['r2_ci95'][1]:.6f}] |")
    lines += ["", f"Primary matched-budget corrected ST-PIGNN beats persistence and IDW on test MAE and R²: {'YES' if pass_point else 'NO'}; paired bootstrap CIs support both comparisons: {'YES' if pass_ci else 'NO'}.", "",
              "source: results/gate_v2b.csv and results/gate_v2b_bootstrap.json; produced by scripts/summarize_gate_v2b.py; config configs/gate_v2b.yaml, seeds/commit/UTC timestamp in gate_v2b_bootstrap.json.", ""]
    (results / "gate_v2b.md").write_text("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
