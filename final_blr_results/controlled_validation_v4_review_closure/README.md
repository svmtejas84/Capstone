# Controlled V4 review closure — evidence index

This directory is a separate exploratory evidence package. The V3 and earlier Bengaluru experiments are frozen. No IEEE manuscript text or London work is included. Read `FINAL_HANDOFF.md` and `FINAL_SCIENTIFIC_VERDICT.md` first, then the audit documents and `OPEN_ISSUES.md`. The September 2025–March 2026 Bengaluru test period was previously examined and is **not independent validation**.

| Evidence | Files |
|---|---|
| Frozen design, correction, resource ceiling | `PROTOCOL_FREEZE.md`, `PROTOCOL_AMENDMENT_01.md`, `RESOURCE_PLAN.md`, `LAPLACIAN_CALIBRATION.json` |
| Historical versus repaired data | `LEAKAGE_LINEAGE_AND_SUPERSEDED_RESULTS.md`, `FORECAST_ORIGIN_AND_LEAD_TIME_AUDIT.md`, `SOURCE_HASHES.csv` |
| Complete V3 methods and scores | `COMPLETE_MODEL_AND_BASELINE_REGISTER.csv`, `tables/COMPLETE_FIVE_HORIZON_EVALUATION.csv/.tex`, `V3_METHOD_IMPLEMENTATION_REGISTER.md` |
| Frozen 20 wind contrasts | `COMPLETE_20_CONTRAST_RESULTS.csv`, `SEED_LEVEL_REGULARIZATION_RESULTS.csv`, `DIRECTIONAL_CONTROL_STATISTICAL_AUDIT.md`, `PENALTY_DIAGNOSTICS_V3.csv` |
| Architecture comparisons | `GRAPH_ARCHITECTURE_COMPARISON.md`, `statistical_analysis/GRAPH_ARCHITECTURE_CONTRASTS.csv`, `statistical_analysis/GRAPH_ARCHITECTURE_SEEDS.csv` |
| Coverage and anchor age | `COVERAGE_AND_BASELINE_AUDIT.md`, `COVERAGE_AND_SHIFT.csv`, `ANCHOR_AGE_AND_ERROR_AUDIT.md`, `ANCHOR_AGE_AND_ERROR.csv`, `ANCHOR_AGE_PER_STATION.csv` |
| New six-hour V4 controls | `ADDITIONAL_WIND_CONTROLS.md`, `TRAINING_SUMMARY.csv`, `metrics/V4_SENSITIVITY_SCORES.csv`, `statistical_analysis/V4_SIX_CONTRASTS.csv`, `statistical_analysis/V4_SEED_CONTRASTS.csv` |
| Penalty mechanism | `PENALTY_EFFECTIVENESS_AUDIT.md`, `PENALTY_DIAGNOSTICS_V4.csv`, `PENALTY_GRADIENT_REPLAY.csv` |
| Figures and verification | `figures/F1`–`F5` in PNG/PDF/SVG, `verification/`, `REPRODUCIBILITY.md` |
| Recovery | Local `training/final/` selected checkpoints and epoch histories, `predictions/` per-pair arrays, `logs/` supervisor records, `RESUME.md` |

The archive intentionally excludes epoch-by-epoch `partial.pt` restart files and large historical V3 source datasets. Selected V4 `best.pt` checkpoints and all V4 prediction NPZs are included and individually checksummed. Pre-amendment full-shuffle attempts are preserved locally and listed as invalid, never scored.
