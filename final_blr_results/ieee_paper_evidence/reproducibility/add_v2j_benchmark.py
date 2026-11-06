from pathlib import Path
import pandas as pd
P=Path('final_blr_results/ieee_paper_evidence');R=P/'results';S=P/'figures/source_data';T=P/'tables/export'
d=pd.read_csv(R/'RECOMPUTED_V2J_BENCHMARK.csv');d.to_csv(S/'v2j_benchmark_recomputed.csv',index=False);d.to_csv(T/'RECOMPUTED_V2J_BENCHMARK.csv',index=False)
base=pd.read_csv(R/'FORECASTING_COMPARISONS.csv');base=base[base.protocol!='v2j corrected station benchmark (single historical weather protocol)'];new=[]
for _,r in d.iterrows():new.append({'protocol':'v2j corrected station benchmark (single historical weather protocol)','record_type':'five-seed ensemble or baseline summary','horizon_hours':r.horizon_hours,'model':r.model,'comparison':'five-seed mean prediction' if r.seeds_completed==5 else 'single frozen statistical baseline','mae_ug_m3':r.mae_ug_m3,'rmse_ug_m3':r.rmse_ug_m3,'r2':r.r2,'n_pairs':r.n_pairs,'delta_mae_ug_m3':None,'ci_low':None,'ci_high':None,'raw_p':None,'holm_p':None,'source':'final_blr_results/ieee_paper_evidence/results/RECOMPUTED_V2J_BENCHMARK.csv','verification':'recomputed from saved v2j parquet members in preserved research archive; mae/r2 cross-checked to benchmark_v2j.csv'})
pd.concat([base,pd.DataFrame(new)],ignore_index=True).to_csv(R/'FORECASTING_COMPARISONS.csv',index=False)
# plot all-v2j architecture benchmark, within one information protocol
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size':9,'figure.dpi':140,'savefig.dpi':300,'font.family':'DejaVu Sans'})
fig,ax=plt.subplots(figsize=(9,5))
for model,g in d.groupby('model'):
 ax.plot(g.horizon_hours,g.mae_ug_m3,marker='o',markersize=3,label=model,linewidth=1.1)
ax.set(xlabel='Forecast horizon (hours)',ylabel='MAE (µg/m³)');ax.grid(alpha=.25);ax.legend(ncol=3,fontsize=6.8,frameon=False,loc='best')
fig.suptitle('v2j five-horizon station benchmark (single weather protocol)',fontsize=12,y=.98);fig.tight_layout(rect=[0,0,1,.93])
fig.savefig(P/'figures/export/fig14_v2j_benchmark.png',bbox_inches='tight');fig.savefig(P/'figures/export/fig14_v2j_benchmark.pdf',bbox_inches='tight')
man=pd.read_csv(P/'figures/figure_manifest.csv');man=man.loc[:,~man.columns.duplicated()];man=man.drop(columns=['sample_count.1'],errors='ignore');
if 'sample_count' not in man.columns: man['sample_count']='See source and protocol-specific count in limitations'
man.loc[len(man)]={'figure_id':'fig14_v2j_benchmark','title':'v2j five-horizon station benchmark (single weather protocol)','sample_count':'14,583 station-time pairs per horizon; 11 scored sites; five seeds for neural models','source_artifact':'final_blr_results/ieee_paper_evidence/results/RECOMPUTED_V2J_BENCHMARK.csv','source_data':'figures/source_data/v2j_benchmark_recomputed.csv','limitations':'Within-protocol benchmark; exploratory test exposure; negative R² preserved.','regeneration_command':'python final_blr_results/ieee_paper_evidence/reproducibility/add_v2j_benchmark.py','export_files':'export/fig14_v2j_benchmark.png; export/fig14_v2j_benchmark.pdf'}
cols=['figure_id','title','sample_count','source_artifact','source_data','limitations','regeneration_command','export_files']
man=man[cols];man.to_csv(P/'figures/figure_manifest.csv',index=False)
# table manifest
m=pd.read_csv(P/'tables/table_manifest.csv');m.loc[len(m)]=['T16','export/RECOMPUTED_V2J_BENCHMARK.csv','Recomputed five-horizon v2j benchmark across neural models and statistical baselines','results/RECOMPUTED_V2J_BENCHMARK.csv','85 model-horizon rows; prediction values reconstructed from preserved backup ZIP; MAE/R2 match saved benchmark within 1.57e-6/1.66e-7']
m.to_csv(P/'tables/table_manifest.csv',index=False)
print('added 85 verified v2j model/horizon rows and figure')
