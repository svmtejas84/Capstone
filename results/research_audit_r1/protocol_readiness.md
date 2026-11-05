# Protocol readiness — engineering handoff, not a new protocol

Source commit examined: `dca4bcce690da6b7865702f91d15dd2e06b6ef75`. This records history for supervisor review. No second-city experimental protocol or model redesign is finalized.

The six historical post-hoc deviations must remain visibly labelled:

1. **Residual formulation:** after poor Gate B/C performance, v2c moved to residual-over-causal-persistence prediction and repaired lag scaling (`results/codex_log/DECISIONS.md:15-21`).
2. **Extended learning-rate grid:** v2c expanded the LR grid to seven values for revised model selection (`DECISIONS.md:18-19`).
3. **Same-hour-yesterday baseline:** later W2/v2g comparisons added this strong seasonal baseline (`DECISIONS.md:28,33-35`).
4. **W6 anchor modification:** train-mean/IDW blend and seasonal-bias adjustments were added after LOSO weaknesses (`DECISIONS.md:30,32`; `results/loso_decision_v2g.csv`).
5. **Lambda sweep:** W7 varied physics weights over five horizons after earlier controls; each weight had validation LR selection (`DECISIONS.md:34-36`; `results/lambda_sweep_v2g.csv`).
6. **Laplacian-separated W7 criterion:** the earlier W7 criterion was superseded and later corrected so Laplacian hits are a separate control, disclosed after interim test intervals had been inspected (`DECISIONS.md:34,36`; `results/lambda_verdict_v2g.json`).

There has been repeated Bengaluru test-set exposure across Gate B/C, diagnostics, W2–W8, protocol inflation, conformal and group-DRO. This makes the historical Bengaluru test set an exploratory benchmark for any new design. None of the six deviations was preregistered retrospectively. Existing within-run validation decisions should be described accurately, but a future confirmatory claim requires a genuinely untouched external evaluation design approved by the supervisor.

## Preconditions for supervisor decision

- Resolve the suspected Asia/Kolkata-to-UTC weather alignment from raw response metadata or a reproducible independent API check, then specify whether historical metrics remain descriptive only. Do not silently rewrite them.
- Decide whether the fixed ≥30 reference-grade hourly station threshold is retained. London has no verified eligibility count; Copenhagen's known official central network is far below 30. Any threshold change alters the study question.
- Define physically meaningful Q if a physics-source claim is intended, including pollutant-specific rates, units, spatial allocation, hourly profiles and uncertainty. LAEI/SPREAD annual maps alone do not provide hourly Q.
- Specify a prospective city dataset, instrument class, UTC/flag handling, weather-grid mapping, spatial split, baseline information sets, calibration scheme, missing-data rule and decision criterion before inspecting new-city test scores.
- Decide whether source-code effects found here require correcting the implementation before any prospective run; preserve historical outputs and audit trail.

**Current readiness:** NOT READY for London/Copenhagen training. This is a data and protocol block, not a prediction about model accuracy. The supervisor should approve any methodological change after reviewing the audit; no training authorization is implied by a later data gate.
