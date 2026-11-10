# IEEE publication assets v2v

This additive package corrects scientific figures, captions, tables, and saved-data audits. It is evidence for a separate manuscript revision; it contains no manuscript source. The frozen v2u package and historical experiment outputs were not modified.

## Contents

- `figures/`: 11 figure assets (F01, F02, F03, F03b, F04, F05, F06a, F06b, F07, F08, F08b), each in PNG, PDF, SVG, with caption sidecar.
- `tables/`: CSV and LaTeX tables T01–T08, with distinct-protocol splits where needed.
- `source_data/`: derived plotting and statistical inputs, source path/hash register, figure and table manifests.
- `analyses/`: evidence reconciliation, data provenance, model selection, spatial, physics, Captum, routing, and optional-experiment audits.
- `scripts/`: deterministic saved-artifact analysis, plotting, table generation, and package verification.
- `latex/`: figure/table insertion snippets only.
- `verification/`: source hashes, package checks, and this round’s verification report.

## Rebuild

From the repository root: `python final_blr_results/ieee_publication_assets_v2v/scripts/build_assets.py`; then `python final_blr_results/ieee_publication_assets_v2v/scripts/build_tables.py`; finally `python final_blr_results/ieee_publication_assets_v2v/scripts/verify_package.py`. Plot generation reads frozen artifacts and does not fit models. The complete source-data analysis is `python final_blr_results/ieee_publication_assets_v2v/scripts/analyze_saved_evidence.py`.

## Interpretation boundaries

The retrospective centered-weather benchmark and forecast-cutoff-safe MLP/TCN benchmark use different information protocols. The 11-site held-out evaluation and forecast-origin-safe decoder evaluation are different populations and tasks. City-node values are experimental neural-assisted estimates without roadside validation. The directional penalty is a training-only heuristic and is not mass conservation. Routing values are scenario-based modeled dose and computational capacity outcomes, not measured exposure effects. Captum attributions are input sensitivity relative to stated baselines, not causal explanations.
