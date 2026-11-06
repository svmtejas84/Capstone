from pathlib import Path
import pandas as pd,numpy as np,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
P=Path('final_blr_results/ieee_paper_evidence');out=P/'figures/export';src=P/'figures/source_data';man=pd.read_csv(P/'figures/figure_manifest.csv')
plt.rcParams.update({'font.size':10,'figure.dpi':140,'savefig.dpi':300,'font.family':'DejaVu Sans'})
def add(fid,title,source,limitations,plot):
 fig,ax=plt.subplots(figsize=(7,4.5));plot(fig,ax);fig.suptitle(title,fontsize=12,y=.98);fig.tight_layout(rect=[0,0,1,.93]);fig.savefig(out/f'{fid}.png',bbox_inches='tight');fig.savefig(out/f'{fid}.pdf',bbox_inches='tight');plt.close(fig)
 global man
 man.loc[len(man)]=[fid,title,f'export/{fid}.png; export/{fid}.pdf',source,'figures/source_data/'+Path(source).name,limitations,'python final_blr_results/ieee_paper_evidence/reproducibility/add_figures.py']
# physics vs laplacian
ph=pd.DataFrame({'horizon_hours':[1,3,6,12,24],'physics_minus_lambda0_mae':[ -.026,-.130,-.410,-.262,.145],'physics_minus_laplacian_mae':[-.073,.178,-.130,.003,-.103],'n_pairs':[14583]*5,'n_sites':[11]*5})
ph.to_csv(src/'v2l_physics_controls.csv',index=False)
def f(fig,ax):
 x=np.arange(len(ph));w=.36;ax.axhline(0,color='black',lw=.8);ax.bar(x-w/2,ph.physics_minus_lambda0_mae,w,label='Physics − λ=0');ax.bar(x+w/2,ph.physics_minus_laplacian_mae,w,label='Physics − Laplacian');ax.set_xticks(x,ph.horizon_hours);ax.set(xlabel='Forecast horizon (hours)',ylabel='ΔMAE (µg/m³)');ax.legend(frameon=False);ax.grid(axis='y',alpha=.25)
add('fig10_physics_vs_laplacian','Directional physics and generic Laplacian effects vary by horizon','final_blr_results/physics_audit/FINAL_PHYSICS_VERDICT.md','Exploratory; report-level paired effects, 11 sites; no physical specificity or conservation inference.',f)
# coverage
site=pd.read_csv('final_blr_results/final_research_v2r/citywide/spatial_decoder/per_station_test_metrics.csv');cov=site[['station_id','n_observations']].copy();cov.to_csv(src/'v2r_station_coverage.csv',index=False)
def f(fig,ax):
 ax.bar(cov.station_id.astype(str),cov.n_observations,color='#4c72b0');ax.set(xlabel='Scored held-out station ID',ylabel='Observed test pairs');ax.tick_params(axis='x',rotation=45);ax.grid(axis='y',alpha=.25)
add('fig11_spatial_site_coverage','Held-out evaluation coverage varies substantially by station','final_blr_results/final_research_v2r/citywide/spatial_decoder/per_station_test_metrics.csv','Eleven scored sites; four eligible stations had zero test targets and remain unscored; repeated times are not independent sites.',f)
# citywide runtime snapshots (full rows only)
bench=pd.read_csv('final_blr_results/final_research_v2r/citywide/road_predictions/citywide_benchmarks.csv');full=bench[bench.nodes==154902].copy();full.to_csv(src/'v2r_citywide_full_benchmarks.csv',index=False)
def f(fig,ax):
 xx=np.arange(len(full));ax.bar(xx,full.wall_seconds,color='#55a868');ax.set_xticks(xx,[str(x)[:10] for x in full.origin_utc],rotation=20);ax.set(xlabel='Frozen forecast target date (UTC)',ylabel='Full-city wall time (seconds)');ax.grid(axis='y',alpha=.25)
add('fig12_citywide_runtime_support','Full-city execution benchmarks for three h6 estimates','final_blr_results/final_research_v2r/citywide/road_predictions/citywide_benchmarks.csv','Computational execution only; three snapshots; expansion runtime does not validate concentrations; 19.45% nodes >5km and 60.58% outside monitor hull.',f)
man.to_csv(P/'figures/figure_manifest.csv',index=False)
print(len(man))
