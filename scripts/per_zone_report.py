"""Generate per-zone diagnostics, bootstrap CIs, and plots.

Input: CSV with columns zone_id, raw_pred, obs, timestamp (PM2.5 units)
Uses: data/processed/calibration_pairs_direct.csv and data/processed/per_zone_scalers.json
Outputs: docs/per_zone_report.json and plots in docs/per_zone_report/
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

REPORT_DIR = Path("docs/per_zone_report")
REPORT_DIR.mkdir(parents=True, exist_ok=True)

CSV_IN = Path("data/processed/calibration_pairs_direct.csv")
SCALERS = Path("data/processed/per_zone_scalers.json")

def bootstrap_ci(data: np.ndarray, stat_func, n_boot=1000, alpha=0.05):
    if len(data) == 0:
        return None
    rng = np.random.default_rng(0)
    boots = []
    for _ in range(n_boot):
        sample = rng.choice(data, size=len(data), replace=True)
        boots.append(stat_func(sample))
    lo = np.percentile(boots, 100 * (alpha / 2.0))
    hi = np.percentile(boots, 100 * (1 - alpha / 2.0))
    return float(lo), float(hi)


def summarize_zone(df_zone: pd.DataFrame, scaler: Dict | None) -> Dict:
    raw = df_zone["raw_pred"].to_numpy(dtype=float)
    obs = df_zone["obs"].to_numpy(dtype=float)
    err = raw - obs
    abs_err = np.abs(err)
    n = len(raw)
    if n == 0:
        return {"n": 0}
    mae = float(np.mean(abs_err))
    rmse = float(np.sqrt(np.mean(err * err)))
    bias = float(np.mean(err))
    worst_abs = float(np.max(abs_err))
    # correlation
    corr = None
    if n > 1 and np.std(raw) > 0 and np.std(obs) > 0:
        corr = float(np.corrcoef(raw, obs)[0,1])
    else:
        corr = None

    # scaled prediction using scaler if provided
    if scaler is not None:
        a = float(scaler.get("a", 1.0))
        b = float(scaler.get("b", 0.0))
        pred_scaled = a * raw + b
        err_s = pred_scaled - obs
        abs_err_s = np.abs(err_s)
        mae_s = float(np.mean(abs_err_s))
        rmse_s = float(np.sqrt(np.mean(err_s * err_s)))
        bias_s = float(np.mean(err_s))
        worst_abs_s = float(np.max(abs_err_s))
    else:
        mae_s = rmse_s = bias_s = worst_abs_s = None

    # bootstrap CIs (for raw and scaled) for MAE and RMSE (use 500 iters for speed)
    ci_mae = bootstrap_ci(abs_err, np.mean, n_boot=500)
    ci_rmse = bootstrap_ci(err, lambda x: float(np.sqrt(np.mean(x * x))), n_boot=500)
    ci_mae_s = None
    ci_rmse_s = None
    if scaler is not None:
        ci_mae_s = bootstrap_ci(abs_err_s, np.mean, n_boot=500)
        ci_rmse_s = bootstrap_ci(err_s, lambda x: float(np.sqrt(np.mean(x * x))), n_boot=500)

    return {
        "n": n,
        "mae_raw": mae,
        "rmse_raw": rmse,
        "bias_raw": bias,
        "worst_abs_raw": worst_abs,
        "mae_scaled": mae_s,
        "rmse_scaled": rmse_s,
        "bias_scaled": bias_s,
        "worst_abs_scaled": worst_abs_s,
        "corr": corr,
        "ci_mae_raw": ci_mae,
        "ci_rmse_raw": ci_rmse,
        "ci_mae_scaled": ci_mae_s,
        "ci_rmse_scaled": ci_rmse_s,
    }


def plot_zone_errors(df_zone: pd.DataFrame, zid: str, outdir: Path):
    fig, ax = plt.subplots(figsize=(6,4))
    sns.boxplot(x=(df_zone['raw_pred'] - df_zone['obs']), ax=ax)
    ax.set_title(f"Error distribution for zone {zid} (raw_pred - obs)")
    ax.set_xlabel('Error (µg/m³)')
    out = outdir / f"zone_{zid}_error_boxplot.png"
    fig.savefig(out, bbox_inches='tight')
    plt.close(fig)

    # scatter predicted vs actual
    fig, ax = plt.subplots(figsize=(6,6))
    sns.scatterplot(x='obs', y='raw_pred', data=df_zone, ax=ax)
    lims = [min(df_zone['obs'].min(), df_zone['raw_pred'].min()), max(df_zone['obs'].max(), df_zone['raw_pred'].max())]
    ax.plot(lims, lims, '--', color='gray')
    ax.set_title(f"Predicted vs Actual for zone {zid}")
    ax.set_xlabel('Actual obs (µg/m³)')
    ax.set_ylabel('Raw prediction (µg/m³)')
    out2 = outdir / f"zone_{zid}_pred_vs_actual.png"
    fig.savefig(out2, bbox_inches='tight')
    plt.close(fig)


def main():
    df = pd.read_csv(CSV_IN)
    df = df.dropna(subset=['raw_pred','obs'])
    df['raw_pred'] = df['raw_pred'].astype(float)
    df['obs'] = df['obs'].astype(float)

    scalers = {}
    if SCALERS.exists():
        with open(SCALERS) as fh:
            scalers = json.load(fh)

    zones = sorted(df['zone_id'].unique())
    report = { 'zones': {}, 'summary': {} }
    all_rows = []
    for zid in zones:
        dfz = df[df['zone_id'] == zid]
        s = scalers.get(str(int(float(zid))))
        summ = summarize_zone(dfz, s)
        report['zones'][str(zid)] = summ
        # plot if n>=3
        if summ.get('n',0) >= 3:
            plot_zone_errors(dfz, str(zid), REPORT_DIR)

    # overall summary
    overall_raw_mae = float(np.mean(np.abs(df['raw_pred'] - df['obs'])))
    overall_raw_rmse = float(np.sqrt(np.mean((df['raw_pred'] - df['obs'])**2)))
    report['summary']['samples'] = int(len(df))
    report['summary']['overall_raw_mae'] = overall_raw_mae
    report['summary']['overall_raw_rmse'] = overall_raw_rmse

    with open(REPORT_DIR / 'per_zone_report.json','w') as fh:
        json.dump(report, fh, indent=2)
    print('wrote', REPORT_DIR / 'per_zone_report.json')

if __name__ == '__main__':
    main()
