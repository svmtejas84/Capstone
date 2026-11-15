"""Read-only V3 saved-prediction audit; writes exclusively to V4."""
from pathlib import Path
import json, hashlib
import numpy as np
import pandas as pd
from final_blr_results.controlled_validation_v3.scripts.analyze_controls import block_analysis, holm
from final_blr_results.controlled_validation_v3.scripts.train_controls import V3, ARR

OUT=V3.parent/'controlled_validation_v4_review_closure'
OUT.mkdir(exist_ok=True)
PRED=V3/'predictions'
H=[1,3,6,12,24]
DETERMINISTIC=['persistence','same_hour_yesterday','station_train_mean','climatology_hod_dow','weather_ridge']
NEURAL=['gru_only','vanilla_gcn','st_gru_gcn','adaptive_graph_st','mlp','tcn']
CONTROLS=['zero','true_wind','shuffled_wind','rotated_wind','laplacian']
PARAMS=dict(gru_only=16193,vanilla_gcn=5441,st_gru_gcn=26241,adaptive_graph_st=24434,mlp=18113,tcn=16641,zero=43393,true_wind=43393,shuffled_wind=43393,rotated_wind=43393,laplacian=43393)

def load(h,v,suffix=''):
 with np.load(PRED/f'h{h}_{v}{suffix}.npz') as z:
  return {k:z[k] for k in ('pred','truth','time_index','station_index')}

def aligned(a,b):
 for k in ('truth','time_index','station_index'): assert np.array_equal(a[k],b[k]),(k,len(a[k]),len(b[k]))

def save(df,name):
 p=OUT/name;p.parent.mkdir(parents=True,exist_ok=True)
 df.to_csv(p,index=False,float_format='%.9g')
 return p

arr=np.load(ARR)
times=pd.to_datetime(arr['times_ns'],utc=True)
sourcehash=hashlib.sha256(Path(ARR).read_bytes()).hexdigest()
assert sourcehash=='bd08d733f924387da82e758d1060703dfcdd121f360b7e8765189d8b7446e202'
base=pd.read_csv(V3/'metrics/baselines.csv')
ctrl=pd.read_csv(V3/'metrics/matched_controls.csv')
sel=pd.read_csv(V3/'verification/baseline_selected_lrs.csv')
rows=[]
for h in H:
 ref=load(h,'zero','_ensemble')
 for v in DETERMINISTIC+NEURAL+CONTROLS:
  suffix='' if v in DETERMINISTIC else '_ensemble'
  p=load(h,v,suffix);aligned(ref,p)
  pred=p['pred'];truth=p['truth']
  mae=float(np.mean(abs(pred-truth)));rmse=float(np.sqrt(np.mean((pred-truth)**2)))
  r2=float(1-np.sum((pred-truth)**2)/np.sum((truth-truth.mean())**2))
  x=(base if v in DETERMINISTIC+NEURAL else ctrl)
  row=x[(x.horizon_hours==h)&((x.model==v) if 'model' in x else (x.variant==v))&((x.seed.astype(str)=='deterministic') if v in DETERMINISTIC else (x.seed.astype(str)=='ensemble'))]
  assert len(row)==1
  assert abs(mae-float(row.iloc[0].mae))<1e-4
  lr=None if v in DETERMINISTIC else (float(sel[(sel.model==v)&(sel.horizon_hours==h)].iloc[0].learning_rate) if v in NEURAL else {1:.001,3:.0003,6:.0003,12:.0003,24:.0003}[h])
  rows.append(dict(horizon_hours=h,method=v,mae_ug_m3=mae,rmse_ug_m3=rmse,r2=r2,scored_pairs=len(pred),trained_seeds=0 if v in DETERMINISTIC else 5,ensemble='deterministic' if v in DETERMINISTIC else 'arithmetic mean of five seed predictions',parameter_count=PARAMS.get(v,''),optimizer='' if v in DETERMINISTIC else 'AdamW',learning_rate=lr,input_protocol='V3 delayed pollutant and past archived weather; operational release unverified',test_status='exposed exploratory',prediction_path=str((PRED/f'h{h}_{v}{suffix}.npz').relative_to(Path.cwd()))))
reg=pd.DataFrame(rows)
assert len(reg)==80
save(reg,'COMPLETE_MODEL_AND_BASELINE_REGISTER.csv')
save(reg,'tables/COMPLETE_FIVE_HORIZON_EVALUATION.csv')
with (OUT/'tables/COMPLETE_FIVE_HORIZON_EVALUATION.tex').open('w') as f:
 f.write('\\begin{tabular}{llrrrrr}\\hline\nHorizon & Method & MAE & RMSE & $R^2$ & Pairs & Seeds \\\\\hline\n')
 for r in rows:
  f.write(f"{r['horizon_hours']} & {r['method'].replace('_',' ')} & {r['mae_ug_m3']:.3f} & {r['rmse_ug_m3']:.3f} & {r['r2']:.3f} & {r['scored_pairs']} & {r['trained_seeds']} \\\\\n")
 f.write('\\hline\\end{tabular}\n')

# The frozen twenty-member V3 family, recomputed at the pair level.
prior=pd.read_csv(V3/'statistical_analysis/primary_contrasts.csv')
assert len(prior)==20
for _,r in prior.iterrows():
 h=int(r.horizon_hours);v=r.contrast.removeprefix('true_wind_minus_')
 a=load(h,'true_wind','_ensemble');b=load(h,v,'_ensemble');aligned(a,b)
 d=np.mean(abs(a['pred']-a['truth'])-abs(b['pred']-b['truth']))
 assert abs(d-r.paired_delta_mae_ug_m3)<2e-5
save(prior,'COMPLETE_20_CONTRAST_RESULTS.csv')
seedrows=[]
for h in H:
 for v in ['zero','shuffled_wind','rotated_wind','laplacian']:
  for seed in [11,23,37,51,79]:
   a=load(h,'true_wind',f'_seed{seed}');b=load(h,v,f'_seed{seed}');aligned(a,b)
   d=np.mean(abs(a['pred']-a['truth'])-abs(b['pred']-b['truth']))
   seedrows.append(dict(horizon_hours=h,comparator=v,seed=seed,true_minus_comparator_mae_ug_m3=d,favors_true=d<0,scored_pairs=len(a['pred'])))
save(pd.DataFrame(seedrows),'SEED_LEVEL_REGULARIZATION_RESULTS.csv')

# Fifteen predeclared graph-architecture contrasts on ensemble predictions.
graph=[];seedgraph=[]
for hi,h in enumerate(H):
 a=load(h,'zero','_ensemble')
 day=times[a['time_index']].floor('D').asi8
 for ci,v in enumerate(['gru_only','tcn','mlp']):
  b=load(h,v,'_ensemble');aligned(a,b)
  d=abs(a['pred']-a['truth'])-abs(b['pred']-b['truth'])
  lohi,p,blocks,days=block_analysis(day,d,54001+h*10+ci)
  graph.append(dict(horizon_hours=h,contrast=f'unregularized_GINE_GRU_minus_{v}',paired_delta_mae_ug_m3=float(d.mean()),ci95_low_ug_m3=lohi[0],ci95_high_ug_m3=lohi[1],block_signflip_p=p,paired_pairs=len(d),utc_days=days,nonoverlap_blocks=blocks,inference='exploratory; 15-member family'))
  for seed in [11,23,37,51,79]:
   sa=load(h,'zero',f'_seed{seed}');sb=load(h,v,f'_seed{seed}');aligned(sa,sb)
   seedgraph.append(dict(horizon_hours=h,comparator=v,seed=seed,paired_delta_mae_ug_m3=float(np.mean(abs(sa['pred']-sa['truth'])-abs(sb['pred']-sb['truth']))),scored_pairs=len(sa['pred'])))
for r,p in zip(graph,holm([r['block_signflip_p'] for r in graph])):r['holm_15_p']=p
save(pd.DataFrame(graph),'statistical_analysis/GRAPH_ARCHITECTURE_CONTRASTS.csv')
save(pd.DataFrame(seedgraph),'statistical_analysis/GRAPH_ARCHITECTURE_SEEDS.csv')

# Latest observed PM2.5 strictly before forecast issue, by station.
obs=arr['observed_mask'];last=np.full(obs.shape,-1,dtype=np.int32)
for j in range(obs.shape[1]):
 idx=np.where(obs[:,j],np.arange(len(obs)),-1)
 last[:,j]=np.maximum.accumulate(idx)
ages=[];station=[]
for h in H:
 p=load(h,'zero','_ensemble');issue=p['time_index']-h;j=p['station_index']
 true=load(h,'true_wind','_ensemble');aligned(p,true)
 prev=np.where(issue>0,last[np.maximum(issue-1,0),j],-1)
 age=np.where(prev>=0,issue-prev,-1)
 e=np.abs(p['pred']-p['truth'])
 et=np.abs(true['pred']-true['truth'])
 bins=[('1h',age==1),('2-3h',(age>=2)&(age<=3)),('4-6h',(age>=4)&(age<=6)),('7-12h',(age>=7)&(age<=12)),('13-24h',(age>=13)&(age<=24)),('>24h',age>24),('none',age<0)]
 for name,mask in bins:
  ages.append(dict(horizon_hours=h,anchor_age_bucket=name,scored_pairs=int(mask.sum()),fraction=float(mask.mean()),unregularized_mae_ug_m3=float(e[mask].mean()) if mask.any() else np.nan,true_wind_mae_ug_m3=float(et[mask].mean()) if mask.any() else np.nan))
 for jj,sid in enumerate(arr['station_ids']):
  mask=j==jj;valid=age[mask]>=0
  station.append(dict(horizon_hours=h,station_id=int(sid),scored_pairs=int(mask.sum()),fallback_pairs=int(np.sum(~valid)),median_observed_anchor_age_h=float(np.median(age[mask][valid])) if valid.any() else np.nan,p90_observed_anchor_age_h=float(np.quantile(age[mask][valid],.9)) if valid.any() else np.nan))
save(pd.DataFrame(ages),'ANCHOR_AGE_AND_ERROR.csv')
save(pd.DataFrame(station),'ANCHOR_AGE_PER_STATION.csv')
coverage=pd.read_csv(V3/'metrics/data_coverage_shift.csv')
save(coverage,'COVERAGE_AND_SHIFT.csv')
print(json.dumps(dict(register_rows=len(reg),contrast_rows=len(prior),architecture_rows=len(graph),seed_rows=len(seedrows),source_sha256=sourcehash),indent=2))
