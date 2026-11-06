# Captum IG results and numerical verdict

**Completed for v2m MLP/TCN station models; corrected ST-PIGNN IG UNVERIFIABLE.** Eighteen compatible v2m checkpoint cells were loaded: seed 11 for both models at five horizons and all five seeds for both models at h=6. The other 32 v2m checkpoint cells exist and passed v2m completion verification but were outside the frozen IG sample. Forty-five station/horizon/time examples, two model families, two baselines and the h=6 extra seeds produced **228 attribution records**, each a 12 × 18 tensor. No ST-PIGNN/λ0/Laplacian corrected checkpoint was found, so no physics contrast or graph/neighbor attribution was fabricated.

## Verification

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

## Descriptive attribution patterns

Using seed 11 and the primary training-mean baseline only, the mean total absolute attribution (sum of 12 × 18 components, µg/m³) rises from h1 to h12 and then falls: MLP **16.12/34.18/41.45/57.58/35.12** and TCN **10.01/40.37/48.08/54.03/38.91** at h1/3/6/12/24. This is a path-dependent magnitude, not a direct measure of predictive skill. Across those examples, `pm25_lagged` has the largest mean absolute feature attribution in both models (MLP 6.40, TCN 7.85 µg/m³). Pressure, humidity and temperature also have substantial absolute attributions; interpretation depends on their fitted scales and the baseline path. The newest lag (cutoff hour) has mean absolute attribution summed over channels 5.67 (MLP) and 9.08 (TCN) µg/m³. All twelve lags retain nonzero attribution; see `temporal_attributions.csv` and `ig_temporal_summary.png`. These are feature/lag effects in the models, not attention weights.

Wind-speed mean signed/absolute attribution is +0.285/1.869 µg/m³ for MLP and +0.106/1.899 for TCN. Wind-direction sine is +0.190/2.365 and +0.170/2.238; cosine is −0.276/1.697 and −0.185/1.565, respectively. Signed values average over different stations/times and can cancel. The direction channels encode circular sine/cosine; a high value here is no evidence of correct upwind transport. `feature_attributions.csv` preserves signed and absolute components separately, with per-station/horizon summaries in `station_horizon_feature_summary.csv`.

Baseline choice changes magnitude materially: on matched records, the zero-standardized to training-mean total absolute attribution ratio has median **1.202**, range **0.701–2.180**. The final prediction is identical across the two baseline calculations, as expected; the attribution path and reference output differ. Selected cutoff wind speeds span 0.18–5.84 m/s with 29 distinct rounded direction readings, so the fixed sample includes varying meteorological conditions. At h=6 the five saved seeds were compared on the three matched station median-time examples for each model; their prediction ranges across seeds are 1.30–13.54 µg/m³ for MLP and 2.84–19.18 for TCN, depending on station. These three examples are too few for a general seed-stability claim, and the high convergence-flag rate limits detailed cross-seed interpretation. Feature and temporal heatmaps are `ig_feature_temporal_mlp.png`, `ig_feature_temporal_tcn.png`, and `ig_temporal_summary.png`.

**Explainability robustness verdict: MIXED.** Model/wrapper/checkpoint equivalence and finite outputs are established for the v2m station baselines. Numerical completeness and baseline sensitivity limit stable fine-grained rankings. Corrected ST-PIGNN physics explainability remains UNVERIFIABLE. None of these IG outputs validates road-level pollution or physical conservation.
