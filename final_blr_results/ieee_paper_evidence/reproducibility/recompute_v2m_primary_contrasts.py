from zipfile import ZipFile
from io import BytesIO
import pandas as pd,numpy as np
v2m='final_blr_results/baselines/v2m/reproducibility/research_results_v2m.zip';old='final_blr_results/research_backup_exports/research_backup_pretrain_v2m.zip'
rows=[]
with ZipFile(v2m) as znew,ZipFile(old) as zold:
 for h in [1,3,6,12,24]:
  name=f'results/benchmark_predictions_h{h}_stpignn_original_seed11_v2j.parquet'
  # five historical ST-PIGNN seeds
  st=[]
  for seed in [11,23,37,51,79]:
   p=f'results/benchmark_predictions_h{h}_stpignn_original_seed{seed}_v2j.parquet'
   st.append(pd.read_parquet(BytesIO(zold.read(p))))
  keys=['target_time_utc','station_id']
  base=st[0][keys+['target_ug_m3','prediction_ug_m3']].rename(columns={'prediction_ug_m3':'s0','target_ug_m3':'target_0'}).sort_values(['target_time_utc','station_id']).reset_index(drop=True)
  for k,d in enumerate(st[1:],1):
   dd=d[keys+['target_ug_m3','prediction_ug_m3']].rename(columns={'prediction_ug_m3':f's{k}','target_ug_m3':f'target_{k}'})
   base=base.merge(dd,on=keys,how='inner',validate='one_to_one')
   if len(base)!=len(d) or not np.allclose(base.target_0,base[f'target_{k}']): raise ValueError(f'ST-PIGNN target mismatch h{h}')
  base['target_ug_m3']=base.target_0
  base['stpignn_prediction']=base[[f's{k}' for k in range(5)]].mean(axis=1)
  for model in ['mlp','tcn']:
   preds=[]
   for seed in [11,23,37,51,79]:
    p=f'final_blr_results/baselines/v2m/{model}/h{h}/seed{seed}/predictions.parquet'
    preds.append(pd.read_parquet(BytesIO(znew.read(p))))
   compare=base[keys+['target_ug_m3','stpignn_prediction']].copy().sort_values(['target_time_utc','station_id']).reset_index(drop=True)
   for k,d in enumerate(preds):
    dd=d[keys+['target_ug_m3','prediction_ug_m3']].rename(columns={'prediction_ug_m3':f'p{k}','target_ug_m3':f'target_baseline_{k}'})
    compare=compare.merge(dd,on=keys,how='inner',validate='one_to_one')
    if len(compare)!=len(d) or not np.allclose(compare.target_ug_m3,compare[f'target_baseline_{k}']):raise ValueError(f'pair mismatch {model} h{h} seed {k}')
   compare['baseline_prediction']=compare[[f'p{k}' for k in range(5)]].mean(axis=1)
   compare['paired_abs_error_diff']=abs(compare.stpignn_prediction-compare.target_ug_m3)-abs(compare.baseline_prediction-compare.target_ug_m3)
   delta=compare.paired_abs_error_diff.mean();base_mae=abs(compare.baseline_prediction-compare.target_ug_m3).mean()
   rows.append({'horizon_hours':h,'baseline':model,'n_pairs':len(compare),'utc_days':pd.to_datetime(compare.target_time_utc,utc=True).dt.floor('D').nunique(),'recomputed_stpignn_mae':abs(compare.stpignn_prediction-compare.target_ug_m3).mean(),'recomputed_baseline_mae':base_mae,'recomputed_delta_mae':delta,'recomputed_relative_percent':100*delta/base_mae})
out=pd.DataFrame(rows);out.to_csv('final_blr_results/ieee_paper_evidence/results/RECOMPUTED_V2M_PRIMARY_DELTAS.csv',index=False)
ref=pd.read_csv('final_blr_results/baselines/v2m/comparisons/primary_ten_comparisons.csv'); comp=[]
for _,r in out.iterrows():
 q=ref[(ref.horizon_hours==r.horizon_hours)&(ref.baseline==r.baseline)].iloc[0]
 comp.append({'horizon_hours':r.horizon_hours,'baseline':r.baseline,'recomputed_delta':r.recomputed_delta_mae,'saved_delta':q.paired_mae_difference,'absolute_difference':abs(r.recomputed_delta_mae-q.paired_mae_difference),'recomputed_relative_percent':r.recomputed_relative_percent,'saved_relative_percent':q.relative_difference_percent,'relative_difference_abs':abs(r.recomputed_relative_percent-q.relative_difference_percent),'n_pairs_match':r.n_pairs==q.n_pairs})
pd.DataFrame(comp).to_csv('final_blr_results/ieee_paper_evidence/results/RECOMPUTED_V2M_PRIMARY_COMPARISON.csv',index=False)
print('recomputed frozen contrasts',len(out),'max delta difference',max(x['absolute_difference'] for x in comp),'max relative difference',max(x['relative_difference_abs'] for x in comp),'all pair counts match',all(x['n_pairs_match'] for x in comp))
print(pd.DataFrame(comp).to_string(index=False))
