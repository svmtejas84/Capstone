# Final publication asset handoff

10 figure variants (eight requested groups), 10 table files (eight requested groups), 17 distinct directly plotted source artifacts.

## Recommended main-paper order

F01 architecture; F02 graphs/stations; F03 multi-horizon benchmark; F04 physics ablation; F05 spatial holdouts. F06a/b, F07, and F08 are valuable supplementary or carefully captioned main-paper evidence if space permits.

## Inventory and use

- **F01_corrected_architecture**: `figures/F01_architecture/F01_corrected_architecture.pdf`; PNG/SVG and caption adjacent. Source: `final_blr_results/final_research_v2r/FINAL_RESEARCH_HANDOFF.md`.
- **F02_bengaluru_graph**: `figures/F02_graph_partitions/F02_bengaluru_graph.pdf`; PNG/SVG and caption adjacent. Source: `data/graphs/bangalore_utm_nodes.parquet`, `data/graphs/bangalore_utm_edges.parquet`, `data/processed/graph/partitioned_manifold_64_clusters.pt`, `results/stations_v2.csv`.
- **F03_multi_horizon_mae**: `figures/F03_forecasting_benchmarks/F03_multi_horizon_mae.pdf`; PNG/SVG and caption adjacent. Source: `final_blr_results/ieee_paper_evidence/results/RECOMPUTED_V2J_BENCHMARK.csv`, `final_blr_results/baselines/v2m/comparisons/ensemble_metrics.csv`.
- **F04_directional_ablation**: `figures/F04_physics_ablations/F04_directional_ablation.pdf`; PNG/SVG and caption adjacent. Source: `final_blr_results/physics_audit/ensemble_analysis/ensemble_decomposition.csv`, `final_blr_results/physics_audit/seed_analysis/per_seed_physics_comparisons.csv`.
- **F05_spatial_holdouts**: `figures/F05_spatial_validation/F05_spatial_holdouts.pdf`; PNG/SVG and caption adjacent. Source: `results/loso_per_station_v2j.csv`, `final_blr_results/final_research_v2r/citywide/spatial_decoder/pooled_test_metrics.csv`.
- **F06a_v2c_h1**: `figures/F06_captum_explainability/F06a_v2c_h1.pdf`; PNG/SVG and caption adjacent. Source: `final_blr_results/final_three_pillars/captum/attribution_tensors.npz`.
- **F06b_v2r_h6**: `figures/F06_captum_explainability/F06b_v2r_h6.pdf`; PNG/SVG and caption adjacent. Source: `final_blr_results/final_three_pillars/captum/v2r_heldout_h6/attribution_tensors.npz`.
- **F07_citywide_snapshot**: `figures/F07_citywide_estimation/F07_citywide_snapshot.pdf`; PNG/SVG and caption adjacent. Source: `final_blr_results/final_research_v2r/citywide/road_predictions/road_predictions_20251008T0700Z.parquet`, `results/stations_v2.csv`.
- **F08_routing_tradeoff**: `figures/F08_routing_evaluation/F08_routing_tradeoff.pdf`; PNG/SVG and caption adjacent. Source: `final_blr_results/final_routing_closure/v2t/ROUTING_COMPARISON_RESULTS.csv`, `final_blr_results/final_routing_closure/v2t/PAIRED_COMPARISONS.csv`.
- **F08b_routing_sensitivity**: `figures/F08_routing_evaluation/F08b_routing_sensitivity.pdf`; PNG/SVG and caption adjacent. Source: `final_blr_results/final_routing_closure/v2t/SENSITIVITY_STABILITY.csv`.

Tables: `T01`, `T02a`, `T02b`, `T03`, `T04a`, `T04b`, `T05`, `T06`, `T07`, `T08`. `T02a/b` and `T04a/b` intentionally separate incompatible protocols. CSV and TeX are paired in `tables/`.

## Regeneration and integration

From repository root:

```sh
python final_blr_results/ieee_publication_assets/scripts/build_assets.py
python final_blr_results/ieee_publication_assets/scripts/build_tables.py
python final_blr_results/ieee_publication_assets/scripts/verify_package.py
```

Select the desired `\input` lines from `latex/figures.tex` and `latex/tables.tex` in the manuscript source. Paths are relative to `latex/`; copy assets or adjust paths if the manuscript lives elsewhere. IEEEtran compilation was unavailable here.

## Scientific boundaries

No new training or experiment occurred. F06 uses v2c h1 and v2r h6 corrected variants, not missing v2j benchmark checkpoints. F07 road values are not roadside observations and decoder LOSO was unfavorable. F08 shows tiny modeled-dose differences and low utilization, not real-world exposure reduction. Directional physics remains a regularization heuristic. Missing original manuscript/reviewer texts still require transfer for the broader paper evidence package.

Verification: `verification/PUBLICATION_ASSET_VERIFICATION.md`. Source fingerprints: `verification/SOURCE_HASHES.csv`.
