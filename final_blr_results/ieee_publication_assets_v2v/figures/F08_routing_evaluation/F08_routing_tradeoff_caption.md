# Routing assignment and modeled-dose trade-off

Original concentration scenario; nine frozen demand batches (252 requests per method). Maximum edge utilization in this scenario was 4.5918% (seed 37, demand 48); the 5.4054% maximum belongs to the spatial-sine perturbation across all four saved concentration fields. Corrected allocator and original matcher assigned all low-load requests; zero shared-edge violations. Corrected versus shortest: −0.001207% modeled dose and +0.001324% travel time. Axes span ±0.5% to show the small differences. This is modeled dose, not measured exposure reduction or classical matching stability.

Source artifacts:
- `final_blr_results/final_routing_closure/v2t/ROUTING_COMPARISON_RESULTS.csv` (SHA-256 `4da5edcfc79d04e41ed42b4b30d408d7f810f9c2578e866c1871b5fb3f3cec47`)
- `final_blr_results/final_routing_closure/v2t/PAIRED_COMPARISONS.csv` (SHA-256 `fbdf12efbb406dde6ca6bbedb477f0caeec4524949f3cbbec4cc9d3c1e9f0401`)

Derived source data: `source_data/F08_assignment.csv; F08_tradeoff.csv`.

Regenerate: `python final_blr_results/ieee_publication_assets_v2v/scripts/build_assets.py`.
