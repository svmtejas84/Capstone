# V4 six-hour prespecified sensitivity results

All 30 valid fits completed on the repaired V3 array using the frozen five seeds, shared learning rate 0.0003, identical GINEConv–GRU backbone, train/validation target masks, optimizer, epoch budget, validation checkpoint rule and predictive features. Four initial full-shuffle fits were invalidated before any V4 test scoring because their permutation used target-eligible hours; `PROTOCOL_AMENDMENT_01.md` records the repair and preserves those attempts separately. The corrected full shuffle permutes all calendar training wind-mask rows once with seed 4404 and is fixed across seeds and epochs. Test results below come only from the 30 corrected checkpoints. The target period is historically exposed, so every finding is exploratory.

| Condition | Ensemble MAE | True 0.06 minus condition | Seven-day block CI | Holm-adjusted six-member p | Seeds favoring true |
|---|---:|---:|---:|---:|---:|
| True wind, λ=0.06 (V3 reference) | 15.366 | — | — | — | — |
| Reverse wind, λ=0.06 | 15.412 | −0.046 | [−0.070,−0.027] | 0.00040 | 2/5 |
| Constant north transport, λ=0.06 | 15.272 | +0.094 | [+0.004,+0.193] | 0.09692 | 1/5 |
| Full-period shuffled wind, λ=0.06 | 15.536 | −0.170 | [−0.227,−0.126] | 0.00006 | 4/5 |
| True wind, λ=0.3 | 15.667 | −0.301 | [−0.460,−0.165] | 0.00204 | 5/5 |
| True wind, λ=1.0 | 16.502 | −1.136 | [−1.575,−0.751] | 0.00015 | 5/5 |
| One-batch magnitude-matched Laplacian, λ=0.021844 | 15.226 | +0.139 | [+0.073,+0.202] | 0.00204 | 2/5 |

Units are µg/m³. All comparisons use the same 14,583 observed test station-hour pairs. Negative paired differences favor the V3 true-wind condition. The V4 six-member family uses 2,000 seven-day moving-block bootstrap draws for intervals and 100,000 nonoverlapping seven-day block sign flips for p-values, with Holm adjustment. The two dependence treatments can disagree: the constant-north moving-block interval barely excludes zero, while its adjusted sign-flip p=0.09692. Neither is confirmatory. Only five station-model seeds exist and they are not independent cities or geographic sites.

The one-batch Laplacian coefficient was frozen **before** training using the V3 unregularized six-hour seed-11 checkpoint on the first 512 training target-hours: raw directional 0.27539447, raw Laplacian 0.75645131, coefficient 0.06×ratio=0.02184366. This matches one raw-loss magnitude, not gradients or full-training exposure. Its lower ensemble MAE than true wind weakens a claim that the wind-directed mechanism is uniquely beneficial. Likewise, constant north has a lower point estimate than true wind, though inference is mixed. Larger λ values degrade six-hour MAE. The different mask densities, seed variability, historical test exposure and lack of independent validation prevent a physical-specificity conclusion.

Numerical sources: `metrics/V4_SENSITIVITY_SCORES.csv`, `statistical_analysis/V4_SIX_CONTRASTS.csv`, `statistical_analysis/V4_SEED_CONTRASTS.csv`, `LAPLACIAN_CALIBRATION.json`, per-seed and ensemble NPZ predictions in `predictions/`. Reproduction code: `scripts/verify_and_score.py`, `scripts/analyze_sensitivity.py`.
