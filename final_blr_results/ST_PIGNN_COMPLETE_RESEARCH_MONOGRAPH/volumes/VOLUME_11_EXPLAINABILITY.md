# Volume 11 — Original and corrected Integrated Gradients

<a id="volume-11"></a>

## Editorial reconstruction and evidentiary boundary

Integrated Gradients attributes a scalar prediction difference relative to a chosen baseline; it cannot establish causal atmospheric transport. v2n explained available MLP/TCN checkpoints, with 85 of 228 completeness records flagged. Later recovery found five v2c h=1 corrected variants and three v2r h=6 outer-LOSO checkpoint folds, producing 54 and 18 additional IG records respectively. The latter are not the missing final v2j/λ0/Laplacian weights. Wrapper prediction equivalence and completeness were checked separately; feature, time, station and neighbor summaries must remain version-tagged. The original synthetic-elevation attribution has no validated terrain interpretation. [EVIDENCE: three-pillar Captum verdict | final_blr_results/final_three_pillars/captum/CAPTUM_FINAL_VERDICT.md | snapshot 1c46a4b]

## Full round-specific source exhibits

The exhibits reproduce the cited local reports as source evidence. Their original round-specific conclusions may be narrower than later findings; read the editorial reconstruction and final synthesis before treating one exhibit as the final verdict.

## Source exhibit 1: `final_blr_results/city_scale/explainability/CAPTUM_IG_METHODOLOGY.md`

[EVIDENCE: `final_blr_results/city_scale/explainability/CAPTUM_IG_METHODOLOGY.md` | SHA-256 `e9fcfa97eb1e81ac81c729bdc4af2e7dfc0d5d12e352bddc0f5f6e485510eee5` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Captum Integrated Gradients methodology

This is a descriptive, post-hoc v2n analysis of **v2m station-wise MLP and TCN**, not of corrected ST-PIGNN physics. It used `captum.attr.IntegratedGradients` on existing v2m checkpoints and cutoff-safe `data_v2m_arrays.npz`; no weights were trained or changed. The frozen design is `../protocol/CITY_SCALE_PROTOCOL.md`; executable code is `run_captum_ig.py`. The original supervised detached launcher did not persist inside the sandbox, so the same `scripts/run_supervised.sh _worker` was run in a foreground PTY. All three attempts exited code 0 but the first version omitted a group COMPLETE marker; output files were verified and the marker repaired. The final script writes that marker. Run controls and per-attempt logs remain under `runs/ig_v2n/`.

#### Exact model and output

The MLP uses two 64-unit ReLU layers over each station's flattened 12 × 18 input. The TCN uses two causal Conv1D layers with dilations 1 and 2 and a 12-position readout. Both share weights across stations and have no graph edge input, neighbor mixing or physics loss. `train_v2m.py` defines both models and saved checkpoint state dictionaries. All 18 checkpoints used here passed strict state loading and the per-cell SHA-256 completion markers. The output wrapper adds the fixed cutoff station anchor in train-standardized log1p space to the network residual, then applies `expm1` to return the **actual scalar final PM2.5 prediction in µg/m³**. The anchor and feature transformation were reconstructed from the v2m fit/array and the same observed-only causal forward fill as training. `run_captum_ig.py` compared every wrapper output with its saved prediction parquet before attribution; the largest absolute difference was 2.67e−5 µg/m³, below the frozen 1e−4 tolerance. The differentiable residual and output transform stay inside the wrapper; the observed cutoff anchor is held fixed, so the attributions describe the 12-hour input conditional on that anchor.

The primary baseline is each selected station's per-channel mean over the training period in fitted model input space, repeated at all 12 lag positions. It is saved as `training_reference.npy`. The second baseline sets standardized channels and missingness to zero while calendar channels remain at their training mean. Both were fixed before inspecting IG. The cutoff anchor remains the same under both baselines. These are reference states, not physically realizable weather/pollution interventions.

#### Sampling and calculation

Selection used observed masks and IDs only: first, median and last test-observed station IDs (5607, 3409385, 6206921), and first/median/last observed test target time for each station at each of h=1,3,6,12,24. The 45 sample IDs and cutoff timestamps are in `sample_selection.json`. Each model/horizon used seed 11 for nine examples and both baselines. At h=6, seeds 23,37,51,79 were added for each station's median-time example and both baselines. This yielded 18 distinct checkpoint cells and 228 IG records. Selection did not inspect error or attribution values.

Captum settings: 64 Gauss-Legendre steps, `internal_batch_size=16`, float32, CPU, one PyTorch thread, fixed random seeds, model evaluation mode. Captum returns an attribution for each of 12 lags × 18 named channels and a convergence delta for each record. `attribution_tensors.npz` aligns row-for-row with `convergence_diagnostics.csv`. `feature_attributions.csv` sums signed attribution across lags and separately sums absolute values; `temporal_attributions.csv` sums across channels. `station_horizon_feature_summary.csv` averages per-example signed and absolute summaries separately. The figures show mean signed and mean absolute tensors, not attention weights. Wind direction has separate sine/cosine channels; their IG values cannot be interpreted as a direct derivative with respect to degrees. The models have no graph-edge or neighbor-station interface, so neither edge nor neighbor attribution is available.

Completeness delta is `f(x)−f(b)−sum(IG)` as reported by Captum. Relative delta divides its absolute value by `max(1, abs(f(x)−f(b)))`. The frozen flag is absolute delta >0.05 µg/m³ or relative delta >1%, alongside nonfinite and wrapper checks. Baseline sensitivity is the ratio of summed absolute attribution between the two baselines on matched model/sample/seed records. Seed variability is descriptive on three matched h=6 station/time examples; it is not an independent test-set replication. The corrected v2j ST-PIGNN, λ=0 and Laplacian checkpoints are missing, so their IG comparison is **UNVERIFIABLE**. A legacy root citywide weight file cannot substitute for them.

IG identifies baseline-relative input sensitivity in these saved models. It cannot prove atmospheric mass conservation, causal wind dependence, Gaussian plume dynamics, road-node prediction validity or intervention importance. GRU lag attributions would not be attention weights; no GRU attribution was performed here.

## Source exhibit 2: `final_blr_results/city_scale/explainability/CAPTUM_IG_RESULTS.md`

[EVIDENCE: `final_blr_results/city_scale/explainability/CAPTUM_IG_RESULTS.md` | SHA-256 `257f9f17e7a6f98af2d15d70c10ef588c3f88a319ec9729d1226976020343f27` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Captum IG results and numerical verdict

**Completed for v2m MLP/TCN station models; corrected ST-PIGNN IG UNVERIFIABLE.** Eighteen compatible v2m checkpoint cells were loaded: seed 11 for both models at five horizons and all five seeds for both models at h=6. The other 32 v2m checkpoint cells exist and passed v2m completion verification but were outside the frozen IG sample. Forty-five station/horizon/time examples, two model families, two baselines and the h=6 extra seeds produced **228 attribution records**, each a 12 × 18 tensor. No ST-PIGNN/λ0/Laplacian corrected checkpoint was found, so no physics contrast or graph/neighbor attribution was fabricated.

#### Verification

| Check | Result |
|---|---:|
| Maximum wrapper versus saved-prediction error | 0.0000267 µg/m³ (passes 0.0001) |
| Nonfinite attribution/delta values | 0 |
| Median absolute Captum completeness delta | 0.0160 µg/m³ |
| 95th percentile absolute delta | 0.1054 µg/m³ |
| Maximum absolute delta | 0.2764 µg/m³ |
| Median relative delta | 0.518% |
| Maximum relative delta | 9.761% |
| Flagged records by frozen quality rule | 85/228 (37.3%) |

The 64-step numerical integral does **not** meet the frozen strict quality flag for many records: MLP 30/114, TCN 55/114. The signed attributions and gross temporal patterns are saved, but fine feature rankings and small differences should be treated as numerically fragile. `convergence_diagnostics.csv` retains every delta and flag. The worker's repeated attempts all produced the same declared 228-record output, and the final tensor SHA-256 is in the reproducibility checksums; a separate cross-hardware bitwise replay was not performed.

#### Descriptive attribution patterns

Using seed 11 and the primary training-mean baseline only, the mean total absolute attribution (sum of 12 × 18 components, µg/m³) rises from h1 to h12 and then falls: MLP **16.12/34.18/41.45/57.58/35.12** and TCN **10.01/40.37/48.08/54.03/38.91** at h1/3/6/12/24. This is a path-dependent magnitude, not a direct measure of predictive skill. Across those examples, `pm25_lagged` has the largest mean absolute feature attribution in both models (MLP 6.40, TCN 7.85 µg/m³). Pressure, humidity and temperature also have substantial absolute attributions; interpretation depends on their fitted scales and the baseline path. The newest lag (cutoff hour) has mean absolute attribution summed over channels 5.67 (MLP) and 9.08 (TCN) µg/m³. All twelve lags retain nonzero attribution; see `temporal_attributions.csv` and `ig_temporal_summary.png`. These are feature/lag effects in the models, not attention weights.

Wind-speed mean signed/absolute attribution is +0.285/1.869 µg/m³ for MLP and +0.106/1.899 for TCN. Wind-direction sine is +0.190/2.365 and +0.170/2.238; cosine is −0.276/1.697 and −0.185/1.565, respectively. Signed values average over different stations/times and can cancel. The direction channels encode circular sine/cosine; a high value here is no evidence of correct upwind transport. `feature_attributions.csv` preserves signed and absolute components separately, with per-station/horizon summaries in `station_horizon_feature_summary.csv`.

Baseline choice changes magnitude materially: on matched records, the zero-standardized to training-mean total absolute attribution ratio has median **1.202**, range **0.701–2.180**. The final prediction is identical across the two baseline calculations, as expected; the attribution path and reference output differ. Selected cutoff wind speeds span 0.18–5.84 m/s with 29 distinct rounded direction readings, so the fixed sample includes varying meteorological conditions. At h=6 the five saved seeds were compared on the three matched station median-time examples for each model; their prediction ranges across seeds are 1.30–13.54 µg/m³ for MLP and 2.84–19.18 for TCN, depending on station. These three examples are too few for a general seed-stability claim, and the high convergence-flag rate limits detailed cross-seed interpretation. Feature and temporal heatmaps are `ig_feature_temporal_mlp.png`, `ig_feature_temporal_tcn.png`, and `ig_temporal_summary.png`.

**Explainability robustness verdict: MIXED.** Model/wrapper/checkpoint equivalence and finite outputs are established for the v2m station baselines. Numerical completeness and baseline sensitivity limit stable fine-grained rankings. Corrected ST-PIGNN physics explainability remains UNVERIFIABLE. None of these IG outputs validates road-level pollution or physical conservation.

## Source exhibit 3: `final_blr_results/final_three_pillars/captum/CHECKPOINT_RECOVERY.md`

[EVIDENCE: `final_blr_results/final_three_pillars/captum/CHECKPOINT_RECOVERY.md` | SHA-256 `0f4e255e069d7e072ce48f5267ec0ab07a3243b40830034fae39cab15fc38e0f` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Captum checkpoint recovery

Candidate checkpoint inventory: `CHECKPOINT_MANIFEST.csv` (84 rows, paths, byte sizes, SHA-256, metadata, input channel count, protocol verdict). The inventory script is `../reproducibility/build_checkpoint_manifest.py`.

#### Findings

- Final v2j corrected ST-PIGNN physics, λ=0 and Laplacian model configurations have saved 15-station prediction parquets and an explicit `NONE SAVED` checkpoint field in `final_blr_results/physics_audit/provenance/model_configurations.csv`. Their gradients cannot be recovered. Checkpoints are **MISSING**, not merely undiscovered under another shape.
- Earlier v2c has five corrected h=1 checkpoints and one-per-pair predictions. Their strict architecture load uses 13 input channels, h=1, log1p residual, 96 width. The wrapper reproduced selected saved predictions to ≤4.58e−5 µg/m³; these weights were used only as `v2c corrected h1`, never labeled v2j.
- v2r preserved h=6 seed-11 outer-LOSO fold checkpoints with 18 input channels, edge_dim 1, and metadata identifying held-out station and cutoff-safe weather. Corresponding `station_forecasts_all.parquet` rows support exact heldout prediction checks. A separate small IG analysis is run only for selected sites whose wrapper meets ≤1e−4 µg/m³; result files and exact used hashes are under `v2r_heldout_h6/`.
- Notebook root `citywide_stpignn_best.pt`/stable/autosave weights are 16-channel historical road-partition models, with target-hour leakage and copied source-station histories documented in the v2q recovery. They are **not compatible substitutes** for corrected station graph models.
- Earlier v2/v2b weights are inventoried but feature schema/split/data protocol differ from final v2j. Tensor compatibility alone does not make them v2j checkpoints.

No new training was performed. The top-level authorization prohibited GPU training; reproducing weights would also not recover historical model identity. Final v2j IG and physics/λ0/Laplacian attribution comparisons remain unavailable.

## Source exhibit 4: `final_blr_results/final_three_pillars/captum/IG_METHODOLOGY.md`

[EVIDENCE: `final_blr_results/final_three_pillars/captum/IG_METHODOLOGY.md` | SHA-256 `d0a448053c8148268817183b0b1b288d36adc5b58284ef62b1459b37407faae9` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Captum Integrated Gradients methodology

#### Checkpoint gate and separate protocol versions

The final v2j training record stores prediction parquets but its `model_configurations.csv` explicitly says `checkpoint_path=NONE SAVED`. Consequently, exact v2j physics/λ0/Laplacian weights cannot be recovered for gradients. Do not attribute v2c weights as if they were v2j. This package reports two separately labeled saved-weight analyses:

1. **v2c h=1 corrected ST-PIGNN:** five historical corrected checkpoints, 13 input channels, 96 hidden units, directed station kNN graph, matching v2c per-pair prediction artifact. Five seeds, three stations × first/median/last eligible h1 test time. Primary baseline is each station/channel's training-time mean repeated across the 12 lags; a zero-input sensitivity baseline is computed for seed 11. Strict checkpoint load and prediction tolerance ≤1e−4 µg/m³ are required. This is older protocol-specific IG, not v2j.
2. **v2r h=6 outer-LOSO corrected ST-PIGNN:** saved corrected 18-channel checkpoints (seed 11, 96 hidden units, 12-hour history, 4-NN station graph) for three sorted first/median/last scored held-out station IDs. Each outer model excludes the held-out station target labels and target-derived training/anchor data. For each, choose first/median/last observed h6 test targets by mask/time only. This is post-hoc analysis on the repeatedly exposed Bengaluru test period, not independent confirmation.

#### v2r wrapper and forecast-time validity

For each held-out fold the feature builder and scaler are reconstructed using the exact fold config and source `src/stpignn.data_v2.build` call (`weather_half_hour_rule=True`, `weather_cutoff_safe=True`). The selected h6 history indices are `target−6−[11,…,0]`; all are at or before the forecast cutoff `target−6`. For a held-out site's node, five pollutant channels are forced to zero, missingness indicates the withheld history, and its persistence anchor uses a train-only fallback. Its observed heldout measurement is not included in input, fit, imputation, anchor, or the checkpoint.

The wrapper computes the exact model residual plus cutoff anchor in train-standardized log1p space, applies `expm1`, and returns the selected station's scalar PM2.5 prediction in µg/m³. Graph edge index/length, station identity, and any non-target output channels remain fixed. IG attributes all 12 × 15 × 18 station/time/channel input values for this scalar. These are feature-input attributions; the method does not attribute edge weights or graph topology.

The primary baseline is the training-period mean for each station/channel in the fold's fitted input space, repeated across 12 lags. Sensitivity baseline zeros the first 13 environmental channels while retaining observed missingness and calendar channels. Baselines are fixed by rule, not attribution outcome. Captum uses 64 Gauss–Legendre integration steps, `internal_batch_size=1`, CPU float32, eval mode, one PyTorch thread, and fixed seeds. Each record stores signed tensors; CSV aggregates signed and absolute values separately. Temporal summaries aggregate over station and feature axes; station summaries aggregate over lag and feature axes. No lag attribution is called attention.

Wrapper output must agree with the exact outer-fold `station_forecasts_all.parquet` heldout prediction within 1e−4 µg/m³ before attribution. Completeness delta is `f(x)−f(b)−sum(IG)`, with relative denominator `max(1,|f(x)−f(b)|)`. Frozen quality flags: absolute delta >0.05 µg/m³ or relative delta >1%; any nonfinite record is a failure. Per-record `.npz` tensors and metadata are written atomically to permit supervised restart without repeating completed attributions.

#### Interpretation boundary

IG describes baseline-relative input sensitivity in these saved models. It does not establish causal influence, feature importance under intervention, atmospheric mass conservation, Gaussian plume validity, street-level accuracy, or physical wind/terrain dependence. The h1 v2c and h6 v2r attributions cannot be pooled as one model/horizon family. The corrected final v2j checkpoint-specific IG, λ0 comparison, and Laplacian comparison remain unavailable because matching v2j checkpoints were not saved.

## Source exhibit 5: `final_blr_results/final_three_pillars/captum/CAPTUM_FINAL_VERDICT.md`

[EVIDENCE: `final_blr_results/final_three_pillars/captum/CAPTUM_FINAL_VERDICT.md` | SHA-256 `5b1ff6a7b2fb0d6b67d704f079d600f8bb694ae53569549bf4e9efae27729ba4` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Captum final verdict

**Classification: MIXED.** Captum Integrated Gradients ran on compatible saved corrected ST-PIGNN checkpoints from two distinct protocol versions. Numerical wrapper parity and completeness diagnostics are strong for the selected examples. This is post-hoc, baseline-relative attribution on previously examined Bengaluru observations; it is not independent confirmation, causal evidence, or physical validation.

#### Coverage

- v2c historical corrected h=1: 5 checkpoints/seeds, 9 deterministic examples, two baselines, 54 records. Maximum prediction-wrapper discrepancy was `4.58e-5 µg/m³`; maximum absolute completeness delta `2.15e-5 µg/m³`; 0 flagged and 0 nonfinite records.
- v2r outer-LOSO corrected h=6: 3 fold checkpoints for held-out stations 5607, 3409385, 6206921; 3 fixed target times per station; two baselines; 18 records. Maximum wrapper discrepancy was `7.63e-6 µg/m³`; maximum absolute completeness delta `7.81e-6 µg/m³`; 0 flagged and 0 nonfinite records.
- The root `IG_RESULTS.csv` combines both versions with an `analysis_version` column. Version-specific result files and full attribution tensors are retained in their subdirectories.

These versions differ in feature schema, horizon, data split and model lineage; their attribution magnitudes must not be compared as a controlled horizon or version effect. v2c and v2r example counts are not spatially representative. Neighbor-station attribution is input attribution through the station graph, not edge attribution. No λ=0 matched checkpoint was recovered for the final corrected protocol; no physics-versus-λ comparison is available. v2j final corrected checkpoints were not saved. The v2n MLP/TCN attribution results remain separate and do not explain ST-PIGNN.

Use the attribution results only to describe how these model outputs change relative to the fixed reference inputs. They do not establish causal influence, atmospheric transport, conservation, true road-level pollution importance, or intervention effects.

## Source exhibit 6: `final_blr_results/ieee_paper_evidence/methodology/EXPLAINABILITY.md`

[EVIDENCE: `final_blr_results/ieee_paper_evidence/methodology/EXPLAINABILITY.md` | SHA-256 `5847fbc06936576cc9220e255fdb86f3418a09d411810262d9900baa1df7dfc1` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Explainability

Captum Integrated Gradients covered 18 compatible v2m station MLP/TCN checkpoint cells; 228 attribution records, each 12×18. Wrapper maximum error was 2.67e-5 µg/m³; zero nonfinite values; 85/228 records exceeded the frozen completeness flag. Median absolute delta 0.0160, 95th percentile 0.1054, max 0.2764 µg/m³; baseline magnitude sensitivity was material. Corrected ST-PIGNN, λ=0 and Laplacian checkpoints were unavailable, so their IG is UNVERIFIABLE. IG describes input effects relative to chosen baselines, not causal effects, physical validity, or road concentration accuracy. See `final_blr_results/city_scale/explainability/`.
