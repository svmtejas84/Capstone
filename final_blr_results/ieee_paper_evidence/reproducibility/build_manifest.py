from pathlib import Path
import hashlib,csv,json,datetime
root=Path('final_blr_results/ieee_paper_evidence')
checks=[]
for p in sorted(root.rglob('*')):
 if p.is_file() and p.name not in {'CHECKSUMS.csv','ARTIFACT_MANIFEST.json'}:
  h=hashlib.sha256(p.read_bytes()).hexdigest(); checks.append((p.relative_to(root).as_posix(),h,p.stat().st_size))
with (root/'reproducibility/CHECKSUMS.csv').open('w',newline='') as f:
 w=csv.writer(f,lineterminator='\n');w.writerow(['relative_path','sha256','bytes']);w.writerows(checks)
manifest={
 'package':'IEEE paper evidence and second-city handover (evidence only)',
 'created_utc':'2026-11-06',
 'repository':'/home/jupyter-1nt23cb058/Capstone',
 'source_commit_at_package_start':'a5b396da3f41c2d626ba072e8cec1a0ee15d383d',
 'branch_at_package_start':'research/bengaluru-v2r-final',
 'training_performed':False,
 'historical_test_recomputed_from_raw_pairs':False,
 'file_hashes_exclude':['reproducibility/ARTIFACT_MANIFEST.json','reproducibility/CHECKSUMS.csv'],
 'limitations':['Original IEEE manuscript PDF not found','Four BigData and two DELCON review source texts not found','v2m predictions stored in preserved ZIP archive; not duplicated in this evidence export','Corrected ST-PIGNN Captum checkpoints unavailable'],
 'important_external_sources':[
  {'path':'notebooks/production/evaluated_wind_advection.ipynb','status':'present; historical notebook; hash below'},
  {'path':'final_blr_results/baselines/v2m/comparisons/ensemble_metrics.csv','status':'saved summary table; hash below'},
  {'path':'final_blr_results/physics_audit/seed_analysis/per_seed_physics_comparisons.csv','status':'saved per-seed table; hash below'},
  {'path':'final_blr_results/final_research_v2r/citywide/spatial_decoder/per_station_test_metrics.csv','status':'saved LOSO metrics; hash below'},
  {'path':'final_blr_results/city_scale/explainability/convergence_diagnostics.csv','status':'saved Captum diagnostics; hash below'}]}
for item in manifest['important_external_sources']:
 p=Path(item['path'])
 if p.exists(): item['sha256']=hashlib.sha256(p.read_bytes()).hexdigest();item['bytes']=p.stat().st_size
 else:item['sha256']=None;item['bytes']=None
manifest['data_and_graph_hashes']=[]
for rel in ['notebooks/production/evaluated_wind_advection.ipynb','data/processed/graph/topology_graph.pt','data/processed/graph/topology_graph_pyg_inference.pt','data/processed/graph/partitioned_manifold_64_clusters.pt','data/processed/graph/topology_nodeid_to_index_map.parquet','data/processed/graph/station_to_topology_node_map.parquet','data/processed/graph/nodes_elevation_true.parquet','data/processed/graph/master_scaled_checkpoint.parquet','data/processed/graph/global_scaler.pkl','final_blr_results/baselines/v2m/reproducibility/research_results_v2m.zip','final_blr_results/research_backup_exports/research_backup_pretrain_v2m.zip','results/benchmark_v2j.csv','results/stations_v2.csv','final_blr_results/FINAL_HANDOFF.md','final_blr_results/physics_audit/FINAL_PHYSICS_VERDICT.md','final_blr_results/baselines/v2m/FINAL_BASELINE_VERDICT.md','final_blr_results/city_scale/final_evidence/FINAL_BENGALURU_RESEARCH_VERDICT.md','final_blr_results/citywide_extension/v2o/SPATIAL_VALIDATION_VERDICT.md','final_blr_results/citywide_extension/v2p_rgdr/RGDR_FINAL_HANDOFF.md','final_blr_results/citywide_extension/v2q/FINAL_V2Q_HANDOFF.md','final_blr_results/final_research_v2r/FINAL_RESEARCH_HANDOFF.md','data/processed/evaluations/routing_results.json','data/processed/evaluations/routing_trip_results.csv']:
 p=Path(rel)
 if p.exists(): manifest['data_and_graph_hashes'].append({'path':rel,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size})
(root/'reproducibility/ARTIFACT_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(f'hashed {len(checks)} package files')
