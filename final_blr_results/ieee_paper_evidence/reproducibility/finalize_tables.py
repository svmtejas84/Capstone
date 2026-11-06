from pathlib import Path
import pandas as pd,csv,json
P=Path('final_blr_results/ieee_paper_evidence');R=P/'results';T=P/'tables';E=T/'export'
# Regenerate routing summary from the saved run artifact.
route=json.loads(Path('data/processed/evaluations/routing_results.json').read_text())
with (R/'ROUTING_RESULTS.csv').open('w',newline='') as f:
 w=csv.writer(f,lineterminator='\n');w.writerow(['requested_trips','admitted_trips','unmatched_trips','comparison_population','astar_mean_dose_ug','gs_mean_dose_ug','dose_reduction_pct','astar_mean_time_min','gs_mean_time_min','time_tradeoff_pct','seed','quota_min','quota_median','quota_max','edge_pm25_min_ug_m3','edge_pm25_median_ug_m3','edge_pm25_max_ug_m3','source']);w.writerow([route[k] for k in ['requested_trips','admitted_trips','unmatched_trips','comparison_population','astar_mean_dose_ug','gs_mean_dose_ug','dose_reduction_pct','astar_mean_time_min','gs_mean_time_min','time_tradeoff_pct','seed','quota_min','quota_median','quota_max','edge_pm25_min','edge_pm25_median','edge_pm25_max']]+['data/processed/evaluations/routing_results.json'])
# Result tables: preserve standard result files and append all reproducible metric checks.
for f in sorted(R.glob('*.csv')):
 pd.read_csv(f).to_csv(E/f.name,index=False)
pd.read_csv(P/'claims/CLAIM_CLASSIFICATIONS.csv').to_csv(E/'CLAIM_CLASSIFICATIONS.csv',index=False)
# Native manuscript-facing tables and source inventories.
for src,dest in [('final_blr_results/baselines/v2m/comparisons/ensemble_metrics.csv','table_v2m_ensemble.csv'),('final_blr_results/physics_audit/seed_analysis/per_seed_physics_comparisons.csv','table_v2l_seed_effects.csv'),('final_blr_results/final_research_v2r/citywide/spatial_decoder/per_station_test_metrics.csv','table_v2r_site_metrics.csv')]:pd.read_csv(src).to_csv(E/dest,index=False)
rows=[
('T1','export/MASTER_RESULTS.csv','Master cross-workstream outcomes','results/MASTER_RESULTS.csv','Exploratory; source and verification status included'),
('T2','export/FORECASTING_COMPARISONS.csv','v2j/v2m horizon metrics and frozen contrasts','results/FORECASTING_COMPARISONS.csv','Protocol labels retained; no cross-protocol ablation claim'),
('T3','export/PHYSICS_ABLATIONS.csv','Per-seed physics and control comparisons','results/PHYSICS_ABLATIONS.csv','Exploratory exposed test; frozen families'),
('T4','export/SPATIAL_GENERALIZATION.csv','Pooled and per-site LOSO/interpolation comparisons','results/SPATIAL_GENERALIZATION.csv','Retrospective and forecast tasks separated'),
('T5','export/CITYWIDE_RESULTS.csv','City execution, runtime, support and validation evidence','results/CITYWIDE_RESULTS.csv','Computational execution is not accuracy'),
('T6','export/EXPLAINABILITY_RESULTS.csv','Captum convergence diagnostics','results/EXPLAINABILITY_RESULTS.csv','v2m MLP/TCN only; ST-PIGNN unavailable'),
('T7','export/ROUTING_RESULTS.csv','Saved routing simulator outcome','results/ROUTING_RESULTS.csv','Admitted-only comparison; static unvalidated field'),
('T8','export/CLAIM_CLASSIFICATIONS.csv','Claim-by-claim evidence classification','claims/CLAIM_CLASSIFICATIONS.csv','All claim categories independent'),
('T9','export/RECOMPUTED_V2J_BENCHMARK.csv','Recomputed five-horizon v2j model and baseline metrics','results/RECOMPUTED_V2J_BENCHMARK.csv','85 rows from archived predictions; tested against saved MAE/R2'),
('T10','export/RECOMPUTED_V2M_INDIVIDUAL_METRICS.csv','Recomputed individual seed metrics','results/RECOMPUTED_V2M_INDIVIDUAL_METRICS.csv','50 model/seed/horizon cells'),
('T11','export/RECOMPUTED_V2M_ENSEMBLE_METRICS.csv','Recomputed five-seed ensemble metrics','results/RECOMPUTED_V2M_ENSEMBLE_METRICS.csv','10 model/horizon rows'),
('T12','export/RECOMPUTED_V2M_PRIMARY_DELTAS.csv','Recomputed frozen paired MAE deltas','results/RECOMPUTED_V2M_PRIMARY_DELTAS.csv','10 predeclared contrasts; reported intervals/p-values retained from source'),
('T13','export/RECOMPUTED_V2M_SUMMARY_COMPARISON.csv','Metric-by-metric archived summary verification','results/RECOMPUTED_V2M_SUMMARY_COMPARISON.csv','5e-6 tolerance; pair counts exact'),
('T14','export/RECOMPUTED_V2M_PRIMARY_COMPARISON.csv','Frozen delta summary cross-check','results/RECOMPUTED_V2M_PRIMARY_COMPARISON.csv','14,583 pairs per contrast'),
('T15','export/RECOMPUTED_V2R_SPATIAL_METRICS.csv','Recomputed v2r pooled and per-site metrics','results/RECOMPUTED_V2R_SPATIAL_METRICS.csv','14,583 targets across 11 sites'),
('T16','export/RECOMPUTED_V2R_SUMMARY_COMPARISON.csv','v2r pooled summary cross-check','results/RECOMPUTED_V2R_SUMMARY_COMPARISON.csv','Three controls match saved summary'),
('T17','export/table_v2m_ensemble.csv','Native ensemble metrics source table','final_blr_results/baselines/v2m/comparisons/ensemble_metrics.csv','Protocol labels retained'),
('T18','export/table_v2l_seed_effects.csv','Native v2l seed metrics source table','final_blr_results/physics_audit/seed_analysis/per_seed_physics_comparisons.csv','Five seeds'),
('T19','export/table_v2r_site_metrics.csv','Native v2r site metrics source table','final_blr_results/final_research_v2r/citywide/spatial_decoder/per_station_test_metrics.csv','Eleven scored sites; four unscored'),
('T20','figures/figure_manifest.csv','Figure sources, sample counts and limitations','figures/figure_manifest.csv','14 PNG/PDF figures'),
('T21','source_registry/EXPERIMENT_SOURCE_REGISTER.csv','Experiment provenance register','source_registry/EXPERIMENT_SOURCE_REGISTER.csv','20 records; unverifiable metadata explicitly marked')]
pd.DataFrame(rows,columns=['table_id','file','content','source','limitations']).to_csv(T/'table_manifest.csv',index=False)
print('refreshed exports and 21-item table/source manifest')
