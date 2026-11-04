"""Summarize fixed protocol levels from existing results; no model fitting."""
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / 'results'

def metric(file, method_col, method, value_col, **filters):
    d = pd.read_csv(R / file)
    for col, val in filters.items():
        d = d[d[col] == val]
    x = d.loc[d[method_col] == method, value_col]
    if len(x) != 1:
        raise ValueError((file, method, filters, len(x)))
    return float(x.iloc[0])

rows=[]
def add(level, description, st, baselines, persistence, source, note=''):
    if not baselines:
        rows.append(dict(level=level, protocol=description, stpignn_mae=st,
                         strongest_baseline='', strongest_baseline_mae=np.nan,
                         headline_gain_ug_m3=np.nan, gain_vs_persistence_ug_m3=np.nan,
                         status='NOT_RECONSTRUCTABLE', note=note, source=source))
        return
    best=min(baselines, key=baselines.get)
    rows.append(dict(level=level, protocol=description, stpignn_mae=st,
                     strongest_baseline=best, strongest_baseline_mae=baselines[best],
                     headline_gain_ug_m3=baselines[best]-st,
                     gain_vs_persistence_ug_m3=persistence-st,
                     status='RECONSTRUCTED', note=note, source=source))

add('P0','legacy notebook, 308 pairs',53.14,{},np.nan,
    'legacy notebook stored checkpoint replay; user-specified P0',
    'Legacy baseline predictions are not stored on the same 308 pairs; headline gain and persistence gain cannot be reconstructed.')
add('P1','timestamp-joined observed-only, raw unfiltered targets',30.584854,
    {'persistence':21.261102,'hour/day climatology':392.031114},21.261102,
    'results/gate_persistence.md',
    'Validation-selected corrected-imputed ST-PIGNN seed 37; 14,623 observed pairs.')
add('P2','P1 + 0-500 target cleaning',
    metric('gate_v2b.csv','method','stpignn_corrected','mae_mean',budget='short'),
    {m:metric('gate_v2b.csv','method',m,'mae_mean',budget='baseline') for m in
     ['persistence','climatology_hod_dow','idw_known_at_t','ridge_meteorology_static']},
    metric('gate_v2b.csv','method','persistence','mae_mean',budget='baseline'),
    'results/gate_v2b.csv','Five-seed short-budget mean, 14,583 cleaned pairs.')
add('P3','P2 + lag/transform fix and residual formulation',
    metric('gate_v2c.csv','method','stpignn_corrected','mae_mean',selection='validation'),
    {m:metric('gate_v2c.csv','method',m,'mae_mean',selection='classical') for m in
     ['persistence','climatology_hod_dow','station_train_mean','idw_known_at_t','ridge_meteorology_static']},
    metric('gate_v2c.csv','method','persistence','mae_mean',selection='classical'),
    'results/gate_v2c.csv','Validation-selected five-seed mean, 14,583 pairs.')
b=pd.read_csv(R/'benchmark_v2g.csv');b=b[b.horizon_hours==1]
def bm(name):return float(b.loc[b.model==name,'test_mae_ug_m3'].iloc[0])
add('P4','P3 + same-hour-yesterday and paired-day decision rule',bm('stpignn_original'),
    {m:bm(m) for m in ['persistence','same_hour_yesterday','ridge_lag_calendar_weather',
                       'climatology_hod_dow','station_train_mean']},bm('persistence'),
    'results/benchmark_v2g.csv; results/benchmark_v2g.md',
    'h=1 five-seed ensemble; point gain requires paired UTC-day CI for a decision, not test-selected model choice.')
out=pd.DataFrame(rows)
out.loc[out.level=='P0','strongest_baseline']='ST GRU-GCN (untrained; reported)'
out.loc[out.level=='P0','strongest_baseline_mae']=62.51
out.loc[out.level=='P0','headline_gain_ug_m3']=62.51-53.14
out.loc[out.level=='P0','status']='REPORTED_ONLY_UNTRAINED'
out.loc[out.level=='P0','note']='Notebook-reported untrained ST GRU-GCN MAE 62.51 versus checkpoint replay 53.14; same-pair baseline predictions and persistence are unavailable.'
out['headline_claim']=[
    'P0: nominal 9.37 gain vs reported untrained ST GRU-GCN; paired validity unverified',
    'P1: no gain versus persistence on raw observed targets',
    'P2: no gain versus persistence after 0-500 cleaning',
    'P3: no gain versus persistence after lag and residual correction',
    'P4: h=1 point gain 0.097 but paired-day CI includes zero; h=3 win is reported separately',
]
out.to_csv(R/'protocol_inflation_v2h.csv',index=False)
fig,ax=plt.subplots(figsize=(7,4));x=np.arange(len(out))
ax.plot(x,out.headline_gain_ug_m3,marker='o',label='gain vs strongest available baseline')
ax.plot(x,out.gain_vs_persistence_ug_m3,marker='s',label='gain vs persistence')
ax.axhline(0,color='black',lw=.8);ax.set_xticks(x,out.level)
ax.set_xlabel('Protocol level');ax.set_ylabel('ST-PIGNN MAE gain (µg/m³; positive is better)')
ax.set_title('Reported gain changes with evaluation protocol')
ax.legend(fontsize=8);fig.tight_layout();(ROOT/'figures').mkdir(exist_ok=True)
fig.savefig(ROOT/'figures/protocol_inflation.pdf');plt.close(fig)
print(out[['level','headline_gain_ug_m3','gain_vs_persistence_ug_m3','status']].to_string(index=False))
