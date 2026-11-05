# Approved v2n scope and execution boundaries

This file records the approved v2n scope supplied in the 2026-11-06 handover order. No separate, more detailed v2n assignment was found in the repository at handover. Quantitative design choices absent here must be fixed and documented before any corresponding analysis; they must not be chosen after viewing test results. The full history, evidence, paths, and blockers are in `final_blr_results/V2N_CODEX_HANDOVER.md`.

## Objective

Conduct a bounded Bengaluru city-scale integration, spatial-validation, Captum explainability, and claim-to-evidence freeze using **existing artifacts and compatible checkpoints only**. No new model training is authorized. Do not start London/Copenhagen training, write the manuscript, alter the architecture, change historical metrics or criteria, or claim validated street-level forecasting or routing performance without direct evidence.

## Workstream 1 — Road graph integrity and provenance

Consolidate the existing v2k structural audit, source graph/tensor provenance, station mappings, edge construction and partition-boundary accounting. Verify referenced artifacts before use. Preserve the distinction between the raw 393,089 edge rows and the processed 424,550 message-passing arcs. Stop if the graph object or provenance differs materially from the v2k record; report the discrepancy without silently rebuilding or replacing historical artifacts.

## Workstream 2 — Station/road feature compatibility

Compare the corrected station-model schema, train-only transformations, temporal cutoff, masks, residual anchors, edge features and checkpoint state with the full road graph and its node-hour inputs. Include the v2m cutoff-safe weather change and the historical v2j centered-weather input difference. Establish exact tensor shape, units, time alignment and source coverage before any forward pass. Stop city-scale inference if features, edge representation, temporal availability or checkpoint compatibility are materially invalid. Never replace missing lagged PM2.5 with an arbitrary value.

## Workstream 3 — Conditional bounded city-scale inference

Only after workstream 2 passes a documented compatibility gate may a bounded, resource-aware inference attempt use an **existing compatible checkpoint**. A synthetic shape or memory profile may assess engineering feasibility but is not predictive validation. Preserve graph topology and partition-boundary limitations. Do not silently substitute the road network for the station kNN graph. Do not fabricate road-node PM2.5 labels, copy station targets to roads, or present a city map as validated output. If the gate fails, report the blocker and do not force inference.

## Workstream 4 — Spatial holdout validation

Use existing W6 LOSO and interpolation predictions for leakage-free analysis where populations, targets and protocol match. Keep held-out observations out of input construction, imputation, normalization, calibration, model selection and graph-derived priors. Preserve the four unscored folds; do not invent targets or drop unfavorable stations after seeing results. Distinguish station-graph transfer from road-node or street-level validation. Existing LOSO checkpoints are not known to be available; do not retrain.

## Workstream 5 — Captum Integrated Gradients

Use only existing checkpoints whose architecture, feature registry, transformation, forecast cutoff and graph/edge tensors are verified compatible. Attribute the **actual forecast output**, with a training-derived baseline. Prespecify deterministic sample selection and at least one baseline-sensitivity check before inspecting attributions. Report feature, temporal, station and horizon attribution, across-seed robustness where compatible seed checkpoints exist, and Captum completeness/convergence delta. Compare physics, λ=0 and Laplacian where compatible saved checkpoints exist; mark unavailable comparisons UNVERIFIABLE. Do not interpret Integrated Gradients as proof of physical causality, mass conservation or atmospheric transport. If only legacy/shifted-weather checkpoints are usable, label that protocol and do not present it as corrected v2j/v2m explainability.

## Workstream 6 — Final Bengaluru claim-to-evidence consolidation

Map each proposed claim to exact code, configuration, predictions, checkpoints, statistical test and limitations. Preserve negative and inconclusive findings: invalid legacy benchmark gain, untrained baseline, lag and weather defects, mixed physics effects, no physics-specific proof, LOSO non-win, corrected DEM null, density inconclusiveness, citywide feature blockers and routing non-validation. Keep v2j-v2m cross-protocol differences explicit. Do not edit the research paper in this round unless separately authorized.

## Workstream 7 — Reproducibility and freeze

Create lightweight manifests, hashes, commands, result provenance and a final status/decision register under `final_blr_results/`, with historical `results/` untouched. Maintain `results/codex_log/{ACTIONS,DECISIONS,QUOTA,RESUME}.md`. Verify actual external backup status rather than assuming local ZIPs are durable. Commit and push lightweight deliverables; do not commit large datasets, checkpoints, caches, ZIPs or sensitive material. Freeze only supported Bengaluru claims and explicitly list unresolved blockers. Stop after the v2n handoff/results; no further training is authorized.

## Universal stop conditions

Stop the dependent workstream on a new material integrity or compatibility failure, missing required checkpoint/input, unsafe active job, or unavailable held-out information. Continue independent read-only documentation where possible. No new training, physics sweep, extra architecture, test tuning, split/target ceiling changes, fabricated labels, citywide accuracy claim, routing effectiveness claim, London work, or paper edit.
