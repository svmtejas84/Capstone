from pathlib import Path
import pandas as pd
p=Path('final_blr_results/ieee_paper_evidence/figures/figure_manifest.csv');d=pd.read_csv(p);d=d.loc[:,~d.columns.duplicated()];d=d.drop(columns=['sample_count.1'],errors='ignore')
samples={
'fig01_forecasting_mae':'14,583 matched pairs per horizon; 5 horizons; 11 scored stations',
'fig02_statistical_baselines':'14,583 matched pairs per horizon; 5 horizons; 11 scored stations',
'fig03_physics_vs_lambda0':'14,583 pairs per horizon; 11 sites; 5 horizons',
'fig04_physics_seed_stability':'14,583 pairs × 5 seeds per horizon; 11 sites',
'fig05_spatial_holdout':'14,583 matched pairs; 11 scored stations; 3 methods',
'fig06_spatial_per_station':'11 scored station sites; 14,583 total pairs',
'fig07_citywide_support':'154,902 road-node estimates; one of three frozen snapshots',
'fig08_rgdr_gate_retention':'14,206 training cutoffs; h=6 feasibility diagnostic',
'fig09_captum_diagnostics':'228 attribution records from 18 checkpoint cells',
'fig10_physics_vs_laplacian':'14,583 pairs per horizon; 11 sites; 5 horizons',
'fig11_spatial_site_coverage':'11 scored sites; 4 additional eligible sites unscored',
'fig12_citywide_runtime_support':'3 frozen h=6 target snapshots; 154,902 nodes each',
'fig13_road_graph_station_locations':'154,902 road nodes; 15 station locations',
'fig14_v2j_benchmark':'14,583 station-time pairs per horizon; 11 scored sites; 5 seeds for neural models'}
d['sample_count']=d.figure_id.map(samples).fillna('See source and protocol-specific count in limitations')
# Keep canonical figure manifest field order
cols=['figure_id','title','sample_count','source_artifact','source_data','limitations','regeneration_command','export_files'];d=d[cols]
d.to_csv(p,index=False)
print('annotated',len(d),'figures')
