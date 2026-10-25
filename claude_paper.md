# ST-PIGNN executable evidence ledger

## 0. Run log

Phase A0/A audit branch: `audit/canonical-notebook-20261023`. Base source commit for all measurements below: `22a0f5ac5a0527bf173e97692e22c20a245bc6a7`; the Phase A audit commit is recorded in git history. The canonical notebook and checkpoint had pre-existing worktree modifications, so `results/audit_canonical.json` records their exact SHA-256 hashes; the base commit alone does not identify those bytes. Hardware: Tesla V100-PCIE-32GB. Runtime libraries: Python system environment, torch 2.8.0+cu128, torch-geometric 2.6.1, pandas 2.3.3, NumPy 1.26.4, SciPy 1.13.1, scikit-learn 1.6.1. The canonical source is `notebooks/production/evaluated_wind_advection.ipynb`, as clarified by the user. Notebook references below use **zero-based cell numbers and one-based lines within each cell**.

Evidence key A: `results/audit_canonical.json`, produced by `scripts/audit_canonical.py`, fixed config matching notebook cell 0, seed 42, source commit above, run 2026-10-22 20:53 UTC. Evidence key R: `results/replay_canonical.json` and `.log`, produced by `scripts/replay_canonical.py`, notebook cells 0, 2, 5, 7, 9, 11, 20, 24, seed 42, checkpoint `citywide_stpignn_best.pt`, source commit above, run timestamp and runtime in that JSON. Evidence key P: `results/refactor_parity.json`, produced by `scripts/check_canonical_refactor_parity.py`, seed 42, fixed 3-node/12-step toy batch, source commit above, run 2026-10-22 20:44 UTC. All values in this document are direct code measurements or exact constants from the named source. Stored notebook output is identified separately from an independent rerun.

Step 1 refactor run: `scripts/replay_canonical.py --deterministic-fp32` from base commit `f84633e0f675245d9b9bdc1d0696fc61d4f9d96f`, seed 42, timestamp in `results/replay_rewired_fp32.json`, Tesla V100-PCIE-32GB, 77.06 seconds on first replay. `scripts/check_full_replay_parity.py` used tolerances MAE 0.01 µg/m³, RMSE 0.03 µg/m³ and PVR 0.002 percentage points, run 2026-10-24 13:52 UTC, same base commit and seed. Exact pre-refactor notebook bytes are retained in `results/legacy_canonical_notebook.ipynb`; the checkpoint bytes remain pinned by SHA-256 in A. The Step 1 commit follows in git history.

Step 2 data run: `scripts/build_data_v2.py`, `configs/data_v2.yaml`, seed 42, source commit `f67653e` for the final registry rerun (exact commit and runtime in `results/data_v2_fit.json`), run 2026-10-24. `scripts/diagnose_data_v2.py`, same config/seed, source commit `3802c23651777bb5cd472d748d590ca30fdb14d6`, run 2026-10-24 14:16 UTC. Step 3 mask run: `scripts/analyze_physics_v2.py`, same config/seed and source commit `71befda`, run 2026-10-24 14:10 UTC. Code assertions and toy tests: `python -m pytest tests/test_data_v2.py tests/test_physics_v2.py`, 8 passed at that run.

Step 4 baseline run: `scripts/evaluate_baselines_v2.py`, configs `gate_v2.yaml` and `data_v2.yaml`, seed 42, source commit `3802c23651777bb5cd472d748d590ca30fdb14d6`, 2026-10-24 14:15 UTC (`results/baselines_v2_run.json`). Initial validation sweep: `scripts/train_gate_v2.py --stage selection`, seed 11, source commit `9478b047933df327debe22af2954c8d954008f57`, 2026-10-24 14:40:41 UTC, 248.05 seconds (`results/neural_selection_initial_run.json`); masked-history sweep from commit `89a6d6ef653e9a086ad667c188a6562b1744814a`, timestamp in `results/neural_selection_run.json`. Final five-seed training: same script `--stage final`, config `configs/gate_v2.yaml`, seeds 11/23/37/51/79, commit `89a6d6e`, 2026-10-24 14:54:47 UTC, 615.87 seconds on Tesla V100-PCIE-32GB (`results/neural_final_run.json`). The legacy checkpoint adapter ran from `89a6d6e` at 2026-10-24 14:55:52 UTC (`results/legacy_checkpoint_v2_run.json`). The paired gate ran from `89a6d6e` at 2026-10-24 14:55:29 UTC, bootstrap seed 4301 (`results/gate_bootstrap_v2.json`). Test PVR ran from `57f3e8036649342413593760198eebfec46d77a4` at 2026-10-24 14:56:38 UTC, seeds 11/23/37/51/79 (`results/pvr_gate_v2_run.json`).

## 1. Provenance verdicts

| Item | Verdict | Evidence |
|---|---|---|
| C1 SRTM elevation in training and IG | STALE | Notebook cell 5:23-35 selects 11 scaled fields and repeats five; neither input Parquet has elevation (A). Graph `x[:,16]` is synthetic: 800–1000 m and Pearson r=0.9999999999999083 with northing, versus SRTM r=0.2613058575. The notebook does not feed graph `x` to the model. Cell 14:87-91 assigns an inaccurate label `Elevation` to input channel 5. |
| C2 emission term Q in loss | STALE | Cell 13:41-58 uses `relu((pred[col]-pred[row])*sigmoid(sum(edge_attr/1000)))²`. There is no Q argument, tensor, unit conversion or subtraction in this training path. `gnn.model.physics_upwind_penalty` is a different function and is not called by cell 13. |
| C3 chronological leak-free split | STALE | Cell 9:121-123 separates target-index ranges, but cell 5:49-77 creates feature histories from the entire pre-scaled Parquet and fills missing nodes by nearest-neighbour timeline; cell 9:98-117 indexes each per-node timeline by `global_time_index % timeline_length` and includes the scored step. Cell 5:23-35 includes `pm2_5_scaled` at that step. Full-period imputation uses bidirectional interpolation and climatology (`scripts/build_gapfill_derived_layer.py:217-299`). The temporal indices are disjoint; feature/fit leakage is not prevented. |
| ST-PIGNN MAE 53.14 / RMSE 89.11 / median AE 30.60 | CURRENT as checkpoint replay outputs; STALE as leak-free observed-only claims | Independent R: 53.1382408 / 89.1050748 / 30.6010437 µg/m³ on 308 nonzero station-node target pairs. Stored cell 24 output is 53.1397 / 89.1073 / 30.6010. The mask does not test `is_imputed` (cell 24:28-35). |
| ST-PIGNN PVR 1.404% / 7,308 of 520,507 | PARTIAL numerical match | Independent R: 7,301 / 520,507 = 1.4026709%; stored cell 20 output is 7,308 / 520,507 = 1.4040%. Seven-edge discrepancy on the retained replay. |
| Vanilla GCN 75.35 / 132.38 / 1.11% / 3.25 ms | STALE as trained baseline | Stored cell 23 output matches these values, but cells 23:10-16 construct fresh models and immediately call `eval()`; no checkpoint load or training occurs. Latency lacks CUDA synchronization (cell 23:48-58). |
| ST GRU-GCN 62.51 / 97.94 / 0.35% / 12.36 ms | STALE as trained baseline | Same untrained baseline path, cells 22:28-49 and 23:10-16, 54-58. |
| IG pressure 13.12%, elevation 12.96%, etc. | STALE as named-feature attribution | Stored cell 14 output contains those percentages; cell 14:87-100 labels positions with names unrelated to cell 5:23-35 actual feature columns. |
| Routing 18.2→13.9 µg, 24.5→26.7 min | UNTESTED by canonical notebook | Routing is external to notebook. A measures saved routing snapshot field 1.2825–1.6286 µg/m³. No valid cross-method routing rerun in Phase A. |
| Ablation rows in draft | UNTESTED by canonical notebook | `scripts/stpignn_ablation_dem.py` is secondary and is not used by the canonical checkpoint replay. |

Source: A, R, P and notebook source at commit above; see scripts, configurations, seed and timestamps in section 0.

## 2. Data

`model_input_node_hourly_features.parquet` has 1,932,700 rows = 22 node IDs × 87,850 distinct timestamps, from 2016-03-21 18:00 UTC to 2026-03-30 03:00 UTC. `master_scaled_checkpoint.parquet` has 1,070,203 rows, 17 station IDs and observations in 2022, 2024, 2025 and 2026. The graph has 154,902 nodes, 424,550 directed edges and 23 `train_mask` nodes. The model-input rows map to 22 nodes in 15 of the saved 64 clusters. These are distinct counts; 23 sensors, 22 model-input nodes and 15 clusters must not be called the same population. `results/stations.csv` lists each ID, projected and geographic coordinates, node index, saved-partition cluster, nonzero scored targets, and independently confirmed non-imputed PM2.5 observations from the master file. Source: A and `scripts/audit_canonical.py`, seed 42, source commit and timestamp in section 0.

Notebook cell 9:25-44 uses sorted unique timestamps to set integer positions. Training starts are `range(0, 87178-12, 128)`, validation starts `range(87178, 87514-12, 24)`, and each target is at start+11. This yields 681 distinct training and 14 distinct validation target hours; 14,969 nonzero training rows and 308 nonzero validation rows at graph sensor nodes. Scored train targets span 2016-03-22 05:00 to 2026-02-24 21:00 UTC. Scored validation targets span 2026-03-02 15:00 to 2026-03-15 15:00 UTC. The nominal boundary index 87178 is 2026-03-02 04:00 UTC. No September 2025 boundary is present in this notebook. The actual loader emits 306 validation graph batches (stored cell 20 progress), then R scores 308 pairs. These are sampled 12-row sequences, not all valid hourly windows, and no next-hour target is used. Source: A, R; scripts, seed, commit and timestamps in section 0.

The notebook divides raw `station_pm25` by hard-coded `TARGET_SCALE=342.9356` (cells 0:61, 9:35-37) and multiplies predictions and targets by it in evaluation (cell 24:38-45). Its statistical meaning is not recorded in the checkpoint. The master `pm2_5_scaled` is separately standardized (A: mean approximately 0, standard deviation approximately 1 across all master rows), so the feature and target scaling definitions differ. `nodes_elevation_true.parquet` has SRTM-like `elevation_true` values 767–957 m; its Pearson/Spearman correlations with UTM northing are 0.2613/0.2260. The graph's existing elevation channel has 800–1000 m and near-perfect northing correlation; neither elevation channel is used by the canonical training feature registry. Source: A; script, seed, commit and timestamp in section 0.

The master PM2.5 tiers and per-year/station counts are in `results/audit_imputation_tiers.csv`; 55,089 PM2.5 rows are tier A observed, 9,510 tier B and 239,256 tier C in the full master file. Only 392 training and 63 validation scored timestamp/station pairs are independently confirmed as non-imputed PM2.5 in the master file; the remaining model-input targets have not been verified as observed, including five station IDs absent from master. The notebook's nonzero mask treats them alike. `1,073,807` is the materialized derived-gapfill row count reported by `data/processed/gapfill/station_timeseries_imputation_build_report.md`, whereas the master has 1,070,203 rows. Source: A and `scripts/audit_canonical.py`, seed 42, source commit and timestamp in section 0.

The draft Table-1 values 60,752 and 594,974 are the raw **all-pollutant row counts** in `data/raw/stations/2022.parquet` and `2025.parquet`, respectively; they are not numbers of stations or observed PM2.5 targets. The raw 2023 station file contains zero rows. Source: `results/data_v2_diagnostics.json`, produced by `scripts/diagnose_data_v2.py`, config/seed/commit/2026-10-24 14:16 UTC timestamp in section 0.

**Step 2 rebuilt data.** `src/stpignn/data_v2.py` loads raw station rows, floors their timezone-aware timestamps to UTC hours, joins weather on one unique global hourly UTC index, and keeps raw PM2.5 observations as the sole evaluation truth. The 37,152-hour index has no generated gaps; source missingness remains explicit before train-fitted fill. Raw PM2.5 covers 15 mapped stations in 10 saved clusters. `results/stations_v2.csv` provides IDs, coordinates, node indices, clusters and observed hours. The 2023 PM2.5 count is zero. At horizon one hour, observed scored pairs are train 32,867, validation 7,204 and test 14,623; training ends 2025-06-29, validation runs 2025-07-01 to 2025-09-21, and test starts 2025-09-23, leaving 24 unassigned hours at each boundary. Horizon-six and horizon-24 counts/dates are in `results/splits_v2.json`. These are all target hours with an observed station value and enough history; the builder also permits windows without observed targets for physics-only training. Source: `results/splits_v2.json`, `results/stations_v2.csv`, `results/data_v2_diagnostics.json`, scripts/config/seed/commits/timestamps in section 0.

Train-only PM2.5 imputation classifies 459,360 potential station-hours: observed O 32,877; PM10-ratio R 6,033; same-hour other-station IDW I 174,403; train-fitted hour/day climatology C 131,462; train station/global median D 114,585. IDW uses static projected distances and inverse-square weights; it does not fit on validation/test target values. Network feature gaps use past-only forward fill for at most 24 hours, then a train-period median. Imputed values are never used as evaluation truth; a reduced-weight training variant is reserved for Step 4. `results/imputation_breakdown_v2.csv` records per-split, year, station and tier counts. The train observed-target mean/SD are 746.7087/10,237.2715 µg/m³, versus median 31 and maximum 647,953; 223 observed train values exceed 1,000 and 212 exceed 10,000. These raw outliers were retained without tuning or hand edits. Legacy 342.9356 is 0.0334987 times the observed train SD. Train-fitted standard and log1p scaler parameters are in `results/data_v2_fit.json`; neither uses validation/test rows. Source: `results/imputation_breakdown_v2.csv`, `results/data_v2_fit.json`, `results/data_v2_diagnostics.json`, scripts/config/seed/commits/timestamps in section 0.

## 3. Methods as implemented

**Imports and components.** Notebook cell 0 imports custom `gnn.model.STPIGNN` and `shared.physics_config`; other cells use NumPy, pandas, PyTorch, PyTorch Geometric, scikit-learn `KMeans`, SciPy `KDTree` and `griddata`, tqdm, Captum `IntegratedGradients`, and Matplotlib. Versions for installed core libraries are in section 0; Captum and Matplotlib versions were not captured. The model is custom `gnn/model.py:STPIGNN` using library `torch_geometric.nn.GINEConv` (2.6.1), `torch.nn.GRU` (torch 2.8.0), `LayerNorm`, dropout, and linear layers. Cell 11:22-29 instantiates 16 inputs, 16 edge features, spatial/temporal hidden sizes 96/96, two GINE layers and the model defaults of one GRU layer and 0.1 dropout. `gnn.model.STPIGNN._spatial_encode` applies linear node encoding, two residual GINE-MLP/LayerNorm/ReLU/dropout blocks on each time step; `forward` feeds the 12 embeddings per node to GRU and a linear head. The graph edge vector is length in metres followed by 15 one-hot road-category flags (A). Cell 2:64-96 applies library `sklearn.cluster.KMeans(random_state=42,n_init=10)` to projected coordinates, then custom `SpatialPartition` extracts edges wholly inside each of 64 clusters. The saved partition artifact is Python-pickled and needs the notebook class to load. Source: A and notebook cells cited, seed 42, commit and timestamp in section 0.

**Actual feature order.** Cell 5:23-35 sets channels 0–15 as `pm2_5_scaled`, `pm10_scaled`, `nitrogen_dioxide_scaled`, `sulphur_dioxide_scaled`, `carbon_monoxide_scaled`, `wind_speed_10m_scaled`, `wind_direction_10m_scaled`, `wind_gusts_10m_scaled`, `temperature_2m_scaled`, `relative_humidity_2m_scaled`, `surface_pressure_scaled`, `nitrogen_dioxide_scaled`, `sulphur_dioxide_scaled`, `pm2_5_scaled`, `pm10_scaled`, `carbon_monoxide_scaled`. Five are duplicates. Cell 4 has an earlier alternative order, but cell 5 rebuilds and overwrites `FEATURE_COLS_16` and the registry. Library pandas `read_parquet`, `groupby`, `sort_values`; custom notebook cell 5 registry and nearest-node timeline fill (`scipy.spatial.KDTree`). It uses no elevation, population, boundary layer, road proximity or traffic channel. Cell 14:87-91 IG labels therefore do not describe the actual channels. The input at the scored step includes a PM2.5 feature, although cell 9 per-node modulo indexing prevents a reliable claim that it is always the same physical hour. Source: A and cited code, seed 42, commit and timestamp in section 0.

**Dataset, masks, physics and training.** Custom cell 9 `TierAwareClusterDatasetV3` samples starts by integer stride, returns `[12,N,16]` features, fills the final-step target from `station_pm25/TARGET_SCALE` for matching node IDs, and uses 0 for absent targets. `WeightedRandomSampler` targets 35% unsupervised physics samples; library `DataLoader` uses batch size 1 with four train/two validation workers. The supervision mask in cell 13:93-95 is `graph.train_mask & (abs(target)>1e-8)`; validation uses all nodes when `part.val_mask is None` (cell 13:204-210), but zero targets are excluded. The mask does not inspect observation provenance. Source: A, R and cited code, seed 42, commit and timestamp in section 0.

Custom cell 7:24-49 calculates source→destination bearings `atan2(dy,dx)`, reverses by 180°, and selects edges whose wrapped angular difference from `xb[0,0,0,6]` is at most `75°/2=37.5°`. Channel 6 is scaled wind direction, yet the mask treats it as degrees. The exact custom cell 13:41-58 physics penalty is `mean(relu((p_dst-p_src) * sigmoid(sum_k(edge_attr_k/1000)))²)` over selected edges. **Q=0 implicitly; no emission Q term or physical Q units are implemented.** The sigmoid is applied to the sum of all 16 edge attributes, including one-hot road flags. Total station-batch loss is masked normalized-target MSE plus `lambda(epoch)*penalty`; physics-only batches use the penalty alone. `lambda(epoch)=0.06*min(1,epoch/25)` (cell 13:64-68). With `max_epochs=15`, the scheduled maximum actually reached would be 0.036; the saved best checkpoint records epoch 2. Library AdamW uses lr 3e-6 and weight decay 0.01, CUDA AMP/GradScaler, gradient clip norm 0.3, batch size 1, max 15 epochs, and a bad-event LR backoff. Source: A, R and cited code, seed 42, commit and timestamp in section 0.

**Evaluation.** Custom cell 24:28-45 concatenates all validation predictions at graph sensor nodes with nonzero targets, rescales by 342.9356, computes pair-weighted MAE, RMSE and median absolute error. It is a monitored-node metric, not a citywide-node metric or an observed-only metric. Cell 20:93-110 computes PVR on every selected upwind edge across validation batches: `100 * count(p_dst-p_src>0.05) / count(selected edges)`, with threshold 0.05 normalized = 17.14678 µg/m³; Q is absent. R gives 7,301/520,507. Cell 15 reports validation clusters where station targets exist. Cell 16 merges sampled train and validation, so its cluster table is not a holdout table. Cell 17:75-82 compares predictions with zero-filled targets for unmonitored clusters, and lines 116-117 contain hard-coded fallback metrics `46.2134, 47.1082, 0.0124`; those are not measurements. Cell 22 defines custom baseline classes using library `GCNConv`; cell 23 evaluates newly initialized, untrained baselines. Cell 14 Captum IG uses a zero baseline and 25 steps on one validation cluster, then mislabels channels. Cell 21:52 hard-codes the spatial hop-decay curve. Source: A, R and cited code, seed 42, commit and timestamp in section 0.

**Routing and secondary variants.** `scripts/prepare_routing_snapshot.py` imports custom `gnn.stpignn_inference._build_temporal_x_seq`, using raw model-input fields and `graph.x` fallback rather than the notebook's scaled registry, then multiplies by 342.9356 and clips to 0–120 µg/m³. The saved 3,459-edge snapshot is 1.2825–1.6286 µg/m³ (A). The mismatch is a feature-construction difference; missing denormalization is ruled out by this code. The notebook does not define dose-A*, speed, RMV, quotas or matching; those require separate Phase F source audit. The current LOSO script uses hidden size 32, five epochs and lr 3e-4 on a station-subset variant, versus the canonical 96, 15 and 3e-6; no claim of architectural parity is justified yet. Source: A and cited scripts, seed 42, commit and timestamp in section 0.

**Step 1 refactor.** `src/stpignn/legacy_canonical.py` retains the audited dataset, mask, loss, metric and baseline architecture. The notebook imports those functions/classes and `src/stpignn/explain.py`, obtains repository paths from `src/stpignn/paths.py`, and no longer changes process cwd or `sys.path`; cell 17's hard-coded fallback metrics were replaced by missing values. LOSO and ablation import `STPIGNN` from `src.stpignn`; the old routing snapshot imports a clearly marked legacy adapter. New scoring and synchronized timing functions are in `src/stpignn/evaluation.py`. Existing LOSO, ablation and routing feature builders remain legacy implementations and are excluded from the new shared-data comparisons. Source: rewired notebook, `scripts/rewire_canonical_notebook.py`, `scripts/rewire_notebook_explain.py`, and full replay files, seed 42, source commit and timestamps in section 0.

**Step 2 feature and forecast definition.** The available network channels in order are lagged PM2.5, PM10, NO2, SO2, CO, wind speed, gusts, temperature, humidity, surface pressure, sine of wind direction, cosine of wind direction, and SRTM elevation. `results/feature_registry.json` gives raw source column and units for each. Raw meteorological wind FROM direction remains a separate unscaled degree tensor. PBLH, population density, road proximity and traffic index have no input sources and were omitted, with reasons in the registry. `DataV2.window` predicts observed PM2.5 at hour `target_index` from `history_hours=12` ending at `target_index-horizon`; it asserts no input index is later than this cutoff. Own-station lagged PM2.5 is allowed, and `mask_own_history=True` zeroes that channel for the spatial/weather-only variant. Raw observations are the target mask; no nonzero-value proxy or modulo indexing is used. Source: `src/stpignn/data_v2.py`, `results/feature_registry.json`, `configs/data_v2.yaml`, seed 42, source commit and timestamp in section 0.

**Step 3 physics options.** `src/stpignn/physics_v2.py` defines compass bearing clockwise from north for UTM source→destination vectors. Wind FROM 270° transports TO 90°; the toy test selects only an eastbound edge. The corrected mask compares that transport bearing to each edge using a 37.5° half-angle. Legacy mask/penalty remain available as a separate option. The corrected penalty applies `sigmoid(edge_length_m/1000)` only, with no one-hot road flags in the sum; graph Laplacian is a separate squared-gradient control. Q is defined as `max(0, coefficient_ug_m3_per_index) * max(0, traffic_index) / target_scale_ug_m3` in normalized units, but the Q variant raises `MissingTrafficIndex` because no traffic-index source exists. `pvr_statistics` uses the same selected edges and optional Q margin at normalized thresholds 0, 0.01, 0.05 and 0.1, and reports their µg/m³ equivalents from the active train-fitted target scale. The corrected and legacy aligned-hour masks disagree on 51.9684% of the directed station edges on average over 1,961 validation target hours; mean selected fractions are 25.4479% and 26.6667%, respectively. The legacy comparison reconstructs the master feature's scaled wind direction by a fitted linear conversion; it is not an exact replay of the notebook's modulo-misaligned time inputs. Source: `results/physics_v2_mask_summary.json`, `results/wind_mask_coverage_v2.csv`, `scripts/analyze_physics_v2.py`, `configs/data_v2.yaml`, seed 42, source commit and 2026-10-24 14:10 UTC timestamp.

**Step 4 trained comparison.** Custom `src/stpignn/models_v2.py` wraps the canonical `gnn.model.STPIGNN` as a 13-input, 96-hidden, two-GINE-layer plus GRU model on a 15-station directed four-nearest-neighbour graph. It also defines library `torch_geometric.nn.GCNConv` two-layer Vanilla GCN (last input hour), GCN plus `torch.nn.GRUCell` on each of 12 input hours, and a graph-free `torch.nn.GRU`. `scripts/train_gate_v2.py` uses library AdamW, 0.01 weight decay, 512 target-hour batches, gradient clip 0.3, fp32 deterministic algorithms, 2-epoch validation-only LR/target-transform sweep and at most 5 final epochs with patience 2. The LR grid is 3e-6, 1e-5, 3e-5, 1e-4 and 3e-4. All final runs use train-fitted log1p targets; corrected, legacy-mask and Laplacian penalties use `lambda=0.06*min(1,epoch/25)`. At epoch 5 this is 0.012. The imputed-target variant weights non-observed training targets at 0.25 but is evaluated only on raw observed targets. The no-own-PM2.5 variant zeros channel 0 throughout the input history. All models use the same observed validation/test pairs. This is station-subgraph training, not a full 154,902-node citywide retrain; five epochs do not establish convergence. Validation-selected rates are in `results/neural_selection_v2.csv`, per-epoch training/validation curves in `results/neural_curves_v2.csv`, and checkpoints in `results/checkpoints_v2/`. Source: these results, `scripts/train_gate_v2.py`, configs, seeds, commits and timestamps in section 0.

Custom `scripts/evaluate_baselines_v2.py` computes last-observed own-station persistence, train-fitted hour-of-day × day-of-week climatology, station train mean, inverse-square IDW from other stations at input time, and library scikit-learn 1.6.1 `Ridge` on meteorology/static inputs. `src/stpignn/evaluation.py:evaluate_arrays` computes pooled and station MAE, RMSE, R², bias, nMAE and median AE on the same observed-target mask. `scripts/evaluate_legacy_checkpoint_v2.py` separately maps the 13 rebuilt features to the legacy checkpoint's 16 slots using full-period master scaling and a 15-node station graph with zero road flags. This is a diagnostic adapter with changed graph/features; its metric is not a like-for-like citywide checkpoint evaluation. `scripts/summarize_gate_v2.py` selects one ST-PIGNN variant and seed on validation MAE, then applies a paired 2,000-replicate UTC-day bootstrap on the test pairs. Source: result files and run metadata listed in section 0.

**A0.2 draft-claim alignment.**

| Draft item | Verdict against canonical notebook | Exact source |
|---|---|---|
| SRTM elevation C1 | DISAGREES | Cell 5:23-35, 49-57; cell 14:87-91 |
| Q loss C2 | DISAGREES | Cell 13:41-58, 105-117 |
| Chronological leak-free C3 | DISAGREES (timestamp ranges disjoint only) | Cell 5:49-77; cell 9:98-123 |
| 75-degree cone | AGREES as **full** cone; half-angle 37.5° | Cell 7:34, 44-50; cell 20:14, 39-45 |
| 64 clusters | AGREES | Cell 0:70; cell 2:64-72 |
| Hidden size 96 | AGREES | Cell 0:71-72; cell 11:22-29 |
| Learning rate 3e-6 | AGREES | Cell 0:64; cell 11:32-36 |
| Lambda maximum 0.06 | AGREES as configured ceiling, not reached in 15 epochs | Cell 0:65,75; cell 13:64-68 |
| 12-hour window | AGREES as 12 sampled rows; DISAGREES with strict lag-only forecast | Cell 0:68; cell 9:98-123 |
| MAE/RMSE/median/PVR definitions | AGREES with formulas above; DISAGREES with observed-only or all-citywide interpretation | Cell 24:28-45; cell 20:93-110 |

Source: canonical notebook source at commit above; R confirms execution, seed 42 and timestamp in section 0.

## 4. Results tables

| Phase A replay item | Value |
|---|---:|
| Scored nonzero station-node/hour pairs | 308 |
| ST-PIGNN MAE / RMSE / median AE, µg/m³ | 53.1382408 / 89.1050748 / 30.6010437 |
| Predicted mean / SD / minimum / maximum, µg/m³ | 46.96875 / 9.1015625 / 28.8125 / 75.75 |
| Target mean / SD / minimum / maximum, µg/m³ | 71.43016 / 85.01051 / 1.66667 / 373.61926 |
| Pearson prediction–target correlation | -0.0204456 |
| PVR violations / active edges / percent | 7,301 / 520,507 / 1.4026709% |

source: `results/replay_canonical.json`, produced by `scripts/replay_canonical.py`; notebook config, seed 42, source commit and 2026-10-22 20:42:30 UTC timestamp in the JSON. The stored notebook output differs by seven PVR violations; no value was adjusted to force agreement. An earlier replay in this session counted 7,304 violations before its result file was overwritten, indicating run-to-run numerical sensitivity despite seed 42. The retained file is the source for the table.

| Step 1 full replay | Value |
|---|---:|
| Scored pairs / active edges | 308 / 520,507 |
| Deterministic fp32 MAE / RMSE, µg/m³ | 53.1334686 / 89.1250458 |
| Deterministic fp32 violations / PVR | 7,304 / 1.4032472% |
| Repeat fp32 difference in MAE, RMSE, violations | 0 / 0 / 0 |
| Difference from retained Phase A replay, MAE / RMSE / PVR percentage points | -0.0047722 / +0.0199710 / +0.0005764 |

source: `results/full_replay_parity.json`, `results/replay_rewired_fp32_run1.json`, `results/replay_rewired_fp32.json`, produced by `scripts/check_full_replay_parity.py` and `scripts/replay_canonical.py`; seed 42, fp32 and deterministic algorithms, base commit `f84633e`, 2026-10-24 13:52 UTC parity timestamp. The full-replay gate passed its stated tolerances. AMP evaluation still changes a few near-threshold PVR edge decisions; fp32 repeats were identical.

| Step 2 observed-only data, horizon 1 | Train | Validation | Test |
|---|---:|---:|---:|
| Scored target hours | 14,210 | 1,961 | 4,063 |
| Scored station-hour pairs | 32,867 | 7,204 | 14,623 |
| Observed target mean, µg/m³ | 746.7087 | 25.1827 | 54.1253 |
| Observed target maximum, µg/m³ | 647,953 | 794 | 6,816.9575 |

source: `results/splits_v2.json`, `results/data_v2_diagnostics.json`, produced by `scripts/build_data_v2.py` and `scripts/diagnose_data_v2.py`; config `configs/data_v2.yaml`, seed 42, commits/timestamps in section 0. Train mean includes the raw extreme readings.

| Step 4 preliminary test baseline | Pairs | MAE, µg/m³ | RMSE, µg/m³ | R² | Bias, µg/m³ | nMAE |
|---|---:|---:|---:|---:|---:|---:|
| Persistence | 14,623 | 21.261102 | 177.317266 | -0.192012 | 0.282816 | 0.392813 |
| Hour/day climatology | 14,623 | 392.031114 | 536.533600 | -9.913710 | 353.313718 | 7.243029 |
| Station train mean | 14,623 | 1,791.916082 | 3,619.446891 | -495.664343 | 1,758.895601 | 33.106812 |
| IDW known stations at input time | 14,623 | 356.371231 | 1,667.627276 | -104.432995 | 311.970743 | 6.584190 |
| Ridge on meteorology/static features | 14,623 | 2,088.573262 | 2,266.730370 | -193.795218 | 2,047.594357 | 38.587745 |

source: `results/baselines_v2_metrics.csv`, produced by `scripts/evaluate_baselines_v2.py`; config `configs/gate_v2.yaml` and `configs/data_v2.yaml`, seed 42, source commit `3802c23651777bb5cd472d748d590ca30fdb14d6`, run 2026-10-24 14:15 UTC. Full pair predictions are in `results/baselines_v2_predictions.parquet`, per-station rows in the metrics CSV. Persistence used its fixed train-mean fallback for 6 pairs, IDW for 1,037 pairs (`results/baselines_v2_run.json`). This is the required baseline report before neural training; the gate verdict awaits trained models.

| Step 4 trained model, same 14,623 observed test pairs | Seeds | MAE mean±SD, µg/m³ | RMSE mean±SD, µg/m³ | R² mean±SD |
|---|---:|---:|---:|---:|
| GRU only | 5 | 30.127329±0.143700 | 162.103406±0.398411 | 0.003758±0.004902 |
| Vanilla GCN | 5 | 30.097257±0.218846 | 162.660735±0.058575 | -0.003100±0.000722 |
| ST GRU-GCN | 5 | 31.369975±0.964364 | 162.793239±0.357185 | -0.004738±0.004413 |
| ST-PIGNN legacy mask/loss | 5 | 30.235636±0.161479 | 161.679976±0.234212 | 0.008959±0.002872 |
| ST-PIGNN corrected mask/loss, observed only | 5 | 30.214535±0.315297 | 161.668441±0.413062 | 0.009097±0.005068 |
| ST-PIGNN Laplacian control | 5 | 30.240379±0.184926 | 161.585571±0.388508 | 0.010113±0.004755 |
| ST-PIGNN corrected plus 0.25-weight imputed training targets | 5 | 31.055491±0.677617 | 161.057199±0.276106 | 0.016578±0.003372 |
| ST-PIGNN corrected, own PM2.5 history zeroed | 5 | 31.298549±0.273053 | 162.262725±0.145603 | 0.001803±0.001792 |

source: `results/neural_summary_v2.csv`, `results/neural_final_v2.csv`, produced by `scripts/train_gate_v2.py` and `scripts/summarize_gate_v2.py`; `configs/gate_v2.yaml` and `configs/data_v2.yaml`, seeds 11/23/37/51/79, source commit `89a6d6e`, 2026-10-24 14:54:47 UTC final-run timestamp. Per-station rows are in `results/neural_per_station_v2.csv`; per-pair outputs and curves are also retained.

| Validation-selected ST-PIGNN gate, 14,623 test pairs | MAE, µg/m³ | RMSE, µg/m³ | R² |
|---|---:|---:|---:|
| Persistence | 21.261102 | 177.317266 | -0.192012 |
| Hour/day climatology | 392.031114 | 536.533600 | -9.913710 |
| Corrected plus imputed targets, seed 37 | 30.584854 | 161.285796 | 0.013787 |

Paired ST-PIGNN minus persistence MAE difference is +9.323752 µg/m³, 95% UTC-day bootstrap CI [+7.535600,+10.784741]; R² difference +0.205799, CI [+0.047942,+0.419453]. The model beats climatology on MAE and R², but it does not beat persistence on MAE; the specified gate **FAILS**. The legacy checkpoint diagnostic adapter scores MAE 39.415929, RMSE 167.628466, R² -0.065305 on these pairs. Source: `results/gate_persistence.md`, `results/gate_bootstrap_v2.json`, `results/legacy_checkpoint_v2_metrics.csv`; produced by `scripts/summarize_gate_v2.py` and `scripts/evaluate_legacy_checkpoint_v2.py`, configs, seed/commit/timestamps in section 0.

| Corrected-mask test PVR, threshold | Corrected ST-PIGNN mean±SD | GRU-only mean±SD | ST GRU-GCN mean±SD |
|---|---:|---:|---:|
| 0 normalized / 0 µg/m³ | 45.48484±1.03588% | 45.33400±0.72124% | 47.06217±3.66755% |
| 0.01 / 102.3727 µg/m³ | 0% | 0% | 0% |
| 0.05 / 511.8636 µg/m³ | 0% | 0% | 0% |
| 0.1 / 1,023.7271 µg/m³ | 0% | 0% | 0% |

source: `results/pvr_gate_v2.csv`, produced by `scripts/evaluate_pvr_gate_v2.py`; `configs/gate_v2.yaml` and `configs/data_v2.yaml`, seeds 11/23/37/51/79, commit `57f3e80`, 2026-10-24 14:56:38 UTC. Corrected test mask has 58,339 active directed edge-hours among 243,780 candidate edge-hours. The train-fitted normalization is 10,237.2715 µg/m³, so the legacy normalized 0.05 threshold is 511.8636 µg/m³ here, not 17.1. Full legacy/corrected masks, all models and thresholds, exact counts and positive-gradient statistics are in the CSV. Q rows cannot be calculated without a measured traffic index.

LOSO, full ablation, routing, corrected IG, calibration diagnostics and figures remain unrun pending the user's Step 5 instruction. Stored untrained notebook baseline output remains documented in section 1 and is not substituted into this table.

## 5. Figures

No Phase A figure was generated. The notebook's existing PNG figure cells are not treated as fresh experimental evidence. Phase I targets remain architecture source, cluster map with stations, prediction field, decay, PVR/gradient, per-station accuracy, LOSO and routing distributions, all with axes and units.

## 6. Claim verdicts

| Claim | Phase A verdict | Deciding evidence |
|---|---|---|
| C1 SRTM elevation in training and IG | CONTRADICTED | No elevation among 16 training inputs; channel 5 is wind speed. |
| C2 Q in training loss | CONTRADICTED | No Q in cell 13 penalty. |
| C3 chronological and leak-free | CONTRADICTED | Full-period feature preprocessing, modulo indexing, target-step PM2.5 input. |
| C4 physics improves accuracy by 15.0% | CONTRADICTED for Step 4 comparison | Corrected ST-PIGNN mean MAE 30.214535 vs trained GRU-GCN 31.369975 and GRU-only 30.127329; no 15.0% gain. |
| C5 physics improves PVR | UNTESTED as a causal claim | At zero threshold corrected ST-PIGNN 45.48484% vs GRU-only 45.33400%; no matched no-physics ST-PIGNN control in this gate. |
| C6 higher PVR due to baseline over-smoothing | UNTESTED | No gradient/smoothness controls. |
| C7 each ablation component necessary | UNTESTED | Canonical checkpoint and ablation are not matched. |
| C8 inductive spatial generalization | CONTRADICTED for cited MAE; UNTESTED on rebuilt model | Canonical 308 pairs and Step 4's 14,623 test pairs are at mapped training stations, not held-out locations. |
| C9 worst-cluster calibration fault | UNTESTED | No fault diagnostics. |
| C10 elevation attribution is terrain | CONTRADICTED | IG's elevation label maps to wind speed channel. |
| C11 routing dose/time benefit | UNTESTED | Saved routing field is 1.2825–1.6286 µg/m³; no independent rerun. |
| C12 matching stability and welfare optimality | UNTESTED | No feasibility or blocking-pair audit. |
| C13 ST-PIGNN lower inference latency | UNTESTED | Baseline timers use unsynchronized CUDA calls and untrained models. |
| C14 23 stations, 15 mapped nodes, 15 clusters consistent | CONTRADICTED | Graph mask 23, model-input mapped nodes 22, populated clusters 15. |

source: A and R for canonical claims, plus `results/neural_summary_v2.csv`, `results/pvr_gate_v2.csv`, and `results/gate_bootstrap_v2.json` for Step 4 claims; producing scripts, configs, seeds, source commits and UTC timestamps are in section 0 and beside the section 4 tables.

## 7. Open issues and BLOCKERS

1. **A0.4 legacy boundary remains partial:** The notebook imports the extracted legacy methods, and repeated deterministic fp32 full replay passes parity (`results/full_replay_parity.json`). Existing secondary LOSO, ablation and routing data builders remain different and must not be pooled with data_v2 results. The notebook still contains relative `citywide_stpignn_best.pt` literals, and `src.stpignn` re-exports custom `gnn.model.STPIGNN` rather than owning its class source. All new Step 2–4 experiments use `src/stpignn/data_v2.py`, `src/stpignn/models_v2.py` and `src/stpignn/evaluation.py`; full Step 1.1 unification of secondary scripts is unfinished. Source: `rg` audit of notebook and named scripts, source commit `57f3e80`, 2026-10-24; see reproduction command in section 8.
2. Canonical notebook side effects: cell 0 changes cwd and `sys.path`, seeds global RNGs and selects global device; cells 2/5/7/9 mutate global partitions and feature registries, read full-period hard-coded Parquets, and use nearest-node timeline substitution; cell 13 overwrites stable and best checkpoints on training or interrupt; cell 14 sets model weights `requires_grad=False`; cells 16/17/18/19/21 write CSVs or figures outside `results/`; cell 17 hard-codes fallback metrics. `scripts/replay_canonical.py` executes only setup and evaluation cells and writes to `results/`, avoiding notebook training/output side effects. Explicit data-context arguments in `src/stpignn/canonical.py` remove globals from the extracted dataset. Remaining side effects await full wiring.
3. The checkpoint stores config, epoch and a June embedded timestamp, but no elevation source, Q flag, fit interval, split dates or raw-data hash. Filesystem mtime is 2026-10-16 17:35 UTC, not the embedded run time. It cannot prove the exact original data artifact from metadata alone. Source: A, seed 42, source commit and timestamp in section 0.
4. The master Parquet contains full-period derived imputation, including bidirectional interpolation and full-period climatology; no train-only fit is documented. The fixed 342.9356 scale has no recorded fitting source. The canonical cell's `pm2_5_scaled` input is not time-aligned to global scored timestamps by a join. These defects block leak-free scientific claims until Phase B rebuilds data.
5. The routing input builder and notebook have different input schemas and scale regimes. Routing code already multiplies by 342.9356 and clips at 120; concentration range cannot be repaired by applying that multiplier again. Phase F must wait for a validated feature-equivalent inference path.
6. Table-1 row counts 60,752 and 594,974 are now identified as raw all-pollutant rows in 2022 and 2025; the derived-gapfill count 1,073,807 and master count 1,070,203 still differ, and the transformation responsible for 3,604 rows has not been proven.
7. Step 2 has no PBLH, population-density, road-proximity or traffic-index source. These channels are absent rather than duplicated. The corrected-Q training variant cannot run until traffic data with documented units exists; its code raises an explicit error. Raw train PM2.5 includes 212 values above 10,000 µg/m³ and a maximum of 647,953; their validity has not been established, and all unfiltered metrics must be interpreted as calculations on those raw observations. Source: `results/feature_registry.json`, `results/data_v2_diagnostics.json`, scripts/config/seed/commit/timestamps in section 0.
8. Step 4 trained only the 15-station subgraph for up to five epochs. There is no full-city retraining or demonstrated convergence. All five-seed corrected ST-PIGNN variants missed persistence on test MAE. The Q penalty and with-Q PVR remain blocked by missing measured traffic. The large train-only target SD makes normalized thresholds 0.01/0.05/0.1 correspond to 102.37/511.86/1,023.73 µg/m³ and yields nearly all-zero thresholded PVR despite 45% zero-threshold positive gradients. Source: `results/neural_final_v2.csv`, `results/pvr_gate_v2.csv`, run metadata, scripts/configs/seeds/commits/timestamps in section 0.

## 8. Reproduction commands

From the repository root on the audited source commit and data snapshot:

```sh
python scripts/audit_canonical.py
python scripts/check_canonical_refactor_parity.py
python scripts/replay_canonical.py
python -m scripts.replay_canonical --deterministic-fp32
python -m scripts.check_full_replay_parity
python -m scripts.build_data_v2
python -m scripts.diagnose_data_v2
python -m scripts.analyze_physics_v2
python -m scripts.evaluate_baselines_v2
python -m scripts.train_gate_v2 --stage selection
python -m scripts.train_gate_v2 --stage selection --models stpignn_no_own_pm25
python -m scripts.train_gate_v2 --stage final
python -m scripts.evaluate_legacy_checkpoint_v2
python -m scripts.summarize_gate_v2
python -m scripts.evaluate_pvr_gate_v2
python -m pytest tests/test_data_v2.py tests/test_physics_v2.py
rg -n 'os\.chdir|sys\.path|/home/jupyter|citywide_stpignn_best|STPIGNN|from gnn' scripts/evaluate_station_lso.py scripts/stpignn_ablation_dem.py scripts/prepare_routing_snapshot.py scripts/evaluate_routing_gs.py src/stpignn notebooks/production/evaluated_wind_advection.ipynb
```

The scripts write the artifacts named beside each table. Step 4's persistence gate failed; Steps 5 onward have not been run.

### Step 4b-A — audited cleaning and rebuilt observed targets

The old gap-fill path dropped null rows and averaged station-hour duplicates but did not document a PM2.5 outlier ceiling. Its saved `y_clean` transformation has no writer in the permitted source files. On the raw-to-old-master join, 208 of 212 raw training station-hours above 10,000 µg/m³ remained old observed-tier rows; four were marked imputed. The documented static graph PM2.5 feature cap is [0,500] µg/m³ (`scripts/build_graph_tensors.py:154-165`); the cleaned forecast variant rejects raw PM2.5 rows outside that range before grouping, imputation, input-history construction and train-only fitting. This transfers a graph-feature bound to targets and is a recorded design choice, not an inferred old target rule. `results/cleaning_counts_v2.csv` counts 887 raw train PM2.5 rows rejected above 500. The cleaned h=1 observed scored pairs are 32,628 train, 7,203 validation and 14,583 test. Cleaned train observed mean/SD/max are 34.135868/22.993734/493.0 µg/m³. Among 55,034 overlapping raw station-hours, old `y_clean` and v2 observed truth disagree on 41,290; this includes missingness and value differences, and does not establish the undocumented transform. Source: `results/old_filtering_audit.md`, `results/old_vs_raw_pm25.csv`, `results/cleaning_counts_v2.csv`, `results/splits_v2.json`, `results/cleaning_compare_v2.json`; produced by `scripts/audit_old_cleaning.py`, `scripts/build_data_v2.py`, `scripts/summarize_cleaning_v2.py`, config `configs/data_v2.yaml`, seed 42, source commit `748472042a59e910aa8924185638fab2cc236894`, UTC timestamps 2026-10-24 15:42:27/15:42:28/15:53:48 respectively. Ten cleaning/data/physics tests passed; raw output: `results/codex_log/runs/gate_a_tests.log`.

### Step 4b-B — cleaned h=1 persistence gate

On the same 14,583 observed test station-hours, persistence MAE/R² is 8.116095 µg/m³ / 0.532089; IDW is 22.698642 / −0.205856; validation-selected corrected ST-PIGNN (short budget, seed 23) is 20.613632 / 0.001594. The five-seed short-budget corrected ST-PIGNN mean±SD MAE is 20.723163±0.131595 µg/m³; the separate five-seed 20-epoch diagnostic mean±SD is 20.689290±0.219278. Paired UTC-day bootstrap (2,000 replicates) for selected short ST-PIGNN minus persistence gives MAE +12.497537 µg/m³ [11.797404,13.163366] and R² −0.530495 [−0.595027,−0.466313]; versus IDW it gives MAE −2.085010 [−3.013297,−1.192179] and R² +0.207449 [0.153649,0.261566]. Thus the primary matched-budget model beats IDW but not persistence on both test MAE and R². Ridge used only weather/static feature indices 5–12. Full five-seed and longer-budget rows, curves, and paired results are in `results/gate_v2b.csv`, `results/gate_v2b.md`, `results/neural_curves_v2b.csv`, and `results/gate_v2b_bootstrap.json`. Source: `scripts/evaluate_baselines_v2.py`, `scripts/train_gate_v2.py`, `scripts/summarize_gate_v2b.py`; configs `configs/data_v2.yaml` and `configs/gate_v2b.yaml`; seeds 11/23/37/51/79, bootstrap seed 4301; neural source commit `4261e2e` and baseline/summary source commit `3688c6e`, UTC summary timestamp 2026-10-24 16:42:58. Prior uncleaned Step 4 files were not overwritten.

### Step 4b-C: cleaned LOSO (2026-10-24 18:21:10 UTC)

Source: `scripts/evaluate_loso_v2.py`, `configs/loso_v2.yaml`, seeds 11/23/37, source commit `e90fd05d7837bea5f99d9c91d3d3758649710386`; raw outputs `results/loso_summary_v2.csv`, `results/loso_per_station_v2.csv`, `results/loso_decision_v2.json`, `results/loso_fallbacks_v2.csv`, `results/loso_predictions_v2.parquet`. Each method scored the same 14,583 observed held-out (station,hour) pairs in 11 scorable folds. Four of 15 mapped stations (5547, 5548, 6975, 2498781) had zero observed test targets and could not be scored. Fold-specific imputation and scaling excluded the held-out station. Neural entries below average predictions across the three fixed seeds per pair.

| Method | Pooled MAE (µg/m³) | Pooled R² |
|---|---:|---:|
| ST-PIGNN, known-station lagged readings | 22.283 | -0.050 |
| ST-PIGNN, weather/static only | 21.215 | -0.065 |
| GRU-only | 21.271 | -0.073 |
| IDW | 22.633 | -0.204 |
| GP with fixed RBF kernel | 24.123 | -0.227 |
| Ordinary kriging, per-hour fitted spherical variogram | 22.588 | -0.197 |
| Nearest-known-station persistence | 26.604 | -0.518 |
| Pooled known-station train mean | 20.634 | -0.085 |
| Ridge, weather/static only | 20.594 | 0.073 |

The predeclared known-station ST-PIGNN versus best spatial baseline (ordinary kriging) comparison is TIE: paired UTC-day bootstrap (2,000 replicates) MAE difference -0.305 µg/m³, 95% CI [-1.164, 0.608]; R² difference +0.147, 95% CI [0.098, 0.192]; station Wilcoxon p=0.278 over 11 scored stations. Ordinary kriging used its train-mean fallback on 5,163/14,583 pairs, GP on 2,428, and IDW on 1,037. The four absent test folds and these fallback rates limit the spatial-generalization claim. No LOSO hyperparameter was changed after test scores.

Individual-seed pooled metrics are in `results/loso_seed_summary_v2.csv`, produced by `scripts/summarize_loso_seeds_v2.py` at 2026-10-24 18:27:49 UTC from `configs/loso_v2.yaml` seeds 11/23/37 and source commit `a08e1e8`; this is distinct from the equal-seed-mean predictions in the table above.

## Step 4g: bounded final round, W1 stop (2026-10-25 08:29 UTC)

Source: `scripts/input_fix_v2g.py`, `configs/data_v2.yaml`, seed 42, source commit `006ba94`, run 2026-10-25T08:29:06 UTC; data and scores in `results/data_v2g_arrays.npz`, `results/input_channels_v2g.csv`, and `results/input_fix_v2g.json`. The imputed PM2.5 and lag PM10 channels were capped at 500 µg/m³. The PM2.5 lag uses the target's training-fitted log1p mean and SD. PM10 uses its own training-fitted log1p mean and SD.

| Train input channel | Mean (µg/m³) | SD (µg/m³) | Max (µg/m³) |
|---|---:|---:|---:|
| PM2.5 lag | 33.418804 | 17.420805 | 500.000000 |
| PM10 lag | 69.129753 | 27.378576 | 500.000000 |

| h=1 test method | MAE (µg/m³) | R² |
|---|---:|---:|
| Train-only AR-with-lag | 11.894099 | 0.374211 |
| Persistence | 8.116094 | 0.532089 |

AR-with-lag has 46.5% higher MAE than persistence after the input repair. This triggers the fixed W1 stop rule; a remaining alignment bug is possible. W2–W8 were not run, and no additional horizons, model comparisons, or criteria are claimed. S4 was already completed and pushed at `006ba94`; its known-station ST-PIGNN MAE/R² is 24.766141/-0.328158 versus ordinary kriging 22.588024/-0.197255, verdict LOSS (`scripts/evaluate_loso_v2c.py`, `configs/loso_v2.yaml`, seeds 11/23/37, source commit `1e4c78d`, `results/loso_summary_v2c.csv`).
