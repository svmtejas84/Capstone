# Supplement to IEEE evidence package

The existing `final_blr_results/ieee_paper_evidence/` package is unchanged. This supplement adds the bounded three-pillar validation executed on 2026-11-07.

- **Conservation:** historical hinge remains non-conservative. A standalone finite-volume diagnostic passes synthetic conservation and convergence checks; it does not validate Bengaluru atmospheric conservation. See `physics/`.
- **Routing:** toy algorithm checks and a recovered historical simulation document 44.4% assignment success and a small increase in admitted-only modeled dose. No independently measured exposure effect or shared-edge capacity guarantee is established. See `routing/`.
- **Explainability:** corrected ST-PIGNN IG was run on v2c h=1 and v2r h=6 saved checkpoints. Both are exploratory and protocol-specific. Final v2j and matched λ=0 checkpoints remain unavailable. See `captum/`.

Any manuscript figure or claim asserting mass conservation, validated exposure reduction, capacity guarantees, causal explanation, or validated road-level accuracy must remain withdrawn. These results supplement rather than overwrite the frozen evidence package.
