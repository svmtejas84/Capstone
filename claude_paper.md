# ST-PIGNN executable evidence ledger

## 0. Run log

Phase A0/A audit branch: `audit/canonical-notebook-20261023`. Base source commit for all measurements below: `22a0f5ac5a0527bf173e97692e22c20a245bc6a7`; the Phase A audit commit is recorded in git history. The canonical notebook and checkpoint had pre-existing worktree modifications, so `results/audit_canonical.json` records their exact SHA-256 hashes; the base commit alone does not identify those bytes. Hardware: Tesla V100-PCIE-32GB. Runtime libraries: Python system environment, torch 2.8.0+cu128, torch-geometric 2.6.1, pandas 2.3.3, NumPy 1.26.4, SciPy 1.13.1, scikit-learn 1.6.1. The canonical source is `notebooks/production/evaluated_wind_advection.ipynb`, as clarified by the user. Notebook references below use **zero-based cell numbers and one-based lines within each cell**.

Evidence key A: `results/audit_canonical.json`, produced by `scripts/audit_canonical.py`, fixed config matching notebook cell 0, seed 42, source commit above, run 2026-10-22 20:53 UTC. Evidence key R: `results/replay_canonical.json` and `.log`, produced by `scripts/replay_canonical.py`, notebook cells 0, 2, 5, 7, 9, 11, 20, 24, seed 42, checkpoint `citywide_stpignn_best.pt`, source commit above, run timestamp and runtime in that JSON. Evidence key P: `results/refactor_parity.json`, produced by `scripts/check_canonical_refactor_parity.py`, seed 42, fixed 3-node/12-step toy batch, source commit above, run 2026-10-22 20:44 UTC. All values in this document are direct code measurements or exact constants from the named source. Stored notebook output is identified separately from an independent rerun.

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

The master PM2.5 tiers and per-year/station counts are in `results/audit_imputation_tiers.csv`; 55,089 PM2.5 rows are tier A observed, 9,510 tier B and 239,256 tier C in the full master file. Only 392 training and 63 validation scored timestamp/station pairs are independently confirmed as non-imputed PM2.5 in the master file; the remaining model-input targets have not been verified as observed, including five station IDs absent from master. The notebook's nonzero mask treats them alike. `1,073,807` is the materialized derived-gapfill row count reported by `data/processed/gapfill/station_timeseries_imputation_build_report.md`, whereas the master has 1,070,203 rows. The current draft's Table-1 labels `60,752` and `594,974` are not in the repository and cannot be assigned a denominator from this audit. Source: A and `scripts/audit_canonical.py`, seed 42, source commit and timestamp in section 0.

## 3. Methods as implemented

**Imports and components.** Notebook cell 0 imports custom `gnn.model.STPIGNN` and `shared.physics_config`; other cells use NumPy, pandas, PyTorch, PyTorch Geometric, scikit-learn `KMeans`, SciPy `KDTree` and `griddata`, tqdm, Captum `IntegratedGradients`, and Matplotlib. Versions for installed core libraries are in section 0; Captum and Matplotlib versions were not captured. The model is custom `gnn/model.py:STPIGNN` using library `torch_geometric.nn.GINEConv` (2.6.1), `torch.nn.GRU` (torch 2.8.0), `LayerNorm`, dropout, and linear layers. Cell 11:22-29 instantiates 16 inputs, 16 edge features, spatial/temporal hidden sizes 96/96, two GINE layers and the model defaults of one GRU layer and 0.1 dropout. `gnn.model.STPIGNN._spatial_encode` applies linear node encoding, two residual GINE-MLP/LayerNorm/ReLU/dropout blocks on each time step; `forward` feeds the 12 embeddings per node to GRU and a linear head. The graph edge vector is length in metres followed by 15 one-hot road-category flags (A). Cell 2:64-96 applies library `sklearn.cluster.KMeans(random_state=42,n_init=10)` to projected coordinates, then custom `SpatialPartition` extracts edges wholly inside each of 64 clusters. The saved partition artifact is Python-pickled and needs the notebook class to load. Source: A and notebook cells cited, seed 42, commit and timestamp in section 0.

**Actual feature order.** Cell 5:23-35 sets channels 0–15 as `pm2_5_scaled`, `pm10_scaled`, `nitrogen_dioxide_scaled`, `sulphur_dioxide_scaled`, `carbon_monoxide_scaled`, `wind_speed_10m_scaled`, `wind_direction_10m_scaled`, `wind_gusts_10m_scaled`, `temperature_2m_scaled`, `relative_humidity_2m_scaled`, `surface_pressure_scaled`, `nitrogen_dioxide_scaled`, `sulphur_dioxide_scaled`, `pm2_5_scaled`, `pm10_scaled`, `carbon_monoxide_scaled`. Five are duplicates. Cell 4 has an earlier alternative order, but cell 5 rebuilds and overwrites `FEATURE_COLS_16` and the registry. Library pandas `read_parquet`, `groupby`, `sort_values`; custom notebook cell 5 registry and nearest-node timeline fill (`scipy.spatial.KDTree`). It uses no elevation, population, boundary layer, road proximity or traffic channel. Cell 14:87-91 IG labels therefore do not describe the actual channels. The input at the scored step includes a PM2.5 feature, although cell 9 per-node modulo indexing prevents a reliable claim that it is always the same physical hour. Source: A and cited code, seed 42, commit and timestamp in section 0.

**Dataset, masks, physics and training.** Custom cell 9 `TierAwareClusterDatasetV3` samples starts by integer stride, returns `[12,N,16]` features, fills the final-step target from `station_pm25/TARGET_SCALE` for matching node IDs, and uses 0 for absent targets. `WeightedRandomSampler` targets 35% unsupervised physics samples; library `DataLoader` uses batch size 1 with four train/two validation workers. The supervision mask in cell 13:93-95 is `graph.train_mask & (abs(target)>1e-8)`; validation uses all nodes when `part.val_mask is None` (cell 13:204-210), but zero targets are excluded. The mask does not inspect observation provenance. Source: A, R and cited code, seed 42, commit and timestamp in section 0.

Custom cell 7:24-49 calculates source→destination bearings `atan2(dy,dx)`, reverses by 180°, and selects edges whose wrapped angular difference from `xb[0,0,0,6]` is at most `75°/2=37.5°`. Channel 6 is scaled wind direction, yet the mask treats it as degrees. The exact custom cell 13:41-58 physics penalty is `mean(relu((p_dst-p_src) * sigmoid(sum_k(edge_attr_k/1000)))²)` over selected edges. **Q=0 implicitly; no emission Q term or physical Q units are implemented.** The sigmoid is applied to the sum of all 16 edge attributes, including one-hot road flags. Total station-batch loss is masked normalized-target MSE plus `lambda(epoch)*penalty`; physics-only batches use the penalty alone. `lambda(epoch)=0.06*min(1,epoch/25)` (cell 13:64-68). With `max_epochs=15`, the scheduled maximum actually reached would be 0.036; the saved best checkpoint records epoch 2. Library AdamW uses lr 3e-6 and weight decay 0.01, CUDA AMP/GradScaler, gradient clip norm 0.3, batch size 1, max 15 epochs, and a bad-event LR backoff. Source: A, R and cited code, seed 42, commit and timestamp in section 0.

**Evaluation.** Custom cell 24:28-45 concatenates all validation predictions at graph sensor nodes with nonzero targets, rescales by 342.9356, computes pair-weighted MAE, RMSE and median absolute error. It is a monitored-node metric, not a citywide-node metric or an observed-only metric. Cell 20:93-110 computes PVR on every selected upwind edge across validation batches: `100 * count(p_dst-p_src>0.05) / count(selected edges)`, with threshold 0.05 normalized = 17.14678 µg/m³; Q is absent. R gives 7,301/520,507. Cell 15 reports validation clusters where station targets exist. Cell 16 merges sampled train and validation, so its cluster table is not a holdout table. Cell 17:75-82 compares predictions with zero-filled targets for unmonitored clusters, and lines 116-117 contain hard-coded fallback metrics `46.2134, 47.1082, 0.0124`; those are not measurements. Cell 22 defines custom baseline classes using library `GCNConv`; cell 23 evaluates newly initialized, untrained baselines. Cell 14 Captum IG uses a zero baseline and 25 steps on one validation cluster, then mislabels channels. Cell 21:52 hard-codes the spatial hop-decay curve. Source: A, R and cited code, seed 42, commit and timestamp in section 0.

**Routing and secondary variants.** `scripts/prepare_routing_snapshot.py` imports custom `gnn.stpignn_inference._build_temporal_x_seq`, using raw model-input fields and `graph.x` fallback rather than the notebook's scaled registry, then multiplies by 342.9356 and clips to 0–120 µg/m³. The saved 3,459-edge snapshot is 1.2825–1.6286 µg/m³ (A). The mismatch is a feature-construction difference; missing denormalization is ruled out by this code. The notebook does not define dose-A*, speed, RMV, quotas or matching; those require separate Phase F source audit. The current LOSO script uses hidden size 32, five epochs and lr 3e-4 on a station-subset variant, versus the canonical 96, 15 and 3e-6; no claim of architectural parity is justified yet. Source: A and cited scripts, seed 42, commit and timestamp in section 0.

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

Main comparisons, five-seed LOSO, ablations, PVR/smoothness thresholds, hyperparameter sweep, routing outcomes, corrected IG, and calibration diagnostics have **no Phase A measured result**. Stored untrained baseline output is documented in section 1, not inserted into a trained-model comparison table. Later phases must use one shared evaluator, corrected observed-only masks, common splits and checkpoint lineage. Phase C's station-subset architecture and its hidden size/epoch/lr differences must be explicit in its CSV.

## 5. Figures

No Phase A figure was generated. The notebook's existing PNG figure cells are not treated as fresh experimental evidence. Phase I targets remain architecture source, cluster map with stations, prediction field, decay, PVR/gradient, per-station accuracy, LOSO and routing distributions, all with axes and units.

## 6. Claim verdicts

| Claim | Phase A verdict | Deciding evidence |
|---|---|---|
| C1 SRTM elevation in training and IG | CONTRADICTED | No elevation among 16 training inputs; channel 5 is wind speed. |
| C2 Q in training loss | CONTRADICTED | No Q in cell 13 penalty. |
| C3 chronological and leak-free | CONTRADICTED | Full-period feature preprocessing, modulo indexing, target-step PM2.5 input. |
| C4 physics improves accuracy by 15.0% | UNTESTED | Baseline is untrained in canonical notebook. |
| C5 physics improves PVR | UNTESTED | No trained matched no-physics control. |
| C6 higher PVR due to baseline over-smoothing | UNTESTED | No gradient/smoothness controls. |
| C7 each ablation component necessary | UNTESTED | Canonical checkpoint and ablation are not matched. |
| C8 inductive spatial generalization | CONTRADICTED for cited MAE | All 308 scored pairs are at mapped station nodes. |
| C9 worst-cluster calibration fault | UNTESTED | No fault diagnostics. |
| C10 elevation attribution is terrain | CONTRADICTED | IG's elevation label maps to wind speed channel. |
| C11 routing dose/time benefit | UNTESTED | Saved routing field is 1.2825–1.6286 µg/m³; no independent rerun. |
| C12 matching stability and welfare optimality | UNTESTED | No feasibility or blocking-pair audit. |
| C13 ST-PIGNN lower inference latency | UNTESTED | Baseline timers use unsynchronized CUDA calls and untrained models. |
| C14 23 stations, 15 mapped nodes, 15 clusters consistent | CONTRADICTED | Graph mask 23, model-input mapped nodes 22, populated clusters 15. |

source: A and R, produced by scripts in section 0, seed 42, source commit and timestamps there.

## 7. Open issues and BLOCKERS

1. **A0.4 incomplete:** `src/stpignn/` now contains importable direct ports of canonical model, dataset, mask, penalty and scoring. Fixed-batch parity passes (`results/refactor_parity.json`, P). The notebook and all secondary scripts have **not** yet been rewired to import it, so a unified end-to-end refactor has not been verified. Later phases must not begin training until wiring and full replay parity are complete. The existing `gnn.model` architecture is already importable.
2. Canonical notebook side effects: cell 0 changes cwd and `sys.path`, seeds global RNGs and selects global device; cells 2/5/7/9 mutate global partitions and feature registries, read full-period hard-coded Parquets, and use nearest-node timeline substitution; cell 13 overwrites stable and best checkpoints on training or interrupt; cell 14 sets model weights `requires_grad=False`; cells 16/17/18/19/21 write CSVs or figures outside `results/`; cell 17 hard-codes fallback metrics. `scripts/replay_canonical.py` executes only setup and evaluation cells and writes to `results/`, avoiding notebook training/output side effects. Explicit data-context arguments in `src/stpignn/canonical.py` remove globals from the extracted dataset. Remaining side effects await full wiring.
3. The checkpoint stores config, epoch and a June embedded timestamp, but no elevation source, Q flag, fit interval, split dates or raw-data hash. Filesystem mtime is 2026-10-16 17:35 UTC, not the embedded run time. It cannot prove the exact original data artifact from metadata alone. Source: A, seed 42, source commit and timestamp in section 0.
4. The master Parquet contains full-period derived imputation, including bidirectional interpolation and full-period climatology; no train-only fit is documented. The fixed 342.9356 scale has no recorded fitting source. The canonical cell's `pm2_5_scaled` input is not time-aligned to global scored timestamps by a join. These defects block leak-free scientific claims until Phase B rebuilds data.
5. The routing input builder and notebook have different input schemas and scale regimes. Routing code already multiplies by 342.9356 and clips at 120; concentration range cannot be repaired by applying that multiplier again. Phase F must wait for a validated feature-equivalent inference path.
6. The user's requested Table-1 source labels 60,752 and 594,974 are unavailable in repository code/data reports. The derived-gapfill count 1,073,807 and master count 1,070,203 differ; the transformation responsible for 3,604 rows has not been proven.

## 8. Reproduction commands

From the repository root on the audited source commit and data snapshot:

```sh
python scripts/audit_canonical.py
python scripts/check_canonical_refactor_parity.py
python scripts/replay_canonical.py
```

The scripts write `results/audit_canonical.json`, `results/stations.csv`, `results/audit_imputation_tiers.csv`, `results/refactor_parity.json`, `results/replay_canonical.json` and `results/replay_canonical.log`. Phase A ends here. Phases B–I require the full A0.4 wiring and data/split repairs above before their requested experiments can be compared with this checkpoint.
