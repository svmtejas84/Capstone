# ST-PIGNN implementations and downstream estimation pathways

The historical road-network lane documents a partitioned GINEConv–GRU implementation and its distinct input protocol; it is not the corrected station-graph benchmark. The corrected forecasting graph has 15 station nodes and 60 directed kNN edges, with a 12-hour window and 18 channels. Weather handling differs across retrospective centered-weather and forecast-cutoff-safe evaluations. The directional hinge is a training-only objective evaluated on predictions; λ=0 and Laplacian are separate conditions. Dashed arrows denote experimental downstream station-to-road decoding and routing. Road-node values are estimates, not observed concentrations; no mass-conservation guarantee is implied.

Source artifacts:
- `final_blr_results/citywide_extension/v2q/ORIGINAL_MODEL_ARCHITECTURE.md` (SHA-256 `875d64aa56f83a0a38a1858e6f633e3666cdd4d047e8fd7ecb88f38f37f3a2a0`)
- `final_blr_results/physics_audit/methodology/PHYSICS_ATTRIBUTION_METHODOLOGY.md` (SHA-256 `f0646f6f9130954e09bcb649c07636ee03f89b507c7ab0a26e82a2a65f9a3449`)
- `final_blr_results/final_research_v2r/FINAL_RESEARCH_HANDOFF.md` (SHA-256 `caafc9c9842e5871c1e9bae8115acb12c883dda38c8e3a63457120b504d6d549`)

Regenerate: `python final_blr_results/ieee_publication_assets_v2v/scripts/build_assets.py`.
