"""Produce per-zone table and coefficient histograms for scaler verification.

Inputs:
 - holdout CSV: data/processed/holdout_pairs.csv (zone_id,raw_pred,obs,timestamp)
 - scalers JSON: data/processed/per_zone_scalers_trained.json

Outputs:
 - docs/scaler_diagnostics.csv
 - docs/scaler_coeff_hist.png
 - docs/scaler_sample_hist.png
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

REPORT_DIR = Path("docs")
REPORT_DIR.mkdir(parents=True, exist_ok=True)


def main(holdout_csv: str, scalers_json: str, out_csv: str):
    df = pd.read_csv(holdout_csv).dropna(subset=['raw_pred','obs'])
    df['raw_pred'] = df['raw_pred'].astype(float)
    df['obs'] = df['obs'].astype(float)

    with open(scalers_json) as fh:
        scalers = json.load(fh)

    zones = sorted(df['zone_id'].unique())
    rows = []
    slopes = []
    counts = []
    for zid in zones:
        dfz = df[df['zone_id'] == zid]
        n = len(dfz)
        raw_mae = float((dfz['raw_pred'] - dfz['obs']).abs().mean()) if n>0 else None
        s = scalers.get(str(zid))
        a = float(s.get('a')) if s else None
        b = float(s.get('b')) if s else None
        # apply scaler to raw predictions (assume scaler is in pm25 units)
        if s is not None:
            pred_adj = a * dfz['raw_pred'] + b
            scaled_mae = float((pred_adj - dfz['obs']).abs().mean()) if n>0 else None
        else:
            scaled_mae = None

        delta = (scaled_mae - raw_mae) if (scaled_mae is not None and raw_mae is not None) else None
        rows.append({
            'zone': zid,
            'n': n,
            'raw_mae_ug': raw_mae,
            'scaled_mae_ug': scaled_mae,
            'delta_mae': delta,
            'slope': a,
            'intercept': b,
        })
        if a is not None:
            slopes.append(a)
        counts.append(n)

    out_df = pd.DataFrame(rows).sort_values('delta_mae', ascending=False)
    out_df.to_csv(out_csv, index=False)

    # plots
    fig, ax = plt.subplots(figsize=(6,4))
    sns.histplot(slopes, bins=50, kde=False, ax=ax)
    ax.set_title('Histogram of scaler slopes (a)')
    ax.set_xlabel('slope a')
    fig.savefig(REPORT_DIR / 'scaler_coeff_hist.png', bbox_inches='tight')
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6,4))
    sns.histplot(counts, bins=50, kde=False, ax=ax)
    ax.set_title('Histogram of per-zone sample counts (holdout)')
    ax.set_xlabel('n samples')
    fig.savefig(REPORT_DIR / 'scaler_sample_hist.png', bbox_inches='tight')
    plt.close(fig)

    print('wrote', out_csv)
    print('wrote', REPORT_DIR / 'scaler_coeff_hist.png')
    print('wrote', REPORT_DIR / 'scaler_sample_hist.png')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--holdout', default='data/processed/holdout_pairs.csv')
    parser.add_argument('--scalers', default='data/processed/per_zone_scalers_trained.json')
    parser.add_argument('--out', default='docs/scaler_diagnostics.csv')
    args = parser.parse_args()
    main(args.holdout, args.scalers, args.out)
