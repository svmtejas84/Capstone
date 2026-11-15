# Controlled validation v3: methods and interpretation rules

## Data and population

The experimental object is the corrected Bengaluru **15-station, 60-directed-edge** forecasting graph, not the historical 154,902-node road graph. Source timestamps span 2022-01-01 through 2026-03-28 UTC. The chronological train, validation and exposed historical test intervals are fixed in `configs/data_v2.yaml`; all five forecast horizons (1, 3, 6, 12, 24 hours) and five seeds (11, 23, 37, 51, 79) are retained. Test metrics cover observed target station-hours, including sites without a recent target-station input; the train and validation loss masks additionally require an eligible observed input at the issue hour. Per-station reporting must show the actual count and distinguish this temporal test from spatial leave-one-station-out evaluation.

The initial v2m array failed a raw-data future-mutation test: raw station readings after an issue time could enter the feature row carrying that same hour label through hour flooring. The initial 20 selection and 54 final cells were stopped and quarantined before test scoring. `PROTOCOL_AMENDMENT_02.md` specifies the repaired input: pollutant channels and their missingness provenance at feature hour c are taken from row c−1; the PM2.5 residual anchor uses observations strictly before c. Targets and their observed masks retain their original timestamp. The repaired array hash is `bd08d733f924387da82e758d1060703dfcdd121f360b7e8765189d8b7446e202`. Historical weather records are selected by record timestamp at or before feature time, typically c−30 minutes. Neither meteorological release time nor station ingestion latency was archived, so operational availability is **unverified**. This is a timestamp-causal retrospective historical-observation experiment.

No sufficiently long untouched later Bengaluru interval was available in the saved source; the September 2025–March 2026 test interval has been inspected in earlier research. New test analyses are therefore exploratory, even when the training and evaluation protocols are frozen before scoring.

## Models and optimization

The principal model is the existing two-layer GINEConv–GRU with 12 historical hourly rows, 18 channels, 64 hidden units and a standardized log1p residual output. The graph has four geographic outgoing neighbors per station. The supervised loss is masked squared error on the standardized log1p target. Inputs and target masks are identical for all matched regularizer conditions. `scripts/train_controls.py` records each cell, epoch history, checkpoint, source-array hash and validation-selected epoch. AdamW weight decay is 0.01, batch size 512, maximum 30 epochs, gradient clipping 0.3, patience five, and minimum epoch 10 for checkpoint selection. The shared learning rate at each horizon was selected from four prespecified candidates using seed-11 λ=0 validation MAE, then held fixed for all regularization variants and seeds. Every matched seed resets initialization and batch order before fitting.

Regularizer conditions are λ=0, actual-wind directional hinge, within-month shuffled-wind hinge, +90° rotated-wind hinge, and a direction-independent Laplacian penalty. Only the regularization-mask wind is changed for shuffle/rotation; predictive weather channels remain unchanged. The primary schedule is λ(epoch)=0.06 min(1,epoch/5), reaching its nominal strength before checkpoint eligibility. The historical 25-epoch schedule is not reproduced as a primary treatment. The directional loss penalizes positive predicted downwind-minus-upwind concentration differences on selected station arcs after a sigmoid length factor; it is a heuristic, **not** a mass balance or advection–diffusion solver. Laplacian and directional penalty magnitudes, active arcs, zero-effective batches and selected effective λ must be reported rather than assumed equivalent.

Same-information neural baselines are MLP, temporal CNN, GRU-only, vanilla GCN, GRU–GCN and adaptive graph. Each uses the repaired 18-channel tensor and the same validation-only learning-rate grid and five seeds. Classical controls are training-only station mean, hour/day climatology, weather ridge, persistence and same-hour yesterday. Exact previous-day observations are used only if strictly before issue; missing observations and the 24-hour horizon use a strictly prior causal anchor. These classical controls are deterministic and do not share an optimizer with neural models.

The saved `weather_ridge` control uses feature channel 0 (repaired past PM2.5), channels 5–17 (weather/static, missingness and calendar), and a train-only target fit. It is accurately described as a **lag/weather ridge**, not a weather-only model. The machine-readable key is retained for stable artifact naming.

## Evaluation and statistical limits

The one-time evaluator saves each seed's raw paired prediction, target, UTC time index and station index before computing seed and mean-prediction-ensemble MAE, RMSE and R². Baseline predictions must match the same target indices. The frozen primary family has 20 true-wind-minus-control ensemble MAE contrasts. A negative difference favors the true-wind condition. Exploratory 95% intervals use 2,000 seven-observed-day moving-block bootstrap samples; exploratory two-sided p-values use 100,000 nonoverlapping seven-day block sign flips with an independent fixed RNG stream and Holm adjustment across 20 contrasts. Five-seed exact sign tests are separate, low-powered diagnostics. UTC days, seeds and station-hours are not independent cities. Per-station temporal MAE is descriptive; no new isolated-station training or external replication was performed.

The same true-wind cone may be applied post hoc to saved predictions for a descriptive ordering-violation rate, restricted to arcs for which both endpoint target observations exist. It is narrower than the all-node training penalty, uses a reported normalized threshold and raw-equivalent units, and cannot establish atmospheric transport validity. Operational and independent spatial or temporal generalization remain outside the evidence of this campaign.

## Exact entry points

- Source data repair and mutation test: `scripts/build_causal_array.py`, `scripts/test_full_future_mutation.py`.
- V100 smoke and contexts: `scripts/smoke_gpu.py`; core fitting: `scripts/train_controls.py`; baseline fitting: `scripts/train_baselines.py`.
- Supervision: repository `scripts/run_supervised.sh` and v3 `scripts/run_stage.sh` / `scripts/run_baseline_stage.sh`.
- Checkpoint integrity: `scripts/verify_training.py`, `scripts/verify_baselines.py`.
- One-time scoring: `scripts/evaluate_controls.py`, `scripts/evaluate_baselines.py`.
- Paired uncertainty and secondary diagnostics: `scripts/analyze_controls.py`, `scripts/secondary_diagnostics.py`, `scripts/wind_cone_diagnostics.py`, `scripts/data_summary.py`.
- Result tables and figures: `scripts/build_results.py`.

All paths above are relative to `final_blr_results/controlled_validation_v3/` unless prefixed with `configs/` or identified as repository `scripts/`. Exact source SHA-256 values are in `data_manifests/source_checksums.csv`; run-specific checkpoint hashes are in each `COMPLETE.json` record. Large data arrays and checkpoints remain local and must be included in or linked from the final verified archive; a Git push alone does not preserve them.
