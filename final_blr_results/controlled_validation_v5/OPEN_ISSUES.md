# V5 scientific limitations and pending outcome checks

These limitations are independent of whether any V5 MAE difference is favorable:

1. **Previously exposed temporal test:** the Bengaluru September 2025–March 2026 period has been inspected in prior rounds. V5 protocol and controls were frozen before new model scoring, but test inference remains exploratory.
2. **Operational input delivery:** archive weather records are timestamped before issue, yet their release time and station-sensor ingestion latency were not captured. Timestamp causality is verified; operational availability is not.
3. **Spatial population:** 15 station nodes, 11 with scored test targets and four without. Repeated target hours are not independent sites; no new spatial holdout, roadside measurements or second-city replication was run.
4. **Sparse and shifting observations:** training has 7.105% observed station-hour coverage, validation 24.106%, and test 21.662%. Validation observed PM2.5 mean 24.970 versus test 44.426 µg/m³. Scored targets disproportionately have recent genuine anchors, so performance may not transfer to unsensed hours.
5. **Graph control scope:** G1 deletes interstation arcs; G2 uses one frozen degree-preserving rewiring (40/60 arcs changed). Even if G0 wins, this is evidence versus those two controls, not proof of universal graph necessity or correct atmospheric connectivity. Edge distances are geometric, not validated transport coefficients.
6. **Temporal control capacity:** L1 adds 192 parameters and three final-row channels; L2 retains parameter count but triples temporal processing. Any gain combines information and representation changes. At h=24 the actual T−24 measurement is ineligible at issue, so L1 cannot test an observed daily-lag signal there.
7. **Regularizer exposure:** directional and Laplacian losses have different active-arc fractions and raw scales. The frozen λ grid and checkpoint-local gradient replay show exposure but cannot make penalty families mathematically equivalent. The directional hinge is not a mass-conservation equation.
8. **Selection asymmetry:** the shared LR per horizon was inherited from validation selection on the unregularized seed-11 model. Subsequent conditions share that LR, which isolates a matched policy but may favor the selecting procedure.
9. **Backup:** Git pushes and the planned ZIP preserve lightweight source and selected artifacts but do not verify an independent USB backup of historical raw data or checkpoints.

Pending until the authorized V5 fit/test sequence finishes: complete-matrix integrity, graph and lag numerical outcomes, validation-selected fairness grid, paired uncertainty, replayed gradients and archive checksum. An unfavorable result will not be omitted.
