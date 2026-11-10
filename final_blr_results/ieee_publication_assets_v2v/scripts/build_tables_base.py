"""Create traceable IEEE table source CSV and LaTeX from saved research artifacts."""
from pathlib import Path
import json
import pandas as pd
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'final_blr_results/ieee_publication_assets'
TAB=OUT/'tables'; TAB.mkdir(parents=True,exist_ok=True)
LAT=OUT/'latex'; LAT.mkdir(parents=True,exist_ok=True)
registered=[]

def src(p): return pd.read_csv(ROOT/p)
def tex_escape(x):
    s=str(x)
    return s.replace('_',r'\_').replace('%',r'\%').replace('&',r'\&').replace('µ',r'$\mu$').replace('²',r'$^2$').replace('λ',r'$\lambda$')
def fmt(v):
    if pd.isna(v):return '--'
    if isinstance(v,(float,np.floating)): return f'{v:.3f}'
    return tex_escape(v)
def emit(tid,title,frame,source,note,label=None):
    frame.to_csv(TAB/f'{tid}.csv',index=False)
    label=label or f'tab:{tid.lower()}'
    cols='l'+'r'*(len(frame.columns)-1)
    lines=[r'\begin{table*}[t]',r'\centering',r'\footnotesize',r'\caption{'+tex_escape(title)+r'. '+tex_escape(note)+r'}',r'\label{'+label+r'}',r'\begin{tabular}{'+cols+'}',r'\hline',
           ' & '.join(tex_escape(c) for c in frame.columns)+r' \\',r'\hline']
    lines += [' & '.join(fmt(v) for v in row)+r' \\' for row in frame.itertuples(index=False,name=None)]
    lines += [r'\hline',r'\end{tabular}',r'\end{table*}']
    (TAB/f'{tid}.tex').write_text('\n'.join(lines)+'\n')
    registered.append(dict(id=tid,title=title,rows=len(frame),source=source,note=note,tex=f'../tables/{tid}.tex',csv=f'../tables/{tid}.csv'))

# T01: all values are descriptive metadata; no unsupported time-coverage assertion.
emit('T01','Dataset and graph summary',pd.DataFrame([
    ['Raw hourly coverage','2022-01-01 to 2026-03-28','date range','data genealogy, Vol. 03'],
    ['Raw hourly rows',37152,'hours','data genealogy, Vol. 03'],
    ['Forecasting sites',15,'stations','stations_v2.csv'],
    ['Station kNN arcs',60,'directed arcs','v2j corrected protocol'],
    ['Input window',12,'hours','v2j corrected protocol'],
    ['Input channels',18,'channels','v2j corrected protocol'],
    ['Forecast horizons','1, 3, 6, 12, 24','hours','v2j corrected protocol'],
    ['Road nodes',154902,'nodes','bangalore_utm_nodes.parquet'],
    ['Raw road edges',393089,'directed rows','bangalore_utm_edges.parquet'],
    ['Processed message arcs',424550,'arcs','topology_graph_pyg_inference.pt'],
    ['Historical partitions',64,'partitions','partitioned_manifold_64_clusters.pt'],
    ['Historical omitted boundary arcs',7134,'arcs','v2k graph integrity audit']],
    columns=['Property','Value','Unit','Provenance']),
    'Canonical graph and corrected station model artifacts; data genealogy Volume 03','Road graph is separate from the 15-station forecasting graph; CRS EPSG:32643. Raw full-period coverage is not the corrected evaluation period.')

a=src('final_blr_results/ieee_paper_evidence/results/RECOMPUTED_V2J_BENCHMARK.csv')
b=src('final_blr_results/baselines/v2m/comparisons/ensemble_metrics.csv')
sel=['persistence','same_hour_yesterday','ridge_lag_calendar_weather','climatology_hod_dow','station_train_mean','vanilla_gcn','gru_only','st_gru_gcn','stpignn_original']
v=a[a.model.isin(sel)][['model','horizon_hours','n_pairs','mae_ug_m3','rmse_ug_m3','r2']].rename(columns={'mae_ug_m3':'MAE','rmse_ug_m3':'RMSE','r2':'R2','n_pairs':'Pairs','horizon_hours':'h (h)','model':'Model'}).sort_values(['Model','h (h)'])
emit('T02a','Corrected forecasting benchmark: v2j',v,'RECOMPUTED_V2J_BENCHMARK.csv','Five-seed ensemble where available; MAE/RMSE in micrograms per cubic metre. Historical v2j weather information protocol; 14,583 paired test observations per horizon.')
v=b[b.model.isin(['mlp','tcn'])][['model','horizon_hours','n_pairs','mae','rmse','r2']].rename(columns={'model':'Model','horizon_hours':'h (h)','n_pairs':'Pairs','mae':'MAE','rmse':'RMSE','r2':'R2'}).sort_values(['Model','h (h)'])
emit('T02b','Cutoff-safe MLP and TCN benchmark: v2m',v,'v2m/comparisons/ensemble_metrics.csv','Five-seed mean-prediction ensembles. v2m weather aggregation differs from historical v2j ST-PIGNN; not identical-input ablations.')

e=src('final_blr_results/physics_audit/ensemble_analysis/ensemble_decomposition.csv')
p=e.pivot(index='horizon_hours',columns='model',values='ensemble_mae')
bl=src('final_blr_results/physics_audit/statistical_robustness/block_bootstrap_sensitivity.csv').set_index('horizon_hours')
mu=src('final_blr_results/physics_audit/statistical_robustness/multiplicity_analysis.csv').set_index('horizon_hours')
t=pd.DataFrame({'h (h)':p.index,'λ=0 MAE':p.stpignn_lambda0.values,'Directional MAE':p.stpignn_original.values,
    'Laplacian MAE':p.stpignn_laplacian.values,'Δdir−λ0':(p.stpignn_original-p.stpignn_lambda0).values,
    'Δdir−Lap':(p.stpignn_original-p.stpignn_laplacian).values,
    '7-day CI low':bl.loc[p.index,'seven_day_ci_low'].values,'7-day CI high':bl.loc[p.index,'seven_day_ci_high'].values,
    'Holm p (35)':mu.loc[p.index,'original_35_holm_p'].values})
emit('T03','Directional physics ablation',t,'v2l ensemble_decomposition.csv; block_bootstrap_sensitivity.csv; multiplicity_analysis.csv',
    'Five-seed ensembles, 14,583 pairs/horizon. Negative ΔMAE favors directional. Seven-day intervals and Holm p refer to directional versus λ=0; Laplacian comparison is descriptive here. Hinge is not mass conservation.')

w=src('results/loso_per_station_v2j.csv')
w=w[w.seasonal_bias_corrected.eq(False)]
wp=w[((w.method=='stpignn_original')&(w.anchor=='train_mean'))|((w.method=='ridge_weather_static')&(w.anchor=='baseline'))]
pv=wp.pivot(index='station_id',columns='method',values='mae').dropna()
n=wp[wp.method=='stpignn_original'].set_index('station_id').loc[pv.index,'n']
t=pd.DataFrame({'Site':pv.index,'Pairs':n.values,'ST-PIGNN MAE':pv.stpignn_original.values,'Ridge MAE':pv.ridge_weather_static.values})
emit('T04a','W6 genuine held-out station results',t,'results/loso_per_station_v2j.csv','Eleven scored sites; four sites had no test targets. MAE in micrograms per cubic metre. Pooled MAE 22.314 ST-PIGNN versus 20.624 weather/static ridge; station timestamps are dependent.')
v=src('final_blr_results/final_research_v2r/citywide/spatial_decoder/pooled_test_metrics.csv')
t=v[['method','n','mae','rmse','r2','scored_stations','decoder_parameter_count']].rename(columns={'method':'Method','n':'Pairs','mae':'MAE','rmse':'RMSE','r2':'R2','scored_stations':'Sites','decoder_parameter_count':'Params'})
emit('T04b','v2r spatial decoder held-out forecast comparison',t,'v2r/citywide/spatial_decoder/pooled_test_metrics.csv','Separate positive-lead-time task. Decoder underperforms forecast-IDW and station mean; not pooled with W6.')

t=pd.DataFrame([{'Method':'ST-PIGNN station forecaster + decoder','Road nodes':154902,'Snapshots':3,'Estimates':464706,
    'Full run (s)':56.44,'Peak RAM (GB)':1.49,'Expansion GPU VRAM (GB)':0,'Support >5 km (%)':19.45,'Outside hull (%)':60.58}])
emit('T05','Experimental citywide computational execution',t,'v2r FINAL_RESEARCH_HANDOFF.md; road_predictions/*.parquet','Six-hour targets; full runtime includes decoder fitting and maps. Per-snapshot expansion 1.12–1.30 s. Values are experimental neural-assisted estimates, not validated roadside predictions.')

ig=[]
for name,path in [('v2c h=1','final_blr_results/final_three_pillars/captum/IG_RESULTS.csv'),('v2r h=6 outer-LOSO','final_blr_results/final_three_pillars/captum/v2r_heldout_h6/IG_RESULTS.csv')]:
    d=src(path)
    if name=='v2c h=1': d=d[d.analysis_version=='v2c_h1']
    ig.append({'Variant':name,'Checkpoints':d.checkpoint_sha256.nunique(),'Primary records':int(d.baseline.eq('training_mean').sum()),
        'All records':len(d),'Baseline':'training mean + sensitivity','IG steps':64,
        'Max |delta|':abs(d.completeness_delta_ug_m3).max(),'Max wrapper error':d.wrapper_abs_error_ug_m3.max(),
        'Nonfinite':d.nonfinite_count.sum()})
emit('T06','Corrected ST-PIGNN Captum verification',pd.DataFrame(ig),'final_three_pillars/captum/IG_RESULTS.csv; v2r_heldout_h6/IG_RESULTS.csv','Units for delta and wrapper error are micrograms per cubic metre. v2c and v2r are different model protocols; neither is the missing v2j benchmark checkpoint.')

r=src('final_blr_results/final_routing_closure/v2t/ROUTING_COMPARISON_RESULTS.csv')
pr=src('final_blr_results/final_routing_closure/v2t/PAIRED_COMPARISONS.csv')
o=r[r.scenario=='original'].groupby('method').agg(requests=('requests','sum'),assigned=('assigned','sum'),violations=('edge_violations','sum'),
    max_utilization=('max_utilization','max'),runtime_s=('runtime_s','sum')).reset_index()
p=pr[(pr.scenario=='original')&(pr.candidate=='corrected_da')&(pr.control=='shortest')]
o['matched_dose_pct_vs_shortest']=np.where(o.method=='corrected_da',p.dose_delta_pct.mean(),np.nan)
o['matched_time_pct_vs_shortest']=np.where(o.method=='corrected_da',p.time_overhead_pct.mean(),np.nan)
emit('T07','Frozen original-field routing benchmark',o,'v2t ROUTING_COMPARISON_RESULTS.csv; PAIRED_COMPARISONS.csv',
    'Nine demand batches, 252 submitted requests/method. Matched percentages refer to corrected versus shortest on common admitted requests. Max utilization is a fraction. Modelled dose is not measured exposure.')

claims=pd.DataFrame([
    ['Station multi-horizon forecasting','MIXED','v2j benchmark; v2m baselines','Strong simple controls and weather protocol differences'],
    ['Directional penalty physical specificity','UNSUPPORTED','v2l physics audit','No consistent superiority to Laplacian; no conservation'],
    ['Held-out station transfer superiority','UNSUPPORTED','W6 LOSO; v2r decoder','Ridge and forecast-IDW outperform'],
    ['Full-city computational execution','SUPPORTED','v2r road predictions','154,902 nodes × 3; experimental estimates'],
    ['Independent roadside accuracy','NOT EVALUATED','No roadside ground truth','Cannot validate road concentrations'],
    ['Captum numerical attribution','SUPPORTED','v2c/v2r IG results','Baseline-relative; limited checkpoint variants'],
    ['Routing edge-capacity feasibility','SUPPORTED','v2t toy tests and benchmark','No classical stability or welfare theorem'],
    ['Real-world exposure reduction','NOT EVALUATED','v2t scenario benchmark','Modeled differences near zero'],
    ['RGDR predictive superiority','NOT EVALUATED','v2r gate diagnostics','No comparative training results'] ],
    columns=['Claim','Status','Evidence','Limit'])
emit('T08','Claim-to-evidence summary',claims,'v2l, W6, v2r, Captum, v2t verdicts','Classifications are bounded to completed Bengaluru evidence; no independent external replication.')

(LAT/'tables.tex').write_text('% v2u IEEE tables; paths relative to ieee_publication_assets/latex\n'+''.join(f'\\input{{{r["tex"]}}}\n' for r in registered))
pd.DataFrame(registered).to_csv(TAB/'table_manifest.csv',index=False)
print('Generated',len(registered),'tables')
