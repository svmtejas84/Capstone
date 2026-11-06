# RGDR gate feasibility — h=6, training and validation only

Source: `run_gate_diagnostics.py`; input `results/data_v2j_arrays.npz`; 15-node/60-directed-edge corrected station graph; fixed wind-from mask and 24-hour max age. τ=4 hours was fitted once as median positive eligible age from train cutoffs. No test target, neural fit or validation-based gate selection was used. Observation-age distribution and full metrics are in `gate_diagnostics_v2r.csv`.

| Split | Fixed directional edge instances | Binary gate mass / retention | Continuous gate mass / retention | Hours with zero continuous penalty | Continuous effective edge sample size | Median positive age |
|---|---:|---:|---:|---:|---:|---:|
| Train | 196,762 | 4,472 / 2.27% | 4,873.2 / 2.48% | 10,621/14,206 (74.75%) | 5,048 | 4 h |
| Validation | 29,910 | 1,985 / 6.64% | 2,190.6 / 7.32% | 265/1,961 (13.51%) | 2,276 | 5 h |

The continuous gate modestly raises training edge mass relative to binary and reduces zero-gate hours by 4.9 percentage points, but remains far below the frozen minimum 10% mass and exceeds the 50% zero-hour limit. It therefore **fails the predeclared optimization exposure gate**. In a fixed first-64-cutoff proxy calculation, all penalties and gradients were finite; train fixed/binary/continuous/generic values were respectively 0.09375/0.01348/0.04074/1.02033, with prediction gradient norms 0.0271/0.0589/0.0542/0.3196. These are deterministic proxy inputs from cutoff observations, not trained model predictions or evidence of predictive benefit. Generic smoothing has a much larger raw scale; no validation-selected rescaling was attempted.

**Decision: stop RGDR model fitting under frozen rule.** Do not tune τ, lookback, gate thresholds, λ or scaling in response. The gate is mathematically implemented and tested, while its feasible optimization signal remains inadequate. This does not test predictive performance and cannot support a positive or negative accuracy effect. Novelty remains NOT ESTABLISHED per `final_blr_results/citywide_extension/v2p_rgdr/RGDR_PRIOR_ART_REVIEW.md`.
