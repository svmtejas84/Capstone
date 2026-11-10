from pathlib import Path
import numpy as np, pandas as pd

ROOT=Path(__file__).resolve().parents[3]; OUT=ROOT/'final_blr_results/ieee_publication_assets_v2v'
TAB=OUT/'tables'; TAB.mkdir(exist_ok=True)
def texesc(x):
 s=str(x).replace('_',r'\_').replace('%',r'\%').replace('&',r'\&').replace('µ',r'$\mu$').replace('₂',r'$_2$').replace('λ',r'$\lambda$')
 return s
def make_tex(name,title,df,note):
 # A direct LaTeX table snippet is supplied for every CSV. Wide evidence tables are supplementary assets.
 cols='l'+'r'*(max(0,len(df.columns)-1)); lines=[r'\begin{table*}[t]',r'\centering',r'\scriptsize',r'\caption{'+texesc(title)+'. '+texesc(note)+r'}',r'\label{tab:'+name.lower()+r'}',r'\begin{tabular}{'+cols+'}',r'\hline',' & '.join(texesc(c) for c in df.columns)+r' \\',r'\hline']
 for row in df.itertuples(index=False,name=None):
  vals=[]
  for v in row:
   vals.append('--' if pd.isna(v) else (f'{v:.3f}' if isinstance(v,(float,np.floating)) else texesc(v)))
  lines.append(' & '.join(vals)+r' \\')
 lines += [r'\hline',r'\end{tabular}',r'\end{table*}']
 (TAB/f'{name}.tex').write_text('\n'.join(lines)+'\n')
def emit(name,title,df,note):
 df.to_csv(TAB/f'{name}.csv',index=False); make_tex(name,title,df,note)

# T01: provenance and graph records.
t01=pd.DataFrame([
 ['Air-quality observations','OpenAQ API records labelled with CPCB station names','hourly / irregular records','15 sites; 11 scored in test','PM2.5 target plus pollutant inputs','Station monitors; values cleaned 0–500 µg/m³'],
 ['Meteorology','Open-Meteo archive, one Bengaluru reference coordinate','hourly historical archive','citywide broadcast to stations','wind, gust, temperature, humidity, pressure, direction','v2j uses centered adjacent :30 mean; v2m uses cutoff-safe availability'],
 ['Road geometry','OpenStreetMap-derived stored graph','static nodes and edges','154,902 nodes','393,089 raw directed edge rows; 424,550 processed arcs','EPSG:32643; 64 historical partitions'],
 ['Terrain','SRTM sampled node elevation','static','15 stations / road nodes as applicable','metres','Verified SRTM; distinct from legacy synthetic northing proxy'],
 ['Forecast graph','Station coordinate kNN','static','15 station nodes','60 directed arcs; 4-nearest-neighbour construction','Separate from road graph'],
 ['Corrected v2j inputs','13 data channels + lag-missingness + four calendar channels','12-hour history','15 station nodes','18 channels','1,3,6,12,24-hour horizons; 14,583 observed test pairs/horizon']
],columns=['Component','Source','Resolution','Coverage','Dimensions / variables','Protocol notes'])
emit('T01_dataset_graph_summary','Dataset and graph summary',t01,'Source records and dataset versions are explicit; station and road graphs are distinct.')

# T02: full benchmark rows, split by protocol and preserve all archived v2j model variants.
a=pd.read_csv(ROOT/'final_blr_results/ieee_paper_evidence/results/RECOMPUTED_V2J_BENCHMARK.csv')
b=pd.read_csv(ROOT/'final_blr_results/baselines/v2m/comparisons/ensemble_metrics.csv')
v2j=a.assign(protocol='Retrospective centered-weather station evaluation',model_name=a.model.map({
 'adaptive_graph_st':'Adaptive graph ST','adaptive_graph_st_fixed_knn':'Adaptive graph ST, fixed kNN','climatology_hod_dow':'Hour/day climatology',
 'gine_gru_wind':'Wind-conditioned GINE–GRU','gru_only':'GRU-only','persistence':'Persistence','ridge_lag_calendar_weather':'Weather ridge',
 'same_hour_yesterday':'Same-hour-yesterday','st_gru_gcn':'ST GRU–GCN','station_train_mean':'Station training mean','stpignn_lambda0':'ST-PIGNN, λ=0',
 'stpignn_laplacian':'ST-PIGNN, Laplacian','stpignn_original':'ST-PIGNN, directional','stpignn_v2':'ST-PIGNN additional variant',
 'stpignn_v2_source_removed':'ST-PIGNN, source term removed','stpignn_v2_transport_removed':'ST-PIGNN, transport term removed','vanilla_gcn':'Vanilla GCN'}))
v2j=v2j.rename(columns={'horizon_hours':'horizon_h','n_pairs':'n_pairs','mae_ug_m3':'mae_ug_m3','rmse_ug_m3':'rmse_ug_m3','r2':'r2'})[['protocol','model_name','model','horizon_h','n_pairs','mae_ug_m3','rmse_ug_m3','r2','seeds_completed']]
v2m=b[b.model.isin(['mlp','tcn'])].copy().assign(protocol='Forecast-cutoff-safe MLP/TCN evaluation')
v2m['model_name']=v2m.model.str.upper();v2m=v2m.rename(columns={'horizon_hours':'horizon_h','mae':'mae_ug_m3','rmse':'rmse_ug_m3'})
for c in ['n_pairs','mae_ug_m3','rmse_ug_m3','r2']:
 if c not in v2m: v2m[c]=np.nan
v2m['seeds_completed']=5
v2m=v2m[['protocol','model_name','model','horizon_h','n_pairs','mae_ug_m3','rmse_ug_m3','r2','seeds_completed']]
t02=pd.concat([v2j,v2m],ignore_index=True).sort_values(['protocol','model_name','horizon_h'])
emit('T02_complete_forecasting_benchmark','Complete saved forecasting benchmark',t02,'v2j and v2m use different weather protocols; cross-protocol contrasts are descriptive, not identical-input ablations.')
# Publication-facing TeX uses descriptive names only; the paired CSV retains internal model IDs for provenance.
make_tex('T02_complete_forecasting_benchmark','Complete saved forecasting benchmark',t02.drop(columns=['model']),
         'Retrospective centered-weather and forecast-cutoff-safe protocols are separate; cross-protocol contrasts are not identical-input ablations. Internal model IDs remain in the companion CSV.')

# T03: paired physical ablations plus block-bootstrap directional-minus-Laplacian results.
e=pd.read_csv(ROOT/'final_blr_results/physics_audit/ensemble_analysis/ensemble_decomposition.csv')
p=e.pivot(index='horizon_hours',columns='model',values='ensemble_mae')
ci=pd.read_csv(OUT/'source_data/F04_directional_vs_laplacian_7day_CI.csv')
mu=pd.read_csv(ROOT/'final_blr_results/physics_audit/statistical_robustness/multiplicity_analysis.csv')
t03=pd.DataFrame({'horizon_h':p.index,'n_pairs':14583,'seeds':5,'mae_lambda0':p.stpignn_lambda0.values,
 'mae_directional':p.stpignn_original.values,'mae_laplacian':p.stpignn_laplacian.values,
 'directional_minus_lambda0':p.stpignn_original.values-p.stpignn_lambda0.values,
 'directional_minus_laplacian':ci.directional_minus_laplacian_mae.values,
 'directional_minus_laplacian_7d_ci_low':ci.seven_day_block_ci_low.values,
 'directional_minus_laplacian_7d_ci_high':ci.seven_day_block_ci_high.values,
 'directional_lambda0_holm35_p':mu.set_index('horizon_hours').loc[p.index,'original_35_holm_p'].values})
emit('T03_directional_regularization','Directional regularization and ablation analysis',t03,'Negative paired differences favor directional regularization. The directional loss is a heuristic and does not enforce mass conservation.')

# T04a station-isolated metrics (all relevant sites; anchor distinction in notes).
site=pd.read_csv(OUT/'source_data/F05_station_paired_errors.csv')
emit('T04a_station_isolated_sites','Station-isolated paired errors',site,'Each row is one held-out site. ST-PIGNN uses a train-mean residual anchor; ridge uses its baseline reconstruction. Same 14,583 target pairs, but not the same output-anchor mechanism; four stations unscored.')
sp=pd.read_csv(ROOT/'final_blr_results/final_research_v2r/citywide/spatial_decoder/pooled_test_metrics.csv')
emit('T04b_decoder_protocol','Separate forecast-origin-safe spatial-decoder evaluation',sp,'Different evaluation protocol from W6. Decoder pooled MAE 27.360 versus forecast-IDW 20.154; pooled difference +7.206 µg/m³, while equal-site difference is +5.101 (95% station-bootstrap CI [1.815, 8.301]).')

# T05 citywide execution evidence.
cb=pd.read_csv(ROOT/'final_blr_results/final_research_v2r/citywide/road_predictions/citywide_benchmarks.csv')
emit('T05_citywide_execution','Citywide experimental estimate execution',cb,'Three frozen six-hour snapshots × 154,902 road nodes. Station model operates on 15-site graph; separate decoder generates estimates. No roadside ground truth.')

# T06 attribution summary: preserve each variant's schema and checkpoint/record count.
ig=pd.read_csv(OUT/'source_data/F06_feature_attribution_summary.csv')
igout=ig.groupby('variant').agg(checkpoint_records=('checkpoint_records_total','first'),attribution_records=('attribution_records','first'),
 baseline=('baseline','first'),lags=('lags','first'),nodes=('nodes','first'),max_completeness_abs=('completeness_max_abs','first'),
 max_wrapper_error=('wrapper_max_abs_error','first')).reset_index()
emit('T06_captum_verification','Captum Integrated Gradients coverage and numerical diagnostics',igout,'The one-hour and six-hour variants have different input schemas, selection protocols, and output attribution scales; magnitudes should not be treated as directly comparable or causal.')
major=ig[ig.feature.isin(['pm25_lagged','temperature','surface_pressure','wind_speed','hour_sin','wind_direction_sin','wind_direction_cos'])]
major=major[['variant','feature','attribution_records','mean_abs_ig_sum_lag_node','mean_signed_ig_sum_lag_node']]
emit('T06b_major_feature_attributions','Selected signed and absolute feature attributions',major,'Mean absolute and signed IG are summed over all 12 lags and 15 station nodes per record, then averaged across primary training-mean-baseline records. Distinct model variants and schemas; not causal and not a controlled horizon comparison.')

# T07 routing from original concentration scenario, separate all-four-scenario capacity evidence.
r=pd.read_csv(ROOT/'final_blr_results/final_routing_closure/v2t/ROUTING_COMPARISON_RESULTS.csv')
orig=r[r.scenario.eq('original')].groupby('method').agg(requests=('requests','sum'),assigned=('assigned','sum'),unassigned=('unassigned','sum'),
 success_rate=('success_rate','mean'),mean_distance_m=('mean_distance_m','mean'),mean_time_min=('mean_time_min','mean'),mean_modeled_dose=('mean_dose_ug','mean'),
 capacity_violations=('edge_violations','sum'),max_utilization=('max_utilization','max'),runtime_s=('runtime_s','sum')).reset_index()
pr=pd.read_csv(ROOT/'final_blr_results/final_routing_closure/v2t/PAIRED_COMPARISONS.csv')
q=pr[(pr.scenario=='original')&(pr.candidate=='corrected_da')&(pr.control=='shortest')]
cor=orig.method.eq('corrected_da'); orig.loc[cor,'dose_diff_pct_vs_shortest']=q.dose_delta_pct.mean();orig.loc[cor,'time_diff_pct_vs_shortest']=q.time_overhead_pct.mean()
orig.to_csv(TAB/'T07_routing_feasibility.csv',index=False);make_tex('T07_routing_feasibility','Routing feasibility and modeled-dose scenario results',orig,'The original concentration scenario has 252 requests across nine batches. Dose/time differences are paired on common admitted trips. These are simulated estimates, not measured exposure reductions or stability guarantees.')

# T08 classifications are intentionally bounded and conservative.
t08=pd.DataFrame([
 ['Multi-horizon station forecasting','MIXED','Corrected station graph; observed station labels; saved multi-horizon predictions','Simple baselines remain strong; weather protocol differs across some model families'],
 ['Superiority over neural baselines','MIXED','17-variant retrospective station benchmark','Exploratory exposed test set; no blanket superiority'],
 ['Directional regularization benefit','MIXED','λ=0, directional, Laplacian comparisons','Horizon-dependent; 7-day paired intervals; no physical specificity'],
 ['Physical conservation','UNSUPPORTED','Directional hinge and finite-volume synthetic diagnostic','Historical loss is not a conservation balance; no empirical conservation validation'],
 ['Spatial generalization','UNSUPPORTED','W6 LOSO and v2r decoder holdouts','Pooled models lose to ridge/IDW; 11 scored sites; 4 unscored'],
 ['Road-node accuracy','NOT EVALUATED','154,902 generated estimates','No independent roadside concentration labels'],
 ['Captum attribution','SUPPORTED for baseline-relative computation','Two compatible ST-PIGNN variants; raw IG tensors','Limited variants, non-comparable magnitudes; attribution is not causal'],
 ['Routing capacity feasibility','SUPPORTED within declared scenarios','v2t focused and benchmark checks','Low-demand synthetic capacity scenarios; no real traffic validation'],
 ['Real-world exposure reduction','NOT EVALUATED','Modeled routing dose scenarios','Dose differences are tiny and concentration field unvalidated'],
 ['RGDR superiority / novelty','NOT ESTABLISHED','Binary/continuous gate diagnostics only','No comparative training results or comprehensive novelty establishment'],
 ['Independent external validation','NOT EVALUATED','No second-city study','Requires new eligible dataset and prospective protocol']
],columns=['Claim','Status','Evidence','Boundary'])
emit('T08_claim_evidence','Claim-to-evidence classifications',t08,'Implementation, numerical output, and empirical validation are separate claims; statuses apply only to the evidence listed.')

tabs=sorted(TAB.glob('T*.tex'))
(OUT/'latex').mkdir(exist_ok=True)
(OUT/'latex/tables.tex').write_text('% v2v corrected evidence tables; include from repository root.\n'+''.join(f'\\input{{final_blr_results/ieee_publication_assets_v2v/tables/{p.name}}}\n' for p in tabs))
pd.DataFrame([{'table':p.stem,'csv':str(p.with_suffix('.csv').relative_to(OUT)),'latex':str(p.relative_to(OUT))} for p in tabs]).to_csv(TAB/'table_manifest.csv',index=False)
print('built tables',len(tabs))
