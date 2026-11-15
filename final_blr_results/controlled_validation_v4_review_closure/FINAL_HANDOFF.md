# Controlled V4 review closure — research handoff

**Terminal status:** saved-prediction audits complete; all 30 corrected, predeclared six-hour sensitivity fits complete; validation and one-time exposed-test scoring complete; numerical figures, tables, penalty gradient replay, manifests and verified local archive complete. No active V4 job remains. The work is exploratory research evidence for supervisor review, not manuscript text or independent confirmation.

## Essential findings

- The historical v2j benchmark uses centered weather with a c+30-minute record after forecast issue c; same-hour pollutant aggregation can also admit post-issue readings. Its performance is superseded for forecast-origin-safe claims. The V3 repair shifts pollutant features one row back and uses a strictly prior anchor, but weather release and sensor ingestion latencies remain unknown.
- V3 has 16 complete methods across 1/3/6/12/24h, with 14,583 common observed target pairs per horizon. The complete 80-row register and 20 frozen wind contrasts are included. Graph-architecture comparisons on the exposed test have some favorable point estimates but do not establish graph necessity.
- At six hours, true-wind λ=0.06 MAE is 15.366 µg/m³; λ=0 is 15.494, with a paired difference −0.129 and block CI spanning zero. New reverse, full shuffle, constant north, λ=0.3, λ=1.0 and one-batch magnitude-matched Laplacian controls were fitted for all five fixed seeds. True wind beats reverse and full shuffle in ensemble MAE, but constant north and matched Laplacian are better. Larger true-wind λ worsens MAE. See `ADDITIONAL_WIND_CONTROLS.md` for every contrast and seed count.
- The post-hoc h6 actual-wind ordering-violation frequency is 24.979% for true wind versus 24.600% for λ=0 on 5,817 common observed-endpoint arcs. Mean squared positive violation magnitude is lower for true wind. One frozen-batch replay gives a 3.98% weighted directional-to-supervised gradient norm ratio at the selected true-wind checkpoint. Neither diagnostic establishes mass conservation or atmospheric causality.
- The test window has 14,583 observed pairs out of 67,320 possible station-hours (21.662% full-graph coverage); four stations have zero test targets. Historical 31.208% uses a narrower 11-station/177-observed-day denominator. Six-hour training PM2.5 input slots are 84.895% imputed and test slots 76.719% imputed. Validation/test observed means are 24.970/44.426 µg/m³.

## Recovery

Read `RESUME.md` and `REPRODUCIBILITY.md`. Source data/checkpoints are pinned by `SOURCE_HASHES.csv`, `verification/CHECKPOINT_MANIFEST.csv` and `verification/PREDICTION_MANIFEST.csv`. The new V4 selected checkpoints and all lossless new prediction arrays are inside the local archive. Restart-only partial files and invalidated checkpoint tensors remain at their listed local paths. `verification/VERIFICATION.md` records completed checks. No V3 training or test scoring should be rerun merely to inspect this package.

Scientific decision: the targeted controls yield **mixed physical-specificity evidence**, with no independent forecasting confirmation. Historical results and negative findings are preserved. Further confirmatory work would require a genuinely untouched temporal/geographic test and verified forecast-source availability, outside this authorized round.
