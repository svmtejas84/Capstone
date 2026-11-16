# V5 engineering and evidence handoff

## Completion state

The isolated V5 campaign is **complete**. It contains 160 new selected-checkpoint fits, the 90-cell six-hour regularizer-strength grid (40 V3/V4 cells reused), 192 new prediction NPZ files, 240 complete score rows, 28 V5 paired ensemble contrasts, 140 V5 seed-level paired rows, 40 new-condition ordering diagnostics, nine CSV/LaTeX numerical table pairs and four PDF/PNG/SVG figure triplets. The branch is `research/controlled-validation-v5`; the frozen protocol SHA-256 is `64682686b29660ff336ed6893e257950ce25c3e03683f68de088f6a808825266`. The source causal array SHA-256 is `bd08d733f924387da82e758d1060703dfcdd121f360b7e8765189d8b7446e202`.

The one-time new-model Bengaluru test score was unlocked only after validation-only selection and remote commit `b80aa597d8cd89382720b64924986b890362749d`. The period was already exposed by prior research, so the result is exploratory. The V100 training fit record is 1.27761 hours, and selected/restart training files used 149,129,418 bytes at the pretest gate. The local checkpoint/prediction archive is verified separately; no independent USB backup is established.

## Principal numerical outcomes

- **Graph edges:** original graph versus self loops is favorable by point estimate at all five horizons, largest at 12 h (−0.891 µg/m³). The degree-preserving rewiring is close and better at 3, 6 and 24 h. At six hours with added daily-lag information held fixed, the original graph improves over self loops by 0.482 and over rewiring by 0.0485 µg/m³. General graph-topology necessity remains inconclusive. Full rows: `tables/T1_GRAPH_TOPOLOGY.csv`, `statistical_analysis/GRAPH_TOPOLOGY_CONTRASTS.csv`, `statistical_analysis/LAG_MATCHED_GRAPH_CONTRASTS.csv`.
- **Daily-lag information:** the augmented model improves over the frozen 12-hour unregularized model at 1, 3, 6, 12 and 24 h by 0.313, 0.854, 1.389, 0.441 and 0.389 µg/m³, respectively. At six hours it scores 14.105 versus 14.130 for same-hour-yesterday, with a paired interval crossing zero. At 24 h, no actual T−24 value is eligible at issue; the gain reflects fallback/age features. Full rows: `tables/T2_LAG_INFORMATION.csv`, `statistical_analysis/LAG_INFORMATION_CONTRASTS.csv`, `statistical_analysis/DAILY_LAG_SIMPLE_BASELINE.csv`.
- **Penalty fairness:** five-seed validation selected actual-wind λ=.06 and larger coefficients for the controls. The selected actual-wind procedure scores 15.366 µg/m³ at six hours versus 15.494 for zero and 15.688–16.629 for selected alternative penalty procedures. The true-versus-zero interval includes zero. Selected control gradients are substantially larger; constant north at common λ=.06 scores 15.272 and beats actual wind by point estimate. Physical specificity is unestablished. Full grid: `tables/T3_REGULARIZER_GRID.csv`, `metrics/FAIRNESS_GRADIENT_REPLAY.csv`, `statistical_analysis/FAIRNESS_SELECTED_CONTRASTS.csv`.
- **Data/diagnostics:** 14,583 test station-hour pairs at each horizon, from only 11 scored stations. Genuine one-hour anchors range from 95.37% of scored pairs at 1 h to 84.42% at 24 h. Training input-slot missingness remains high. The six-hour actual-wind model has lower positive ordering-difference magnitude than zero regularization but a slightly higher thresholded violation frequency; this does not measure conservation. Full rows: `ANCHOR_AGE_ALL_METHODS.csv`, `PENALTY_DIAGNOSTICS_COMPLETE.csv`, `PENALTY_DIAGNOSTICS_NEW_CONDITIONS.csv`.

## Navigation

1. `FINAL_SCIENTIFIC_VERDICT.md`: question-by-question classifications, paired intervals, negative findings and scientific limits.
2. `PROTOCOL_FREEZE.md` and `PROTOCOL_AMENDMENT_01.md`/`02.md`: pretest hypotheses, fixed cells and documented pretest corrections.
3. `DATA_ELIGIBILITY.md`, `FORECAST_LEAD_AND_INFORMATION_PARITY.md`, `COMPLETE_IMPLEMENTATION_REGISTER.md`, `METHODOLOGY.md`: cutoff, feature, architecture and regularizer facts.
4. `TRAINING_SELECTION_REGISTER.csv`, `metrics/FAIRNESS_GRID_VALIDATION.csv`, `metrics/FAIRNESS_VALIDATION_SELECTION.json`: all run selections and the validation-only strength choice.
5. `metrics/NEW_TEST_SCORES.csv`, `predictions/`, `statistical_analysis/`, `tables/`, `figures/`: per-condition metrics and lossless paired evidence.
6. `verification/PRETEST_GATE.md`, `verification/FINAL_VERIFICATION.md`, `verification/verification_summary.json`, `verification/release_checks.json`: real execution checks.
7. `REPRODUCIBILITY.md` and `RESUME.md`: exact commands, process logs, restart restrictions and external V3/V4 dependencies.
8. `OPEN_ISSUES.md`: unresolved scientific questions and backup limits.

## Recovery commands

From `/home/jupyter-1nt23cb058/Capstone`:

```bash
git switch research/controlled-validation-v5
git status --short
sha256sum final_blr_results/controlled_validation_v5/PROTOCOL_FREEZE.md
sha256sum final_blr_results/controlled_validation_v3/data_manifests/data_v3_causal_arrays.npz
PYTHONPATH=. MPLCONFIGDIR=/tmp/mpl_v5 python final_blr_results/controlled_validation_v5/scripts/verify_v5.py
PYTHONPATH=. MPLCONFIGDIR=/tmp/mpl_v5 python final_blr_results/controlled_validation_v5/scripts/verify_release.py
```

The guarded scorer **must not** be run again after `metrics/NEW_TEST_SCORES.csv` exists; saved predictions and scores are the authoritative V5 exposed-test record. To regenerate numerical tables and figures without training or rescoring, use `scripts/build_results.py` and `scripts/plot_v5.py` with `PYTHONPATH=.` and `MPLCONFIGDIR=/tmp/mpl_v5`. See `REPRODUCIBILITY.md` for all source and archive commands. Preserve V3/V4 checkpoint paths; the V5 ZIP excludes their raw data and restart-only `partial.pt` files.
