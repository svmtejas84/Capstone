"""Read-only independent recomputation of reported Bengaluru metrics."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
from src.stpignn.paths import REPO_ROOT

R=REPO_ROOT/'results'
O=R/'research_audit_r1'
O.mkdir(exist_ok=True)
SOURCE='dca4bcce690da6b7865702f91d15dd2e06b6ef75'

def mae(y,p):return float(np.mean(np.abs(np.asarray(y,dtype=float)-np.asarray(p,dtype=float))))
def r2(y,p):
 y=np.asarray(y,dtype=float);p=np.asarray(p,dtype=float)
 return float(1-np.sum((y-p)**2)/np.sum((y-y.mean())**2))
def ci_day(diff,dates,seed,rep=2000):
 codes,unique=pd.factorize(dates,sort=False)
 counts=np.bincount(codes,minlength=len(unique));sums=np.bincount(codes,weights=diff,minlength=len(unique))
 rng=np.random.default_rng(seed);draw=rng.integers(0,len(unique),size=(rep,len(unique)))
 vals=sums[draw].sum(1)/counts[draw].sum(1)
 return np.quantile(vals,[.025,.975]).tolist()

def dem():
 raw=pd.read_parquet(R/'dem_predictions_v2h.parquet')
 keys=['horizon_hours','variant','model','target_time_utc','station_id']
 duplicates=raw.duplicated(keys+['seed']).sum()
 groups=raw.groupby(keys,sort=True)
 seed_counts=groups.seed.nunique()
 target_consistency=groups.target.nunique().max()
 pooled=groups.agg(target=('target','first'),prediction=('prediction','mean')).reset_index()
 reported=pd.read_csv(R/'dem_study_v2h.csv')
 max_mae_error=0.;comp={}
 for row in reported[reported.record_type=='variant'].itertuples():
  d=pooled[(pooled.horizon_hours==row.horizon_hours)&(pooled.variant==row.variant)&(pooled.model==row.model)]
  max_mae_error=max(max_mae_error,abs(mae(d.target,d.prediction)-row.test_mae_ug_m3))
 for h in (1,24):
  model='adaptive_graph_st'
  a=pooled[(pooled.horizon_hours==h)&(pooled.model==model)&(pooled.variant=='srtm')]
  b=pooled[(pooled.horizon_hours==h)&(pooled.model==model)&(pooled.variant=='none')]
  j=a.merge(b[['target_time_utc','station_id','target','prediction']],on=['target_time_utc','station_id'],suffixes=('_srtm','_none'),validate='one_to_one')
  assert len(j)==len(a)==len(b) and np.allclose(j.target_srtm,j.target_none)
  diff=np.abs(j.prediction_srtm-j.target_srtm)-np.abs(j.prediction_none-j.target_srtm)
  dates=pd.to_datetime(j.target_time_utc,utc=True).dt.date.to_numpy()
  c=ci_day(diff,dates,4303+h)
  row=reported[(reported.horizon_hours==h)&(reported.model==model)&(reported.comparison=='srtm_minus_none')].iloc[0]
  comp[str(h)]={'n_pairs':len(j),'delta_mae':float(diff.mean()),'ci95':c,'reported_delta':float(row.delta_mae_ug_m3),'reported_ci':[float(row.mae_ci_low),float(row.mae_ci_high)]}
 station=pd.read_csv(R/'dem_station_values_v2h.csv')
 graph=pd.read_parquet(REPO_ROOT/'data/processed/graph/nodes_elevation_true.parquet')[['osmid','elevation_true']]
 merged=station.merge(graph,left_on='node_id',right_on='osmid',validate='one_to_one')
 return {'raw_rows':len(raw),'unique_fit_keys':raw[keys+['seed']].drop_duplicates().shape[0],'duplicate_prediction_keys':int(duplicates),'seeds_min_max':[int(seed_counts.min()),int(seed_counts.max())],'target_nunique_max':int(target_consistency),'max_variant_mae_abs_error':max_mae_error,'srtm_vs_none':comp,'station_elevation_max_abs_error':float(np.max(np.abs(merged.elevation_m-merged.elevation_true_y))),'elevation_northing_r':float(station.elevation_m.corr(station.northing_m))}

def w4():
 z=np.load(R/'data_v2g_arrays.npz');times=pd.DatetimeIndex(pd.to_datetime(z['times_ns'],utc=True));y=z['observed_target'];obs=z['observed_mask'];ids=z['station_ids']
 train=np.asarray((times>=pd.Timestamp('2022-01-01T00:00:00Z'))&(times<=pd.Timestamp('2025-06-29T23:00:00Z')))
 val=np.asarray((times>=pd.Timestamp('2025-07-01T00:00:00Z'))&(times<=pd.Timestamp('2025-09-21T23:00:00Z')))
 test=np.asarray((times>=pd.Timestamp('2025-09-23T00:00:00Z'))&(times<=pd.Timestamp('2026-03-28T23:00:00Z')))
 frame=pd.read_csv(R/'sensor_density_v2h.csv');scored=frame[frame.status=='scored']
 populations=[];draw_mismatch=0;n_mismatch=0;within_draw_mismatch=0
 for h in (1,24):
  train_pairs=(obs[h:]&obs[:-h]&train[h:,None]).sum(0);val_pairs=(obs[h:]&obs[:-h]&val[h:,None]).sum(0)
  eligible=ids[train_pairs>0];val_eligible=set(ids[val_pairs>0].tolist())
  for count in (3,5):
   for draw in range(1,6):
    part=scored[(scored.horizon_hours==h)&(scored.train_station_count==count)&(scored.draw==draw)]
    assert len(part)==5
    rng=np.random.default_rng(4400+count*100+draw)
    for _ in range(100):
     chosen=rng.choice(eligible,count,replace=False)
     if any(int(s) in val_eligible for s in chosen):break
    listed=set(map(int,str(part.train_station_ids.iloc[0]).split(';')))
    if listed!=set(map(int,chosen)):draw_mismatch+=1
    if part.train_station_ids.nunique()!=1 or part.test_n.nunique()!=1:within_draw_mismatch+=1
    held=~np.isin(ids,chosen);mask=obs & test[:,None] & held[None,:]
    # Context.hours[test] scores every observed target at a held-out station.
    n=int(mask.sum());target=y[mask]
    if not (part.test_n==n).all():n_mismatch+=1
    populations.append({'horizon_hours':h,'train_station_count':count,'draw':draw,'train_station_ids':';'.join(map(str,sorted(chosen))),'target_n':n,'target_mean':float(target.mean()),'target_sd':float(target.std()),'target_median':float(np.median(target))})
 p=pd.DataFrame(populations);p.to_csv(O/'w4_target_populations.csv',index=False)
 return {'scored_rows':len(scored),'blocked_rows':int(len(frame)-len(scored)),'draws':len(p),'draw_selection_mismatches':draw_mismatch,'within_draw_population_mismatches':within_draw_mismatch,'test_n_mismatches':n_mismatch,'target_n_range_by_count':{str(k):[int(v.target_n.min()),int(v.target_n.max())] for k,v in p.groupby('train_station_count')},'target_mean_range_by_count':{str(k):[float(v.target_mean.min()),float(v.target_mean.max())] for k,v in p.groupby('train_station_count')},'all_cross_count_target_n_equal':bool(p.groupby(['horizon_hours','draw']).target_n.nunique().eq(1).all())}

def protocol():
 result={}
 p1=pd.read_parquet(R/'neural_predictions_v2.parquet');b1=pd.read_parquet(R/'baselines_v2_predictions.parquet')
 p1=p1[(p1.model=='stpignn_corrected_imputed')&(p1.seed==37)]
 result['P1']={'st_mae':mae(p1.target_ug_m3,p1.prediction_ug_m3),'persistence_mae':mae(b1.target_ug_m3,b1.persistence_ug_m3),'pairs_st':len(p1),'pairs_baseline':len(b1),'keys_equal':set(map(tuple,p1[['station_id','target_time_utc']].to_numpy()))==set(map(tuple,b1[['station_id','target_time_utc']].to_numpy()))}
 for level,suf,baseline in [('P2','v2b','baselines_v2b_predictions.parquet'),('P3','v2c','baselines_v2b_predictions.parquet')]:
  d=pd.read_parquet(R/f'neural_predictions_{suf}.parquet');d=d[d.model=='stpignn_corrected']
  se=d.groupby('seed').apply(lambda q:mae(q.target_ug_m3,q.prediction_ug_m3),include_groups=False)
  ensemble=d.groupby(['station_id','target_time_utc'],as_index=False).agg(target=('target_ug_m3','first'),prediction=('prediction_ug_m3','mean'))
  b=pd.read_parquet(R/baseline)
  result[level]={'st_mean_seed_mae':float(se.mean()),'st_ensemble_mae':mae(ensemble.target,ensemble.prediction),'persistence_mae':mae(b.target_ug_m3,b.persistence_ug_m3),'seeds':se.index.astype(int).tolist(),'pairs_per_seed':d.groupby('seed').size().unique().astype(int).tolist(),'baseline_pairs':len(b),'keys_equal':set(map(tuple,d[d.seed==se.index[0]][['station_id','target_time_utc']].to_numpy()))==set(map(tuple,b[['station_id','target_time_utc']].to_numpy()))}
 return result

def conformal():
 reported=pd.read_csv(R/'conformal_v2h.csv');records=[];max_cov=max_score=max_width=0.;n_mismatch=0
 for path in sorted((R/'conformal_predictions_v2h').glob('*.parquet')):
  d=pd.read_parquet(path);cal=d[d.split=='calibration'];test=d[d.split=='test']
  assert pd.to_datetime(cal.time,utc=True).max()<pd.to_datetime(test.time,utc=True).min()
  y=test.target.to_numpy(dtype=float);pred=test.prediction.to_numpy(dtype=float)
  err=np.abs(cal.target.to_numpy(dtype=float)-cal.prediction.to_numpy(dtype=float))
  dates=pd.to_datetime(test.time,utc=True).dt.date.to_numpy()
  h=int(d.horizon_hours.iloc[0]);cal_name=str(d.calibration.iloc[0]);model=str(d.model.iloc[0])
  for nominal in (.8,.9):
   rank=min(len(err),int(np.ceil((len(err)+1)*nominal)))
   q=float(np.sort(err)[rank-1])
   for variant in ('fixed','rolling_daily'):
    widths=np.full(len(y),q)
    if variant=='rolling_daily':
     history=err.copy()
     for day in np.unique(dates):
      at=np.flatnonzero(dates==day)
      rank_day=min(len(history),int(np.ceil((len(history)+1)*nominal)))
      widths[at]=float(np.sort(history)[rank_day-1])
      history=np.r_[history,np.abs(y[at]-pred[at])]
    low=np.maximum(0,pred-widths);high=pred+widths
    cover=(y>=low)&(y<=high)
    score=high-low+2/(1-nominal)*np.maximum(low-y,0)+2/(1-nominal)*np.maximum(y-high,0)
    row=reported[(reported.horizon_hours.astype(str)==str(h))&(reported.calibration==cal_name)&(reported.model==model)&(reported.nominal==nominal)&(reported.variant==variant)].iloc[0]
    max_cov=max(max_cov,abs(float(cover.mean())-row.coverage));max_score=max(max_score,abs(float(score.mean())-row.interval_score));max_width=max(max_width,abs(float((high-low).mean())-row.mean_width))
    n_mismatch+=int(len(y)!=row.n)
    records.append({'horizon':h,'calibration':cal_name,'model':model,'nominal':nominal,'variant':variant,'n_cal':len(err),'n_test':len(y),'coverage':float(cover.mean()),'mean_width':float((high-low).mean()),'interval_score':float(score.mean()),'q_initial':q})
 return {'prediction_files':len(list((R/'conformal_predictions_v2h').glob('*.parquet'))),'recomputed_horizon_rows':len(records),'max_coverage_abs_error':max_cov,'max_interval_score_abs_error':max_score,'max_width_abs_error':max_width,'n_mismatches':n_mismatch,'example':records[0]}

def groupdro():
 raw=pd.read_parquet(R/'loso_groupdro_predictions_v2h.parquet');base=pd.read_parquet(R/'loso_predictions_v2c.parquet');base=base[(base.seed==-1)&(base.method=='ridge_weather_static')]
 grp=raw.groupby(['station_id','method','target_time_utc','target'],as_index=False).prediction.mean()
 out={}
 for method in ('erm','dro_eta_0.01','dro_eta_0.1'):
  d=grp[grp.method==method];j=d.merge(base[['station_id','target_time_utc','prediction','target']],on=['station_id','target_time_utc'],suffixes=('_model','_baseline'),validate='one_to_one')
  assert len(j)==len(d)==len(base) and np.allclose(j.target_model,j.target_baseline)
  y=j.target_model;pm=j.prediction_model;pb=j.prediction_baseline
  diff=np.abs(pm-y)-np.abs(pb-y);dates=pd.to_datetime(j.target_time_utc,utc=True).dt.date.to_numpy()
  out[method]={'n':len(j),'seeds':sorted(raw[raw.method==method].seed.unique().astype(int).tolist()),'mae':mae(y,pm),'r2':r2(y,pm),'baseline_mae':mae(y,pb),'baseline_r2':r2(y,pb),'delta_mae':float(diff.mean()),'ci95':ci_day(diff,dates,4303)}
 reported=pd.read_csv(R/'loso_groupdro_v2h.csv')
 return {'raw_rows':len(raw),'fit_keys':raw[['station_id','method','seed']].drop_duplicates().shape[0],'scored_stations':sorted(raw.station_id.unique().astype(int).tolist()),'selected_eta_reported':float(reported.loc[reported.method=='group-DRO','selected_eta'].iloc[0]),'methods':out}

if __name__=='__main__':
 result={'source_commit_examined':SOURCE,'W3':dem(),'W4':w4(),'P1_P3':protocol(),'conformal':conformal(),'groupdro':groupdro()}
 (O/'recomputed_metrics.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:('written' if isinstance(v,dict) else v) for k,v in result.items()},indent=2))
