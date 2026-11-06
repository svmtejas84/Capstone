# RGDR final verdict — v2r

**Decision: UNSUPPORTED under the frozen feasibility rule; predictive effect NOT EVALUATED.**

`RGDR_BINARY_V1` is preserved as an unchanged copy of `src/stpignn/rgdr.py` and its v2p outcome remains: about 2.3% train directional-edge retention, roughly 79–80% zero-gate train hours. `RGDR_CONTINUOUS_V2` is implemented in `src/stpignn/rgdr_continuous.py` and preserved under this deliverable. It uses observation age with `τ=4 h`, the training-only median positive eligible age, 24-hour maximum lookback, and edge reliability `q_src q_dst`.

All 13 focused tests passed: the continuous-v2 tests plus existing binary RGDR and corrected-physics tests. They cover fixed-loss equivalence at constant-one reliability and at constant fractional reliability when the unchanged normalization denominator is above its floor, wind-mask direction, bounds, missing/zero-weight behavior, finite gradients, differentiability, future-observation exclusion, train-only τ, batch/reproducibility behavior and existing physics behavior.

The frozen h=6 diagnostic retained 4,873.2/196,762 fixed directional edge mass (2.48%) in training; 10,621/14,206 hours (74.75%) had zero continuous penalty. Validation retention was 7.32%, with 13.51% zero hours. The gate therefore fails both preregistered exposure checks (≥10% mass and <50% zero train hours). A finite proxy gradient does not establish a useful learned optimization signal. The proxy comparison's raw continuous gradient norm was 0.0542 versus fixed 0.0271, binary 0.0589, and generic smoothing 0.3196; these are not trained-model gradients.

Per the frozen stop rule, no RGDR GPU training, validation metric comparison, or 12-cell pilot was run. λ=0 and the three regularized training controls were therefore not compared predictively. Do not claim RGDR improves forecasting, solves sparsity, is novel, establishes physical specificity, conserves mass, or generalizes. Prior-art status remains **NOT ESTABLISHED** in `final_blr_results/citywide_extension/v2p_rgdr/RGDR_PRIOR_ART_REVIEW.md`. A new independent dataset and a revised, supervisor-approved reliability definition/protocol would be needed for further training.
