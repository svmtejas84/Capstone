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

### Step 4g W2 h=1 checkpoint (2026-10-25 09:30 UTC)

Source: `scripts/benchmark_v2g.py`, `scripts/summarize_benchmark_v2g.py`, `configs/benchmark_v2g.yaml`, seeds [11,23,37,51,79], original source commit `d2ce207`, corrected reference/report source commit `aa5044c`. The fixed four-LR validation search and five-seed final runs cover all 12 neural methods at h=1. Test scoring uses all 14,583 observed targets; only training and validation selection require an observed immediate lag. Full rows, parameter counts, training time and paired UTC-day 2,000-bootstrap results are in `results/benchmark_runs_v2g.csv`, `results/horizon_curve_v2g.csv`, `results/benchmark_v2g.md` and `figures/horizon_curve.pdf`. The initial Ridge and original-penalty/Laplacian reference outputs were preserved as provisional files and corrected before this table.

| h (hours) | Test method | MAE (µg/m³) | R² |
|---:|---|---:|---:|
| 1 | Persistence | 8.116095 | 0.532089 |
| 1 | Same-hour-yesterday | 14.130312 | 0.283173 |
| 1 | A: GINE+GRU+wind | 8.056366 | 0.547921 |
| 1 | B: adaptive graph ST | 8.025968 | 0.543357 |
| 1 | C: ST-PIGNN v2 transport+source | 9.320887 | 0.546394 |
| 1 | Original penalty ST-PIGNN | 8.018825 | 0.585597 |

At h=1, A and B meet the fixed win rule: paired UTC-day test MAE differences against persistence are -0.059730 (95% CI [-0.093491,-0.024862]) and -0.090127 ([-0.111708,-0.068875]) µg/m³, and both also beat same-hour-yesterday with intervals excluding zero. C does not meet the physics-in-architecture criterion against its four specified controls. Other horizons remain queued; this checkpoint is not the final horizon conclusion.

### Step 4g W2 h=6 checkpoint (2026-10-25 09:51 UTC)

Source: `scripts/benchmark_v2g.py`, `scripts/summarize_benchmark_v2g.py`, `configs/benchmark_v2g.yaml`, seeds [11,23,37,51,79], source commit `a2596c8`. All 12 neural methods and five references were scored on the same 14,583 observed test targets; full parameter counts, times and paired-day intervals are in `results/benchmark_runs_v2g.csv` and `results/benchmark_v2g.md`.

| h (hours) | Test method | MAE (µg/m³) | R² |
|---:|---|---:|---:|
| 6 | Persistence | 16.606891 | -0.161368 |
| 6 | Same-hour-yesterday | 14.130312 | 0.283173 |
| 6 | A: GINE+GRU+wind | 15.780365 | 0.130968 |
| 6 | B: adaptive graph ST | 15.127259 | 0.125511 |
| 6 | C: ST-PIGNN v2 transport+source | 16.406056 | 0.068911 |
| 6 | Original penalty ST-PIGNN | 14.840548 | 0.183055 |

At h=6 no A/B/C method beats both persistence and same-hour-yesterday. This is an interim horizon statement; h=24, 3 and 12 remain queued.

### Step 4g W2 h=24 checkpoint (2026-10-25 10:07 UTC)

Source: `scripts/benchmark_v2g.py`, `scripts/summarize_benchmark_v2g.py`, `configs/benchmark_v2g.yaml`, seeds [11,23,37,51,79], source commit `ac40419`. All 12 neural methods and five references were scored on 14,583 observed test targets; full rows and UTC-day bootstrap intervals are in `results/benchmark_v2g.csv`/`.md` and the vector `figures/horizon_curve.pdf`.

| h (hours) | Test method | MAE (µg/m³) | R² |
|---:|---|---:|---:|
| 24 | Persistence | 14.130312 | 0.283173 |
| 24 | Same-hour-yesterday | 14.130312 | 0.283173 |
| 24 | A: GINE+GRU+wind | 14.038469 | 0.389258 |
| 24 | B: adaptive graph ST | 13.657661 | 0.400369 |
| 24 | C: ST-PIGNN v2 transport+source | 14.754175 | 0.357254 |
| 24 | Original penalty ST-PIGNN | 13.788623 | 0.374789 |

B meets the fixed win rule at h=24: paired UTC-day ΔMAE against both persistence and same-hour-yesterday is -0.472651 µg/m³, 95% CI [-0.774896,-0.195378]. C does not meet the physics-in-architecture criterion in the priority-horizon summary. h=3 and 12 remain queued.

### Step 4g W2 h=3 checkpoint (2026-10-25 12:52 UTC)

Source: `scripts/benchmark_v2g.py`, `scripts/summarize_benchmark_v2g.py`, config `configs/benchmark_v2g.yaml`, seeds [11,23,37,51,79], source commit `e0fd782`. All 12 neural methods and five references were scored on 14,583 observed test targets. Full parameter counts, train times, and paired UTC-day intervals are in `results/benchmark_runs_v2g.csv` and `results/benchmark_v2g.md`.

| h (hours) | Test method | MAE (µg/m³) | R² |
|---:|---|---:|---:|
| 3 | Persistence | 13.244358 | 0.100938 |
| 3 | Same-hour-yesterday | 14.130312 | 0.283173 |
| 3 | A: GINE+GRU+wind | 12.966157 | 0.151948 |
| 3 | B: adaptive graph ST | 13.053448 | 0.128142 |
| 3 | C: ST-PIGNN v2 transport+source | 13.685781 | 0.225417 |
| 3 | Original penalty ST-PIGNN | 12.310651 | 0.303082 |

A and B meet the fixed win rule at h=3; C does not meet the physics-in-architecture criterion. h=12 remains queued.

### Step 4g W6 LOSO (2026-10-25 13:14 UTC)

Source: `scripts/evaluate_loso_v2g.py`, `configs/gate_v2c.yaml`, Gate C seeds [11,23,37], source commit `3a1a8c3`. Both neural anchors use fold-isolated training and last-30-train-day blend/bias fits. Full paired UTC-day bootstrap intervals and per-fold rows are in `results/loso_summary_v2g.csv`, `results/loso_decision_v2g.csv`, and `results/loso_per_station_v2g.csv`. S4 LOSO LOSS is retained unchanged.

| Anchor | Adaptive graph ST | GINE+GRU+wind | Original ST-PIGNN |
|---|---|---|---|
| Train-fold mean | LOSS | TIE | LOSS |
| Train-mean/IDW blend | TIE | TIE | LOSS |
| Train-fold mean, train-tail bias adjusted | TIE | LOSS | TIE |
| Blend, train-tail bias adjusted | LOSS | LOSS | TIE |

No neural method meets the fixed LOSO WIN rule. Lower test R² than the best baseline blocks WIN for the bias-adjusted methods even where paired MAE improves.

### Step 4g W2 h=12 and final W5 criteria (2026-10-25 13:30 UTC)

Source: `scripts/benchmark_v2g.py`, `scripts/summarize_benchmark_v2g.py`, config `configs/benchmark_v2g.yaml`, seeds [11,23,37,51,79], source commit `3a1a8c3`. All 12 neural methods and five references were scored on 14,583 observed targets at h=12. Full parameter counts, training times, paired UTC-day intervals, and all five horizons are in `results/benchmark_runs_v2g.csv`, `results/benchmark_v2g.csv`/`.md`, `results/horizon_curve_v2g.csv`, and `figures/horizon_curve.pdf`.

| h (hours) | Test method | MAE (µg/m³) | R² |
|---:|---|---:|---:|
| 12 | Persistence | 19.105561 | -0.456901 |
| 12 | Same-hour-yesterday | 14.130312 | 0.283173 |
| 12 | A: GINE+GRU+wind | 17.372966 | 0.030026 |
| 12 | B: adaptive graph ST | 17.356680 | -0.059821 |
| 12 | C: ST-PIGNN v2 transport+source | 18.239329 | -0.101382 |
| 12 | Original penalty ST-PIGNN | 15.637205 | 0.138050 |

Final fixed criteria: A and B meet the win rule at h=1 and h=3, and B also at h=24; neither meets it at h=6 or h=12. C physics-in-architecture support is not met at any horizon. W3 DEM criterion remains not run because the five-hour limit elapsed.

## Step 4g-2 (2026-10-25 13:42 UTC)

Saved W2 predictions were used to append all 60 paired UTC-day 2,000-bootstrap MAE intervals and their widths to `results/benchmark_v2g.md`; no model was retrained. Source `scripts/append_benchmark_intervals_v2g.py`, config `configs/benchmark_v2g.yaml`, seeds [11,23,37,51,79], source commit `cf20056`.

| h (hours) | Model minus persistence ΔMAE (µg/m³) | 95% CI (µg/m³) | CI width (µg/m³) |
|---:|---|---:|---:|
| 24 | Adaptive graph ST: -0.472651 | [-0.774896, -0.195378] | 0.579518 |
| 24 | Original ST-PIGNN: -0.341689 | [-0.846439, +0.151647] | 0.998086 |

These are nominal intervals across 60 model-horizon-reference comparisons; no multiplicity adjustment was applied. W7 is running; W3, W4 and W8 follow.

## Step 4h: deviation 6 bounded round

Generated 2026-11-04T15:27:55.624456+00:00 from script `scripts/append_step4h_v2h.py` at source commit `62f0df18622aef4a6fe51c35a439200a0225c0f4`. This generation timestamp and commit apply to each source line below; study-specific source commits are also shown. All model selection used validation or fixed training choices; no test-driven horizon, fold, station or seed exclusion. Earlier results are unchanged.

### W7 physics weight check

Source `scripts/lambda_sweep_v2g.py`, config `configs/benchmark_v2g.yaml`, seeds [11,23,37,51,79], source commit `7f19982cc238fd09324c44e9cfd099dc5d9d4dca`, 2,000 paired UTC-day bootstrap draws; Step 4h check at the commit and time above.

All five horizons [1,3,6,12,24] are present. The original ST-PIGNN has one nominal hit (h=6, λ=0.06, about -0.28 µg/m³ versus λ=0); it is not replicated at another horizon or weight. There are 25 original-model and 25 Laplacian positive-weight comparisons. Laplacian findings are a separate control and do not count as support for the original physics penalty.

### Protocol-inflation analysis

Source `scripts/protocol_inflation_v2h.py`, stored P0/P1/P2/P3/P4 result files, h=1 for comparable point gains; no retraining. P4 paired UTC-day interval is from `results/benchmark_v2g.md`.

| Level | ST-PIGNN MAE | Gain vs strongest baseline | Gain vs persistence | Headline |
|---|---:|---:|---:|---|
| P0 | 53.140 | 9.370 | NA | P0: nominal 9.37 gain vs reported untrained ST GRU-GCN; paired validity unverified |
| P1 | 30.585 | -9.324 | -9.324 | P1: no gain versus persistence on raw observed targets |
| P2 | 20.723 | -12.607 | -12.607 | P2: no gain versus persistence after 0-500 cleaning |
| P3 | 8.259 | -0.143 | -0.143 | P3: no gain versus persistence after lag and residual correction |
| P4 | 8.019 | 0.097 | 0.097 | P4: h=1 point gain 0.097 but paired-day CI includes zero; h=3 win is reported separately |

P0 nominal gain uses the notebook-reported untrained ST GRU-GCN MAE 62.51 versus checkpoint replay 53.14; same-pair baseline predictions and persistence are unavailable, so paired validity is unverified. P4 h=1 nominal gain is 0.097 µg/m³, but its paired-day CI crosses zero; h=3 has a separate supported win.

### W4 held-out station density

Source `scripts/lowdata_v2h.py`, config `configs/benchmark_v2g.yaml`, five fixed draw/model seeds [11,23,37,51,79], source commit `01a87a0`; full draw rows and spread in `results/sensor_density_v2h.csv`, vector figure `figures/sensor_density.pdf`.

| Horizon | Method | Train stations | Held-out MAE mean ± SD | R² mean ± SD | Draws |
|---:|---|---:|---:|---:|---:|
| 1 | adaptive_graph_st | 3 | 19.866 ± 4.006 | -0.092 ± 0.068 | 5 |
| 1 | adaptive_graph_st | 5 | 20.670 ± 4.393 | -0.091 ± 0.015 | 5 |
| 1 | gru_only | 3 | 19.651 ± 3.860 | -0.063 ± 0.042 | 5 |
| 1 | gru_only | 5 | 20.517 ± 4.351 | -0.063 ± 0.023 | 5 |
| 1 | ridge_lag_weather | 3 | 21.088 ± 3.285 | -0.251 ± 0.078 | 5 |
| 1 | ridge_lag_weather | 5 | 22.188 ± 3.970 | -0.232 ± 0.078 | 5 |
| 1 | stpignn_lambda0 | 3 | 19.831 ± 3.910 | -0.083 ± 0.067 | 5 |
| 1 | stpignn_lambda0 | 5 | 20.507 ± 4.303 | -0.067 ± 0.013 | 5 |
| 1 | stpignn_original | 3 | 19.848 ± 3.889 | -0.083 ± 0.055 | 5 |
| 1 | stpignn_original | 5 | 22.177 ± 6.001 | -0.180 ± 0.168 | 5 |
| 24 | adaptive_graph_st | 3 | 19.907 ± 3.921 | -0.074 ± 0.050 | 5 |
| 24 | adaptive_graph_st | 5 | 20.735 ± 3.947 | -0.067 ± 0.028 | 5 |
| 24 | gru_only | 3 | 19.730 ± 3.681 | -0.053 ± 0.027 | 5 |
| 24 | gru_only | 5 | 20.422 ± 4.173 | -0.030 ± 0.017 | 5 |
| 24 | ridge_lag_weather | 3 | 21.071 ± 2.869 | -0.244 ± 0.141 | 5 |
| 24 | ridge_lag_weather | 5 | 21.616 ± 3.704 | -0.170 ± 0.103 | 5 |
| 24 | stpignn_lambda0 | 3 | 19.916 ± 3.449 | -0.104 ± 0.065 | 5 |
| 24 | stpignn_lambda0 | 5 | 20.473 ± 4.241 | -0.032 ± 0.045 | 5 |
| 24 | stpignn_original | 3 | 20.178 ± 3.415 | -0.135 ± 0.102 | 5 |
| 24 | stpignn_original | 5 | 21.830 ± 5.361 | -0.156 ± 0.097 | 5 |

Ten-station cases remain BLOCKED because only eight stations have observed-lag training pairs. All scored draw-mean R² values are negative. Different 3- and 5-station draws preclude a causal density interpretation of their mean difference.

### Probabilistic intervals

Source `scripts/conformal_v2h.py`, config `configs/benchmark_v2g.yaml`, source commit `37531f7`, fixed seed 11, LR 3e-4, 10 epochs, train-tail and validation calibration, nominal 80% and 90%, fixed and daily rolling variants, 2,000 paired UTC-day interval-score bootstraps. Validation calibration is exploratory because A/B architecture ranking used validation. Full per-station and per-month coverage is in `results/conformal_station_month_v2h.csv`.

| Horizon | Model | 80% train-tail fixed coverage | Width | Interval score | Value verdict |
|---:|---|---:|---:|---:|---|
| 1 | persistence | 0.675 | 9.942 | 64.741 | NO |
| 1 | same_hour_yesterday | 0.658 | 21.817 | 100.459 | NO |
| 1 | ridge_lag | 0.638 | 10.817 | 65.708 | NO |
| 1 | gru_only | 0.657 | 10.413 | 61.884 | NO |
| 1 | stpignn_original | 0.669 | 10.803 | 60.990 | NO |
| 1 | best_ab | 0.683 | 10.973 | 61.271 | NO |
| 3 | persistence | 0.675 | 17.867 | 102.270 | NO |
| 3 | same_hour_yesterday | 0.658 | 21.817 | 100.459 | NO |
| 3 | ridge_lag | 0.668 | 20.391 | 92.046 | NO |
| 3 | gru_only | 0.674 | 18.582 | 91.827 | NO |
| 3 | stpignn_original | 0.696 | 20.055 | 88.561 | NO |
| 3 | best_ab | 0.655 | 19.096 | 95.422 | NO |
| 6 | persistence | 0.698 | 26.052 | 123.296 | NO |
| 6 | same_hour_yesterday | 0.658 | 21.817 | 100.459 | NO |
| 6 | ridge_lag | 0.691 | 28.333 | 103.706 | NO |
| 6 | gru_only | 0.694 | 25.017 | 106.444 | NO |
| 6 | stpignn_original | 0.700 | 25.827 | 101.628 | NO |
| 6 | best_ab | 0.702 | 25.193 | 104.478 | NO |
| 12 | persistence | 0.716 | 32.595 | 139.200 | NO |
| 12 | same_hour_yesterday | 0.658 | 21.817 | 100.459 | NO |
| 12 | ridge_lag | 0.661 | 29.040 | 115.356 | NO |
| 12 | gru_only | 0.668 | 26.295 | 122.163 | NO |
| 12 | stpignn_original | 0.686 | 27.315 | 108.291 | NO |
| 12 | best_ab | 0.657 | 27.691 | 127.946 | NO |
| 24 | persistence | 0.639 | 20.750 | 101.330 | NO |
| 24 | same_hour_yesterday | 0.639 | 20.750 | 101.330 | NO |
| 24 | ridge_lag | 0.603 | 22.892 | 98.830 | NO |
| 24 | gru_only | 0.643 | 22.517 | 93.624 | NO |
| 24 | stpignn_original | 0.655 | 23.594 | 92.179 | NO |
| 24 | best_ab | 0.668 | 23.850 | 91.742 | NO |
| pooled | best_ab | 0.673 | 21.361 | 96.172 | NO |
| pooled | gru_only | 0.667 | 20.565 | 95.188 | NO |
| pooled | persistence | 0.680 | 21.441 | 106.167 | NO |
| pooled | ridge_lag | 0.652 | 22.295 | 95.129 | NO |
| pooled | same_hour_yesterday | 0.654 | 21.604 | 100.633 | NO |
| pooled | stpignn_original | 0.681 | 21.519 | 90.330 | NO |

No model meets the fixed criterion at any horizon or nominal level; coverage is outside ±5 points of nominal in the primary train-tail fixed analysis. Rolling daily updates improve coverage but do not change the verdict.

### Group-DRO station-attribute LOSO

Source `scripts/loso_groupdro_v2h.py`, `configs/data_v2.yaml`, `configs/benchmark_v2g.yaml`, five-seed source commit `e4e2305`, seeds [11,23,37,51,79], 15 folds, 2,000 paired UTC-day bootstraps. Static embedding fields available at every station: SRTM elevation and projected UTM x/y coordinates, standardized using known training stations per fold. No station ID enters the embedding. η ∈ {0.01,0.1} chosen by validation MAE. ERM uses the same backbone; both use the train-fold mean residual anchor. W6 train-mean/IDW blend results remain separately in `results/loso_summary_v2g.csv`.

| Method | MAE | R² | Best baseline | Baseline MAE | Baseline R² | Paired MAE 95% CI | Verdict |
|---|---:|---:|---|---:|---:|---:|---|
| ERM | 21.320 | -0.135 | ridge_weather_static | 20.594 | 0.073 | [0.143, 1.293] | LOSS |
| group-DRO | 21.356 | -0.148 | ridge_weather_static | 20.594 | 0.073 | [0.210, 1.324] | LOSS |

Four zero-test-target folds remain unscored: [5547, 5548, 6975, 2498781]. Per-station MAE and R² appear in `results/loso_station_predictability_v2h.csv`.

### W3 SRTM terrain ablation

Source `scripts/dem_study_v2h.py`, config `configs/benchmark_v2g.yaml`, control-list source commit `212cbcd`, seeds [11,23,37,51,79], five terrain shuffle seeds [4201,4202,4203,4204,4205], 2,000 paired UTC-day bootstrap draws. Per-station SRTM values verified against `nodes_elevation_true.parquet` in `results/dem_station_values_v2h.csv`.

SRTM elevation versus northing Pearson correlation: 0.368.

| Horizon | Model | Control | SRTM minus control MAE | 95% CI |
|---:|---|---|---:|---:|
| 1 | adaptive_graph_st | srtm_minus_none | -0.015 | [-0.019, -0.010] |
| 1 | adaptive_graph_st | srtm_minus_northing_only | -0.014 | [-0.019, -0.009] |
| 1 | adaptive_graph_st | srtm_minus_shuffled_mean | -0.015 | [-0.020, -0.011] |
| 1 | adaptive_graph_st | srtm_minus_shuffle_1 | -0.031 | [-0.038, -0.024] |
| 1 | adaptive_graph_st | srtm_minus_shuffle_2 | -0.011 | [-0.015, -0.007] |
| 1 | adaptive_graph_st | srtm_minus_shuffle_3 | -0.010 | [-0.014, -0.006] |
| 1 | adaptive_graph_st | srtm_minus_shuffle_4 | -0.013 | [-0.017, -0.008] |
| 1 | adaptive_graph_st | srtm_minus_shuffle_5 | -0.016 | [-0.021, -0.011] |
| 1 | gru_only | srtm_minus_none | 0.031 | [0.009, 0.055] |
| 1 | gru_only | srtm_minus_northing_only | 0.050 | [0.027, 0.075] |
| 1 | gru_only | srtm_minus_shuffled_mean | 0.047 | [0.028, 0.068] |
| 1 | gru_only | srtm_minus_shuffle_1 | 0.017 | [-0.009, 0.044] |
| 1 | gru_only | srtm_minus_shuffle_2 | 0.049 | [0.020, 0.081] |
| 1 | gru_only | srtm_minus_shuffle_3 | 0.012 | [-0.013, 0.038] |
| 1 | gru_only | srtm_minus_shuffle_4 | 0.058 | [0.040, 0.078] |
| 1 | gru_only | srtm_minus_shuffle_5 | 0.026 | [0.012, 0.041] |
| 24 | adaptive_graph_st | srtm_minus_none | 0.048 | [-0.010, 0.105] |
| 24 | adaptive_graph_st | srtm_minus_northing_only | 0.190 | [0.070, 0.306] |
| 24 | adaptive_graph_st | srtm_minus_shuffled_mean | 0.070 | [0.000, 0.138] |
| 24 | adaptive_graph_st | srtm_minus_shuffle_1 | 0.024 | [-0.112, 0.158] |
| 24 | adaptive_graph_st | srtm_minus_shuffle_2 | 0.092 | [0.010, 0.172] |
| 24 | adaptive_graph_st | srtm_minus_shuffle_3 | -0.024 | [-0.082, 0.041] |
| 24 | adaptive_graph_st | srtm_minus_shuffle_4 | -0.054 | [-0.123, 0.011] |
| 24 | adaptive_graph_st | srtm_minus_shuffle_5 | 0.059 | [-0.081, 0.194] |
| 24 | gru_only | srtm_minus_none | 0.045 | [-0.011, 0.098] |
| 24 | gru_only | srtm_minus_northing_only | -0.316 | [-0.437, -0.192] |
| 24 | gru_only | srtm_minus_shuffled_mean | 0.010 | [-0.048, 0.065] |
| 24 | gru_only | srtm_minus_shuffle_1 | -0.087 | [-0.190, 0.013] |
| 24 | gru_only | srtm_minus_shuffle_2 | -0.063 | [-0.146, 0.022] |
| 24 | gru_only | srtm_minus_shuffle_3 | -0.111 | [-0.174, -0.047] |
| 24 | gru_only | srtm_minus_shuffle_4 | 0.054 | [-0.001, 0.108] |
| 24 | gru_only | srtm_minus_shuffle_5 | -0.059 | [-0.166, 0.039] |

W3 h=1 DEM criterion for validation-best adaptive_graph_st: MET across the fixed controls.
W3 h=24 DEM criterion for validation-best adaptive_graph_st: NOT MET across the fixed controls.

### W8 citywide input precheck

Source `scripts/citywide_precheck_v2h.py`, source commit `dd94737`, no training or seed; full audit and timestamp in `results/citywide_precheck_v2h.md`.

Nodes: 154902.
Distinct weather source points: 1 (12.9716 N, 77.5946 E).
Nodes with stored hourly model-input rows: 22/154902; nodes with no stored temporal model-input data: 154880.
Unique weather series among stored nodes: 18.
Stored nodes whose weather series exactly duplicates another stored node's: 5/22 (22.727273%).
If the single raw weather series were broadcast to all topology nodes, duplicate fraction would be 100.000000%.
Nodes with SRTM elevation: 154902/154902; missing: 0.
Nodes mapped to a station: 23/154902; without a station: 154879.
Nodes with no weather or SRTM data after broadcast: 0.
BLOCKED: a single weather source would give more than 50% identical citywide node series.

The bounded round stops here; no routing, integrated gradients, citywide training or second-city study was run.

## Step 4i — timestamp measurement and fixed-gate city lookup

Source: `scripts/pull_weather.py:26-36,72-95,111-113`; `src/stpignn/data_v2.py:41-47,302-305,320-324`; `results/weather_timestamp_check_v2i.md`; 37,152 hours, 2022-01-01 through 2026-03-28; source commit `84b7f88`, measurement commit `d2ae851`; 2026-11-05 UTC; no seed or training.

| Bengaluru weather timestamp measurement | Value |
|---|---:|
| Open-Meteo request timezone | Asia/Kolkata (UTC+5:30) |
| Raw Parquet index timezone | Naive; no offset metadata |
| First three `2022.parquet` timestamps | 2022-01-01 00:00, 01:00, 02:00 |
| v2 parser assumption for naive weather | UTC; floor to hour |
| Mean 2 m temperature maximum in pipeline clock | 14:00; 28.596°C (13:00: 28.591°C) |
| Expected temperature-peak UTC window | 08:30–10:30 |
| Temperature-peak offset from window midpoint | +4.5 h; hourly empirical proxy |
| Timestamp-label offset from request and parser | +5.5 h |
| Shortwave-radiation nighttime check | Unavailable; column absent |
| Verdict | SHIFT CONFIRMED |

Source: dependency inventory `results/weather_timestamp_check_v2i.md`; data config `configs/data_v2.yaml`; source commit `84b7f88`; 2026-11-05 UTC.

| Stored weather-dependent arrays | Weather-dependent result families |
|---|---|
| `results/data_v2_arrays.npz`, `results/data_v2g_arrays.npz`, fold-local v2 rebuilds | v2/v2b/v2c neural and weather-baseline predictions and gates; W2 benchmark; W7 lambda; W3 DEM; W4 sensor density; W6 LOSO; v2h group-DRO and conformal; protocol-inflation derivative |

Source: `results/second_city_feasibility_v2i.md`, `results/london_station_eligibility_v2i.csv`; [LAQN station/species API](https://api.erg.ic.ac.uk/AirQuality/Information/MonitoringSiteSpecies/GroupName=London/Json), [LAQN annual report API](https://api.erg.ic.ac.uk/AirQuality/Annual/MonitoringReport/SiteCode=BX2/Year=2024/Json), [LAEI 2022](https://data.london.gov.uk/dataset/london-atmospheric-emissions-inventory-laei-2022-2lg5g), [Delhi AQI stations](https://aqi.delhi.gov.in/stations), [IITM SAFAR inventory](https://www.tropmet.res.in/156-event_details), [ERA5](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels?tab=overview), [SRTM](https://www.usgs.gov/centers/eros/science/usgs-eros-archive-digital-elevation-shuttle-radar-topography-mission-srtm-1); access 2026-11-05 UTC; source commit `573668e`; no seed or training.

| Candidate | Eligible reference-grade stations with ≥2 years hourly PM2.5, 2022–2026 | Coverage/network count observed | Licence status | PM2.5 emissions / traffic source | Verified hourly Q | Fixed ≥30-station gate |
|---|---|---|---|---|---|---|
| London | UNKNOWN | LAQN 85 historical PM25 listings; 47 listed for ≥730 days in 2022–2025; 45 with positive annual capture in ≥2 years; 35 with ≥17,520 estimated valid hours from rounded annual capture; instrument method unresolved | LAQN API documentation: OGL v2; LAEI 2022: OGL v3; exact per-extract terms to verify | LAEI 2022: 1-km annual tonnes/year PM2.5 grid and major-road links; LAQN API documents traffic-counter feed | No | UNKNOWN; no training pass |
| Delhi | UNKNOWN | Official live network: 60 stations, 55 reporting in cited snapshot; historical PM2.5 hours/methods unresolved | Delhi AQI: GODL-India; exact raw-repository extract terms unresolved | IITM SAFAR 2018 400-m PM2.5 inventory and 2020 ~0.4-km annual sectoral grid; sampled junction traffic counts | No | UNKNOWN; no training pass |

Source: [ERA5 dataset](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels?tab=overview), DOI 10.24381/cds.adbb2d47, hourly 0.25° and CC-BY; [USGS SRTM 1 Arc-Second Global](https://www.usgs.gov/centers/eros/science/usgs-eros-archive-digital-elevation-shuttle-radar-topography-mission-srtm-1), DOI 10.5066/F7PR7TFT, ~30 m; access 2026-11-05 UTC.

## Step 4j — corrected weather timestamps

All earlier weather-dependent scores remain labelled **shifted weather**. The v2j scores use the confirmed Asia/Kolkata timestamp correction and the fixed half-hour rule: subtract 5 h 30 min from each raw local timestamp, then average the records at UTC h−1:30 and h:30 to represent hour h. The first raw local record (2022-01-01 00:00) becomes 2021-12-31 18:30 UTC; the first complete UTC hour is 19:00. The first model hour (2022-01-01 00:00 UTC) averages 2021-12-31 23:30 and 2022-01-01 00:30. The last six model hours lack a complete pair and use the existing bounded forward fill and train-only fallback. The mean 2 m temperature peaks at **08:00 UTC**.

Source: `src/stpignn/data_v2.py`, `scripts/build_data_v2j.py`, `tests/test_weather_half_hour_v2j.py`; config `configs/data_v2.yaml`, data seed 42; source commit `9dbaabbdd57676c3898c923c80ec782e6c561407`; generated 2026-11-05T16:14:09.150138+00:00.

### Fixed horizon benchmark

The same cleaning bounds (0–500 µg/m³), splits, train-only fitting, imputed-lag indicator, same-space log1p channels, residual output, model families, learning-rate grid, and five seeds were retained. A win requires a lower point test MAE than both persistence and same-hour-yesterday and a paired UTC-day 2,000-replicate MAE CI below zero against each.

| h | Model | Shifted MAE | Shifted R² | Corrected MAE | Corrected R² | Win shifted → corrected |
|---:|---|---:|---:|---:|---:|---|
| 1 | persistence | 8.116 | 0.532 | 8.116 | 0.532 | 0 → 0 |
| 1 | same_hour_yesterday | 14.130 | 0.283 | 14.130 | 0.283 | 0 → 0 |
| 1 | Ridge | 8.692 | 0.566 | 8.706 | 0.570 | 0 → 0 |
| 1 | ST-PIGNN original | 8.019 | 0.586 | 8.026 | 0.585 | 0 → 0 |
| 1 | A | 8.056 | 0.548 | 7.984 | 0.577 | 1 → 1 |
| 1 | B | 8.026 | 0.543 | 7.947 | 0.590 | 1 → 1 |
| 1 | C | 9.321 | 0.546 | 9.530 | 0.526 | 0 → 0 |
| 3 | persistence | 13.244 | 0.101 | 13.244 | 0.101 | 0 → 0 |
| 3 | same_hour_yesterday | 14.130 | 0.283 | 14.130 | 0.283 | 0 → 0 |
| 3 | Ridge | 13.176 | 0.308 | 13.357 | 0.314 | 0 → 0 |
| 3 | ST-PIGNN original | 12.311 | 0.303 | 12.342 | 0.305 | 1 → 1 |
| 3 | A | 12.966 | 0.152 | 12.744 | 0.280 | 1 → 1 |
| 3 | B | 13.053 | 0.128 | 13.052 | 0.130 | 1 → 1 |
| 3 | C | 13.686 | 0.225 | 13.321 | 0.226 | 0 → 0 |
| 6 | persistence | 16.607 | -0.161 | 16.607 | -0.161 | 0 → 0 |
| 6 | same_hour_yesterday | 14.130 | 0.283 | 14.130 | 0.283 | 0 → 0 |
| 6 | Ridge | 15.814 | 0.177 | 16.106 | 0.171 | 0 → 0 |
| 6 | ST-PIGNN original | 14.841 | 0.183 | 14.706 | 0.181 | 0 → 0 |
| 6 | A | 15.780 | 0.131 | 16.026 | 0.122 | 0 → 0 |
| 6 | B | 15.127 | 0.126 | 15.171 | 0.097 | 0 → 0 |
| 6 | C | 16.406 | 0.069 | 15.856 | 0.095 | 0 → 0 |
| 12 | persistence | 19.106 | -0.457 | 19.106 | -0.457 | 0 → 0 |
| 12 | same_hour_yesterday | 14.130 | 0.283 | 14.130 | 0.283 | 0 → 0 |
| 12 | Ridge | 17.396 | 0.084 | 17.390 | 0.085 | 0 → 0 |
| 12 | ST-PIGNN original | 15.637 | 0.138 | 15.509 | 0.142 | 0 → 0 |
| 12 | A | 17.373 | 0.030 | 16.877 | 0.080 | 0 → 0 |
| 12 | B | 17.357 | -0.060 | 16.926 | -0.007 | 0 → 0 |
| 12 | C | 18.239 | -0.101 | 17.664 | -0.000 | 0 → 0 |
| 24 | persistence | 14.130 | 0.283 | 14.130 | 0.283 | 0 → 0 |
| 24 | same_hour_yesterday | 14.130 | 0.283 | 14.130 | 0.283 | 0 → 0 |
| 24 | Ridge | 14.960 | 0.353 | 15.005 | 0.358 | 0 → 0 |
| 24 | ST-PIGNN original | 13.789 | 0.375 | 13.902 | 0.377 | 0 → 0 |
| 24 | A | 14.038 | 0.389 | 14.188 | 0.391 | 0 → 0 |
| 24 | B | 13.658 | 0.400 | 13.744 | 0.396 | 1 → 1 |
| 24 | C | 14.754 | 0.357 | 14.709 | 0.344 | 0 → 0 |

| h | Corrected qualifying models | Any-model win |
|---:|---|---|
| 1 | adaptive_graph_st, gine_gru_wind, gru_only | MET |
| 3 | adaptive_graph_st, adaptive_graph_st_fixed_knn, gine_gru_wind, gru_only, stpignn_lambda0, stpignn_laplacian, stpignn_original | MET |
| 6 | none | NOT MET |
| 12 | none | NOT MET |
| 24 | adaptive_graph_st, st_gru_gcn | MET |

Source: `scripts/benchmark_v2j.py`, `scripts/summarize_benchmark_v2j.py`, `scripts/weather_fix_comparison_v2j.py`; config `configs/benchmark_v2g.yaml`; seeds [11,23,37,51,79], bootstrap seed 4303, 2,000 UTC-day draws; source commit `9dbaabbdd57676c3898c923c80ec782e6c561407`; generated 2026-11-05T16:14:09.150138+00:00. All 85 model/horizon pairs are in `results/weather_fix_comparison_v2j.csv`.

### Leave-one-station-out transfer

All 15 fixed folds were retained; four have zero observed test targets and are reported without a score. Both W6 anchors were evaluated. The fixed W6 WIN/TIE/LOSS rule compares each neural method with the best fixed spatial baseline on paired UTC days.

| Anchor | Neural method | Raw MAE | Raw verdict | Bias-adjusted MAE | Bias-adjusted verdict |
|---|---|---:|---|---:|---|
| train_mean | adaptive_graph_st | 21.342 | LOSS | 21.361 | LOSS |
| train_mean | gine_gru_wind | 20.588 | TIE | 20.717 | LOSS |
| train_mean | gru_only | 21.404 | LOSS | 21.409 | LOSS |
| train_mean | stpignn_original | 22.314 | LOSS | 21.769 | TIE |
| train_mean_idw_blend | adaptive_graph_st | 20.740 | TIE | 20.711 | LOSS |
| train_mean_idw_blend | gine_gru_wind | 20.798 | TIE | 20.956 | LOSS |
| train_mean_idw_blend | gru_only | 21.029 | TIE | 21.010 | LOSS |
| train_mean_idw_blend | stpignn_original | 21.456 | LOSS | 21.114 | LOSS |

Source: `scripts/evaluate_loso_v2j.py`; configs `configs/data_v2.yaml`, `configs/benchmark_v2g.yaml`, `configs/loso_v2.yaml`; seeds [11,23,37], bootstrap seed 4303, 2,000 UTC-day draws; source commit `9dbaabbdd57676c3898c923c80ec782e6c561407`; generated 2026-11-05T16:14:09.150138+00:00. Unscored stations: 5547, 5548, 6975, 2498781. No neural WIN.

### Fixed lambda check and DEM control

Physics helps only when lambda>0 has lower point test MAE than lambda=0 and the paired UTC-day MAE CI excludes zero. The full lambda sweep was not repeated.

| h | Original ST-PIGNN lambda | Test MAE | ΔMAE vs 0 | 95% CI | Helps |
|---:|---:|---:|---:|---|---|
| 1 | 0.00 | 8.052 | 0.000 | [0.000, 0.000] | NOT MET |
| 1 | 0.06 | 8.026 | -0.026 | [-0.049, -0.001] | MET |
| 1 | 0.30 | 8.072 | 0.020 | [-0.008, 0.048] | NOT MET |
| 1 | 1.00 | 8.117 | 0.065 | [0.040, 0.091] | NOT MET |
| 24 | 0.00 | 13.755 | 0.000 | [0.000, 0.000] | NOT MET |
| 24 | 0.06 | 13.967 | 0.211 | [0.026, 0.399] | NOT MET |
| 24 | 0.30 | 14.094 | 0.339 | [0.122, 0.561] | NOT MET |
| 24 | 1.00 | 15.120 | 1.364 | [0.972, 1.801] | NOT MET |

The original physics criterion is MET at h=1 for lambda=0.06 and NOT MET at h=24. The Laplacian control has no qualifying positive-lambda cell at either checked horizon.

| h | Validation-best A/B/C model | SRTM − no terrain ΔMAE | 95% CI | All-control DEM verdict shifted → corrected |
|---:|---|---:|---|---|
| 1 | adaptive_graph_st | -0.148 | [-0.214, -0.082] | 1 → 0 |
| 24 | stpignn_v2 | -0.076 | [-0.146, -0.009] | 0 → 0 |

Both corrected-weather DEM horizons fail the predeclared all-control criterion because the fixed `shuffle_2` control CI includes zero. The earlier shifted-weather h=1 DEM verdict was MET; its h=24 verdict was NOT MET.

Source: `scripts/lambda_check_v2j.py`, `scripts/dem_study_v2j.py`, `scripts/weather_fix_comparison_v2j.py`; config `configs/benchmark_v2g.yaml`; seeds [11,23,37,51,79], fixed lambda grid [0,0.06,0.3,1], shuffle seeds [4201..4205], 2,000 UTC-day draws; source commit `9dbaabbdd57676c3898c923c80ec782e6c561407`; generated 2026-11-05T16:14:09.150138+00:00.
