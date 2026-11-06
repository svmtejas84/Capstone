from pathlib import Path
import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
P=Path('final_blr_results/ieee_paper_evidence'); out=P/'figures/export'; src=P/'figures/source_data'; out.mkdir(parents=True,exist_ok=True)
plt.rcParams.update({'font.size':10,'axes.titlesize':12,'axes.labelsize':10,'figure.dpi':140,'savefig.dpi':300,'font.family':'DejaVu Sans'})
manifest=[]
def save(fig,id,title,source,lim):
 fig.suptitle(title,fontsize=12,y=.98); fig.tight_layout(rect=[0,0,1,.93]); fig.savefig(out/f'{id}.png',bbox_inches='tight'); fig.savefig(out/f'{id}.pdf',bbox_inches='tight'); plt.close(fig); srcmap={'final_blr_results/baselines/v2m/comparisons/ensemble_metrics.csv':'figures/source_data/v2m_ensemble_metrics.csv','final_blr_results/physics_audit/FINAL_PHYSICS_VERDICT.md':'figures/source_data/v2l_physics_effects.csv','final_blr_results/physics_audit/seed_analysis/per_seed_physics_comparisons.csv':'figures/source_data/v2l_per_seed_physics.csv','final_blr_results/final_research_v2r/citywide/spatial_validation/SPATIAL_VALIDATION_VERDICT.md':'figures/source_data/v2r_spatial_pooled.csv','final_blr_results/final_research_v2r/citywide/spatial_decoder/per_station_test_metrics.csv':'figures/source_data/v2r_per_station_metrics.csv','final_blr_results/final_research_v2r/citywide/road_predictions/map_points_20251008T0700Z.csv':'figures/source_data/v2r_citywide_snapshot_support.csv','final_blr_results/final_research_v2r/rgdr/gate_diagnostics/gate_diagnostics_v2r.csv':'figures/source_data/v2r_rgdr_gate_diagnostics.csv','final_blr_results/city_scale/explainability/convergence_diagnostics.csv':'figures/source_data/captum_convergence_diagnostics.csv'}; manifest.append([id,title,f'export/{id}.png; export/{id}.pdf',source,srcmap.get(source,source),lim,'python final_blr_results/ieee_paper_evidence/reproducibility/generate_figures.py'])
# 1 baseline MAE by horizon
p=Path('final_blr_results/baselines/v2m/comparisons/ensemble_metrics.csv'); d=pd.read_csv(p); d.to_csv(src/'v2m_ensemble_metrics.csv',index=False)
d=d[d.model.isin(['mlp','tcn','stpignn_original','ridge_lag_calendar_weather','persistence','same_hour_yesterday','station_train_mean','climatology_hod_dow','vanilla_gcn','gru_only','st_gru_gcn'])]
fig,ax=plt.subplots(figsize=(8,4.8))
for n,g in d.groupby('model'):
 if g.horizon_hours.nunique()>=5: ax.plot(g.horizon_hours,g.mae,marker='o',linewidth=1.5,label=n)
ax.set(xlabel='Forecast horizon (hours)',ylabel='MAE (µg/m³)');ax.legend(ncol=2,fontsize=7,frameon=False);ax.grid(alpha=.25)
save(fig,'fig01_forecasting_mae','Exploratory Bengaluru benchmark MAE by horizon — protocols differ', 'final_blr_results/baselines/v2m/comparisons/ensemble_metrics.csv','v2m MLP/TCN weather protocol differs from historical ST-PIGNN; report-level ensemble metrics; repeated Bengaluru test exposure.')
# 2 selected strong baselines
sel=d[d.model.isin(['mlp','tcn','stpignn_original','ridge_lag_calendar_weather','persistence','same_hour_yesterday','station_train_mean','climatology_hod_dow'])]
fig,ax=plt.subplots(figsize=(8,4.8))
for n,g in sel.groupby('model'): ax.plot(g.horizon_hours,g.mae,marker='o',label=n)
ax.set(xlabel='Forecast horizon (hours)',ylabel='MAE (µg/m³)');ax.legend(ncol=2,fontsize=8,frameon=False);ax.grid(alpha=.25)
save(fig,'fig02_statistical_baselines','Neural and conventional baseline MAE by horizon','final_blr_results/baselines/v2m/comparisons/ensemble_metrics.csv','Cross-protocol comparison; do not interpret as identical-input ablation.')
# 3 physics effects
p=Path('final_blr_results/physics_audit/FINAL_PHYSICS_VERDICT.md'); h=np.array([1,3,6,12,24]); delta=np.array([-.026,-.130,-.410,-.262,.145])
df=pd.DataFrame({'horizon_hours':h,'physics_minus_lambda0_mae_ug_m3':delta,'pairs':[14583]*5,'sites':[11]*5,'source_report':['final_blr_results/physics_audit/FINAL_PHYSICS_VERDICT.md']*5});df.to_csv(src/'v2l_physics_effects.csv',index=False)
fig,ax=plt.subplots(figsize=(7,4));ax.axhline(0,color='black',lw=.8);ax.bar(h,delta,color=['#5470c6' if x<0 else '#c44e52' for x in delta]);ax.set(xlabel='Forecast horizon (hours)',ylabel='ΔMAE (physics − λ=0, µg/m³)');ax.grid(axis='y',alpha=.25)
save(fig,'fig03_physics_vs_lambda0','Directional penalty effect is horizon-dependent','final_blr_results/physics_audit/FINAL_PHYSICS_VERDICT.md','Negative favors physics; paired raw prediction arrays not present in package; no physical validity inference.')
# 4 per-seed stability from csv
p=Path('final_blr_results/physics_audit/seed_analysis/per_seed_physics_comparisons.csv'); d=pd.read_csv(p); d.to_csv(src/'v2l_per_seed_physics.csv',index=False);d=d[d.comparison=='physics-lambda0']
fig,ax=plt.subplots(figsize=(7,4.5))
for seed,g in d.groupby('seed'):ax.plot(g.horizon_hours,g.paired_mae_difference,marker='o',alpha=.7,label=str(seed))
ax.axhline(0,color='black',lw=.8);ax.set(xlabel='Forecast horizon (hours)',ylabel='Paired ΔMAE (physics − λ=0, µg/m³)');ax.legend(title='Seed',ncol=5,fontsize=8);ax.grid(alpha=.25)
save(fig,'fig04_physics_seed_stability','Per-seed directional penalty effects','final_blr_results/physics_audit/seed_analysis/per_seed_physics_comparisons.csv','Five seeds; exploratory exposed test; ensemble dependence and block sensitivity documented in v2l report.')
# 5 spatial pooled methods
vals=['Training-only mean','Forecast IDW','Compact decoder']; maes=[20.634,20.154,27.360]; rmses=[38.614,39.295,44.046]
df=pd.DataFrame({'method':vals,'mae_ug_m3':maes,'rmse_ug_m3':rmses,'r2':[-.085,-.124,-.412],'n_pairs':[14583]*3,'n_sites':[11]*3});df.to_csv(src/'v2r_spatial_pooled.csv',index=False)
fig,ax=plt.subplots(figsize=(7,4));x=np.arange(3);ax.bar(x-.18,maes,.36,label='MAE');ax.bar(x+.18,rmses,.36,label='RMSE');ax.set_xticks(x,vals,rotation=12);ax.set_ylabel('Error (µg/m³)');ax.legend(frameon=False);ax.grid(axis='y',alpha=.25)
save(fig,'fig05_spatial_holdout','Six-hour LOSO: compact decoder underperforms controls','final_blr_results/final_research_v2r/citywide/spatial_validation/SPATIAL_VALIDATION_VERDICT.md','11 independent station sites; 14,583 repeated station-time pairs; not roadside validation.')
# 6 per site MAE + coverage
p=Path('final_blr_results/final_research_v2r/citywide/spatial_decoder/per_station_test_metrics.csv'); d=pd.read_csv(p);d.to_csv(src/'v2r_per_station_metrics.csv',index=False); fig,ax=plt.subplots(figsize=(9,5));x=np.arange(len(d));
for off,col,label in [(-.24,'train_only_spatial_mean_mae','Mean'),(0,'forecast_idw_mae','Forecast IDW'),(.24,'forecast_decoder_mae','Decoder')]:ax.bar(x+off,d[col],width=.23,label=label)
ax.set_xticks(x,d.station_id.astype(str),rotation=45);ax.set(xlabel='Held-out station ID',ylabel='MAE (µg/m³)');ax.legend(frameon=False);ax.grid(axis='y',alpha=.25); save(fig,'fig06_spatial_per_station','Per-station six-hour LOSO MAE','final_blr_results/final_research_v2r/citywide/spatial_decoder/per_station_test_metrics.csv','Site is the independent spatial unit; station counts vary; four stations unscored.')
# 7 support diagnostic
p=Path('final_blr_results/final_research_v2r/citywide/road_predictions/map_points_20251008T0700Z.csv'); d=pd.read_csv(p); d.to_csv(src/'v2r_citywide_snapshot_support.csv',index=False)
fig,ax=plt.subplots(figsize=(6,5)); colors=np.where(d.poor_support_gt5km,'#c44e52','#4c72b0'); ax.scatter(d.utm_x_m/1000,d.utm_y_m/1000,c=colors,s=1,alpha=.35,rasterized=True); ax.set(xlabel='Projected easting (km)',ylabel='Projected northing (km)');
save(fig,'fig07_citywide_support','Road-node estimate locations: support flag (>5 km from monitor)','final_blr_results/final_research_v2r/citywide/road_predictions/map_points_20251008T0700Z.csv','One frozen h6 snapshot; estimates are not observations; no road labels; red flags indicate support distance only.')
# 8 RGDR retention
p=Path('final_blr_results/final_research_v2r/rgdr/gate_diagnostics/gate_diagnostics_v2r.csv'); d=pd.read_csv(p);d.to_csv(src/'v2r_rgdr_gate_diagnostics.csv',index=False); train=d[d.split=='train'].iloc[0]
fig,ax=plt.subplots(figsize=(6,4)); labels=['Binary V1','Continuous V2'];vals=[train.binary_retention_fraction*100,train.continuous_retention_fraction*100];ax.bar(labels,vals,color=['#8172b2','#55a868']);ax.axhline(10,color='#c44e52',ls='--',label='Frozen 10% minimum');ax.set(ylabel='Directional edge mass retained (%)',title='Training-only h=6 feasibility');ax.legend(frameon=False);ax.grid(axis='y',alpha=.25)
save(fig,'fig08_rgdr_gate_retention','RGDR gates retain little training directional mass','final_blr_results/final_research_v2r/rgdr/gate_diagnostics/gate_diagnostics_v2r.csv','Training diagnostic only; continuous gate 74.75% zero-penalty hours; no predictive model training.')
# 9 Captum completeness flags
p=Path('final_blr_results/city_scale/explainability/convergence_diagnostics.csv');d=pd.read_csv(p);d.to_csv(src/'captum_convergence_diagnostics.csv',index=False)
fig,ax=plt.subplots(figsize=(7,4));d['abs_delta']=d.completeness_delta_ug_m3.abs();d.boxplot(column='abs_delta',by='model',ax=ax,grid=False);ax.set_title('');fig.suptitle('');ax.set(xlabel='Model family',ylabel='Absolute completeness delta (µg/m³)');ax.grid(axis='y',alpha=.25)
save(fig,'fig09_captum_diagnostics','Captum Integrated Gradients completeness diagnostics','final_blr_results/city_scale/explainability/convergence_diagnostics.csv','228 attribution records; 85 flagged; only v2m MLP/TCN; corrected ST-PIGNN checkpoint unavailable.')
with (P/'figures/figure_manifest.csv').open('w') as f:
 f.write('figure_id,title,export_files,source_artifact,source_data,limitations,regeneration_command\n')
 for r in manifest:f.write(','.join('"'+str(x).replace('"','""')+'"' for x in r)+'\n')
print('figures',len(manifest))
