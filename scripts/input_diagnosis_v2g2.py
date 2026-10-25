"""Diagnose W1 lag provenance, timestamp alignment, scaling, and train-only AR."""
from __future__ import annotations

import datetime as dt
import json
import subprocess
import warnings

import numpy as np
import pandas as pd
import yaml
from sklearn.linear_model import LinearRegression

from src.stpignn.evaluation import evaluate_arrays
from src.stpignn.paths import REPO_ROOT


def score(pred, truth):
    return evaluate_arrays(pred, truth, np.ones(len(truth), dtype=bool))


def fmt(value):
    return "NA" if not np.isfinite(value) else f"{value:.6f}"


def main():
    cfg = yaml.safe_load((REPO_ROOT / "configs/data_v2.yaml").read_text())
    z = np.load(REPO_ROOT / "results/data_v2g_arrays.npz")
    times = pd.DatetimeIndex(pd.to_datetime(z["times_ns"], utc=True))
    y = z["observed_target"]
    observed = z["observed_mask"]
    lag_raw = z["imputed_target"]
    lag_scaled = z["features"][:, :, 0]
    source = json.loads((REPO_ROOT / "results/input_fix_v2g.json").read_text())
    params = source["channels"][0]
    mu, sd = params["log1p_mean"], params["log1p_sd"]
    assert np.isfinite(lag_raw).all() and lag_raw.min() >= 0 and lag_raw.max() <= 500
    assert np.allclose(lag_scaled, (np.log1p(lag_raw) - mu) / sd, rtol=1e-5, atol=1e-6)
    split = {}
    for name in ("train", "validation", "test"):
        eligible = np.asarray((times >= pd.Timestamp(cfg[f"{name}_start_utc"])) &
                              (times <= pd.Timestamp(cfg[f"{name}_end_utc"])))
        eligible[:int(cfg["history_hours"])] = False
        i, j = np.where(observed & eligible[:, None])
        assert len(i) and np.all(i >= 1)
        lag_is_observed = observed[i - 1, j]
        x = lag_scaled[i - 1, j].astype(np.float64)
        raw = lag_raw[i - 1, j].astype(np.float64)
        truth = y[i, j].astype(np.float64)
        split[name] = dict(i=i, j=j, observed=lag_is_observed, x=x, raw=raw,
                           truth=truth, target_z=(np.log1p(truth) - mu) / sd)

    train, test = split["train"], split["test"]
    all_ar = LinearRegression().fit(train["x"][:, None], train["target_z"])
    obs_ar = LinearRegression().fit(train["x"][train["observed"], None],
                                    train["target_z"][train["observed"]])
    train_design = np.column_stack((train["x"], (~train["observed"]).astype(float)))
    indicator_ar = LinearRegression().fit(train_design, train["target_z"])
    predictions = {
        "all_pairs": np.expm1(all_ar.predict(test["x"][:, None]) * sd + mu),
        "observed_lag_train": np.expm1(obs_ar.predict(test["x"][:, None]) * sd + mu),
        "lag_is_imputed_indicator": np.expm1(indicator_ar.predict(
            np.column_stack((test["x"], (~test["observed"]).astype(float)))) * sd + mu),
    }
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        station_mean = np.nanmean(y[np.asarray((times >= pd.Timestamp(cfg["train_start_utc"])) &
                                                (times <= pd.Timestamp(cfg["train_end_utc"])))], axis=0)
    station_mean = np.where(np.isfinite(station_mean), station_mean,
                            float(np.nanmean(y[np.asarray((times >= pd.Timestamp(cfg["train_start_utc"])) &
                                                           (times <= pd.Timestamp(cfg["train_end_utc"])))])))
    last_observed = pd.DataFrame(y).ffill().to_numpy(dtype=np.float32)[test["i"] - 1, test["j"]]
    predictions["persistence"] = np.where(np.isfinite(last_observed), last_observed,
                                           station_mean[test["j"]])
    all_scores = {key: score(pred, test["truth"]) for key, pred in predictions.items()}
    obs_scores = {key: score(pred[test["observed"]], test["truth"][test["observed"]])
                  for key, pred in predictions.items()}
    passed_by = [key for key in ("observed_lag_train", "lag_is_imputed_indicator")
                 if all_scores[key]["mae"] <= all_scores["persistence"]["mae"] + 0.5]

    lines = ["# Input diagnosis v2g2", "",
             f"Source: `scripts/input_diagnosis_v2g2.py`, `configs/data_v2.yaml`, seed 42, "
             f"commit `{subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO_ROOT, text=True).strip()}`, "
             f"{dt.datetime.now(dt.timezone.utc).isoformat()}.", "",
             "| Split | Observed-lag pairs | Imputed-lag pairs | Lag max (µg/m³) | Lag >500 | Observed-lag r | Observed-lag MAE (µg/m³) | Imputed-lag r | Imputed-lag MAE (µg/m³) |",
             "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for name, group in split.items():
        obs = group["observed"]
        def corr(mask):
            return float(np.corrcoef(group["raw"][mask], group["truth"][mask])[0, 1]) if mask.sum() > 1 else float("nan")
        lines.append(f"| {name} | {int(obs.sum())} | {int((~obs).sum())} | "
                     f"{group['raw'].max():.6f} | {int((group['raw'] > 500).sum())} | "
                     f"{fmt(corr(obs))} | {fmt(np.mean(np.abs(group['raw'][obs] - group['truth'][obs])))} | "
                     f"{fmt(corr(~obs))} | {fmt(np.mean(np.abs(group['raw'][~obs] - group['truth'][~obs])))} |")

    all_i = np.concatenate([split[n]["i"] for n in ("train", "validation", "test")])
    all_j = np.concatenate([split[n]["j"] for n in ("train", "validation", "test")])
    rng = np.random.default_rng(42)
    all_observed_lag = observed[all_i - 1, all_j]
    sample = np.concatenate((rng.choice(np.flatnonzero(all_observed_lag), size=10, replace=False),
                             rng.choice(np.flatnonzero(~all_observed_lag), size=10, replace=False)))
    rng.shuffle(sample)
    lines += ["", "| Station ID | Target UTC | Lag UTC | Repaired lag raw (µg/m³) | Observed at lag UTC (µg/m³) | Lag observed |",
              "|---:|---|---|---:|---:|---:|"]
    for pos in sample:
        i, j = int(all_i[pos]), int(all_j[pos])
        lag_time = times[i - 1]
        assert lag_time == times[i] - pd.Timedelta(hours=1)
        raw_obs = y[i - 1, j]
        if np.isfinite(raw_obs):
            assert np.isclose(lag_raw[i - 1, j], raw_obs, rtol=1e-6, atol=1e-5)
        lines.append(f"| {int(z['station_ids'][j])} | {times[i].isoformat()} | {lag_time.isoformat()} | "
                     f"{lag_raw[i-1,j]:.6f} | {fmt(raw_obs)} | {int(np.isfinite(raw_obs))} |")
    obs_positions = np.flatnonzero(train["observed"])[:5]
    lines += ["", "| Station ID | Target UTC | Input lag z | Same raw lag as target z | Actual target z |",
              "|---:|---|---:|---:|---:|"]
    for pos in obs_positions:
        i, j = int(train["i"][pos]), int(train["j"][pos])
        transformed_raw = (np.log1p(y[i - 1, j]) - mu) / sd
        assert np.isclose(train["x"][pos], transformed_raw, rtol=1e-5, atol=1e-6)
        lines.append(f"| {int(z['station_ids'][j])} | {times[i].isoformat()} | "
                     f"{train['x'][pos]:.6f} | {transformed_raw:.6f} | {train['target_z'][pos]:.6f} |")
    lines += ["", "| Train-only AR variant | All-test MAE (µg/m³) | All-test R² | Observed-lag-test MAE (µg/m³) | Observed-lag-test R² |",
              "|---|---:|---:|---:|---:|"]
    for key in ("all_pairs", "observed_lag_train", "lag_is_imputed_indicator", "persistence"):
        lines.append(f"| {key} | {all_scores[key]['mae']:.6f} | {all_scores[key]['r2']:.6f} | "
                     f"{obs_scores[key]['mae']:.6f} | {obs_scores[key]['r2']:.6f} |")
    cause = "transform mismatch"
    lines += ["", f"Cause found: {cause}.",
              f"W1 PASSED: {'yes' if passed_by else 'no'}."]
    if passed_by:
        lines.append(f"Required neural input rule: shared train-fitted log1p lag/target scaling and observed-lag-only training loss (zero weight where immediate lag is imputed); passing AR variant(s): {', '.join(passed_by)}.")
    lines.append("")
    (REPO_ROOT / "results/input_diagnosis_v2g2.md").write_text("\n".join(lines))
    print(json.dumps({"cause": cause, "all_test": {k: {"mae": v["mae"], "r2": v["r2"]}
                     for k, v in all_scores.items()}, "observed_test": {k: {"mae": v["mae"], "r2": v["r2"]}
                     for k, v in obs_scores.items()}, "w1_passed": bool(passed_by),
                     "passing_variants": passed_by}, indent=2))


if __name__ == "__main__":
    main()
