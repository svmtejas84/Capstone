"""Append factual Step 4h tables from finalized deviation-6 artifacts once."""
from datetime import datetime, timezone
from pathlib import Path
import json
import subprocess
import pandas as pd
from src.stpignn.paths import REPO_ROOT

R=REPO_ROOT/'results'
P=REPO_ROOT/'claude_paper.md'

def fmt(x,n=3):
    return 'NA' if pd.isna(x) else f'{x:.{n}f}'

def main():
    if subprocess.run(['rg','-q','^## Step 4h',str(P)],check=False).returncode==0:
        raise RuntimeError('Step 4h already present; refusing duplicate append')
    required=['lambda_verdict_v2g.json','protocol_inflation_v2h.csv','sensor_density_summary_v2h.csv',
              'sensor_density_verdict_v2h.json','conformal_v2h.csv','loso_groupdro_v2h.csv',
              'loso_station_predictability_v2h.csv','dem_study_v2h.csv','dem_station_values_v2h.csv',
              'citywide_precheck_v2h.md']
    for name in required:
        if not (R/name).is_file():raise FileNotFoundError(R/name)
    now=datetime.now(timezone.utc).isoformat()
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO_ROOT,text=True).strip()
    proto=pd.read_csv(R/'protocol_inflation_v2h.csv')
    density=pd.read_csv(R/'sensor_density_summary_v2h.csv')
    con=pd.read_csv(R/'conformal_v2h.csv')
    loso=pd.read_csv(R/'loso_groupdro_v2h.csv')
    dem=pd.read_csv(R/'dem_study_v2h.csv')
    station=pd.read_csv(R/'dem_station_values_v2h.csv')
    w7=json.loads((R/'lambda_verdict_v2g.json').read_text())
    density_verdict=json.loads((R/'sensor_density_verdict_v2h.json').read_text())
    city=(R/'citywide_precheck_v2h.md').read_text().splitlines()
    lines=['','## Step 4h: deviation 6 bounded round', '',
           f'Generated {now} from script `scripts/append_step4h_v2h.py` at source commit `{commit}`. All model selection used validation or fixed training choices; no test-driven horizon, fold, station or seed exclusion. Earlier results are unchanged.', '',
           '### W7 physics weight check', '',
           'Source `scripts/lambda_sweep_v2g.py`, config `configs/benchmark_v2g.yaml`, seeds [11,23,37,51,79], 2,000 paired UTC-day bootstrap draws; summary checked in Step 4h at the commit and time above.', '',
           f'All five horizons [1,3,6,12,24] are present. The original ST-PIGNN has one nominal hit (h=6, λ=0.06, about -0.28 µg/m³ versus λ=0); it is not replicated at another horizon or weight. There are 25 original-model and 25 Laplacian positive-weight comparisons. Laplacian findings are a separate control and do not count as support for the original physics penalty.', '',
           '### Protocol-inflation analysis', '',
           'Source `scripts/protocol_inflation_v2h.py`, stored P0/P1/P2/P3/P4 result files, h=1 for comparable point gains; no retraining. P4 paired UTC-day interval is from `results/benchmark_v2g.md`.', '',
           '| Level | ST-PIGNN MAE | Gain vs strongest baseline | Gain vs persistence | Headline |',
           '|---|---:|---:|---:|---|']
    for r in proto.itertuples():
        lines.append(f'| {r.level} | {fmt(r.stpignn_mae)} | {fmt(r.headline_gain_ug_m3)} | {fmt(r.gain_vs_persistence_ug_m3)} | {r.headline_claim} |')
    lines += ['', 'P0 same-pair baseline and persistence predictions on the legacy 308 pairs are unavailable, so its gain is not reconstructed. P4 h=1 nominal gain is 0.097 µg/m³, but its paired-day CI crosses zero; h=3 has a separate supported win.', '',
              '### W4 held-out station density', '',
              'Source `scripts/lowdata_v2h.py`, config `configs/benchmark_v2g.yaml`, five fixed draw/model seeds [11,23,37,51,79], source commit `01a87a0`; full draw rows and spread in `results/sensor_density_v2h.csv`, vector figure `figures/sensor_density.pdf`.', '',
              '| Horizon | Method | Train stations | Held-out MAE mean ± SD | R² mean ± SD | Draws |',
              '|---:|---|---:|---:|---:|---:|']
    for r in density.itertuples():
        lines.append(f'| {r.horizon_hours} | {r.model} | {r.train_station_count} | {fmt(r.mae_mean)} ± {fmt(r.mae_sd)} | {fmt(r.r2_mean)} ± {fmt(r.r2_sd)} | {r.draws} |')
    lines += ['', 'Ten-station cases remain BLOCKED because only eight stations have observed-lag training pairs. All scored draw-mean R² values are negative. Different 3- and 5-station draws preclude a causal density interpretation of their mean difference.', '',
              '### Probabilistic intervals', '',
              'Source `scripts/conformal_v2h.py`, config `configs/benchmark_v2g.yaml`, fixed seed 11, LR 3e-4, 10 epochs, train-tail and validation calibration, nominal 80% and 90%, fixed and daily rolling variants, 2,000 paired UTC-day interval-score bootstraps. Validation calibration is exploratory because A/B architecture ranking used validation. Full per-station and per-month coverage is in `results/conformal_station_month_v2h.csv`.', '',
              '| Horizon | Model | 80% train-tail fixed coverage | Width | Interval score | Value verdict |',
              '|---:|---|---:|---:|---:|---|']
    sub=con[(con.calibration=='train_tail')&(con.nominal==.8)&(con.variant=='fixed')&(con.horizon_hours!='pooled')]
    for r in sub.itertuples():
        lines.append(f'| {r.horizon_hours} | {r.model} | {fmt(r.coverage)} | {fmt(r.mean_width)} | {fmt(r.interval_score)} | {"YES" if r.adds_probabilistic_value else "NO"} |')
    lines += ['', 'No model meets the fixed criterion at any horizon or nominal level; coverage is outside ±5 points of nominal in the primary train-tail fixed analysis. Rolling daily updates improve coverage but do not change the verdict.', '',
              '### Group-DRO station-attribute LOSO', '',
              'Source `scripts/loso_groupdro_v2h.py`, `configs/data_v2.yaml`, `configs/benchmark_v2g.yaml`, seeds [11,23,37,51,79], 15 folds, 2,000 paired UTC-day bootstraps. Static embedding fields available at every station: SRTM elevation and projected UTM x/y coordinates, standardized using known training stations per fold. No station ID enters the embedding. η ∈ {0.01,0.1} chosen by validation MAE. ERM uses the same backbone; both use the train-fold mean residual anchor. W6 train-mean/IDW blend results remain separately in `results/loso_summary_v2g.csv`.', '',
              '| Method | MAE | R² | Best baseline | Baseline MAE | Baseline R² | Paired MAE 95% CI | Verdict |',
              '|---|---:|---:|---|---:|---:|---:|---|']
    for r in loso.itertuples():
        lines.append(f'| {r.method} | {fmt(r.mae)} | {fmt(r.r2)} | {r.best_baseline} | {fmt(r.baseline_mae)} | {fmt(r.baseline_r2)} | [{fmt(r.mae_ci_low)}, {fmt(r.mae_ci_high)}] | {r.verdict} |')
    unscored=pd.read_csv(R/'loso_station_predictability_v2h.csv')
    ids=unscored.loc[unscored.method=='unscored','station_id'].astype(int).tolist()
    lines += ['', f'Four zero-test-target folds remain unscored: {ids}. Per-station MAE and R² appear in `results/loso_station_predictability_v2h.csv`.', '',
              '### W3 SRTM terrain ablation', '',
              'Source `scripts/dem_study_v2h.py`, config `configs/benchmark_v2g.yaml`, seeds [11,23,37,51,79], five terrain shuffle seeds [4201,4202,4203,4204,4205], 2,000 paired UTC-day bootstrap draws. Per-station SRTM values verified against `nodes_elevation_true.parquet` in `results/dem_station_values_v2h.csv`.', '',
              f'SRTM elevation versus northing Pearson correlation: {fmt(station.elevation_m.corr(station.northing_m))}.', '',
              '| Horizon | Model | Control | SRTM minus control MAE | 95% CI |',
              '|---:|---|---|---:|---:|']
    comparisons=dem[dem.record_type=='paired_bootstrap']
    for r in comparisons.itertuples():
        lines.append(f'| {r.horizon_hours} | {r.model} | {r.comparison} | {fmt(r.delta_mae_ug_m3)} | [{fmt(r.mae_ci_low)}, {fmt(r.mae_ci_high)}] |')
    lines += ['', '### W8 citywide input precheck', '',
              'Source `scripts/citywide_precheck_v2h.py`, no training or seed; full audit in `results/citywide_precheck_v2h.md`.', '']
    lines += [line for line in city if line.startswith(('Nodes:', 'Distinct weather', 'Nodes with stored', 'Unique weather', 'Stored nodes', 'Nodes with SRTM', 'Nodes mapped', 'Nodes with no weather', 'BLOCKED:', 'PRECHECK PASSED'))]
    lines += ['', 'The bounded round stops here; no routing, integrated gradients, citywide training or second-city study was run.', '']
    with P.open('a') as f:f.write('\n'.join(lines))
    print('Appended Step 4h',len(lines),'lines',now,commit)

if __name__=='__main__':main()
