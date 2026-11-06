from pathlib import Path
from zipfile import ZipFile
from io import BytesIO
import pandas as pd,numpy as np
archive=Path('final_blr_results/baselines/v2m/reproducibility/research_results_v2m.zip')
models=['mlp','tcn']; horizons=[1,3,6,12,24]; seeds=[11,23,37,51,79]
def metrics(y,p):
 e=p-y
 return {'mae':float(np.mean(np.abs(e))),'rmse':float(np.sqrt(np.mean(e**2))),'r2':float(1-np.sum(e**2)/np.sum((y-y.mean())**2)),'n_pairs':int(len(y))}
individual=[]; ensemble=[]
with ZipFile(archive) as z:
 for model in models:
  for h in horizons:
   frames=[]
   for seed in seeds:
    name=f'final_blr_results/baselines/v2m/{model}/h{h}/seed{seed}/predictions.parquet'
    df=pd.read_parquet(BytesIO(z.read(name)));frames.append(df)
    mm=metrics(df.target_ug_m3.to_numpy(),df.prediction_ug_m3.to_numpy());individual.append({'model':model,'horizon_hours':h,'seed':seed,**mm})
   base=frames[0][['target_time_utc','station_id','target_ug_m3']].copy()
   for j,df in enumerate(frames):
    if not base[['target_time_utc','station_id','target_ug_m3']].equals(df[['target_time_utc','station_id','target_ug_m3']]):raise ValueError(f'pair mismatch {model} h{h} seed{seeds[j]}')
    base[f'p{j}']=df.prediction_ug_m3.to_numpy()
   pm=base[[f'p{j}' for j in range(5)]].mean(axis=1).to_numpy(); yy=base.target_ug_m3.to_numpy()
   ensemble.append({'model':model,'horizon_hours':h,'aggregation':'five-seed mean prediction',**metrics(yy,pm)})
ind=pd.DataFrame(individual);ens=pd.DataFrame(ensemble)
ind.to_csv('final_blr_results/ieee_paper_evidence/results/RECOMPUTED_V2M_INDIVIDUAL_METRICS.csv',index=False);ens.to_csv('final_blr_results/ieee_paper_evidence/results/RECOMPUTED_V2M_ENSEMBLE_METRICS.csv',index=False)
refi=pd.read_csv('final_blr_results/baselines/v2m/comparisons/individual_seed_metrics.csv');refe=pd.read_csv('final_blr_results/baselines/v2m/comparisons/ensemble_metrics.csv')
comp=[]
for _,r in ind.iterrows():
 x=refi[(refi.model==r.model)&(refi.horizon_hours==r.horizon_hours)&(refi.seed==r.seed)].iloc[0]
 for m in ['mae','rmse','r2','n_pairs']:comp.append({'table':'individual','model':r.model,'horizon_hours':r.horizon_hours,'seed':r.seed,'metric':m,'recomputed':r[m],'saved':x[m],'abs_diff':abs(float(r[m])-float(x[m]))})
for _,r in ens.iterrows():
 x=refe[(refe.model==r.model)&(refe.horizon_hours==r.horizon_hours)&(refe.aggregation==r.aggregation)].iloc[0]
 for m in ['mae','rmse','r2','n_pairs']:comp.append({'table':'ensemble','model':r.model,'horizon_hours':r.horizon_hours,'seed':'five-seed','metric':m,'recomputed':r[m],'saved':x[m],'abs_diff':abs(float(r[m])-float(x[m]))})
c=pd.DataFrame(comp);c['match_within_5e-6']=c.abs_diff<5e-6;c.to_csv('final_blr_results/ieee_paper_evidence/results/RECOMPUTED_V2M_SUMMARY_COMPARISON.csv',index=False)
print('individual model-seed cells',len(ind),'ensembles',len(ens),'metric comparisons',len(c),'max_abs_difference',c.abs_diff.max(),'mismatches',int((~c['match_within_5e-6']).sum()))
