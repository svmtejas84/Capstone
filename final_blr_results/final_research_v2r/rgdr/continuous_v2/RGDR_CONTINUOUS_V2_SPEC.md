# RGDR_CONTINUOUS_V2 specification

Preserved binary predecessor: `src/stpignn/rgdr.py`, label **RGDR_BINARY_V1**, and unchanged v2p diagnostics. Continuous implementation: `src/stpignn/rgdr_continuous.py`.

At forecast cutoff c, `Δ_i(c)` is the elapsed number of continuous hourly UTC steps since the latest finite observed PM2.5 reading at station i at or before c. The helper accepts only the observed mask and cutoff indices, not targets or future values. Reliability is `q_i=exp(-Δ_i/τ)` for `0 ≤ Δ_i ≤ 24 h`; no prior observation, age >24 h, or missing age gives q=0; age zero gives q=1. τ is the median positive eligible age across the frozen training cutoff sample, excluding zero, missing, and >24 h values. Here τ=4 h. No free parameter was added.

For directed edge e=(src,dst), `r_e=q_src q_dst`. The original corrected wind mask, source/destination convention, length geometry `g_e=sigmoid(length_m/1000)`, rectified term `h_e=ReLU(g_e(ŷ_dst−ŷ_src))`, normalization by `max(Σ M_e r_e,1)`, λ=0.06 and warm-up are unchanged:

`P_RGDR = Σ M_e r_e h_e² / max(Σ M_e r_e,1)`; `L = L_data + λ_epoch P_RGDR`.

For positive denominator, gradient for node k is `2 Σ_e M_e r_e g_e h_e 1[h_e>0] (1[k=dst]−1[k=src]) / Σ M r`, with λ multiplier in total loss. Reliability is detached data provenance. If all q=1, the penalty equals fixed directional corrected penalty. If every reliability is zero, the returned differentiable penalty and its prediction gradient are zero. `q` describes elapsed-time weighting only; it is not calibrated uncertainty or a statement about physical validity. Generic smoothing comparator uses the same r and g with squared signed edge differences and no wind mask or directional rectification.

Tests: `tests/test_rgdr_continuous_v2r.py` plus unchanged `tests/test_rgdr.py` and `tests/test_physics_v2.py`. Thirteen passed. Constant fractional reliability equivalence is asserted when the existing denominator is above its floor; with very small aggregate reliability, the preserved clamp-at-one can scale the loss down. The age test alters observations strictly after a cutoff and verifies identical age. No test or diagnostic reads Bengaluru test targets to choose τ.
