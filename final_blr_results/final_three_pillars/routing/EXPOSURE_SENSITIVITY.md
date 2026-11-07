# Exposure sensitivity and interpretation

Existing modeled route results are in `ROUTING_RESULTS.csv` and the historical source files cited by `ROUTING_BENCHMARK_PROTOCOL.md`. The admitted-only allocated-route dose was 0.2718266 µg versus 0.2714979 µg for distance A*: a 0.1211% increase. Mean travel time increased from 3.53589 to 3.54106 minutes (+0.1463%). Demand success was 444/1,000 (44.4%); 55.6% were unallocated. The simulation's 15 km/h speed and 3.5 m³/h RMV are fixed cyclist-like assumptions. The reported quantity is integrated inhaled mass from a static predicted field, not personal exposure measurement or dose absorbed by a body.

No concentration perturbation sensitivity was run. Available road values are sparse-support neural-assisted estimates with poor decoder LOSO performance; neither a calibrated distribution nor a justified perturbation scale exists. An arbitrary perturbation would add apparent precision without empirical basis. No robust route benefit is established. A future bounded scenario could use fixed spatial perturbations, but must label the amplitude as a stress test, not calibrated uncertainty, and report route selection changes, dose/time distributions, support distance, and capacity feasibility at each of the three existing v2r snapshots.

Separate concepts:

- Algorithmic modeled-dose minimization: **implemented for candidate generation** under a supplied static concentration field.
- Estimated exposure change: **historically simulated and unfavorable** (dose increased slightly among assigned trips).
- Independent real-world exposure reduction: **not evaluated**.
