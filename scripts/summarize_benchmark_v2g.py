"""Summarize fixed W2/W5 horizons and paired UTC-day criteria."""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import json
import subprocess

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.stpignn.evaluation import evaluate_arrays
from src.stpignn.paths import REPO_ROOT


def paired_ci(a, b, y, dates, seed, replicates=2000):
    """Return paired differences a minus b for MAE and R², resampling UTC days."""
    unique, day = np.unique(dates, return_inverse=True)
    n = len(unique)
    count = np.bincount(day, minlength=n)
    ae = np.bincount(day, weights=np.abs(a-y)-np.abs(b-y), minlength=n)
    se = np.bincount(day, weights=(a-y)**2-(b-y)**2, minlength=n)
    sy = np.bincount(day, weights=y, minlength=n)
    sy2 = np.bincount(day, weights=y*y, minlength=n)
    rng = np.random.default_rng(seed)
    sample = rng.integers(0, n, size=(replicates, n))
    total_n = count[sample].sum(1)
    dmae = ae[sample].sum(1)/total_n
    sst = sy2[sample].sum(1)-sy[sample].sum(1)**2/total_n
    dr2 = -se[sample].sum(1)/sst
    return (float(np.mean(np.abs(a-y))-np.mean(np.abs(b-y))),
            np.quantile(dmae, [0.025, 0.975]).tolist(),
            float(1-np.sum((a-y)**2)/np.sum((y-y.mean())**2) -
                  (1-np.sum((b-y)**2)/np.sum((y-y.mean())**2))),
            np.quantile(dr2, [0.025, 0.975]).tolist())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--horizons", nargs="*", type=int, default=[1,3,6,12,24])
    args = parser.parse_args()
    all_rows, pred_by_h = [], {}
    for horizon in args.horizons:
        frames = []
        for path in glob.glob(str(REPO_ROOT / f"results/benchmark_predictions_h{horizon}_*_v2g.parquet")):
            if "_provisional_v2g.parquet" in path:
                continue
            frames.append(pd.read_parquet(path))
        if not frames:
            continue
        data = pd.concat(frames, ignore_index=True)
        expected = 5
        grouped = data.groupby(["model", "target_time_utc", "station_id"], observed=True, sort=False)
        counts = grouped.seed.nunique().groupby(level=0).min()
        keep = [name for name in counts.index if name in ("persistence", "same_hour_yesterday",
                "climatology_hod_dow", "station_train_mean", "ridge_lag_calendar_weather") or counts[name] == expected]
        data = data[data.model.isin(keep)]
        mean = data.groupby(["model", "target_time_utc", "station_id"], observed=True, as_index=False).agg(
            target_ug_m3=("target_ug_m3", "first"), prediction_ug_m3=("prediction_ug_m3", "mean"))
        pivot = mean.pivot(index=["target_time_utc", "station_id", "target_ug_m3"],
                           columns="model", values="prediction_ug_m3")
        if pivot.isna().any().any():
            raise AssertionError(f"Unequal test masks h={horizon}")
        pred_by_h[horizon] = pivot
        y = pivot.index.get_level_values("target_ug_m3").to_numpy(dtype=float)
        for name in pivot.columns:
            metric = evaluate_arrays(pivot[name].to_numpy(), y, np.ones(len(y), bool))
            all_rows.append({"horizon_hours": horizon, "model": name, "test_n": metric["n"],
                             "test_mae_ug_m3": metric["mae"], "test_r2": metric["r2"],
                             "seeds_completed": int(counts[name])})
    if not all_rows:
        raise RuntimeError("No complete horizon predictions")
    curve = pd.DataFrame(all_rows).sort_values(["model", "horizon_hours"])
    curve.to_csv(REPO_ROOT / "results/horizon_curve_v2g.csv", index=False)
    curve.to_csv(REPO_ROOT / "results/benchmark_v2g.csv", index=False)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    for name, group in curve.groupby("model"):
        width = 2.3 if name in ("persistence", "same_hour_yesterday", "gine_gru_wind",
                                "adaptive_graph_st", "stpignn_v2", "stpignn_original") else 0.9
        axes[0].plot(group.horizon_hours, group.test_mae_ug_m3, marker="o", lw=width, label=name)
        axes[1].plot(group.horizon_hours, group.test_r2, marker="o", lw=width, label=name)
    axes[0].set(xlabel="Forecast horizon (hours)", ylabel="Test MAE (µg/m³)")
    axes[1].set(xlabel="Forecast horizon (hours)", ylabel="Test R²")
    for ax in axes:
        ax.grid(alpha=0.2)
        ax.set_xticks([1,3,6,12,24])
    fig.legend(*axes[0].get_legend_handles_labels(), loc="lower center", ncol=4, fontsize=7)
    fig.tight_layout(rect=[0,0.17,1,1])
    (REPO_ROOT / "figures").mkdir(exist_ok=True)
    fig.savefig(REPO_ROOT / "figures/horizon_curve.pdf")
    plt.close(fig)
    lines = ["# Benchmark v2g", "",
             f"Source `scripts/summarize_benchmark_v2g.py`, `configs/benchmark_v2g.yaml`, seeds [11,23,37,51,79], commit `{subprocess.check_output(['git','rev-parse','HEAD'], cwd=REPO_ROOT, text=True).strip()}`, {dt.datetime.now(dt.timezone.utc).isoformat()}.", "",
             "| h (hours) | Model | Test pairs | MAE (µg/m³) | R² |",
             "|---:|---|---:|---:|---:|"]
    for row in curve.sort_values(["horizon_hours", "model"]).itertuples():
        lines.append(f"| {row.horizon_hours} | {row.model} | {row.test_n} | {row.test_mae_ug_m3:.6f} | {row.test_r2:.6f} |")
    lines += ["", "## Fixed criteria", ""]
    wins = []
    support = []
    for horizon, pivot in sorted(pred_by_h.items()):
        y = pivot.index.get_level_values("target_ug_m3").to_numpy(dtype=float)
        dates = pd.to_datetime(pivot.index.get_level_values("target_time_utc"), utc=True).date
        for model in ("gine_gru_wind", "adaptive_graph_st", "stpignn_v2", "stpignn_original"):
            if model not in pivot:
                lines.append(f"h={horizon}, {model}: not assessed (incomplete predictions).")
                continue
            parts = []
            favorable = True
            for baseline in ("persistence", "same_hour_yesterday"):
                dmae, ci, _, _ = paired_ci(pivot[model].to_numpy(), pivot[baseline].to_numpy(), y,
                                           dates, 4303+horizon)
                favorable &= ci[1] < 0
                parts.append(f"{baseline} ΔMAE {dmae:+.6f} CI [{ci[0]:+.6f},{ci[1]:+.6f}]")
            lines.append(f"h={horizon}, {model}: {'met' if favorable else 'not met'}; " + "; ".join(parts) + ".")
            if favorable:
                wins.append((horizon, model))
        model = "stpignn_v2"
        controls = ("stpignn_v2_source_removed", "stpignn_v2_transport_removed",
                    "stpignn_lambda0", "stpignn_laplacian")
        if model in pivot and all(c in pivot for c in controls):
            checks = []
            for control in controls:
                dmae, ci_mae, dr2, ci_r2 = paired_ci(pivot[model].to_numpy(), pivot[control].to_numpy(), y,
                                                       dates, 4303+horizon)
                checks.append(ci_mae[1] < 0 or ci_r2[0] > 0)
                lines.append(f"h={horizon}, C vs {control}: {'met' if checks[-1] else 'not met'}; ΔMAE {dmae:+.6f} CI [{ci_mae[0]:+.6f},{ci_mae[1]:+.6f}]; ΔR² {dr2:+.6f} CI [{ci_r2[0]:+.6f},{ci_r2[1]:+.6f}].")
            support.append(all(checks))
        else:
            lines.append(f"h={horizon}, C physics support: not assessed (incomplete predictions).")
    dem_path=REPO_ROOT/"results/dem_study_v2g.csv"
    if dem_path.exists():
        dem=pd.read_csv(dem_path)
        selection=pd.read_csv(REPO_ROOT/"results/benchmark_selection_v2g.csv")
        best=selection[(selection.horizon_hours==1)&selection.model.isin(
            ["gine_gru_wind","adaptive_graph_st","stpignn_v2"])].sort_values("validation_mae").iloc[0].model
        dem_checks=dem[(dem.record_type=="paired_bootstrap")&(dem.model==best)]
        dem_met=(len(dem_checks)==2 and dem_checks.met.astype(str).str.lower().eq("true").all())
        dem_line=f"DEM criterion: {'met' if dem_met else 'not met'}."
    else:
        dem_line="DEM criterion: not assessed."
    lines += ["", f"Any-model win: {'met' if wins else 'not met'}.",
              f"C physics-in-architecture support: {'met' if any(support) else 'not met' if support else 'not assessed'}.",
              dem_line, ""]
    (REPO_ROOT / "results/benchmark_v2g.md").write_text("\n".join(lines))
    print(json.dumps({"horizons": sorted(pred_by_h), "models": sorted(curve.model.unique()),
                      "wins": wins, "c_physics_support": any(support) if support else None}, indent=2))


if __name__ == "__main__":
    main()
