# Volume 10 — Compatibility, interpolation and neural-assisted road estimates

<a id="volume-10"></a>

## Editorial reconstruction and evidentiary boundary

v2n correctly blocked direct corrected-ST-PIGNN inference on road nodes: missing road time series, incompatible graph/edge semantics and absent matching v2j weights. v2o then built retrospective station-to-road IDW estimates, which are not six-hour forecasts. v2q found a historical road-partition model but its input construction was not issue-time-safe. v2r used corrected h=6 station forecasts and a frozen 1,249-parameter spatial decoder to populate all 154,902 road nodes at three preselected times: 464,706 experimental neural-assisted values. The decoder's held-out-site deficit makes the maps computational demonstrations, not validated roadside concentrations. Median nearest-station distance was 3.315 km; 19.45% of nodes were >5 km from a monitor and 60.58% outside the station convex hull. [EVIDENCE: v2r handoff | final_blr_results/final_research_v2r/FINAL_RESEARCH_HANDOFF.md | snapshot 1c46a4b]

## Full round-specific source exhibits

The exhibits reproduce the cited local reports as source evidence. Their original round-specific conclusions may be narrower than later findings; read the editorial reconstruction and final synthesis before treating one exhibit as the final verdict.

## Source exhibit 1: `final_blr_results/city_scale/inference/INFERENCE_VERDICT.md`

[EVIDENCE: `final_blr_results/city_scale/inference/INFERENCE_VERDICT.md` | SHA-256 `5cec5013c1e3dbbcacd52a6b7b3adab231bc8ec1a0a0f61905d9b1b45f0650ac` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### v2n bounded full-city inference verdict

**BLOCKED — zero road nodes inferred.** The frozen Phase 2 gate failed before the small-subgraph step. A small or medium road-subgraph forward pass would need arbitrary missing temporal pollutant inputs, a substituted graph/edge interface, or unverified legacy weights; none is a defensible compatibility test of the corrected station model. Full-graph execution and partition-equivalence testing therefore did not run. No prediction artifact or city concentration map was produced.

The full road tensor is 154,902 nodes, 424,550 directed symmetrized message arcs, static `x=[154902,17]`, and 16 road edge channels. The validated forecast model uses 15 monitored stations, 12 × 18 dynamic features, distance edges, causal station PM2.5 anchors, and corrected v2j weights that were not archived. Node-hour features cover 22 road nodes, leaving 154,880 uncovered. Sixty-four stored induced partitions omit 7,134 cross-boundary arcs and have a different feature width. v2m MLP/TCN checkpoints are compatible only with their own 15-station cutoff-safe inputs and do not use the road graph. The legacy root citywide checkpoint does not establish corrected-v2j compatibility.

The v2k memory estimate of 134 MB for 12 × 154,902 × 18 float32 input, 27 MB for edge attributes, and 476 MB for one 12 × 154,902 × 64 hidden activation is an estimate, not measured runtime or peak VRAM. No v2n full-graph runtime, throughput, CPU RAM, GPU VRAM, repeatability or output-integrity benchmark exists; all are **NOT MEASURED**. The sandbox NVIDIA driver is unavailable, which would separately prevent a V100 measurement here, but feature/checkpoint failure is the scientific stop condition. The output class is **BLOCKED**, not an experimental estimate or validated road-node prediction.

Gate inputs and counts: `../graph/graph_integrity.csv`, `../graph/graph_compatibility.md`, `../features/feature_registry.csv`, `../features/feature_validation.md`, `final_blr_results/road_graph/graph_measurements_v2k.json`. No training or fabricated road-node pollutant lag was used.

## Source exhibit 2: `final_blr_results/citywide_extension/v2o/CITYWIDE_METHODOLOGY.md`

[EVIDENCE: `final_blr_results/citywide_extension/v2o/CITYWIDE_METHODOLOGY.md` | SHA-256 `74503dd0f27b8eabbcd6b508a9ad641ade68a9c99f79bf101e6c391ea570e33e` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### v2o citywide methodology

The frozen protocol is `CITYWIDE_INFERENCE_PROTOCOL.md`; the executable is `run_spatial_bridge.py`. It reads the v2m data array solely for cleaned station observations/masks/coordinates and reads raw OSM road coordinates plus the verified SRTM-derived node elevation table. The v2m observed target and mask are byte-identical to v2j; no v2m neural forecast is used. The method is inverse squared Euclidean distance weighting in EPSG:32643, with no fitted hyperparameter and no road-graph message passing. The nearest observed station and a train-other-station mean provide transparent validation controls. Exact equations and path alternatives are in `SPATIAL_ESTIMATION_METHOD.md`.

Target times were selected by a mask-only first/median/last rule among test hours with at least four contemporaneously observed monitors. Each road estimate uses those monitors' *same-hour* cleaned PM2.5; hence the result is retrospective reconstruction, not forecast-origin eligible at positive lead time. Eleven target-observed stations support held-out validation; each is completely removed from its own interpolator. Four station folds have no test target and are recorded as unscored. Validation metrics are computed only on real observed targets, with unavailable predictions left missing; matched-population comparisons are explicit. No test metric chooses the IDW power or snapshots.

For each road snapshot the runner computes in 16,384-node chunks, verifies 1,000- and 10,000-node prefix equality, finite/nonnegative output, unique row/index mapping, SRTM coordinate join and source/output SHA-256. Delaunay hull status and nearest-support distance provide uncalibrated support diagnostics. CPU wall time and RSS are measured; GPU VRAM does not apply. The fixed map display greys out unsupported areas. Files are generated atomically where large Parquet output is involved, and `scripts/run_supervised.sh` supplied locking, per-attempt logs and a COMPLETE marker. The sandbox's detached launcher did not persist, so the documented foreground supervised worker completed one attempt with exit code zero.

The old corrected ST-PIGNN cannot be invoked at these road nodes: no matching weights, 12×18 road histories, observed pollutant anchors or compatible edge semantics exist. A new road-graph neural model would require the independent supervision and protocol in `SPATIAL_ESTIMATION_METHOD.md`; v2o did not train it. No validated road-node concentration or route exposure claim follows.

## Source exhibit 3: `final_blr_results/citywide_extension/v2o/CITYWIDE_EXECUTION_RESULTS.md`

[EVIDENCE: `final_blr_results/citywide_extension/v2o/CITYWIDE_EXECUTION_RESULTS.md` | SHA-256 `044e49f6a18fd7845263254df546bd80efb944711ab08356c764c1ac7312f9b8` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### v2o full-city computational execution

The frozen retrospective IDW bridge executed at **all 154,902 road nodes** for three mask-selected UTC hours: 2025-10-08 13:00 (four observed monitors), 2026-02-10 07:00 (six), and 2026-03-28 23:00 (four). `road_node_estimates.parquet` has 464,706 rows with unique `(target_time_utc, road_row_index)` keys, ordered `osmid` mapping, UTM coordinates, verified SRTM elevation, estimate, support count/distance/hull flags and `observed_road_label=False`. Every estimate is finite and nonnegative; range 0 to 98 µg/m³ to rounding. Output SHA-256 `45bf6740a75b22abae499934329e395d3e066d77a64f9c905615c838c12d0738`.

The first 1,000 and 10,000 nodes were computed separately at each hour and compared with the corresponding full-city prefixes; maximum difference was **0 µg/m³** in all six checks. Full IDW kernel times were 0.165, 0.081 and 0.091 s, or about 0.94, 1.90 and 1.70 million nodes/s; these exclude source reading, plotting and Parquet writing. Total supervised run time was 10.14 s. Peak process RSS reported by `ru_maxrss` was 427,916 KiB (about 418 MiB). GPU VRAM is inapplicable; this CPU spatial interpolator used no GPU. `execution_benchmarks.csv`, `execution_summary.json` and `runs/v2o_bridge/` retain measurements, source/output hashes, attempt log and COMPLETE marker.

The 64 graph partitions were not used: IDW depends on monitor distances, not road-message passing. Chunking at 16,384 nodes preserved the exact prefix result; road graph boundary halos do not apply. The three city maps (`citywide_idw_*.png`) color only the better-supported subset; gray nodes are outside the eligible-monitor convex hull or >5 km from their nearest eligible monitor. These are **interpolated estimates**, not ST-PIGNN neural predictions or observed road concentrations. Computational completion does not establish their street-level accuracy.

## Source exhibit 4: `final_blr_results/citywide_extension/v2o/CITYWIDE_UNCERTAINTY_AND_SUPPORT.md`

[EVIDENCE: `final_blr_results/citywide_extension/v2o/CITYWIDE_UNCERTAINTY_AND_SUPPORT.md` | SHA-256 `98d0cca76eee96e03cfb624d5924f12c103bdd8aec139c3befd46e4ed17cff1e` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### v2o citywide support diagnostics

The output records nearest same-hour eligible monitor distance, number of eligible support monitors, and whether each road node lies outside their convex hull. The display flag `poor_support` is outside-hull **or** nearest distance >5 km, fixed before scores; it is a map marker, not a calibrated uncertainty threshold.

| UTC snapshot | Supporting monitors | Median nearest distance | 90th percentile distance | Outside hull | Poor support |
|---|---:|---:|---:|---:|---:|
| 2025-10-08 13:00 | 4 | 5.01 km | 8.94 km | 75.0% | 86.1% |
| 2026-02-10 07:00 | 6 | 4.71 km | 9.25 km | 82.9% | 84.9% |
| 2026-03-28 23:00 | 4 | 6.18 km | 13.08 km | 85.9% | 90.6% |

These high fractions show that most road nodes require interpolation beyond the small contemporaneous monitor hull, especially at the last snapshot. Holding out one of eleven observed sites does not calibrate a prediction interval for all roads, and station representativeness differs from street microenvironments. No kriging/GP posterior or empirical road-node interval is claimed. A distance-to-monitor figure cannot be converted to a concentration error bar without independent observed sites and an appropriate calibration design. The raw weather archive has only one known coordinate; no street-level wind variation is introduced. The maps explicitly gray out poor-support areas.

## Source exhibit 5: `final_blr_results/citywide_extension/v2q/CITYWIDE_NEURAL_VERDICT.md`

[EVIDENCE: `final_blr_results/citywide_extension/v2q/CITYWIDE_NEURAL_VERDICT.md` | SHA-256 `fc3b9708a0c7c4254785f0f4f3fa659b4986ea6696aa9d420e39a9c01de91723` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### v2q neural citywide verdict

| Question | Verdict | Evidence |
|---|---|---|
| Original notebook and architecture recovered | YES, historical | 26 cells statically inspected; exact GINE–GRU source and strict-loading root checkpoint documented. |
| Original model reproducible as implemented | PARTIAL | Archived `results/full_replay_parity.json` reports bounded replay parity; current notebook differs from the older audit hash and contains no saved outputs. |
| Original model valid as lead-time city forecast | UNSUPPORTED | Same-hour input/target, modulo timeline lookup, 154,880 copied node histories, scaled wind angle, omitted partition arcs. |
| Compatible original weights found | YES, historical only | Root best checkpoint is 16-input/16-edge, 98,497 parameters; not corrected v2j. |
| Forecast-safe spatial decoder validation | NOT RUN | Necessary cross-fitted support-station forecasts and fold checkpoints are absent. |
| Full-city v2q neural inference | BLOCKED | Zero nodes/timestamps; no validated forecast-origin road input or tested decoder. |
| Independent roadside accuracy | NOT EVALUATED | No independent road-level PM2.5 observations. |

The v2q scientific blocker is **missing cutoff-safe, target-isolated station-to-road forecast inputs**, not a failure to instantiate a neural tensor. The smallest path forward is to create audited cross-fitted station forecasts under an approved bounded LOSO plan, then compare mean, IDW and compact decoder on identical future targets. Do not use legacy city maps as forecasts or the v2o retrospective IDW run as a forecasting control. Preserve corrected W6 ST-PIGNN LOSO loss to ridge.

## Source exhibit 6: `final_blr_results/final_research_v2r/citywide/methodology/CITYWIDE_METHODOLOGY.md`

[EVIDENCE: `final_blr_results/final_research_v2r/citywide/methodology/CITYWIDE_METHODOLOGY.md` | SHA-256 `d91db12524ee852fa3aa3e8d44cbdc7e9e4de7ef833db32b9df71446d5abdc71` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### v2r citywide methodology

#### Model and data

The original production notebook checkpoint was not used: v2q found target-hour pollutant input, copied station timelines at road nodes and modulo time indexing. The v2r source model instead reuses corrected station-level code in `src/stpignn/{data_v2,models_v2,station_graph,physics_v2}.py`, with its 15-station/60-directed-edge graph. Road graph edges are not used by the decoder and are not treated as transport. The corrected GINE–GRU has 18 input channels, a 12-hour window, hidden size 96 and a one-step h=6 output; each model has 95,809 parameters.

Source data is `results/data_v2j_arrays.npz` built under `configs/data_v2.yaml`; model selection uses `configs/loso_v2.yaml`. Data source hashes and fold configurations are recorded in each fold's config, summary and checkpoint. `src/stpignn.data_v2.build` is called with held-out station exclusion, half-hour weather alignment and the forecast-cutoff-safe weather rule. Target PM2.5 uses the corrected log1p-compatible residual/anchor transformation. The input window indices end at target−6 hours and are asserted strictly before the target. The held-out station's pollutant channels and anchor are hidden; train-only global means provide fallback only for that station's anchor. No road-node pollutant labels or fabricated inputs are created.

#### Cross-fitting and spatial holdout

The 18 input channels are: `pm25_lagged` (observed PM2.5 with train-fitted/causal fill), PM10, NO2, SO2, CO, 10 m wind speed, wind gusts, 2 m temperature, relative humidity, surface pressure, sine and cosine of 10 m wind direction, SRTM elevation, a pollutant-observation missingness indicator, and four hour/day-of-week sine/cosine calendar channels. Units follow `src/stpignn/data_v2.py::POLLUTANTS` and `WEATHER` (PM2.5/PM10 µg/m³; NO2/SO2 ppb; CO as declared by the source; wind m/s; temperature °C; humidity %; pressure hPa; elevation metres; circular/calendar channels unitless). Weather is a point series broadcast across the station graph, not street-varying. This fit uses cutoff-safe half-hour timestamp alignment, not historical weather interpolation. PBLH, population, traffic and differentiated street wind are unavailable and were not added.

For each of 15 query-site outer folds, a separate inner model is fitted on the earlier block through 2025-01-30 23:00 UTC, selected on 2025-02-01 through 2025-03-30, and forecasts cross-fitted decoder examples from 2025-04-02 through 2025-06-29. The outer model excludes the query station from all pollutant history/targets/preprocessing, is fitted through 2025-06-29, selected on 2025-07-01 through 2025-09-21, and forecasts the exposed test period beginning 2025-09-23. Split gaps are at least 24 hours. One fixed seed (11), learning rate 1e-4, batch size 512, up to 20 epochs and patience 4 were used; selection was validation-only. Thirty cells completed. Each inner/outer summary records cutoff and exclusion assertions, best checkpoint SHA-256, pair counts, time and peak CUDA allocation. The all-station seed-11 source fit was a bounded feasibility model and is not used in spatial holdout scoring or citywide support.

The decoder reuses `final_blr_results/citywide_extension/v2q/spatial_decoder.py::CompactSpatialDecoder`, unchanged capacity (hidden 32, 1,249 parameters). Its four fixed inputs are IDW support forecast/100, nearest support distance/10,000 m, support count/15, and query minus mean support SRTM elevation/100 m. The predicted residual is added to p=2 IDW. Exactly 13 nearest stations are used. Each held-out target station is removed from decoder labels and forecast support. The decoder is AdamW, learning rate 1e-3, weight decay 0.01, at most ten epochs, patience three; seed 42 plus held-out station ID. Validation selects the best epoch. Controls are a training-only spatial mean and forecast-IDW using station forecasts at the same forecast origin.

#### Full-city estimate construction

Road coordinates and ordered OSM identity come from `data/graphs/bangalore_utm_nodes.parquet`; true SRTM-derived elevation comes from `data/processed/graph/nodes_elevation_true.parquet`, joined and checked by equal ordered `osmid` and coordinates. The city table preserves raw row index as `node_index`. Three forecast origins were frozen before map output; each target is origin +6 h. For each station j, support forecast j is taken from the corrected outer GINE–GRU model whose fold excluded j. Thus the support values are station-isolated predictions, not observations. The 13 nearest support stations are selected geometrically for every road coordinate. IDW and the learned decoder are both saved.

The run performs 1,000-node and 10,000-node staged checks before each complete 154,902-node calculation, then compares both methods with the staged prefixes (maximum absolute error 0). Values must be finite and nonnegative; mapping must contain all node indices exactly once. Maps color estimated PM2.5 and overlay nodes more than 5 km from a station. Convex-hull status and distance are support diagnostics only, not calibrated uncertainty. The run uses CPU for road expansion; station models were fitted on a V100. No road-level truth exists.

#### Evaluation and statistical limits

Spatial holdout metrics are computed on the same observed target pairs for all methods. Coverage is paired; unscored stations remain listed in the eligibility register. Pooled MAE/RMSE/R² describe station-time pairs, while uncertainty contrasts resample station sites (11 independent scored locations) with 2,000 bootstrap draws and seed 4303. These data have repeated Bengaluru exposure and remain exploratory. A completed full-city array shows only computational coverage; it cannot establish roadside accuracy, calibration, exposure validity, transport physics or predictive advantage.

## Source exhibit 7: `final_blr_results/final_research_v2r/citywide/CITYWIDE_FINAL_VERDICT.md`

[EVIDENCE: `final_blr_results/final_research_v2r/citywide/CITYWIDE_FINAL_VERDICT.md` | SHA-256 `7298e1f71b8ac8d4a05405b2b05515477b15748f7efa4941eae917033bf0e278` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### v2r citywide forecasting verdict

| Criterion | Result | Evidence |
|---|---|---|
| Valid h=6 source forecasts generated | **YES, exploratory** | 15 outer station-isolated corrected GINE–GRU folds; 30 inner/outer fit cells complete. Cutoff assertions and per-fold manifests record issue-time safety. |
| Compact decoder trained | **YES** | Frozen 1,249-parameter architecture; 9,819 cross-fitted training examples, 7,203 validation examples; selected epoch 3, validation MAE 13.127 µg/m³. |
| Spatial holdout evaluation | **COMPLETE, unfavorable** | 11 scored stations, 14,583 pairs; four stations unscored. Decoder pooled MAE 27.360, IDW 20.154, training-only spatial mean 20.634. |
| Decoder improvement over controls | **NO** | Decoder MAE higher than each control at 9/11 sites; station-bootstrap equal-site ΔMAE vs IDW +5.101 (95% CI +1.815,+8.302). |
| Full road-node execution | **COMPLETE as a computational demonstration** | 154,902/154,902 nodes at three prespecified h=6 target timestamps; all outputs finite and geographically indexed. |
| Forecast-time input validity | **PASS for the recorded pipeline** | Outer station forecasts used 12 history hours ending at target−6 h; each support station's estimate comes from the outer GINE–GRU fold that excluded that station. No target-time PM observations were supplied. |
| Independent roadside accuracy | **NOT ESTABLISHED** | No road-level reference measurements; station LOSO is unfavorable for decoder and only eleven spatial sites were scored. |

#### Execution and artifacts

Targets are 2025-10-08 13:00, 2026-02-10 07:00 and 2026-03-28 23:00 UTC. Each output contains 154,902 road-node rows, preserving `node_index` and `osmid`, coordinates in UTM metres, all 13 supporting station IDs, the IDW comparator, decoder estimate, nearest-support distance, convex-hull flag and >5 km support flag. Prediction tables and city figures are in `road_predictions/` and `figures/`.

The supervised road-output stage took 56.44 seconds including final decoder fitting, three maps and artifact writing; per-snapshot full graph processing took 1.12–1.30 seconds (about 119k–138k nodes/s), peak process RSS 1.36–1.49 GB, and GPU VRAM 0 for the road-node expansion. The source station models were trained on the V100 (maximum measured allocation 1.831 GB per fold model). Prefix checks for 1,000 and 10,000 nodes matched full-output IDW and decoder predictions exactly (max absolute difference 0). The full results include three files of 8.9 MB each. Inference completion demonstrates computational coverage, not physical validity or accuracy.

#### Classification

Citywide outputs are **EXPERIMENTAL NEURAL-ASSISTED ROAD-NODE ESTIMATES**, not observed concentrations, not independently validated roadside predictions, and not evidence that the original 154,902-node road GNN was restored. The corrected GINE–GRU forecasts monitored stations; a compact spatial decoder propagates them to road coordinates. The decoder loses to both spatial controls in held-out evaluation. Support is weak over 19.45% of road nodes under the uncalibrated nearest-station >5 km diagnostic; 60.58% lie outside the convex hull of the 15 stations. These are support diagnostics, not calibrated intervals.

Known limits: eleven scored station sites, four unscored; repeated exposure to Bengaluru data; station-to-road extrapolation; no roadside truth; no calibrated prediction intervals; station meteorology is spatially sparse; 13-nearest support forecasts may share source-model errors; model selection was validation-only but all evidence is exploratory. Do not claim accurate citywide concentration, traffic exposure validity, or ST-PIGNN road-graph inference.

## Source exhibit 8: `final_blr_results/ieee_paper_evidence/methodology/CITYWIDE_ESTIMATION.md`

[EVIDENCE: `final_blr_results/ieee_paper_evidence/methodology/CITYWIDE_ESTIMATION.md` | SHA-256 `e398ce0577fd9148f9d17f177a23761c6cb52257d5bb24c12e6d6942e8403c28` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Citywide estimation

The road topology has 154,902 nodes but is not the forecasting graph. v2o produced retrospective IDW estimates. v2r generated three six-hour neural-assisted estimates per road node using corrected station forecasts plus a compact spatial decoder: 464,706 values total. They are experimental estimates, not observations, and have unfavorable held-out decoder evidence. Median nearest-monitor distance 3.315 km; 19.45% of nodes exceed 5 km; 60.58% lie outside the monitor convex hull. These are support diagnostics, not calibrated intervals. v2r expansion took 1.12–1.30 s per snapshot, peak RSS about 1.49 GB, GPU VRAM 0 for expansion; station source-fold models used up to 1.831 GB GPU. No independent roadside accuracy.
