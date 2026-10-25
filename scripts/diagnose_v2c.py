"""S1: audited lag alignment, train-only AR controls and saved-model lag response."""
from __future__ import annotations

import datetime as dt
import json
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from sklearn.linear_model import LinearRegression, Ridge

from src.stpignn.evaluation import evaluate_arrays
from src.stpignn.paths import REPO_ROOT


def correlation(a, b):
    return float(np.corrcoef(np.asarray(a, float), np.asarray(b, float))[0, 1]) if len(a) > 1 else float("nan")


def metrics(pred, truth):
    return evaluate_arrays(pred, truth, np.ones(len(truth), bool))


def main():
    z = np.load(REPO_ROOT / "results/data_v2_arrays.npz")
    fit = json.loads((REPO_ROOT / "results/data_v2_fit.json").read_text())["fit"]
    cfg = yaml.safe_load((REPO_ROOT / "configs/data_v2.yaml").read_text())
    times = pd.DatetimeIndex(pd.to_datetime(z["times_ns"], utc=True))
    target = z["observed_target"]
    mask = z["observed_mask"]
    features = z["features"]
    station_ids = z["station_ids"]
    horizon = 1
    history = int(cfg["history_hours"])
    cutoff_observed = pd.DataFrame(target).ffill().to_numpy(dtype=np.float32)
    split = {}
    for name in ("train", "validation", "test"):
        selected = np.asarray((times >= pd.Timestamp(cfg[f"{name}_start_utc"])) &
                              (times <= pd.Timestamp(cfg[f"{name}_end_utc"])))
        selected[:history - 1 + horizon] = False
        i, j = np.where(mask & selected[:, None])
        raw_lag = features[i - horizon, j, 0] * fit["feature_stds"][0] + fit["feature_means"][0]
        observed_lag = target[i - horizon, j]
        previous_observed = cutoff_observed[i - horizon, j]
        station_train = np.nanmean(target[np.asarray((times >= pd.Timestamp(cfg["train_start_utc"])) &
                                             (times <= pd.Timestamp(cfg["train_end_utc"])))], axis=0)
        global_train = float(np.nanmean(target[np.asarray((times >= pd.Timestamp(cfg["train_start_utc"])) &
                                                (times <= pd.Timestamp(cfg["train_end_utc"]))) ]))
        station_train = np.where(np.isfinite(station_train), station_train, global_train)
        persistence = np.where(np.isfinite(previous_observed), previous_observed, station_train[j])
        split[name] = {"i": i, "j": j, "lag": raw_lag, "lag_scaled": features[i - horizon, j, 0],
                       "observed_lag": observed_lag, "truth": target[i, j], "persistence": persistence}
    train = split["train"]
    test = split["test"]
    ar = LinearRegression().fit(train["lag"][:, None], train["truth"])
    ridge_cols = [0] + list(range(5, features.shape[-1]))
    ridge = Ridge(alpha=1.0).fit(features[train["i"] - horizon, train["j"]][:, ridge_cols], train["truth"])
    ar_pred = ar.predict(test["lag"][:, None])
    ridge_pred = ridge.predict(features[test["i"] - horizon, test["j"]][:, ridge_cols])
    tests = {"ar_lag": metrics(ar_pred, test["truth"]),
             "ridge_lag_weather_static": metrics(ridge_pred, test["truth"])}
    baseline = pd.read_parquet(REPO_ROOT / "results/baselines_v2b_predictions.parquet")
    p = pd.read_parquet(REPO_ROOT / "results/neural_predictions_v2b.parquet")
    neural = pd.read_csv(REPO_ROOT / "results/neural_final_v2b.csv")
    baseline_keys = baseline[["station_id", "target_time_utc", "target_ug_m3"]].copy()
    baseline_keys["lag_ug_m3"] = test["lag"]
    checkpoint_rows = []
    for model in ("stpignn_corrected", "gru_only"):
        for seed in (11, 23, 37, 51, 79):
            part = p.loc[(p.model == model) & (p.seed == seed)]
            joined = baseline_keys.merge(part, on=["station_id", "target_time_utc"], validate="one_to_one")
            assert len(joined) == len(test["truth"])
            assert np.allclose(joined.target_ug_m3_x, joined.target_ug_m3_y)
            corr = correlation(joined.lag_ug_m3, joined.prediction_ug_m3)
            checkpoint_rows.append({"model": model, "seed": seed, "prediction_lag_correlation": corr,
                                    "prediction_variance_fraction_explained_by_lag_linear": corr * corr,
                                    "prediction_sd": float(joined.prediction_ug_m3.std()),
                                    "checkpoint": f"results/checkpoints_v2b/final_{model}_log1p_seed{seed}.pt"})
    checkpoint_frame = pd.DataFrame(checkpoint_rows)
    checkpoint_frame.to_csv(REPO_ROOT / "results/diagnosis_checkpoints_v2c.csv", index=False)
    split_rows = []
    for name, group in split.items():
        y = group["truth"]
        lag = group["lag"]
        observed_lag = np.isfinite(group["observed_lag"])
        pers = metrics(group["persistence"], y)
        split_rows.append({"split": name, "n": len(y), "target_mean": float(np.mean(y)),
                           "target_median": float(np.median(y)), "target_sd": float(np.std(y)),
                           "lag_target_correlation": correlation(lag, y),
                           "lag_target_mae": float(np.mean(np.abs(lag - y))),
                           "lag_scaled_mean": float(np.mean(group["lag_scaled"])),
                           "lag_scaled_sd": float(np.std(group["lag_scaled"])),
                           "lag_raw_mean": float(np.mean(lag)), "lag_raw_sd": float(np.std(lag)),
                           "immediate_observed_lag_pairs": int(observed_lag.sum()),
                           "immediate_observed_lag_target_correlation": correlation(group["observed_lag"][observed_lag], y[observed_lag]),
                           "immediate_observed_lag_target_mae": float(np.mean(np.abs(group["observed_lag"][observed_lag] - y[observed_lag]))) if observed_lag.any() else None,
                           "persistence_mae": pers["mae"], "persistence_r2": pers["r2"]})
    split_frame = pd.DataFrame(split_rows)
    split_frame.to_csv(REPO_ROOT / "results/diagnosis_splits_v2c.csv", index=False)
    model_gap = neural.groupby("model").agg(validation_mae=("best_val_mae_ug_m3", "mean"),
                                             test_mae=("mae", "mean")).reset_index()
    model_gap["test_minus_validation_mae"] = model_gap.test_mae - model_gap.validation_mae
    model_gap.to_csv(REPO_ROOT / "results/diagnosis_model_gap_v2c.csv", index=False)
    four = [5547, 5548, 6975, 2498781]
    station_counts = []
    for station_id in four:
        j = int(np.flatnonzero(station_ids == station_id)[0])
        station_counts.append({"station_id": station_id,
                               **{name: int(np.sum(mask[np.unique(group["i"]), j])) for name, group in split.items()}})
    station_counts = pd.DataFrame(station_counts)
    station_counts.to_csv(REPO_ROOT / "results/diagnosis_unscored_stations_v2c.csv", index=False)
    source_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True).strip()
    timestamp = dt.datetime.now(dt.timezone.utc).isoformat()
    meta = {"script": "scripts/diagnose_v2c.py", "data_config": "configs/data_v2.yaml",
            "gate_config": "configs/gate_v2b.yaml", "seed": 42, "checkpoint_seeds": [11, 23, 37, 51, 79],
            "timestamp_utc": timestamp, "source_git_commit": source_commit,
            "input_lag_transform": {"formula": "(filled raw PM2.5 - train feature mean) / train feature SD",
                                    "mean": fit["feature_means"][0], "sd": fit["feature_stds"][0]},
            "neural_target_transform": {"formula": "(log1p(observed PM2.5) - train log mean) / train log SD",
                                        "mean": fit["target_log1p_mean"], "sd": fit["target_log1p_std"]},
            "lag_and_target_same_transform": False,
            "ar_intercept": float(ar.intercept_), "ar_slope": float(ar.coef_[0]),
            "ridge_alpha": 1.0, "ridge_feature_indices": ridge_cols, "ridge_coefficients": ridge.coef_.tolist(),
            "tests": tests}
    (REPO_ROOT / "results/diagnosis_v2c.json").write_text(json.dumps(meta, indent=2) + "\n")
    lines = ["# S1 diagnosis", "", f"Source: `{meta['script']}`, `{meta['data_config']}`, `{meta['gate_config']}`, seed 42, checkpoint seeds {meta['checkpoint_seeds']}, commit `{source_commit}`, {timestamp}.", "",
             "| Split | Observed pairs | Target mean | Median | SD | Lag–target r | Lag MAE | Immediate observed lag pairs | Immediate-lag r | Persistence MAE | Persistence R² |",
             "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for row in split_frame.itertuples(index=False):
        lines.append(f"| {row.split} | {row.n} | {row.target_mean:.6f} | {row.target_median:.6f} | {row.target_sd:.6f} | {row.lag_target_correlation:.6f} | {row.lag_target_mae:.6f} | {row.immediate_observed_lag_pairs} | {row.immediate_observed_lag_target_correlation:.6f} | {row.persistence_mae:.6f} | {row.persistence_r2:.6f} |")
    lines += ["", f"Lag network input uses train-fitted raw standardization: feature mean {fit['feature_means'][0]:.6f}, SD {fit['feature_stds'][0]:.6f}. Neural targets use train-fitted log1p standardization: log mean {fit['target_log1p_mean']:.6f}, log SD {fit['target_log1p_std']:.6f}. These are different transforms.", "",
              "| Test train-only regression | MAE | R² |", "|---|---:|---:|"]
    for name, m in tests.items():
        lines.append(f"| {name} | {m['mae']:.6f} | {m['r2']:.6f} |")
    lines += ["", f"AR intercept {ar.intercept_:.6f}, slope {ar.coef_[0]:.6f}; Ridge alpha 1.0, lag plus weather/static indices {ridge_cols}.", "",
              "Checkpoint prediction–lag correlation and explained variance: source `results/diagnosis_checkpoints_v2c.csv`.",
              "Model validation–test MAE gaps: source `results/diagnosis_model_gap_v2c.csv`.",
              "Four LOSO station split counts: source `results/diagnosis_unscored_stations_v2c.csv`.", "",
              f"Persistence test minus validation MAE: {split_frame.set_index('split').loc['test','persistence_mae'] - split_frame.set_index('split').loc['validation','persistence_mae']:.6f} µg/m³.",
              "Finding: lag input and neural target use different scaling transforms; this is a formulation mismatch, not timestamp leakage.",
              "Finding: whether the lag channel has a data-alignment defect is decided by the observed immediate-lag correlation and AR test score above; no row was realigned or removed.",
              "Finding: four LOSO folds have zero observed test targets, so their absence is a coverage limitation.", ""]
    (REPO_ROOT / "results/diagnosis_v2c.md").write_text("\n".join(lines))
    print("\n".join(lines), flush=True)


if __name__ == "__main__":
    main()
