# Captum Integrated Gradients methodology

## Checkpoint gate and separate protocol versions

The final v2j training record stores prediction parquets but its `model_configurations.csv` explicitly says `checkpoint_path=NONE SAVED`. Consequently, exact v2j physics/λ0/Laplacian weights cannot be recovered for gradients. Do not attribute v2c weights as if they were v2j. This package reports two separately labeled saved-weight analyses:

1. **v2c h=1 corrected ST-PIGNN:** five historical corrected checkpoints, 13 input channels, 96 hidden units, directed station kNN graph, matching v2c per-pair prediction artifact. Five seeds, three stations × first/median/last eligible h1 test time. Primary baseline is each station/channel's training-time mean repeated across the 12 lags; a zero-input sensitivity baseline is computed for seed 11. Strict checkpoint load and prediction tolerance ≤1e−4 µg/m³ are required. This is older protocol-specific IG, not v2j.
2. **v2r h=6 outer-LOSO corrected ST-PIGNN:** saved corrected 18-channel checkpoints (seed 11, 96 hidden units, 12-hour history, 4-NN station graph) for three sorted first/median/last scored held-out station IDs. Each outer model excludes the held-out station target labels and target-derived training/anchor data. For each, choose first/median/last observed h6 test targets by mask/time only. This is post-hoc analysis on the repeatedly exposed Bengaluru test period, not independent confirmation.

## v2r wrapper and forecast-time validity

For each held-out fold the feature builder and scaler are reconstructed using the exact fold config and source `src/stpignn.data_v2.build` call (`weather_half_hour_rule=True`, `weather_cutoff_safe=True`). The selected h6 history indices are `target−6−[11,…,0]`; all are at or before the forecast cutoff `target−6`. For a held-out site's node, five pollutant channels are forced to zero, missingness indicates the withheld history, and its persistence anchor uses a train-only fallback. Its observed heldout measurement is not included in input, fit, imputation, anchor, or the checkpoint.

The wrapper computes the exact model residual plus cutoff anchor in train-standardized log1p space, applies `expm1`, and returns the selected station's scalar PM2.5 prediction in µg/m³. Graph edge index/length, station identity, and any non-target output channels remain fixed. IG attributes all 12 × 15 × 18 station/time/channel input values for this scalar. These are feature-input attributions; the method does not attribute edge weights or graph topology.

The primary baseline is the training-period mean for each station/channel in the fold's fitted input space, repeated across 12 lags. Sensitivity baseline zeros the first 13 environmental channels while retaining observed missingness and calendar channels. Baselines are fixed by rule, not attribution outcome. Captum uses 64 Gauss–Legendre integration steps, `internal_batch_size=1`, CPU float32, eval mode, one PyTorch thread, and fixed seeds. Each record stores signed tensors; CSV aggregates signed and absolute values separately. Temporal summaries aggregate over station and feature axes; station summaries aggregate over lag and feature axes. No lag attribution is called attention.

Wrapper output must agree with the exact outer-fold `station_forecasts_all.parquet` heldout prediction within 1e−4 µg/m³ before attribution. Completeness delta is `f(x)−f(b)−sum(IG)`, with relative denominator `max(1,|f(x)−f(b)|)`. Frozen quality flags: absolute delta >0.05 µg/m³ or relative delta >1%; any nonfinite record is a failure. Per-record `.npz` tensors and metadata are written atomically to permit supervised restart without repeating completed attributions.

## Interpretation boundary

IG describes baseline-relative input sensitivity in these saved models. It does not establish causal influence, feature importance under intervention, atmospheric mass conservation, Gaussian plume validity, street-level accuracy, or physical wind/terrain dependence. The h1 v2c and h6 v2r attributions cannot be pooled as one model/horizon family. The corrected final v2j checkpoint-specific IG, λ0 comparison, and Laplacian comparison remain unavailable because matching v2j checkpoints were not saved.
