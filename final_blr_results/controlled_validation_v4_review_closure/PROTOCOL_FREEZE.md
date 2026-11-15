# V4 review-closure protocol — frozen before new training

Status: exploratory sensitivity campaign on the previously examined Bengaluru test interval. The corrected V3 array, station graph, feature protocol, architecture, training and validation chronology, target masks, and five seeds are fixed. No independent confirmation is possible here.

## Saved-data audits

Recompute the complete 16-method by five-horizon benchmark, the frozen 20 wind contrasts, and 15 architecture contrasts (unregularized GINEConv–GRU minus GRU-only, TCN, MLP at five horizons) from aligned saved per-pair predictions. Use the V3 seven-observed-day moving-block bootstrap (2,000 draws), 100,000-draw non-overlapping seven-day block sign-flip, and Holm correction within the predeclared 15-member architecture family. Keep the V3 20-member wind family unchanged. Report five seed-matched differences separately. All p-values remain exploratory.

Anchor age uses the latest genuinely observed PM2.5 at a time strictly earlier than the forecast issue. Buckets: 1 hour, 2–3, 4–6, 7–12, 13–24, over 24, and no previous observation. Compute descriptive pair-weighted errors by bucket and per-station age summaries. Do not call input imputation an observed target.

## New six-hour sensitivity only

The source is the repaired V3 causal array (`bd08d733f924387da82e758d1060703dfcdd121f360b7e8765189d8b7446e202`), 15 nodes, 60 directed station arcs, 12 hours × 18 input channels, train/validation/test periods and target masks as in V3. All variants share the V3 GINEConv–GRU backbone, seed-specific initialization, 512-hour batch, AdamW learning rate 0.0003 and weight decay 0.01, gradient clipping 0.3, maximum 30 epochs, five-epoch patience, selection from epoch 10 onward by validation MAE, and five-epoch linear lambda warmup. The five fixed seeds are 11, 23, 37, 51, 79. Predictive weather inputs are identical across variants. The exposed test set is scored only after all selected checkpoints and validation diagnostics are frozen.

Six new conditions, 30 fits total:

1. `reverse_wind_006`: transport-to bearing rotated +180°, λ maximum 0.06.
2. `constant_north_006`: fixed transport-to bearing 0° (north), λ maximum 0.06.
3. `full_shuffle_006`: one fixed training-hour permutation of regularizer wind masks with RNG seed 4404, shared by seeds and epochs; λ maximum 0.06. Validation/test predictive features and diagnostic wind remain unchanged.
4. `true_wind_03`: true mask, λ maximum 0.3.
5. `true_wind_10`: true mask, λ maximum 1.0.
6. `laplacian_matched`: Laplacian loss with λ maximum calibrated **before training** from the ratio of mean raw true-directional to raw Laplacian penalties on one frozen training batch evaluated using the V3 six-hour seed-11 unregularized checkpoint. No test labels enter calibration. Record both raw means, batch indices, checkpoint hash and resulting coefficient. This matches one training-batch magnitude, not gradient or whole-training exposure.

V3 six-hour zero, true-wind 0.06 and Laplacian 0.06 checkpoints are fixed comparators; they will not be retrained. All new fits use a separate V4 directory, with atomic per-epoch partial checkpoints, logs, completion markers and a single-instance lock. New runs have no test access. The primary new exploratory comparison family is true-wind 0.06 minus each of the six new conditions, with Holm correction across six tests; report all directions and seeds. No selecting a preferred condition by test outcome. No expansion to other horizons.

Resource stop: one V100; at most four GPU-hours and 2 GiB new checkpoint storage. A failed cutoff-integrity or numerical test stops new training. A projected breach of budget stops remaining cells, which are listed NOT RUN. Raw and weighted penalties, mask exposure, zero-mask batches, validation errors, selected epochs and fit time are logged. The diagnostic violation threshold is 0.05 in standardized transformed target units, with only wind-eligible arcs whose endpoint targets are both observed.

This protocol may be amended only in a new numbered file with reason and timing. No amendment may use exposed test results to choose controls or coefficients.
