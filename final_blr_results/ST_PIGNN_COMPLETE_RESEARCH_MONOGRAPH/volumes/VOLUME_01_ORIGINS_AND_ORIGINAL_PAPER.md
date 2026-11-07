# Volume 1 — Origins and the recoverable original paper

<a id="volume-01"></a>

## Editorial reconstruction and evidentiary boundary

The earliest recoverable implementation is the production notebook and its imported `gnn/model.py`, not the unavailable submitted PDF. The paper's title and selected numerical claims are supplied by the author, but its ten pages, exact figures, captions, equations and references cannot be verified. Historical claims of MAE 53.14 µg/m³ for ST-PIGNN, 75.35 for GCN, 62.51 for GRU-GCN and PVR 1.404% must therefore remain historical assertions until the PDF and its source table are transferred. The notebook is a different sort of evidence: it establishes what code existed, including 64 road partitions, a 16-channel GINE–GRU, a direct normalized output and a legacy directional hinge. It cannot establish that the submitted prose accurately represented those operations. The recovered old checkpoint strictly loads, but target-hour input, duplicated pollutant channels, modulo timeline lookup and sparse station supervision invalidate an observed-only, issue-time-safe full-road accuracy interpretation. The corrected station model is a later, distinct experiment. [EVIDENCE: v2q recovery | final_blr_results/citywide_extension/v2q/ORIGINAL_MODEL_ARCHITECTURE.md | repository snapshot 1c46a4b]

## Full round-specific source exhibits

The exhibits reproduce the cited local reports as source evidence. Their original round-specific conclusions may be narrower than later findings; read the editorial reconstruction and final synthesis before treating one exhibit as the final verdict.

## Source exhibit 1: `final_blr_results/ieee_paper_evidence/source_registry/MANUSCRIPT_SOURCE_REGISTER.md`

[EVIDENCE: `final_blr_results/ieee_paper_evidence/source_registry/MANUSCRIPT_SOURCE_REGISTER.md` | SHA-256 `ec94ea64280fd2212ed0f18a846c3a6b8eb191f4e134a0e100f11088c0a83470` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Manuscript and source register

Expected historical file: `ST_PIGNN_IEEE_Big_Data_Conf(2).pdf`; not found in the repository or the checked home-directory search. No verified repository copy located. Exact manuscript quotations, figure/page mapping, and reference-by-reference correction therefore remain UNVERIFIABLE pending transfer through the repository's normal file-transfer mechanism.

The rejected manuscript title supplied by the author is “Spatio-Temporal Physics-Informed Graph Neural Networks to aid Urban Toxicity Navigation for Vulnerable Commuters”. Its claims are historical only. `claude_paper.md` and other adjacent drafts are not treated as the supplied PDF.

Expected reviews: four IEEE BigData 2026 reviews and two IEEE DELCON 2026 reviews. Full texts are absent. Matrices list issue topics supplied in the task and actual counter-evidence, but reviewer assignment and exact wording are intentionally blank/pending.

Primary verified internal sources are the frozen v2j–v2r reports, raw saved summary/prediction tables where available, Git commit `a5b396da3f41c2d626ba072e8cec1a0ee15d383d` (package start), and linked artifact paths in the experiment register.

Chronological experiment inventory: `CHRONOLOGY.md`; machine-readable register: `EXPERIMENT_SOURCE_REGISTER.csv`.

## Source exhibit 2: `final_blr_results/citywide_extension/v2q/ORIGINAL_NOTEBOOK_RECOVERY.md`

[EVIDENCE: `final_blr_results/citywide_extension/v2q/ORIGINAL_NOTEBOOK_RECOVERY.md` | SHA-256 `6c2799de855437b55e83a4f67216039dec0f929cc6a2ebd51305181e21ff6cbf` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Original production notebook recovery

Source: `notebooks/production/evaluated_wind_advection.ipynb`, SHA-256 `242d0cf3d2f95c78a011841ed2aec2e100cc8c326e6211c918a8bd70504b8161`, inspected statically on 2026-11-06. It has 26 code cells, zero Markdown cells, and zero saved outputs or execution counts. Cell indices here are zero based. Historical audit used a different notebook hash (`0c2f...`) and therefore supports the extracted implementation and checkpoint, not byte-for-byte execution of today's notebook. No cell was executed in this recovery.

| Component | Found? | Original code location | Reusable? | Limitation |
|---|---|---|---|---|
| OSM topology and indexed coordinates | Yes | cell 2; `data/processed/graph/topology_graph_pyg_inference.pt`, node map, `data/graphs/bangalore_utm_nodes.parquet` | Directly as topology | 154,902 road nodes are not monitors; graph does not encode air transport. |
| 64 KMeans partitions | Yes | cells 2–3; `src/stpignn/legacy_canonical.py:SpatialPartition` | With corrections | 7,134 cross-partition message arcs omitted; no halo equivalence. |
| GINE–GRU model | Yes | cell 11 imports `src.stpignn.STPIGNN`; source `gnn/model.py:STPIGNN` | Historical architecture | 16 duplicated channels, direct one-step output, distinct from corrected 18-channel model. |
| Node-hour input builder | Yes | cells 4–5, 9; `TierAwareClusterDatasetV3` in `legacy_canonical.py` | Historical only | 22/154,902 temporal node series; cell 5 copies entire nearest series to 154,880 nodes; modulo indexing destroys calendar alignment. |
| Wind mask and penalty | Yes | cells 7, 13, 20; `legacy_canonical.py` | Audit only | Uses first node's scaled wind-direction channel as degrees; reverse-bearing mask and hinge are heuristics, not conservation. |
| Training and checkpoint save | Yes | cells 0, 9, 11, 13 | Historical replay | Input window's last hour equals supervised target hour; no forecast lead, zero targets treated as missing; checkpoint epoch 2. |
| Checkpoint load | Yes | cells 14–17, 20; `gnn/checkpoint.py` | Historical replay | Root `citywide_stpignn_best.pt` loads strictly (16 input/16 edge, 96 hidden, 2 GINE, 98,497 parameters); not corrected v2j weights. |
| Full-road inference/plots | Partial | cells 17–19, 24 | Technical demonstration only | Partition outputs use copied inputs and lost boundary arcs; cell 19 averages across validation times, so maps are not forecast snapshots. |
| Captum IG | Yes | cell 14; `src/stpignn/explain.py` | With corrections | Zero baseline and duplicate feature names; target wrapper/quality require separate audit. |
| Navigation/routing | External | `gnn/stpignn_inference.py`, `scripts/prepare_routing_snapshot.py` | Historical only | Static fallback and unvalidated edge concentrations; notebook itself contains no routing optimizer. |

The notebook **contains road-partition model training and forward passes**, but **does not establish a scientifically valid full-road forecasting pathway**. The graph has 154,902 nodes; supervised loss is at 23 snapped `train_mask` nodes and actual temporal rows cover 22 nodes. Cell 5's nearest-neighbor *timeline copying* fills the rest. Cell 9 sets target time to `t_start + 11` while input spans `t_start..t_start+11`; the pollutant input at the target hour can therefore expose the target. These are methodological blockers, not missing software conveniences. No replacement architecture may reuse these input rules.

Surviving root best checkpoint SHA-256 `7f4bc65f0aaba920f2269a1b385b7c408b5c3e2ce7855233af9a8523ca2cdd3f` loads strictly via `gnn/checkpoint.py`. Historical `results/replay_canonical.json` reports a 75.97 s V100 replay, 308 scored validation pairs, MAE 53.138 µg/m³ and near-zero negative correlation; this is an **audited historical replay**, not a new independent v2q forecast validation. `results/audit_canonical.json` records 22 temporal node IDs, 23 graph sensor-mask nodes and 15 partitions with temporal source rows. The current notebook file differs from the older audit hash, so exact saved-cell-output reproduction is unavailable.

## Source exhibit 3: `final_blr_results/citywide_extension/v2q/ORIGINAL_MODEL_ARCHITECTURE.md`

[EVIDENCE: `final_blr_results/citywide_extension/v2q/ORIGINAL_MODEL_ARCHITECTURE.md` | SHA-256 `875d64aa56f83a0a38a1858e6f633e3666cdd4d047e8fd7ecb88f38f37f3a2a0` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Original model architecture and target semantics

`gnn/model.py:STPIGNN` is the source imported by notebook cell 0/11 through `src.stpignn`. A 16→96 linear node encoder is followed at each of 12 input times by two residual GINEConv blocks (96 hidden, 16 edge channels, LayerNorm/ReLU/dropout). A single 96-unit GRU runs per node across those spatial embeddings; a linear 96→1 head gives a **direct** normalized scalar `[batch,nodes]`. There is no residual forecast anchor, attention, road-edge output head or multi-horizon head. Root best checkpoint strictly loads with 98,497 parameters; global config sets 15 maximum epochs, λ max 0.06 and `TARGET_SCALE=342.9356`. Saved epoch is 2.

Road edge attributes are length plus 15 highway indicators from the processed PyG topology. The 16 temporal channels in cells 4–5 are eleven scaled pollutant/weather fields plus five **duplicated pollutant fields**, not sixteen distinct measurements. `master_scaled_checkpoint.parquet` has 17 station IDs, while `model_input_node_hourly_features.parquet` has 22 node IDs. Cell 9 uses `station_pm25 / TARGET_SCALE` as the direct target; it fills missing target with zero and then masks zeros. This is not the corrected log1p-compatible residual transformation.

`TierAwareClusterDatasetV3` creates an input window through hour `t_start+11` and the target at that same hour. Its `t_curr % node_registry.shape[0]` lookup can wrap a station timeline and is not timestamp alignment. The physics mask in cell 7 compares reverse edge bearing to a channel-6 value taken at node zero; channel 6 is scaled wind direction, so it is not verified as degrees. `compute_wind_advection_penalty` applies a length/edge-attribute-scaled directed hinge. No mass conservation or Gaussian plume equation is enforced by notebook cell 13.

Training batches are 64 spatial partitions with station-supervised or physics-only modes. This is training over *road graph partitions with copied sparse-source inputs*, not training on observed PM2.5 at all road nodes. Cells 15–17 score only station-mask nodes. Cell 19 generates 64 cluster maps by averaging partition predictions over validation times; it does not serialize timestamped full-city forecasts. Cross-partition arcs are lost.

## Source exhibit 4: `final_blr_results/citywide_extension/v2q/ORIGINAL_NOTEBOOK_DEPENDENCY_MAP.md`

[EVIDENCE: `final_blr_results/citywide_extension/v2q/ORIGINAL_NOTEBOOK_DEPENDENCY_MAP.md` | SHA-256 `e8ebae89f26da32dfb96d1022f70971c3eca840ac5b21b74cb97da83199c30fd` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Notebook dependency map (zero-based cell indices)

| Cells | Imports / source | External data or output | Risk / status |
|---|---|---|---|
| 0–1 | NumPy, pandas, torch, `src.stpignn`, `gnn.model`, `shared.physics_config` | root checkpoint saver | Configuration and save function; no saved outputs. |
| 2–3 | sklearn KMeans, `legacy_canonical.SpatialPartition` | topology PyG, node map, OSM UTM nodes | Geometry/topology valid; partitions drop boundary arcs. |
| 4–6 | pandas, `scipy.spatial.KDTree` | master scaled Parquet | Cell 5 supersedes cell 4 and copies complete pollutant timelines to missing nodes. |
| 7–8 | torch, legacy wind-mask port | partition edge bearings | First-node scaled wind direction later passed as degrees. |
| 9–10 | `legacy_canonical.TierAwareClusterDatasetV3`, DataLoader | model-input node-hour Parquet | Same-hour input/target and modulo timelines. |
| 11–12 | `gnn.model.STPIGNN` | graph edge dimension | 16×16 GINE–GRU checkpoint compatible. |
| 13 | legacy penalty and metric ports | `citywide_stpignn_{checkpoint_STABLE,best}.pt` | Training and checkpoint overwrite; do not execute. |
| 14 | Captum IG, `src.stpignn.explain` | best checkpoint | Historical explainability only. |
| 15–17 | sklearn metrics, torch | best checkpoint, CSV reports | Scores monitoring nodes only; one cell mixes train and validation. |
| 18–19 | scipy griddata, matplotlib | contour figures in notebook results | Plotting interpolates/averages model outputs; no valid city forecast. |
| 20–24 | legacy mask, baseline classes, metrics | best checkpoint, figures | PVR is a directional threshold statistic; cell 21 hard-codes spatial-decay values; cell 23 baseline models are instantiated but not trained. |
| 25 | empty | none | none. |

No Markdown cells or saved execution outputs exist. The notebook has no road-node observation generator, explicit forecast-origin builder, trained spatial decoder or routing optimizer. `gnn/stpignn_inference.py` is an external route-local helper and falls back to repeated static graph features if temporal construction fails; it is not a validated notebook citywide prediction path.

## Source exhibit 5: `final_blr_results/citywide_extension/v2q/ORIGINAL_VS_CORRECTED_COMPARISON.md`

[EVIDENCE: `final_blr_results/citywide_extension/v2q/ORIGINAL_VS_CORRECTED_COMPARISON.md` | SHA-256 `f9c67987699543ce15a9088233a77a3c0bc7a942810856239631e90f042aaf71` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Original versus corrected Bengaluru model

| Property | Original notebook | Corrected v2j/v2m |
|---|---|---|
| Graph nodes | 154,902 road nodes partitioned into 64; 23 snapped graph mask nodes | 15 monitoring stations |
| Edges | 424,550 processed road arcs; 7,134 boundary arcs dropped in partitions | 60 directed station kNN edges |
| Inputs/window | 16 channels (11 + 5 duplicates), 12 hours; sparse station timeline copied to roads | 18 versioned channels, 12 hours, station-specific cutoff-safe history |
| Target/output | Direct `station_pm25 / 342.9356` at last input hour | Future observed PM2.5, log1p-compatible residual |
| Training | Road partitions, station mask plus physics-only batches, one historical split | Corrected chronological station-graph experiments |
| Wind/physics | Scaled wind channel treated as degrees; reverse-bearing hinge | Corrected directional hinge, still heuristic |
| Weather | Historical master/model-input tables with inconsistent aggregation/alignment | Distinct documented v2j and v2m protocols |
| Weights | Root legacy checkpoint present and strict-load compatible | Matching final v2j benchmark/LOSO weights absent; older station checkpoints have other protocols |
| Prediction locations | Road-partition output possible, observed validation at monitor snaps only | Monitored stations |

**DIRECTLY REUSABLE:** OSM node IDs/coordinates/topology and checkpoint loading for historical replay. **REUSABLE WITH CORRECTIONS:** architecture source, partition mechanics, geometry/bearing code, output-map plumbing. **HISTORICAL ONLY:** root weights, duplicated-feature schema, 64-partition maps and old replay. **SCIENTIFICALLY INVALID for new forecasting:** full pollutant timeline copy, modulo time lookup, target-hour pollutant input, unverified scaled-wind angle, zero-as-missing target rule and cross-partition truncation. **MISSING:** genuine road-node PM2.5 histories/targets, compatible corrected ST-PIGNN checkpoint, independent roadside observations and tested lead-time station-to-road decoder.

Original-model checkpoint shape compatibility does not repair the information set or establish road prediction accuracy. The earlier corrected W6 LOSO result remains MAE 22.314 for ST-PIGNN versus 20.624 for weather/static ridge on eleven scored sites; do not merge populations with the legacy replay.

## Source exhibit 6: `results/MANIFEST.md`

[EVIDENCE: `results/MANIFEST.md` | SHA-256 `ecde34223166ff9574b2a40ffaf03abc0785eb273077b16bc44a86961cd7a5aa` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Phase A evidence artifacts

Generated on branch `audit/canonical-notebook-20261023` from source commit `22a0f5ac5a0527bf173e97692e22c20a245bc6a7`. Configuration: `configs/audit_canonical.yaml`; seed 42. Each JSON records its precise UTC run timestamp. Input data and checkpoint are existing repository workspace artifacts and are not copied here.

| File | Producer | Content |
|---|---|---|
| `audit_canonical.json` | `scripts/audit_canonical.py` | Checkpoint, graph, time split, station, elevation, PM2.5 tier and routing-field measurements |
| `audit_imputation_tiers.csv` | `scripts/audit_canonical.py` | All master rows by year, station ID and tier; includes non-PM2.5 pollutants |
| `stations.csv` | `scripts/audit_canonical.py` | Model-input station/node mapping, coordinates, saved partition cluster, nonzero scored targets and independently confirmed observed PM2.5 hours |
| `replay_canonical.json` | `scripts/replay_canonical.py` | Independent checkpoint MAE, RMSE, median AE, scored pairs, PVR and prediction summary |
| `replay_canonical.log` | `scripts/replay_canonical.py` | Raw notebook cell execution output, including progress and counters |
| `refactor_parity.json` | `scripts/check_canonical_refactor_parity.py` | Fixed-batch equality for extracted dataset, mask, penalty and metrics |

The replay executes selected canonical notebook cells without training or notebook figure/output cells. It reproduces the original data path and checkpoint but is not an observed-only or leak-free evaluation.

#### Rebuilt data and persistence gate

These files were generated on branch `audit/canonical-notebook-20261023` with `configs/data_v2.yaml` and `configs/gate_v2.yaml`. Each associated `*_run.json`, `data_v2_fit.json`, `feature_registry.json` or `gate_bootstrap_v2.json` records its source git commit, script, seed and UTC timestamp. The precise run provenance is also listed in `claude_paper.md` section 0.

| File | Producer | Content |
|---|---|---|
| `data_v2_arrays.npz`, `data_v2_fit.json`, `feature_registry.json`, `splits_v2.json` | `scripts/build_data_v2.py` | Aligned hourly tensors, train-fitted statistics, unique feature order and split counts |
| `stations_v2.csv`, `imputation_breakdown_v2.csv` | `scripts/build_data_v2.py` | Station mapping and per-station/year/tier provenance |
| `data_v2_diagnostics.json` | `scripts/diagnose_data_v2.py` | Raw row counts, target distribution, train-only scale diagnostics |
| `physics_v2_mask_summary.json`, `wind_mask_coverage_v2.csv` | `scripts/analyze_physics_v2.py` | Legacy versus corrected wind-mask coverage |
| `baselines_v2_predictions.parquet`, `baselines_v2_metrics.csv`, `baselines_v2_run.json` | `scripts/evaluate_baselines_v2.py` | Common-mask classical baseline predictions, pooled and per-station metrics |
| `neural_selection_v2.csv`, `neural_selection_initial_run.json`, `neural_selection_run.json` | `scripts/train_gate_v2.py --stage selection` | Validation-only learning-rate and target-scaler sweep |
| `neural_final_v2.csv`, `neural_predictions_v2.parquet`, `neural_curves_v2.csv`, `neural_final_run.json`, `checkpoints_v2/` | `scripts/train_gate_v2.py --stage final` | Five-seed trained scores, per-pair predictions, learning curves and checkpoints |
| `neural_summary_v2.csv`, `neural_per_station_v2.csv`, `gate_bootstrap_v2.json`, `gate_persistence.md` | `scripts/summarize_gate_v2.py` | Five-seed summary, station metrics and paired day-bootstrap gate |
| `legacy_checkpoint_v2_predictions.parquet`, `legacy_checkpoint_v2_metrics.csv`, `legacy_checkpoint_v2_run.json` | `scripts/evaluate_legacy_checkpoint_v2.py` | Diagnostic old-checkpoint adapter on rebuilt observed test targets |
| `pvr_gate_v2.csv`, `pvr_gate_v2_run.json` | `scripts/evaluate_pvr_gate_v2.py` | Test PVR for corrected and legacy masks, all trained seeds and thresholds without Q |

The gate failed because the validation-selected ST-PIGNN had higher test MAE than persistence. Q results are blocked by an absent measured traffic index. The old-checkpoint adapter changes both graph and feature construction, so its score is diagnostic only.
