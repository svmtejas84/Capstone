# RGDR falsifiable hypothesis

The corrected station model uses a global coefficient on a wind-cone directional monotonicity penalty. Earlier v2l analysis found mixed horizon/seed effects, a more stable h6 association, no conservation, and no reliable advantage over generic Laplacian smoothing. Larger historical penalty strengths sometimes degraded accuracy. These are motivation, not evidence for the proposed change.

**Hypothesis:** restricting the directional penalty to edges whose two cutoff PM2.5 lags are genuinely observed, using only input-provenance indicators known by forecast cutoff, may improve training/validation robustness relative to a fixed penalty. **Alternative:** reliability gating has no benefit or worsens forecasting, potentially because it removes useful edge constraints or makes the effective penalty sparse. The method is a testable variant, not a physical law or established new contribution.

Development is limited to synthetic tests and training/validation diagnostics on Bengaluru. The repeatedly examined Bengaluru test period is excluded from RGDR configuration selection. No external dataset is ready for a confirmatory claim; a future multi-seed controlled comparison requires the frozen plan and supervisor review in `RGDR_FROZEN_EVALUATION_PROTOCOL.md`.
