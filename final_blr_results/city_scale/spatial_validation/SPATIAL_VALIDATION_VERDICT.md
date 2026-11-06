# Spatial generalization verdict

**UNSUPPORTED for ST-PIGNN superiority at unmonitored stations; road-node accuracy NOT EVALUATED.** This consolidates saved station-graph leave-one-station-out (LOSO) results. No v2n LOSO model was trained or scored. The corrected v2j W6 data builder excludes held-out station pollutant channels before imputation and fitting (`src/stpignn/data_v2.py`, `excluded_station_id` path), and test targets remain observed-only. The saved procedure uses fold-specific 14-station training with the held-out location represented by weather/static inputs and a train-only anchor; a compatible fold checkpoint was not archived, so forward-level leakage replay is **UNVERIFIABLE**. Existing code and saved prediction protocol support isolation, but this is not an independent code audit of each original training process.

The fixed corrected v2j comparison has 15 mapped folds, **11 scored spatial sites**, four unscored because station IDs 5547, 5548, 6975 and 2498781 have zero observed test targets. The 14,583 target pairs are repeated hours across only eleven sites, not 14,583 independent spatial replicates. Per-station MAE/RMSE/R² and counts for all six selected controls are in `loso_per_station_comparison.csv`, regenerated from `results/loso_per_station_v2j.csv` by `build_spatial_table.py` without changed populations. Station geometry follows the same sparse Bengaluru monitoring network; it does not sample arbitrary roads or microenvironments.

## Corrected v2j W6 pooled comparison

All rows below use the same 14,583 scored pairs, no seasonal-bias correction and the `train_mean` neural anchor. These are the saved corrected v2j protocol, not the separate earlier v2g population/protocol.

| Method | MAE µg/m³ | RMSE µg/m³ | R² | n |
|---|---:|---:|---:|---:|
| ST-PIGNN original | 22.314 | 40.821 | −0.213 | 14,583 |
| Weather/static ridge | 20.624 | 35.462 | 0.085 | 14,583 |
| Station train mean | 20.634 | 38.614 | −0.085 | 14,583 |
| IDW | 22.633 | 40.676 | −0.204 | 14,583 |
| Ordinary kriging | 22.588 | 40.562 | −0.197 | 14,583 |
| RBF Gaussian process | 24.123 | 41.070 | −0.227 | 14,583 |

The prespecified corrected v2j ST-PIGNN versus validation-best weather/static ridge decision is **LOSS**: ΔMAE +1.690 µg/m³, paired UTC-day 95% CI [+1.116,+2.275], ΔR² −0.298 (`results/loso_decision_v2j.csv`). The alternative IDW-blend anchor still yields LOSS with ΔMAE +0.831 and CI [+0.301,+1.357]. No corrected W6 neural WIN was reported across either anchor/bias treatment. The rows in this table are not evidence that kriging or GP always underperform; interpolation controls can fall back when contemporaneous known-station observations or fits are insufficient, and method availability varies by hour. The original fallback accounting is in `results/loso_fallbacks_v2.csv`; do not transfer those counts to v2j without checking exact protocol.

For historical context only, the earlier v2 Gate C comparison of known-station ST-PIGNN to ordinary kriging had pooled ΔMAE −0.305 µg/m³ but paired CI [−1.164,+0.608] and Wilcoxon p=0.278 across eleven scored sites (`results/loso_decision_v2.json`). This was a TIE, not a spatial-transfer win, and must not be pooled with v2j. W6 also tested seasonal-bias and anchor changes; their populations and information sets must remain labeled separately.

The road graph's one-component structural integrity is a topology result. It does not validate PM2.5 estimates at unsensed road nodes, which lack complete model inputs and independent concentration truth. The 23 station-to-road snaps are neither 23 scored held-out road sites nor proof of road-level generalization. Meaningful uncertainty would require independently observed spatial sites and a new fixed protocol; v2n adds none. Source methods: `scripts/evaluate_loso_v2.py`, `results/loso_summary_v2j.csv`, `results/loso_per_station_v2j.csv`, `results/loso_unscored_folds_v2j.csv`, `final_blr_results/road_graph/spatial_validation_feasibility.md`.
