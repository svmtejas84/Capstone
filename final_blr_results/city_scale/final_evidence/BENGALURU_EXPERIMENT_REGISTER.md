# Bengaluru experiment register — frozen through v2n

| Round | Protocol and source | Artifact and outcome | Reuse limit |
|---|---|---|---|
| Original / Gate B–C | `results/gate_v2c.md`, `results/loso_decision_v2.json` | Lag defect repaired; station Gate C TIE against ordinary kriging, 11 scored sites | Earlier weather and post-hoc revisions; retain as historical |
| W1–W8 / v2g–v2h | `results/benchmark_v2g.md`, `results/loso_summary_v2g.csv`, `results/citywide_precheck_v2h.md` | Architecture/density/conformal/DEM studies; citywide weather-source precheck BLOCKED | Different historical information sets; no road accuracy |
| v2j | `results/benchmark_v2j.csv`, `results/loso_summary_v2j.csv`, `results/lambda_check_v2j.csv` | Corrected local-time weather; any-model fixed win h1/3/24; no W6 neural LOSO WIN | Centered c−30/c+30 weather includes post-cutoff value; no saved corrected neural weights |
| v2k | `final_blr_results/FINAL_HANDOFF.md`, `road_graph/graph_measurements_v2k.json`, `baselines/paired_architecture_comparisons.csv` | Road graph structurally valid; 35 matched architecture contrasts; corrected full-road inference BLOCKED | Topology is not predictive accuracy; exploratory test reuse |
| v2l | `final_blr_results/physics_audit/FINAL_PHYSICS_VERDICT.md` | Physics predictive effects mixed by horizon/seed; specificity/conservation unsupported | Saved v2j predictions only, no weight-level mechanism |
| v2m | `final_blr_results/baselines/v2m/FINAL_BASELINE_VERDICT.md`, `comparisons/primary_ten_comparisons.csv` | 50/50 MLP/TCN cells; no TCN contrast survives ten-test Holm | Cutoff-safe weather differs from historical ST-PIGNN inputs |
| v2n graph/feature/inference | `final_blr_results/city_scale/{graph,features,inference}/` | 154,902 road nodes; direct corrected full-city inference BLOCKED before forward pass; zero nodes inferred | Missing road histories/anchors and corrected checkpoint |
| v2n spatial | `final_blr_results/city_scale/spatial_validation/SPATIAL_VALIDATION_VERDICT.md` | Corrected W6 ST-PIGNN LOSS to ridge; 11 scored sites | Station-graph LOSO only |
| v2n IG | `final_blr_results/city_scale/explainability/CAPTUM_IG_RESULTS.md` | 228 Captum records for v2m MLP/TCN; 85 numerical quality flags | No corrected ST-PIGNN/physics IG; baseline-relative only |

The historical six post-hoc deviations, source commits, and missing artifact classes remain in `final_blr_results/archive/historical_results_register.md` and `final_blr_results/V2N_CODEX_HANDOVER.md`. This register is a map of the completed work, not an independent replication or new training record. The Bengaluru test set was repeatedly examined. No London or Copenhagen experiment, new model training, or revised manuscript was performed in v2n.
