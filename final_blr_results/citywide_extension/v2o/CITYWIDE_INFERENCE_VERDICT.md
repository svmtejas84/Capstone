# v2o independent verdicts

| Question | Verdict | Evidence and boundary |
|---|---|---|
| Road graph structural integrity | SUPPORTED | v2k: 154,902 nodes, 393,089 raw directed rows, 424,550 message arcs, one connected component. |
| Road-node feature completeness | UNSUPPORTED for corrected ST-PIGNN | Complete road geometry/SRTM only; 154,880 nodes lack archived temporal rows, and observed pollutant lags/anchors are absent. |
| Spatial estimator validity | MIXED | Fixed IDW is a mathematically explicit same-time estimator; held-out pooled MAE 23.133 on 84.5% coverage, worse than train-only mean 21.943 on matched pairs. |
| Full-city computational execution | SUPPORTED for IDW | Three snapshots × 154,902 road nodes, 464,706 finite complete rows, exact prefix checks. |
| Independent spatial generalization | NOT ESTABLISHED | Eleven observed Bengaluru station sites on an exposed test period; no independent road monitors or new city. |
| Citywide forecast validity | UNSUPPORTED | Same-hour support readings make these retrospective estimates, not lead-time forecasts. |
| Uncertainty calibration | NOT EVALUATED | Distance/hull/support are uncalibrated diagnostics; poor support flags 84.9–90.6% of nodes. |
| ST-PIGNN-specific citywide inference | BLOCKED | No matching corrected weights or honest compatible road histories/edges. Zero road nodes received ST-PIGNN output. |

**Terminal v2o outcome:** citywide *retrospective interpolated estimates* were computed and archived with weak station-level predictive diagnostics and poor spatial support. No validated street-level concentrations, neural road forecasts, exposure routing gains or independent confirmation are claimed. This closes v2o and permits the separately scoped v2p method-development phase.
