# Model-variant inventory and repeated test-exposure audit

## Saved model inventory

The authoritative recomputed retrospective benchmark has **17 model/variant names × five horizons = 85 rows**. Each row preserves MAE, RMSE, (R^2), observed pair count, seed count, and saved-summary discrepancy fields in `source_data/F03_all_variants.csv` and `tables/T02_complete_forecasting_benchmark.csv`.

The seventeen names are:

1. Adaptive graph ST.
2. Adaptive graph ST with fixed kNN.
3. Hour-of-day/day-of-week climatology.
4. Wind-conditioned GINE–GRU.
5. GRU-only.
6. Persistence.
7. Weather ridge.
8. Same-hour-yesterday.
9. ST GRU–GCN.
10. Station training mean.
11. ST-PIGNN, zero regularization.
12. ST-PIGNN, Laplacian smoothing.
13. ST-PIGNN, directional regularization.
14. ST-PIGNN v2.
15. ST-PIGNN v2 with source term removed.
16. ST-PIGNN v2 with transport term removed.
17. Vanilla GCN.

MLP and TCN are additional model families in the separate forecast-cutoff-safe benchmark (50 individual model/seed/horizon cells and five-horizon ensemble metrics). They do not belong to the 17 retrospective v2j variants.

## Strong baseline values verified

The saved 14,583-pair results verify the reviewer-reported rounded values:

| Baseline | MAE (µg/m³) | RMSE (µg/m³) | R² | Horizons represented |
|---|---:|---:|---:|---|
| Hour/day climatology | 21.46865 | 38.74625 | −0.09245 | same fixed estimate at all five horizons |
| Station training mean | 20.96465 | 37.33642 | −0.01440 | same fixed estimate at all five horizons |
| Same-hour-yesterday | 14.13031 | 31.38600 | +0.28317 | archived implementation repeats this value across the reported horizon labels |

Adaptive graph ST has MAE 7.94665 at one hour and 13.74402 at 24 hours (with 3/6/12-hour values in the full table). A second fixed-kNN adaptive graph is separately recorded. The 24-hour same-hour-yesterday reference is naturally aligned with its construction; repeated same value for other labels is an artifact of the benchmark summary representation and must not be presented as a distinct lead-specific baseline without checking timestamp construction.

## Wind-conditioned GINE–GRU versus zero-regularization ST-PIGNN

Both variants use the same corrected v2j 18-channel input array, station graph, chronological split, and 14,583 scored pairs; their result rows are within the same retrospective weather protocol. Their architecture and training objectives differ: `gine_gru_wind` applies a temporal GRU first and then one GINE layer with distance and wind-along-edge attributes (`src/stpignn/models_v3.py`), while the corrected ST-PIGNN uses its own spatial-temporal GINE–GRU implementation. Learning rates are validation-selected separately per model/horizon under the common LR grid using seed 11, then five seeds are evaluated.

| Horizon | Wind-conditioned GINE–GRU MAE | ST-PIGNN λ=0 MAE | Difference (wind model − λ=0) |
|---:|---:|---:|---:|
| 1 h | 7.984 | 8.052 | −0.068 |
| 3 h | 12.744 | 12.472 | +0.273 |
| 6 h | 16.026 | 15.116 | +0.909 |
| 12 h | 16.877 | 15.772 | +1.105 |
| 24 h | 14.188 | 13.757 | +0.431 |

No different weather-input protocol explains these within-v2j differences in the source. The differences reflect distinct model definitions, validation-selected configuration, and seed variability; this is not a matched isolated ablation of wind conditioning. The one-hour difference is small; at longer horizons the wind-conditioned model is worse in pooled MAE. Do not call this a large unexplained gap. Historical ST-PIGNN versus v2m MLP/TCN is a separate cross-protocol comparison and cannot be treated as the same controlled benchmark.

## Repeated test exposure and selection provenance

The same Bengaluru test interval and 14,583 targets were examined across numerous W-series and corrected v2 experiments, followed by post-hoc physics, attribution, spatial, citywide, and publication analyses. The current 17-variant table is a recomputation of saved prediction files; it is not a fresh prospective comparison. For v2j neural variants, LR selection used validation data and a frozen five-seed schedule, but the test period had already been repeatedly exposed across prior experiments. Baseline rows generally have one deterministic fit/value, while neural model rows have five seed runs. v2m MLP/TCN used a distinct cutoff-safe weather protocol and underwent a separate fixed benchmark.

Detailed row-level protocol and source differences are recorded in the complete CSV table. The figure shows a selected readable subset and its separate protocols; F03b shows all 17 retrospective variants. Negative (R^2) and unfavorable model comparisons are retained.
