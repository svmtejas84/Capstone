# Final physics attribution verdict — v2l

**Scope:** post-hoc reanalysis of existing corrected v2j Bengaluru predictions. Source training commit `9a299f1bf01787f26750515cad8dff370e9c9aa0`; v2k comparison commit `931bf09975dd17bfdca4f26259ede91046974f07`; v2l decision commit `2b2ab47`. No training, test-time selection, manuscript edit or citywide inference occurred. Complete methods: `methodology/PHYSICS_ATTRIBUTION_METHODOLOGY.md`.

## 1. Predictive contribution and multiplicity

The table uses matched five-seed mean predictions on the same 14,583 observed station-hour targets (177 UTC days) at every horizon. Negative Δ favors physics. The original 35-test Holm results are preserved; the five-horizon family is a separately labelled retrospective sensitivity analysis.

| h | Physics−λ0 ensemble ΔMAE (µg/m³) | Nominal 95% UTC-day CI | Original 35-test Holm p | Retrospective five-test Holm p |
|---:|---:|---:|---:|---:|
| 1 | −0.026 | [−0.050,−0.001] | 0.4453 | 0.0840 |
| 3 | −0.130 | [−0.210,−0.055] | 0.0175 | 0.0025 |
| 6 | −0.410 | [−0.550,−0.274] | 0.0175 | 0.0025 |
| 12 | −0.262 | [−0.381,−0.139] | 0.0175 | 0.0025 |
| 24 | +0.145 | [−0.013,+0.314] | 0.6357 | 0.0840 |

There is exploratory evidence of better ensemble prediction at h=3,6,12 under both adjusted families. The h=1 nominal interval excludes zero, as did the separate fixed h=1 lambda check, but its 35-test Holm result does not; the h=24 ensemble is worse by point estimate. No historical success criterion is revised.

## 2. Seed stability and ensemble dependence

| h | Seeds favoring physics | Mean individual-seed ΔMAE | Ensemble ΔMAE | Extra physics ensemble gain |
|---:|---:|---:|---:|---:|
| 1 | 1/5 | +0.009 | −0.026 | +0.036 |
| 3 | 3/5 | −0.005 | −0.130 | +0.125 |
| 6 | 5/5 | −0.566 | −0.410 | −0.156 |
| 12 | 4/5 | −0.254 | −0.262 | +0.008 |
| 24 | 3/5 | +0.155 | +0.145 | +0.011 |

At h=1 the ensemble gain reverses the average individual-model direction; at h=3 it accounts for nearly all the benefit. At h=6/12 individual models also improve, although h=12 is not universal across seeds. Seed counts are descriptive training variability on one test population, not independent replications. Full per-seed intervals and spread are in `seed_analysis/`.

## 3. Model-selection validity

The three models share the exact 43,393-parameter backbone, corrected input arrays, graph/edge features, target transformation and observed test mask. Their source loss branches differ by upwind hinge, zero penalty or Laplacian gradient penalty. Each had four LR trials with seed-11 validation MAE, the same 30-epoch/patience-five budget, and five complete final seeds. No test-based selection is visible. Selected LRs differ at h=1,6,12,24, and best epochs differ, so this is a fair **validation-selected procedural ablation** but not a common-LR/common-epoch causal estimate of the penalty alone. No corrected v2j checkpoint exists for weight-level audit. Details: `selection_audit/model_selection_review.md`.

## 4. Statistical and temporal robustness

The original 2,000-replicate UTC-day bootstrap and sign-flip values reproduce to rounding. Resampling is paired by day and observation-weighted; day-level sign symmetry and independence remain assumptions. Seven-consecutive-calendar-day moving-block CIs are [−0.068,+0.015], [−0.252,−0.042], [−0.632,−0.209], [−0.451,−0.076], [−0.064,+0.342] for h=1,3,6,12,24. Thus h=3/6/12 remain negative in this dependence sensitivity, h=1 does not. Months favor physics in 4/7, 6/7, 6/7, 6/7 and 1/7 respectively; unfavorable months were retained. The five largest absolute day sums account for 13–20% of absolute day effect depending on horizon. See `statistical_robustness/`.

## 5. Physics versus Laplacian and physical behavior

Physics−Laplacian ensemble ΔMAE is −0.073, +0.178, −0.130, +0.003 and −0.103 µg/m³ across h=1,3,6,12,24. In the original 35-test family, physics has adjusted favorable evidence at h=1 and h=6; Laplacian is better at h=3; h=12 is indistinguishable and h=24 only nominally favors physics. The wind-cone PVR>0 of physics is lower than λ0 at h=1/12 but **higher** at h=3/6/24. Spatial gradients, variance and near-constant output rates do not show a unique transport-consistency signature. The same sparse observed station edges provide a descriptive reference, not street-level truth. The upwind hinge has no measured emissions Q and does not enforce mass conservation. Lower PVR or hinge magnitude cannot prove atmospheric validity. Details: `physical_diagnostics/`.

## 6. Historical reconciliation and limits

Shifted-weather W7 found a weak λ=0.06 benefit only at h=6 among five horizons and generally harmful larger λ. Corrected v2j shifted h=1 into a small favorable fixed-check cell and retained no h=24 benefit. v2k's broader benchmark additionally found h=3/6/12 ensemble contrasts, but different weather, selection and aggregation prevent pooling old and new experiments as independent replication. Earlier physics-null findings and negative Laplacian/λ cells remain in `reconciliation/historical_physics_evidence.md`. The Bengaluru test set has been repeatedly exposed, horizons share observations, only 11 stations provide test targets, and no compatible citywide checkpoint or validated street-level ground truth exists.

## Separate classifications

| Question | Classification | Reason |
|---|---|---|
| Predictive effect | **MIXED** | Exploratory adjusted benefit at h=3/6/12; h=1 fragile and h=24 absent. |
| Seed robustness | **MIXED** | Stronger at h=6/12, weak/inconsistent at h=1/3/24. |
| Ensemble dependence | **PRESENT** | Dominant at h=1/3; not the principal source at h=6/12. |
| Physics specificity | **UNSUPPORTED** | Laplacian and transport-proxy comparisons are inconsistent; no conservation/Q evidence. |
| Independent confirmation | **NOT AVAILABLE** | Same repeatedly examined Bengaluru test set; no external holdout. |

These classifications separate statistical predictive association from causal architectural attribution. A physical mechanism cannot be established from these saved outputs alone. Required local prediction caches have no verified independent durable backup; `reproducibility/` lists paths, checksums and the no-training regeneration command.
