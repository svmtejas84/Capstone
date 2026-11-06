# v2q neural citywide verdict

| Question | Verdict | Evidence |
|---|---|---|
| Original notebook and architecture recovered | YES, historical | 26 cells statically inspected; exact GINE–GRU source and strict-loading root checkpoint documented. |
| Original model reproducible as implemented | PARTIAL | Archived `results/full_replay_parity.json` reports bounded replay parity; current notebook differs from the older audit hash and contains no saved outputs. |
| Original model valid as lead-time city forecast | UNSUPPORTED | Same-hour input/target, modulo timeline lookup, 154,880 copied node histories, scaled wind angle, omitted partition arcs. |
| Compatible original weights found | YES, historical only | Root best checkpoint is 16-input/16-edge, 98,497 parameters; not corrected v2j. |
| Forecast-safe spatial decoder validation | NOT RUN | Necessary cross-fitted support-station forecasts and fold checkpoints are absent. |
| Full-city v2q neural inference | BLOCKED | Zero nodes/timestamps; no validated forecast-origin road input or tested decoder. |
| Independent roadside accuracy | NOT EVALUATED | No independent road-level PM2.5 observations. |

The v2q scientific blocker is **missing cutoff-safe, target-isolated station-to-road forecast inputs**, not a failure to instantiate a neural tensor. The smallest path forward is to create audited cross-fitted station forecasts under an approved bounded LOSO plan, then compare mean, IDW and compact decoder on identical future targets. Do not use legacy city maps as forecasts or the v2o retrospective IDW run as a forecasting control. Preserve corrected W6 ST-PIGNN LOSO loss to ridge.
