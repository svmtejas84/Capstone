# V3 implementation facts, from source and saved records

| Fact | Verified implementation | Evidence |
|---|---|---|
| Graph | 15 stations; directed 4-nearest-neighbor graph, 60 arcs; projected coordinates; edge feature is distance in metres for the corrected GINEConv–GRU | `scripts/benchmark_v2j.py:Context.__init__`; `src/stpignn/station_graph.py` |
| Input | 12 hourly rows × 15 stations × 18 channels; 13 base channels plus PM2.5 imputation flag plus four cyclic hour/day channels | `scripts/benchmark_v2j.py:Context.__init__`; `src/stpignn/data_v2.py:build` |
| Base feature channels, order 0–12 | lagged PM2.5; PM10; NO2; SO2; CO; wind speed; wind gust; temperature; relative humidity; surface pressure; wind direction sine; wind direction cosine; SRTM station elevation | `src/stpignn/data_v2.py:POLLUTANTS,WEATHER,build`; V3 array feature width 13 |
| Derived channels, order 13–17 | `lag_is_imputed`; sin(hour); cos(hour); sin(day-of-week); cos(day-of-week) | `scripts/benchmark_v2j.py:Context.__init__`; `controlled_validation_v3/scripts/smoke_gpu.py` |
| Pollutant-time repair | Each of channels 0–4 at feature hour c comes from source row c−1; anchor uses the latest observed PM2.5 strictly before c | `controlled_validation_v3/scripts/build_causal_array.py`; `PROTOCOL_AMENDMENT_02.md` |
| Weather | Most recent archived half-hour record timestamped no later than feature hour; operational release unknown | `src/stpignn/data_v2.py:build(weather_cutoff_safe=True)`; `DATA_ELIGIBILITY.md` |
| Wind mask | Wind FROM compass degrees +180° to transport TO; edge bearing clockwise from north; active if within 37.5° half-cone, i.e. 75° full cone; NaN wind yields inactive | `scripts/benchmark_v2j.py:Context.__init__`; `src/stpignn/physics_v2.py` |
| Calm wind | The mask does not apply a wind-speed threshold; a finite direction remains mask-eligible even when speed is zero. The separate wind-along predictor feature is speed-scaled. | `scripts/benchmark_v2j.py:Context.__init__` |
| Wind time | Forecast issue row c=T−h, not target row T | `controlled_validation_v3/scripts/train_controls.py:train_cell` (`masks[index-ctx.horizon]`) |
| Wind reference | The single archived weather series at station index 0 is shared across station graph arcs; no street-scale wind field | `scripts/benchmark_v2j.py:Context.__init__` (`z["features"][:,0,5]`, `raw_wind_degrees`) |
| Directional penalty | Mean over active arc-hours of squared positive destination-minus-source predicted PM2.5 difference, multiplied by sigmoid(edge length in km) before squaring. Predicted physical PM2.5 is divided by training target SD before penalty; it is not a dimensioned mass flux. | `src/stpignn/physics_v2.py:batched_penalty`; `controlled_validation_v3/scripts/train_controls.py:train_cell` |
| Laplacian penalty | Mean squared prediction difference over all directed arcs. Original coefficient max 0.06; V4 one-batch magnitude-matched coefficient separately 0.02184366. | same sources; V4 `LAPLACIAN_CALIBRATION.json` |
| Supervised loss | Mean squared error of standardized log1p target over observed/eligible labels; validation selection uses physical-unit MAE | `controlled_validation_v3/scripts/train_controls.py:train_cell`; `scripts/benchmark_v2j.py:Context.evaluate` |
| Optimizer | AdamW, weight decay 0.01, batch 512 target hours, gradient clip norm 0.3 | `controlled_validation_v3/scripts/train_controls.py:BASE_CFG,train_cell` |
| LR selection | Grid 0.0001, 0.0003, 0.001, 0.003. One seed-11 unregularized GINEConv–GRU fit selects a shared LR by validation MAE per horizon; each baseline architecture uses its own seed-11 validation selection. | `controlled_validation_v3/scripts/train_controls.py:main`; `train_baselines.py:main`; `verification/baseline_selected_lrs.csv` |
| LR asymmetry | Regularized controls inherit the unregularized seed-11 LR; this is matched optimization but not equal variant-specific tuning opportunity. A shared LR selected this way may favor λ=0. | same code; scientific inference limitation |
| Epochs | Maximum 30, minimum selected checkpoint epoch 10, patience 5; λ(e)=0.06 min(1,e/5) for original controls, so every selected regularized V3 checkpoint reached 0.06. | `train_controls.py:train_cell`; `metrics/training_diagnostics.csv` |
| Completed fit count | 20 valid control LR-selection, 125 valid control final, 120 baseline LR-selection, 150 baseline final = 415. Four of 275 valid final cells ran to epoch cap; selected best epoch range 10–29. Another 74 pre-repair candidate fits were quarantined before test scoring. | `metrics/training_diagnostics.csv`; `verification/FINAL_VERIFICATION.md` |
| Corrected GINEConv–GRU parameters | 43,393 on 18 channels, hidden width 64 | `verification/smoke_gpu.json` |
| Baseline parameters | GRU-only 16,193; vanilla GCN 5,441; ST-GRU-GCN 26,241; adaptive graph 24,434; MLP 18,113; TCN 16,641 | `controlled_validation_v3/RESUME.md` baseline smoke; `COMPLETE_MODEL_AND_BASELINE_REGISTER.csv` |
| Adaptive graph | Two temporal dilated Conv1d layers produce station embeddings. A learned 15×16 node-embedding Gram matrix yields pair logits, modified by a learned scalar times wind-along values on kNN edges, then row softmax and spatial weighted average. This is learned affinity, not a measured atmospheric transport graph. | `controlled_validation_v3/scripts/train_baselines.py`; `src/stpignn/models_v3.py:AdaptiveGraphST` |
| Wind-along scaling caveat | `Context.__init__` denormalizes V3/V2m weather channel 5 with the historical v2j fit when constructing a wind-along edge input. The v2j wind-speed mean/SD are 3.343475/1.423970; V2m values are 3.343644/1.458159. The corrected GINEConv–GRU backbone does not consume this wind-along tensor; the adaptive-graph baseline does. This is a small numeric scaling mismatch in a derived edge input, not a changed source timestamp. | `scripts/benchmark_v2j.py:Context.__init__,make,forward`; `results/data_v2j_fit.json`; `final_blr_results/baselines/v2m/data/data_v2m_fit.json`; `src/stpignn/models_v3.py:AdaptiveGraphST` |
| Target/scoring | Observed PM2.5 only; 14,583 common exposed-test station-hour pairs per horizon, 11 stations scored; four no test targets | `metrics/data_coverage_shift.csv`; saved prediction triples |

The V3 training mask includes only targets with a source observation at the issue row under the delayed-array semantics, while the exposed test score uses every observed target at the target hour. This changes the training versus test population and should be considered in interpretation. Actual sensor ingestion and archive publication times were not recorded. The model does not certify operational issue-time availability.


## V5 exact extensions (frozen before test scoring)

The preceding V3 implementation facts are copied from the frozen V4 audit; V5 does not alter those sources. V5-specific training code is `scripts/train_graph_lag.py` and `scripts/train_fairness.py` in this directory. Original G0 and L0 are V3 `zero` checkpoints. The neural shape and optimizer remain the same except for the explicitly declared lag conditions:

| Condition | Input shape per batch | Directed arcs | Input channels | Parameter count | Geometry |
|---|---|---:|---:|---:|---|
| G0 original station graph | B×12×15×18 | 60 | 18 | 43,393 | Original UTM kNN distances |
| G1 self loops | B×12×15×18 | 15 | 18 | 43,393 | Zero-length loops only |
| G2 fixed-seed rewired | B×12×15×18 | 60 | 18 | 43,393 | Recomputed UTM endpoint distances |
| L1 lag-24 augmented | B×12×15×21 | 60 | 21 | 43,585 | Original graph |
| L2 36-hour history | B×36×15×18 | 60 | 18 | 43,393 | Original graph |

G2 swaps destinations of two directed arcs only when the resulting arcs are distinct and non-self, preserving every node's directed in/out degree. Fixed RNG seed 5505. G1 removes all interstation messages but leaves GINE/GRU parameters unchanged. L1's three channels appear only at the final temporal row: standardized log1p daily-lag/fallback value, genuine daily-lag indicator, and capped actual source age. An observed T−24 row is accepted only when strictly earlier than issue. L2 left-pads the first hours with source row zero, preserving V3 train/validation/test target masks. Both V5 stage runners use seed 11/23/37/51/79, learning rates `{1:.001,3:.0003,6:.0003,12:.0003,24:.0003}`, AdamW 0.01 weight decay, batch 512, 30-epoch cap, best validation MAE at epoch >=10, patience 5. Same seed controls initial state where parameter shapes match. [SOURCE: V5 `scripts/train_graph_lag.py`, V3 `scripts/train_controls.py`, V5 `verification/preflight.json`.]

V5 six-hour fairness uses the same 43,393-parameter backbone and 60 original arcs. Five regularizer families are trained at λ=.3 and 1.0; historical λ=.06 cells and true-wind λ=.3/1.0 are reused. Family strength selection is the five-seed mean validation MAE, tie lower λ, before any new-model test scoring. Effective λ at selected epochs is the selected maximum because checkpoint eligibility starts at epoch 10 and warmup ends at epoch 5. Source code records epoch-specific raw supervised loss, raw and weighted penalty, directional arc count and zero-active-batch count; checkpoint-local gradient ratios require separate replay and are not inferred from loss magnitude. [SOURCE: V5 `scripts/train_fairness.py`, V3/V4 selected checkpoints, V5 `PROTOCOL_FREEZE.md`.]

All test inference remains exploratory because the Bengaluru period was previously examined. Weather release and station ingestion delays remain unverified. No new geographic holdout is part of V5.
