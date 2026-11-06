# RGDR controls and comparison status

Frozen controls: (1) λ=0, (2) original fixed directional penalty, (3) reliability-weighted generic symmetric smoothing, and (4) continuous RGDR. All would use matched corrected ST-PIGNN architecture, h=6, seeds 11/23/37, same data/split and validation selection.

| Arm | Implementation/diagnostic | Predictive fit status |
|---|---|---|
| λ=0 | Frozen in `EXPERIMENT_PROTOCOL.md`; no change to data loss | NOT RUN |
| Fixed directional | Existing `src/stpignn/physics_v2.py` comparator and v2j history | No matched v2r fit |
| Reliability-weighted generic smoothing | Train-only proxy in `gate_diagnostics_v2r.csv`, same continuous edge reliability, no wind mask or directional hinge | No matched v2r fit |
| Continuous RGDR | `src/stpignn/rgdr_continuous.py`; train/validation exposure scan | Training stopped at frozen feasibility gate |

The generic proxy magnitude was much larger than the other raw terms; no post hoc validation scaling was attempted. Predictive control comparisons, optimization exposure on model predictions, seed variability and validation metrics are **NOT EVALUATED** because continuous RGDR failed its predeclared train-only exposure gate. This stop prevents repeated gate tuning against the exposed Bengaluru validation/test record.
