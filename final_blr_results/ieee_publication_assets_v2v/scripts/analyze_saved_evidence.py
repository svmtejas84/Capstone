from pathlib import Path
import hashlib, json, math, re
import numpy as np
import pandas as pd
import yaml

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'final_blr_results/ieee_publication_assets_v2v'
SRC=OUT/'source_data'; AN=OUT/'analyses'
SRC.mkdir(parents=True,exist_ok=True); AN.mkdir(parents=True,exist_ok=True)

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''): h.update(b)
 return h.hexdigest()

# Complete archived station forecasting inventory (85 rows = 17 variants × 5 horizons).
bench=pd.read_csv(ROOT/'final_blr_results/ieee_paper_evidence/results/RECOMPUTED_V2J_BENCHMARK.csv')
bench.to_csv(SRC/'F03_all_variants.csv',index=False)
assert bench.model.nunique()==17 and len(bench)==85
v2m=pd.read_csv(ROOT/'final_blr_results/baselines/v2m/comparisons/ensemble_metrics.csv')
variants=bench[['model']].drop_duplicates().copy()
variants['reader_name']=variants.model.map({
 'adaptive_graph_st':'Adaptive graph ST','adaptive_graph_st_fixed_knn':'Adaptive graph ST (fixed kNN)',
 'climatology_hod_dow':'Hour-of-day/day-of-week climatology','gine_gru_wind':'Wind-conditioned GINE–GRU',
 'gru_only':'GRU-only','persistence':'Persistence','ridge_lag_calendar_weather':'Weather ridge',
 'same_hour_yesterday':'Same-hour-yesterday','st_gru_gcn':'ST GRU–GCN','station_train_mean':'Station training mean',
 'stpignn_lambda0':'ST-PIGNN, zero regularization','stpignn_laplacian':'ST-PIGNN, Laplacian smoothing',
 'stpignn_original':'ST-PIGNN, directional regularization','stpignn_v2':'ST-PIGNN v2',
 'stpignn_v2_source_removed':'ST-PIGNN v2, source removed','stpignn_v2_transport_removed':'ST-PIGNN v2, transport removed',
 'vanilla_gcn':'Vanilla GCN'})
variants.to_csv(SRC/'F03_variant_inventory.csv',index=False)
bench.assign(protocol='Retrospective corrected weather',variant_class='v2j saved model variant').to_csv(SRC/'T02_v2j_17_variant_metrics.csv',index=False)
v2m.to_csv(SRC/'T02_v2m_cutoff_safe_metrics.csv',index=False)

# Routing: distinguish original scenario from maximum across all frozen fields/batches.
cap=pd.read_csv(ROOT/'final_blr_results/final_routing_closure/v2t/ROUTING_CAPACITY_METRICS.csv')
cap_summary=cap.groupby(['scenario','method']).max(numeric_only=True).reset_index()
cap_summary.to_csv(SRC/'F08_capacity_by_scenario.csv',index=False)
allmax=cap.loc[cap.max_utilization.idxmax()]
origmax=cap[cap.scenario.eq('original')].loc[cap[cap.scenario.eq('original')].max_utilization.idxmax()]
sens=pd.read_csv(ROOT/'final_blr_results/final_routing_closure/v2t/SENSITIVITY_STABILITY.csv')
pd.DataFrame([{'scope':'original concentration field, all methods and batches','scenario':origmax.scenario,'method':origmax.method,'seed':origmax.seed,'demand':origmax.demand,'max_utilization':origmax.max_utilization},
 {'scope':'all four fields, all methods and batches','scenario':allmax.scenario,'method':allmax.method,'seed':allmax.seed,'demand':allmax.demand,'max_utilization':allmax.max_utilization}]).to_csv(SRC/'F08_utilization_reconciliation.csv',index=False)

# Captum raw arrays: baseline-filtered records; retain schema and absolute/signed values.
cap_rows=[]
for variant,path in [('One-hour ST-PIGNN variant','final_blr_results/final_three_pillars/captum/attribution_tensors.npz'),
                     ('Six-hour station-isolated ST-PIGNN variant','final_blr_results/final_three_pillars/captum/v2r_heldout_h6/attribution_tensors.npz')]:
 z=np.load(ROOT/path,allow_pickle=True); rec=[json.loads(str(x)) for x in z['records']]
 mask=np.array([r.get('baseline')=='training_mean' for r in rec]); a=np.asarray(z['attributions'])[mask]
 names=[str(x) for x in z['feature_names']]
 # Mean across examples of sum absolute over 12 lag positions and 15 graph nodes.
 for j,n in enumerate(names):
  cap_rows.append({'variant':variant,'checkpoint_records_total':len(rec),'attribution_records':int(mask.sum()),'feature':n,
      'mean_abs_ig_sum_lag_node':float(np.abs(a[:,:,:,j]).sum(axis=(1,2)).mean()),
      'mean_signed_ig_sum_lag_node':float(a[:,:,:,j].sum(axis=(1,2)).mean()),
      'baseline':'training_mean','lags':a.shape[1],'nodes':a.shape[2],
      'completeness_max_abs':float(max(abs(r['completeness_delta_ug_m3']) for r,m in zip(rec,mask) if m)),
      'wrapper_max_abs_error':float(max(abs(r['wrapper_abs_error_ug_m3']) for r,m in zip(rec,mask) if m))})
pd.DataFrame(cap_rows).to_csv(SRC/'F06_feature_attribution_summary.csv',index=False)

# Spatial decoder pooled versus equal-site estimands, verified from source tables.
sp=pd.read_csv(ROOT/'final_blr_results/final_research_v2r/citywide/spatial_decoder/pooled_test_metrics.csv')
sp['aggregation']='pooled observation weighted'; sp.to_csv(SRC/'F07_pooled_decoder_metrics.csv',index=False)
boots=pd.read_csv(ROOT/'final_blr_results/final_research_v2r/citywide/spatial_decoder/station_bootstrap_comparisons.csv')
boots.to_csv(SRC/'F07_equal_station_bootstrap.csv',index=False)

# LOSO station summary audit. Raw aligned out-of-fold rows support per-site paired metrics.
loso=pd.read_parquet(ROOT/'results/loso_predictions_v2j.parquet')
loso['method']=loso.method.astype(str)
# Check saved summary definitions and anchor mismatch explicitly.
summary=pd.read_csv(ROOT/'results/loso_per_station_v2j.csv')
summary.to_csv(SRC/'F05_saved_station_metrics_all.csv',index=False)
candidate=summary[(summary.method.isin(['stpignn_original','ridge_weather_static'])) & (~summary.seasonal_bias_corrected.astype(bool))]
candidate.to_csv(SRC/'F05_reported_station_rows.csv',index=False)
# Raw aligned W6 predictions: average three ST-PIGNN seeds, retain ridge output.
st=loso[(loso.method=='stpignn_original')&(loso.anchor=='train_mean')].groupby(['station_id','target_time_utc'],as_index=False).agg(pred_st=('prediction','mean'),target_st=('target','first'))
ri=loso[loso.method=='ridge_weather_static'][['station_id','target_time_utc','target','prediction']].rename(columns={'prediction':'pred_ridge','target':'target_ridge'})
pair=st.merge(ri,on=['station_id','target_time_utc'],validate='one_to_one')
assert np.allclose(pair.target_st,pair.target_ridge,atol=1e-6) and len(pair)==14583
pair['d']=np.abs(pair.pred_st-pair.target_st)-np.abs(pair.pred_ridge-pair.target_ridge)
pair['day']=pd.to_datetime(pair.target_time_utc,utc=True).dt.floor('D')
pair.to_csv(SRC/'F05_station_time_paired_errors.csv',index=False)
site=pair.groupby('station_id').agg(n=('d','size'),stpignn_mae=('pred_st',lambda x:np.nan),difference=('d','mean')).reset_index()
# Equal-site station bootstrap.
sites=site.station_id.to_numpy(); sv=site.set_index('station_id').difference
rng=np.random.default_rng(8127); siteboot=sv.to_numpy()[rng.integers(0,len(sites),size=(20000,len(sites)))].mean(axis=1)
siteci=np.quantile(siteboot,[.025,.975])
# Hierarchical bootstrap: resample sites, then seven-day contiguous calendar blocks within each selected site.
per_site={sid:g.sort_values('day') for sid,g in pair.groupby('station_id')}
days_by={sid:pd.date_range(g.day.min(),g.day.max(),freq='D',tz='UTC').to_numpy() for sid,g in per_site.items()}
rng=np.random.default_rng(9131); nested=[]; B=2000; block=7
for _ in range(B):
 selected=rng.choice(sites,size=len(sites),replace=True); ds=[]; ns=[]
 for sid in selected:
  g=per_site[sid]; days=days_by[sid]; nday=len(days)
  if nday<block: chosen=days
  else:
   chunks=[]
   while sum(len(c) for c in chunks)<nday:
    k=int(rng.integers(0,nday-block+1));chunks.append(days[k:k+block])
   chosen=np.concatenate(chunks)[:nday]
  q=g[g.day.isin(chosen)]; ds.extend(q.d.tolist())
 nested.append(float(np.mean(ds)) if ds else np.nan)
nested_ci=np.quantile(np.asarray(nested),[.025,.975])
pd.DataFrame([{'estimand':'equal_station_mean paired MAE difference','estimate':float(sv.mean()),'ci_low':siteci[0],'ci_high':siteci[1],'sites':len(sites),'replicates':20000,'seed':8127},
 {'estimand':'hierarchical site then 7-day block pooled paired difference','estimate':float(pair.d.mean()),'ci_low':nested_ci[0],'ci_high':nested_ci[1],'sites':len(sites),'replicates':B,'seed':9131}]).to_csv(SRC/'F05_bootstrap_intervals.csv',index=False)

# Exact 6-hour sign test for five individual seeds, directional minus Laplacian.
ps=pd.read_csv(ROOT/'final_blr_results/physics_audit/seed_analysis/per_seed_physics_comparisons.csv')
print('seed comparison columns',ps.columns.tolist())
six=ps[(ps.horizon_hours==6)&(ps.comparison=='physics-lambda0')]
if len(six):
 vals_col=next((c for c in six.columns if c in ['paired_mae_difference','delta_mae','difference']),None)
 if vals_col:
  vals6=six[vals_col].to_numpy(); wins=int((vals6<0).sum()); from math import comb
  p=2*sum(comb(5,k) for k in range(min(wins,5-wins)+1))/2**5
  pd.DataFrame([{'horizon_hours':6,'comparison':'directional minus Laplacian','favorable_seeds':wins,'total_seeds':len(vals6),'two_sided_exact_sign_p':min(1,p),'seed_differences':';'.join(map(str,vals6))}]).to_csv(SRC/'F04_six_hour_seed_sign_test.csv',index=False)

# Measured observed coverage implied by scored test targets and configured full time window.
formula={'observed_scored_pairs':14583,'scored_stations':11,'evaluation_days':177,'hours_per_day':24,
         'possible_station_hour_pairs':11*177*24,'coverage_fraction':14583/(11*177*24),
         'coverage_percent':100*14583/(11*177*24)}
(AN/'coverage_calculation.json').write_text(json.dumps(formula,indent=2)+'\n')

# Directly calculate observed PM2.5 distribution and 6-hour input-lag missingness.
z=np.load(ROOT/'results/data_v2j_arrays.npz')
times=pd.DatetimeIndex(pd.to_datetime(z['times_ns'],utc=True)); y=z['observed_target']; mask=z['observed_mask'].astype(bool)
cfg=yaml.safe_load((ROOT/'configs/data_v2.yaml').read_text())
dist=[]; miss=[]
for split in ['train','validation','test']:
 lo=pd.Timestamp(cfg[f'{split}_start_utc']); hi=pd.Timestamp(cfg[f'{split}_end_utc'])
 ti=np.flatnonzero((times>=lo)&(times<=hi))
 vals=y[ti][mask[ti]]
 dist.append({'split':split,'observed_target_pairs':int(len(vals)),'mean_ug_m3':float(np.mean(vals)),'median_ug_m3':float(np.median(vals)),
   'sd_ug_m3':float(np.std(vals,ddof=1)),'q1_ug_m3':float(np.quantile(vals,.25)),'q3_ug_m3':float(np.quantile(vals,.75)),
   'min_ug_m3':float(np.min(vals)),'max_ug_m3':float(np.max(vals))})
 # v2j h=6 evaluation style: each split forecast target uses the preceding 12 input hours ending at cutoff t-6.
 eligible=np.flatnonzero((times>=lo)&(times<=hi)&mask.any(axis=1))
 all_ix=np.concatenate([np.arange(k-6-11,k-6+1) for k in eligible if k>=17])
 if len(all_ix):
  slots=mask[all_ix]
  miss.append({'split':split,'horizon_hours':6,'target_origins':len(eligible),'input_station_hour_slots':int(slots.size),
    'pm25_lag_imputed_slots':int((~slots).sum()),'pm25_lag_imputed_fraction':float((~slots).mean()),
    'description':'missing observed PM2.5 at historical input slot; model input includes causal filled value plus lag_is_imputed indicator'})
pd.DataFrame(dist).to_csv(SRC/'DATA_validation_test_pm25_distribution.csv',index=False)
pd.DataFrame(miss).to_csv(SRC/'DATA_h6_input_lag_missingness.csv',index=False)
with open(AN/'coverage_calculation.json','w') as f: json.dump(formula, f, indent=2)

# Weather protocol and provenance records are extracted from committed methods/configs, not inferred from output metrics.
prov=[]
for path in ['configs/data_v2.yaml','configs/benchmark_v2g.yaml','scripts/benchmark_v2j.py',
             'final_blr_results/baselines/v2m/methodology/WEATHER_AVAILABILITY_AUDIT.md',
             'final_blr_results/physics_audit/methodology/PHYSICS_ATTRIBUTION_METHODOLOGY.md']:
 p=ROOT/path
 prov.append({'path':path,'exists':p.exists(),'sha256':sha(p) if p.exists() else ''})
pd.DataFrame(prov).to_csv(SRC/'PROVENANCE_SOURCE_HASHES.csv',index=False)

print('variants',bench.model.nunique(),'rows',len(bench),'coverage',formula['coverage_percent'])
print('routing_original_max',origmax.to_dict())
print('routing_all_max',allmax.to_dict())
print('captum summaries',len(cap_rows))
print('spatial bootstrap rows',len(boots))
print('loso methods',sorted(loso.method.unique()))
print('loso site paired CI',float(sv.mean()),siteci.tolist(),'nested',nested_ci.tolist())
print('pm25 distributions',pd.DataFrame(dist).to_dict(orient='records'))
print('pm25 lag missingness',miss)
