from pathlib import Path
import pandas as pd,numpy as np
base=Path('final_blr_results/final_research_v2r/citywide/spatial_decoder')
d=pd.read_parquet(base/'folds/all_spatial_test_predictions.parquet')
methods=['train_only_spatial_mean','forecast_idw','forecast_decoder']
def metrics(g,m):
 y=g.target_ug_m3.to_numpy();p=g[m].to_numpy();e=p-y
 return {'n_pairs':len(y),'mae':float(np.mean(np.abs(e))),'rmse':float(np.sqrt(np.mean(e**2))),'r2':float(1-np.sum(e**2)/np.sum((y-y.mean())**2))}
rows=[]
for sid,g in d.groupby('station_id'):
 for m in methods: rows.append({'level':'station','station_id':sid,'method':m,**metrics(g,m)})
for m in methods: rows.append({'level':'pooled','station_id':'all','method':m,**metrics(d,m)})
out=pd.DataFrame(rows);out.to_csv('final_blr_results/ieee_paper_evidence/results/RECOMPUTED_V2R_SPATIAL_METRICS.csv',index=False)
ref=pd.read_csv(base/'pooled_test_metrics.csv'); comps=[]
for _,r in out[out.level=='pooled'].iterrows():
 rr=ref[ref.method==r.method].iloc[0]
 for metric in ['mae','rmse','r2','n_pairs']:
  refkey={'n_pairs':'n'}[metric] if metric=='n_pairs' else metric
  if refkey not in rr.index: refkey={'train_only_spatial_mean':'mean','forecast_idw':'idw','forecast_decoder':'decoder'}[r.method]+'_'+refkey
  if refkey in rr.index:
   a=float(r[metric]);b=float(rr[refkey]);comps.append({'method':r.method,'metric':metric,'recomputed':a,'saved_summary':b,'absolute_difference':abs(a-b),'match_within_1e-8':abs(a-b)<1e-8})
pd.DataFrame(comps).to_csv('final_blr_results/ieee_paper_evidence/results/RECOMPUTED_V2R_SUMMARY_COMPARISON.csv',index=False)
print('rows',len(d),'stations',d.station_id.nunique(),'metrics',len(rows));print(out[out.level=='pooled'].to_string(index=False));print(pd.DataFrame(comps).to_string(index=False))
