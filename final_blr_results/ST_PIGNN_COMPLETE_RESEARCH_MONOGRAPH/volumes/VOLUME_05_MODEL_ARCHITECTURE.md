# Volume 5 — Original and corrected GINE–GRU architectures

<a id="volume-05"></a>

## Editorial reconstruction and evidentiary boundary

The original `gnn/model.py` implementation applies 16→96 node encoding, two residual edge-aware GINE blocks at each of 12 hours, a 96-unit GRU and a scalar direct output; the recovered checkpoint has 98,497 parameters. Its 16 features include five duplicated pollutant channels. Corrected experiments instead use an 18-channel 12-hour station sequence with log1p-compatible residual forecasting and a 15-node graph; a v2l comparison reports a common 43,393-parameter backbone. The same tensor shape would not prove transfer between these feature/edge semantics. MLP and TCN v2m baselines used a later weather availability protocol, so their test contrasts are not identical-information architecture ablations. [EVIDENCE: original architecture | final_blr_results/citywide_extension/v2q/ORIGINAL_MODEL_ARCHITECTURE.md | snapshot 1c46a4b]

## Full round-specific source exhibits

The exhibits reproduce the cited local reports as source evidence. Their original round-specific conclusions may be narrower than later findings; read the editorial reconstruction and final synthesis before treating one exhibit as the final verdict.

## Source exhibit 1: `final_blr_results/citywide_extension/v2q/ORIGINAL_MODEL_ARCHITECTURE.md`

[EVIDENCE: `final_blr_results/citywide_extension/v2q/ORIGINAL_MODEL_ARCHITECTURE.md` | SHA-256 `875d64aa56f83a0a38a1858e6f633e3666cdd4d047e8fd7ecb88f38f37f3a2a0` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Original model architecture and target semantics

`gnn/model.py:STPIGNN` is the source imported by notebook cell 0/11 through `src.stpignn`. A 16→96 linear node encoder is followed at each of 12 input times by two residual GINEConv blocks (96 hidden, 16 edge channels, LayerNorm/ReLU/dropout). A single 96-unit GRU runs per node across those spatial embeddings; a linear 96→1 head gives a **direct** normalized scalar `[batch,nodes]`. There is no residual forecast anchor, attention, road-edge output head or multi-horizon head. Root best checkpoint strictly loads with 98,497 parameters; global config sets 15 maximum epochs, λ max 0.06 and `TARGET_SCALE=342.9356`. Saved epoch is 2.

Road edge attributes are length plus 15 highway indicators from the processed PyG topology. The 16 temporal channels in cells 4–5 are eleven scaled pollutant/weather fields plus five **duplicated pollutant fields**, not sixteen distinct measurements. `master_scaled_checkpoint.parquet` has 17 station IDs, while `model_input_node_hourly_features.parquet` has 22 node IDs. Cell 9 uses `station_pm25 / TARGET_SCALE` as the direct target; it fills missing target with zero and then masks zeros. This is not the corrected log1p-compatible residual transformation.

`TierAwareClusterDatasetV3` creates an input window through hour `t_start+11` and the target at that same hour. Its `t_curr % node_registry.shape[0]` lookup can wrap a station timeline and is not timestamp alignment. The physics mask in cell 7 compares reverse edge bearing to a channel-6 value taken at node zero; channel 6 is scaled wind direction, so it is not verified as degrees. `compute_wind_advection_penalty` applies a length/edge-attribute-scaled directed hinge. No mass conservation or Gaussian plume equation is enforced by notebook cell 13.

Training batches are 64 spatial partitions with station-supervised or physics-only modes. This is training over *road graph partitions with copied sparse-source inputs*, not training on observed PM2.5 at all road nodes. Cells 15–17 score only station-mask nodes. Cell 19 generates 64 cluster maps by averaging partition predictions over validation times; it does not serialize timestamped full-city forecasts. Cross-partition arcs are lost.

## Source exhibit 2: `final_blr_results/citywide_extension/v2q/ORIGINAL_VS_CORRECTED_COMPARISON.md`

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

## Source exhibit 3: `final_blr_results/ieee_paper_evidence/methodology/MODEL_ARCHITECTURE.md`

[EVIDENCE: `final_blr_results/ieee_paper_evidence/methodology/MODEL_ARCHITECTURE.md` | SHA-256 `fdeb08b161ed4f2081489583f6ec9228d5a91292e9c7847673cdce9c956035e6` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Model architecture evidence

Corrected ST-PIGNN is a station-graph GINE–GRU model with 18 channels, 12 input hours, log1p-compatible residual forecasting over causal persistence, and an observed-target objective. The production notebook's historical implementation is a separate 16-channel road-partition GINE–GRU pathway with a surviving historical checkpoint; the notebook input construction included target-hour leakage and other invalid assumptions. Do not present its weights as corrected-model evidence.

v2m MLP and TCN controls completed 50 cells (two model families, five horizons, five seeds each) under a different weather-information protocol from historical ST-PIGNN. The v2r spatial decoder is the existing compact 1,249-parameter model; it did not outperform its controls.

Source inventory: `results/research_audit_r1/architecture_inventory.md`, `final_blr_results/citywide_extension/v2q/ORIGINAL_MODEL_ARCHITECTURE.md`, and version-specific round reports.

## Source exhibit 4: `final_blr_results/ieee_paper_evidence/methodology/TRAINING_AND_EVALUATION.md`

[EVIDENCE: `final_blr_results/ieee_paper_evidence/methodology/TRAINING_AND_EVALUATION.md` | SHA-256 `64c4cd69e3c2cf5e6f03319b4e68e08f00c55b0bf8b04dea4706b8dac26ee935` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Training and evaluation

Keep each round's split, features, model selection, and test population separate. The v2l frozen comparisons use 14,583 matched station-hour pairs over 177 UTC days at each horizon, 11 scored sites. v2m contains all 50 MLP/TCN model-seed-horizon cells and ten frozen primary comparisons; its weather protocol differs from historical ST-PIGNN. Bengaluru's test set has repeated exposure and is exploratory, not independent confirmation.

No experiments were run to create this evidence package. v2m archived individual predictions were used to recompute 50 individual model-seed cells, ten five-seed ensemble metrics and the ten frozen paired ST-PIGNN contrasts; v2r LOSO paired predictions were used to independently recalculate pooled and site metrics. `results/RESULTS_VERIFICATION.md` labels provenance. Statistical comparisons are within their original frozen family; do not create new favorable multiplicity families.

## Source exhibit 5: `final_blr_results/baselines/v2m/methodology/BASELINE_BENCHMARK_METHODOLOGY.md`

[EVIDENCE: `final_blr_results/baselines/v2m/methodology/BASELINE_BENCHMARK_METHODOLOGY.md` | SHA-256 `9ef92affddcc34ca3c290ddb7bc37ed4e940cbb4dc0eec1fcbc133d2676884ea` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### v2m baseline benchmark methodology

#### Scope and provenance

This exploratory, post-hoc Bengaluru benchmark adds a station-wise two-layer MLP and two-layer causal TCN. It uses the exposed historical test set and is not independent confirmation. The purpose is to assess whether graph/recurrent complexity provides a useful forecasting gain over simpler models. The frozen protocol is `final_blr_results/baselines/v2m/EXPERIMENT_PROTOCOL.md`; source is `final_blr_results/baselines/v2m/reproducibility/train_v2m.py`, evaluator `evaluate_v2m.py`, data builder `build_data_v2m.py`. The implementation was committed before training at `07dd9e2`; the dataset/protocol fix at `a9307de`. Training began at 2026-11-05 19:44 UTC and the final supervised run ended at 19:49:52 UTC on a Tesla V100-PCIE-32GB. No CPU neural training was performed.

#### Data and forecast origin

The 15-station dataset has 0–500 µg/m³ observed PM2.5 targets. Train is 2022-01-01 through 2025-06-29, validation 2025-07-01 through 2025-09-21, and test 2025-09-23 through 2026-03-28 UTC, with the existing gaps. Eleven stations contribute test observations. All five horizons use exactly 14,583 observed target pairs over 177 UTC days; no target observations are inferred from imputed station input channels. The 12-hour history ends at forecast cutoff `c = target time − horizon`. The input has 13 fitted data channels, `lag_is_imputed`, and four calendar channels, giving 18 per station-hour. Training-only fitting and the original causal pollutant fill are retained. PM2.5 targets and PM2.5/PM10 lag features use compatible train-fitted log1p standardization. Output is a standardized-log1p residual over the last observed PM2.5 at or before c; reconstruction applies expm1. Train and validation require an observed immediate lag, while the test scores all observed targets.

The only v2m input change is the weather cutoff fix. Raw weather timestamps are Asia/Kolkata local clock values labeled UTC; subtract exactly 5 h 30 min to obtain the correct UTC :30 timestamp. At hour c, choose the latest corrected weather observation timestamped at or before c, normally c−30 min, with the preexisting 24-hour forward limit. Historical v2j features averaged c−30 and c+30, so historical baseline predictions have a different weather information set. The test target/mask/timeline/station arrays are byte-identical to v2j. The archive weather source is retrospective reanalysis; use in actual deployed forecasting requires a separately verified issue-time operational source. The source correction removes the specific c+30 temporal look-ahead from the v2m inputs. `data_v2m_arrays.npz` SHA-256 is `8dfe2a3eebdd7900c86d738c1225c1941ac716305282c2efc17a5da8c4bb84d5`; all training cells record this digest. Temperature peaks at 09:00 UTC.

#### Architectures and training

MLP: each station's 12×18 input is flattened to 216, then Linear(216,64), ReLU, Linear(64,64), ReLU, Linear(64,1); 18,113 parameters. TCN: each station separately uses causal Conv1D(18,64,k=3,d=1), ReLU, causal Conv1D(64,64,k=3,d=2), ReLU, and Linear(64×12,1) over all 12 final temporal positions; 16,641 parameters. The final convolutional position has a seven-step receptive field, while the readout can use the complete 12-hour window. Both models share weights across stations and use no graph, attention, recurrent layer, or physics regularizer. Synthetic CPU checks verified shape, finite gradients, station independence and that future timestep changes leave earlier TCN representations unchanged. The v2m data test verified the exact weather offset, unchanged targets/masks, finite feature shape and a sample cutoff.

All cells use AdamW, weight decay 0.01, batch size 512, width 64, at most 30 epochs, patience 5, gradient-norm clip 0.3, and masked squared error in standardized log1p space. Seed 11 chooses one LR per model/horizon from {0.0001,0.0003,0.001,0.003} using validation MAE only; each final seed {11,23,37,51,79} is then trained at that LR. Each seed's best epoch is chosen by validation MAE. This matches the historical selection policy but the new models have different parameter budgets and the weather inputs differ. Per-cell metrics record selected LR, best epoch, total epochs, validation MAE, test metrics, runtime, parameter count, and peak allocated GPU bytes. The code did not preserve every per-epoch loss/validation value; that requested history is unavailable and must not be invented. Selection-candidate final validation metrics are saved in each `validation_selection.json`.

#### Evaluation and statistics

For target `y_i` and prediction `p_i`, MAE = `mean|p_i−y_i|`, RMSE = `sqrt(mean(p_i−y_i)^2)`, and R² = `1−sum(p_i−y_i)^2/sum(y_i−mean(y))^2`. The five-seed ensemble predicts `p̄_i = mean_s p_{s,i}`. Mean individual-seed MAE and ensemble MAE are distinct and reported separately. Every saved prediction includes target UTC timestamp and station ID; the evaluator requires the exact same ordered keys and target values for all comparisons and never silently intersects populations.

The primary family is ten paired contrasts: historical ST-PIGNN minus new MLP and minus new TCN at all five horizons. Negative MAE difference favors ST-PIGNN. For each UTC day, sum its paired absolute-error differences and count its observations. Draw 2,000 UTC days with replacement using seed `4303 + 100h + model index`; divide the sampled difference sum by sampled observation count, yielding an observation-weighted bootstrap. Report percentile 95% intervals. A 2,000-replicate UTC-day sign-flip test provides raw two-sided Monte Carlo p-values; Holm step-down adjusts the ten p-values. These intervals are nominal and not Holm-adjusted. Day-level exchangeability and sign symmetry are assumptions, not established facts. Horizons are dependent; the family is exploratory and post-hoc. Historical statistical and neural controls are descriptive matched-pair comparisons. **All historical model comparisons are cross-protocol because their weather information set differs.** No causal architectural or identical-input ablation claim follows from the differences.

#### Reproducibility and limits

Run one supervised group with `PYTHONPATH=. bash scripts/run_supervised.sh launch final_blr_results/baselines/v2m/runs/MODEL_hH -- python final_blr_results/baselines/v2m/reproducibility/train_v2m.py --model MODEL --horizon H`; the full recoverable run used `--all` and `runs/all_v2m`. Recompute metrics without training via `PYTHONPATH=. python final_blr_results/baselines/v2m/reproducibility/evaluate_v2m.py`. Per-cell `COMPLETE.json` records checkpoint/prediction/metric SHA-256. See `reproducibility/regeneration_instructions.md` for exact recovery and archive commands.

The Bengaluru test has repeated exposure and six earlier post-hoc methodological deviations: residual/lag repair, LR-grid expansion, seasonal baseline addition, LOSO anchor modification, lambda sweep, and later Laplacian-separated W7 criterion. Seasonal distribution shift, the fixed 500 µg/m³ ceiling, 15 stations, only eleven test-observed stations, shared horizons, possible temporal dependence and limited spatial transfer constrain interpretation. No validated full-road-graph or street-level prediction, measured emissions Q, or independent external replication exists. The local ZIP archives await external download under the supervisor's explicit backup exception.
