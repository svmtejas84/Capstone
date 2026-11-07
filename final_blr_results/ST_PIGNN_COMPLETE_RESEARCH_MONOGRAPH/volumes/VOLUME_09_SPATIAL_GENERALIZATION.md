# Volume 9 — Station isolation and spatial controls

<a id="volume-09"></a>

## Editorial reconstruction and evidentiary boundary

Spatial generalization is tested by holding out an entire station, not by counting many hours at that site as independent locations. Corrected W6 LOSO scored 11 stations (four had no eligible test targets): ST-PIGNN MAE 22.314 versus weather/static ridge 20.624 µg/m³. In v2r, forecast-IDW and training-only spatial mean outperformed the frozen compact decoder: 20.154 and 20.634 versus 27.360 µg/m³ over 14,583 common pairs, with decoder worse at nine of eleven scored stations. Retrospective same-hour IDW is a different task from a six-hour forecast assembled from station predictions. These unfavorable controls are evidence against spatial-transfer superiority on this exposed dataset. [EVIDENCE: v2r handoff | final_blr_results/final_research_v2r/FINAL_RESEARCH_HANDOFF.md | snapshot 1c46a4b]

## Full round-specific source exhibits

The exhibits reproduce the cited local reports as source evidence. Their original round-specific conclusions may be narrower than later findings; read the editorial reconstruction and final synthesis before treating one exhibit as the final verdict.

## Source exhibit 1: `final_blr_results/city_scale/spatial_validation/SPATIAL_VALIDATION_VERDICT.md`

[EVIDENCE: `final_blr_results/city_scale/spatial_validation/SPATIAL_VALIDATION_VERDICT.md` | SHA-256 `5508528614e95d67ff3b676270218ed16fe00b2b9775649ee6ef43d861361c5a` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Spatial generalization verdict

**UNSUPPORTED for ST-PIGNN superiority at unmonitored stations; road-node accuracy NOT EVALUATED.** This consolidates saved station-graph leave-one-station-out (LOSO) results. No v2n LOSO model was trained or scored. The corrected v2j W6 data builder excludes held-out station pollutant channels before imputation and fitting (`src/stpignn/data_v2.py`, `excluded_station_id` path), and test targets remain observed-only. The saved procedure uses fold-specific 14-station training with the held-out location represented by weather/static inputs and a train-only anchor; a compatible fold checkpoint was not archived, so forward-level leakage replay is **UNVERIFIABLE**. Existing code and saved prediction protocol support isolation, but this is not an independent code audit of each original training process.

The fixed corrected v2j comparison has 15 mapped folds, **11 scored spatial sites**, four unscored because station IDs 5547, 5548, 6975 and 2498781 have zero observed test targets. The 14,583 target pairs are repeated hours across only eleven sites, not 14,583 independent spatial replicates. Per-station MAE/RMSE/R² and counts for all six selected controls are in `loso_per_station_comparison.csv`, regenerated from `results/loso_per_station_v2j.csv` by `build_spatial_table.py` without changed populations. Station geometry follows the same sparse Bengaluru monitoring network; it does not sample arbitrary roads or microenvironments.

#### Corrected v2j W6 pooled comparison

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

## Source exhibit 2: `final_blr_results/citywide_extension/v2o/SPATIAL_VALIDATION_VERDICT.md`

[EVIDENCE: `final_blr_results/citywide_extension/v2o/SPATIAL_VALIDATION_VERDICT.md` | SHA-256 `e4e268d622273a2ff9521b85f9f041eefc584289a87d7be49ffcfd9ec952b45a` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### v2o spatial validation verdict

**Retrospective IDW spatial accuracy: weak and incompletely covered.** `SPATIAL_VALIDATION_RESULTS.csv` and `spatial_validation_pairs.parquet` come from `run_spatial_bridge.py` using fixed power 2 and genuine held-out station isolation. For each target pair, the held-out station is removed from same-hour interpolation inputs; no model or weight is fitted on its test target. The train-other-station mean comparator uses training observations from other stations only. Eleven stations have test observations, four (5547, 5548, 6975, 2498781) have none and remain unscored. The 14,583 pairs are only eleven spatial sites and cannot be treated as independent locations.

| Method | Scored n / 14,583 | Coverage | Pooled MAE µg/m³ | RMSE µg/m³ | R² |
|---|---:|---:|---:|---:|---:|
| Fixed IDW p=2 | 12,328 | 84.54% | 23.133 | 42.606 | −0.176 |
| Nearest observed monitor | 13,616 | 93.37% | 26.640 | 46.743 | −0.510 |
| Training-only other-station mean | 14,583 | 100% | 20.563 | 38.480 | −0.078 |

On the **12,328 exact IDW-eligible pairs**, nearest-monitor MAE is 27.007 and training-only other-station mean MAE is 21.943, versus IDW 23.133. IDW improves on nearest on that matched population but is worse than the train-only mean. The pooled primary IDW figure is not compared causally with the nearest 13,616-pair row because coverage differs. Per-station IDW coverage ranges from 26.0% to 100%; station 3409388 has 56.9% and station 6119271 only 26.0%. Several per-station R² values are strongly negative, especially at low-variance sites. The full per-station table retains every scored site.

This is **same-time retrospective spatial reconstruction**: other monitors' observations at target hour t are used as inputs. It is not h-step forecasting and cannot be compared directly with corrected W6 forecast LOSO. The earlier W6 ST-PIGNN LOSS to weather/static ridge (MAE 22.314 vs 20.624, 11 scored stations) remains a separate negative result in `final_blr_results/city_scale/spatial_validation/SPATIAL_VALIDATION_VERDICT.md`. Both Bengaluru evaluations use an exposed test period; neither is independent spatial confirmation. No new IDW tuning was chosen after these results.

## Source exhibit 3: `final_blr_results/citywide_extension/v2o/SPATIAL_ESTIMATION_METHOD.md`

[EVIDENCE: `final_blr_results/citywide_extension/v2o/SPATIAL_ESTIMATION_METHOD.md` | SHA-256 `58f33ed0d702167fccff5847fcff7477744585d4f5267943f9f4bf8ccd650f34` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### v2o spatial estimation pathways

**A — existing learned ST-PIGNN road inference: BLOCKED.** The corrected 15-station directed distance-kNN model has no matching archived neural weights; its 12×18 station history, residual anchors and distance edges do not match the static OSM road graph. The 22 archived road nodes with node-hour rows do not supply complete observed pollutant lag histories for 154,902 nodes. The v2m MLP/TCN station checkpoints cannot turn this into ST-PIGNN road inference. No model forward pass is forced.

**B — explicit bridge: fixed IDW power 2.** For road location x and observed same-hour monitor values y_i(t), use w_i(x)=1/max(d(x,i),10⁻⁶ m)² and estimate Σw_i y_i/Σw_i. An exact coincident monitor location returns that monitor's reading. The nearest eligible monitor's same-hour value is the mandatory comparator; a train-other-station mean is a reference. Distances are Euclidean in EPSG:32643. No variogram/GP fit is attempted because sparse, time-varying support and the already exposed test set do not justify a test-chosen complex interpolator. Earlier ordinary kriging/GP W6 comparisons remain in v2j. These v2o road outputs are **retrospective interpolated estimates**, not neural forecasts or observations. No meteorology or elevation term is fitted.

Station validation removes the held-out monitor from every same-hour support set. Power 2 and the output times are fixed in `CITYWIDE_INFERENCE_PROTOCOL.md` before scores. Other monitors' same-hour test readings are legitimate retrospective inputs but would be future information for a lead-time forecast. Road-node uncertainty is represented only by support diagnostics, not calibrated predictive intervals.

**C — new road-graph model (protocol proposal only):** requires independently measured or scientifically calibrated road supervision, complete issue-time temporal weather/pollutant covariates at all nodes, station/road measurement representativeness analysis, graph edge semantics matched to the model, train-only scalers and imputation, explicit forecast cutoffs, disjoint spatial holdouts, conventional interpolation controls, a GPU memory/throughput budget and independent external validation. None is presently satisfied. No road-graph neural training is launched.

## Source exhibit 4: `final_blr_results/final_research_v2r/citywide/spatial_validation/SPATIAL_VALIDATION_VERDICT.md`

[EVIDENCE: `final_blr_results/final_research_v2r/citywide/spatial_validation/SPATIAL_VALIDATION_VERDICT.md` | SHA-256 `dc5e89207a9f8e087fe5f3fa5dc8668d9b1f947c6fc65e4cb8b3e97c76ff1011` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### v2r spatial validation verdict

#### Protocol and population

Exploratory six-hour station-isolated LOSO evaluation on the corrected 15-station graph. Forecast inputs ended at target minus six hours. Fifteen outer folds were fit; each held-out station was removed from pollutant inputs, target fitting, anchor construction, and preprocessing. For decoder fitting, support forecasts came from the time-block cross-fit models fitted through 2025-01-30 and forecast for 2025-04-02 through 2025-06-29. Decoder model selection used the 2025-07-01 through 2025-09-21 validation period. Test targets were not used for fit or model selection. All Bengaluru results remain exploratory because this dataset and test period have been repeatedly examined.

Four station folds had no eligible test targets; the scored evaluation contains 11 station sites and 14,583 station-time pairs. The same pairs were used by all three methods. Confidence intervals resample the 11 sites equally, not the timestamps.

#### Pooled comparison

| Method | MAE (µg/m³) | RMSE (µg/m³) | R² | Coverage | Sites |
|---|---:|---:|---:|---:|---:|
| Training-only station mean | 20.634 | 38.614 | −0.085 | 14,583/14,583 | 11 |
| Six-hour station forecasts + p=2 IDW | **20.154** | 39.295 | −0.124 | 14,583/14,583 | 11 |
| Six-hour station forecasts + learned decoder | 27.360 | 44.046 | −0.412 | 14,583/14,583 | 11 |

The decoder (1,249 parameters) had higher MAE than IDW at 9/11 scored stations and higher MAE than the station-mean control at 9/11. Equal-site mean paired MAE differences (decoder minus control) were +5.101 µg/m³ versus IDW (station-bootstrap 95% CI +1.815 to +8.302) and +5.939 versus the mean (+2.514 to +9.379). These descriptive intervals do not establish population-level inference with eleven exposed Bengaluru sites. Per-station MAE, RMSE, R² and counts are in `../spatial_decoder/per_station_test_metrics.csv`; paired intervals are in `../spatial_decoder/station_bootstrap_comparisons.csv`; raw predictions are in `../spatial_decoder/folds/all_spatial_test_predictions.parquet`.

The simple forecast-IDW baseline is the strongest of the three on pooled MAE. IDW and the decoder do not improve consistently over the training-only station mean. All pooled R² values are negative. This does not support citywide road accuracy.

#### Provenance and limitations

All support values are corrected GINE–GRU h=6 predictions made at the corresponding issue time; support forecasts used for test targets came from the outer fold excluding the query station. The decoder was trained only on cross-fitted forecast examples, uses fixed projected distances and verified SRTM elevation, and was selected by validation MAE. No held-out target enters a support forecast or decoder fit. Four unscored stations remain unscored rather than removed from the register. The number of independent spatial test sites is eleven, not 14,583.

Structural validity of the separate road graph is not evidence of spatial prediction accuracy. No independent road-side observations were available. Preserve earlier W6 LOSO (ST-PIGNN MAE 22.314 vs weather/static ridge 20.624) and v2o retrospective IDW findings; those use different populations/protocols and are not pooled here.

## Source exhibit 5: `final_blr_results/ieee_paper_evidence/methodology/SPATIAL_VALIDATION.md`

[EVIDENCE: `final_blr_results/ieee_paper_evidence/methodology/SPATIAL_VALIDATION.md` | SHA-256 `65ba49ae6a1748a6abfe487fadbfde21cb8753769d56d77e6ec20267dbb104f9` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Spatial validation

W6 corrected LOSO: 11 scored stations, four unscored (5547, 5548, 6975, 2498781), 14,583 repeated pairs. ST-PIGNN MAE 22.314 versus weather/static ridge 20.624 µg/m³; station is the spatial unit, not timestamp.

v2o IDW was retrospective same-hour spatial reconstruction, not positive-lead forecasting: IDW scored 12,328/14,583 pairs and did not improve on train-only mean. v2r evaluated same-origin six-hour forecasts with 15 outer station-isolated folds plus time-block cross-fitting; 11 sites/14,583 pairs. Train-only mean MAE 20.634, forecast-IDW 20.154, decoder 27.360 µg/m³. Decoder lost to both controls at 9/11 sites. No roadside independent truth. Preserve populations and tasks separately.
