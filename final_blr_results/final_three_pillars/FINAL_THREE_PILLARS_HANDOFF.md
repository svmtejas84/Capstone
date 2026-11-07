# Final three-pillars handoff

Date: 2026-11-07. Starting HEAD: `52c119c320b014a285f399e8de9420d364d17614`; branch: `research/bengaluru-v2r-final`. Work is limited to physics diagnostics, routing recovery/toy validation, and bounded Captum attribution. No model training, new forecasting, or test-guided tuning was performed.

## Physical conservation

The legacy production notebook applies a direction-masked endpoint hinge on concentration differences, weighted by an edge attribute. It has no time derivative, finite-volume mass, flux divergence, emissions source, removal, or complete boundary accounting. It does **not** conserve mass. The v2l corrected directional regularizer is also a monotonicity heuristic rather than a conservation equation.

A standalone finite-volume diagnostic was implemented and run on synthetic periodic and bounded domains. It verified constant-field balance, one-dimensional advection/diffusion convergence, source/sink balance, boundary-flux accounting, and closed-domain mass to the tolerances recorded in `physics/NUMERICAL_TEST_RESULTS.md`. Classification: **CONSERVATION FORMULATION VALIDATED NUMERICALLY** for the synthetic discretization, but **PHYSICALLY ASSUMPTION-BOUND** for real Bengaluru air. Empirical atmospheric conservation is not evaluated because measured cell geometry, emissions, diffusivity, meteorological fields, vertical structure, and defensible atmospheric boundary conditions are unavailable. Historical checkpoints are unaffected and must not be described as mass-conserving.

## Routing and exposure

Recovered implementation paths are documented in `routing/ROUTING_IMPLEMENTATION.md`. Deterministic toy graphs verify shortest/fastest/min-dose behavior, disconnected paths, and a shared-edge capacity counterexample. The API Gale–Shapley path representation cannot enforce overlapping edge capacity; the offline bundle allocator represents shared links but is a heuristic quota process and does not establish classical stable matching or welfare optimality.

The available seed-42 historical simulation admitted 444 of 1,000 requests (44.4%). Among admitted requests, modeled dose rose 0.1211% and travel time rose 0.1463% relative to its recorded comparison. The underlying static concentration snapshot is not a validated forecast. A new full-network route benchmark was not run because input concentration/capacity provenance does not support a valid extension. Independent real-world exposure reduction, travel-time benefit, and capacity guarantees are **UNSUPPORTED**.

## Captum

IG completed on v2c h=1 (54 baseline/example records across five checkpoints and nine fixed examples) and v2r outer-LOSO h=6 (18 records across three held-out stations and two baselines). Wrapper errors and completeness deltas are small; no nonfinite or flagged records were found. Full tensors, row-level records, summaries, selection metadata, figures, scripts and run markers are retained under `captum/`. Results explain only model sensitivity relative to selected baselines. They are not causal or physical evidence.

The final corrected v2j checkpoints and matched λ=0 checkpoints are missing; no compatible historical artifacts were found for those comparisons. v2c/v2r models are not substitutes for v2j weights. No regeneration training was authorized or performed.

## Claims and recovery

The machine-readable status table is `CLAIM_EVIDENCE_MATRIX.csv`. The updated IEEE package reference is `IEEE_EVIDENCE_SUPPLEMENT.md`. Full checksums and regeneration commands are under `reproducibility/`; the verified ZIP path and SHA-256 are recorded in `reproducibility/ARCHIVE_VERIFICATION.json`.

The working branch and source notebook are identified in `RECOVERY_AUDIT.md`. Read `captum/CAPTUM_FINAL_VERDICT.md`, `physics/PHYSICS_FINAL_VERDICT.md`, and `routing/ROUTING_FINAL_VERDICT.md` before reusing any pillar claim. Final Git/remote status is recorded in `results/codex_log/RESUME.md` after push verification.
