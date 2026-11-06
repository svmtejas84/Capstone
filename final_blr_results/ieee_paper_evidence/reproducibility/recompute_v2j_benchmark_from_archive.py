from zipfile import ZipFile
from io import BytesIO
from pathlib import Path
import pandas as pd,numpy as np
archive='final_blr_results/research_backup_exports/research_backup_pretrain_v2m.zip'
ref=pd.read_csv('results/benchmark_v2j.csv')
base_member=lambda h:f'results/benchmark_predictions_h{h}_baselines_v2j.parquet'
seedlist=[11,23,37,51,79]
rows=[]
with ZipFile(archive) as z:
 for _,rr in ref.iterrows():
  h=int(rr.horizon_hours);model=rr.model
  if model in ['persistence','same_hour_yesterday','station_train_mean','climatology_hod_dow','ridge_lag_calendar_weather']:
   df=pd.read_parquet(BytesIO(z.read(base_member(h))));df=df[(df.model==model)&(df.horizon_hours==h)].copy();
   if df.empty: raise ValueError(f'no baseline rows {model} h{h}')
   y=df.target_ug_m3.to_numpy();p=df.prediction_ug_m3.to_numpy();nseeds=1
  else:
   pieces=[]
   for seed in seedlist:
    member=f'results/benchmark_predictions_h{h}_{model}_seed{seed}_v2j.parquet'
    df=pd.read_parquet(BytesIO(z.read(member)));pieces.append(df)
   keys=['target_time_utc','station_id'];base=pieces[0][keys+['target_ug_m3','prediction_ug_m3']].rename(columns={'target_ug_m3':'target_0','prediction_ug_m3':'p0'}).sort_values(keys).reset_index(drop=True)
   for i,d in enumerate(pieces[1:],1):
    add=d[keys+['target_ug_m3','prediction_ug_m3']].rename(columns={'target_ug_m3':f'target_{i}','prediction_ug_m3':f'p{i}'})
    base=base.merge(add,on=keys,validate='one_to_one')
    if not np.allclose(base.target_0,base[f'target_{i}']):raise ValueError(f'target mismatch {model} h{h}')
   y=base.target_0.to_numpy();p=base[[f'p{i}' for i in range(5)]].mean(axis=1).to_numpy();nseeds=5
  e=p-y;mae=float(np.mean(np.abs(e)));rmse=float(np.sqrt(np.mean(e**2)));r2=float(1-np.sum(e**2)/np.sum((y-y.mean())**2))
  rows.append({'horizon_hours':h,'model':model,'n_pairs':len(y),'mae_ug_m3':mae,'rmse_ug_m3':rmse,'r2':r2,'seeds_completed':nseeds,'saved_mae':float(rr.test_mae_ug_m3),'saved_r2':float(rr.test_r2),'abs_mae_diff':abs(mae-float(rr.test_mae_ug_m3)),'abs_r2_diff':abs(r2-float(rr.test_r2))})
out=pd.DataFrame(rows);out.to_csv('final_blr_results/ieee_paper_evidence/results/RECOMPUTED_V2J_BENCHMARK.csv',index=False)
print('rows',len(out),'all 14583 pairs',bool((out.n_pairs==14583).all()),'max MAE diff',out.abs_mae_diff.max(),'max R2 diff',out.abs_r2_diff.max())
