# Routing assignment and modeled-dose trade-off

Original concentration scenario; same nine frozen demand batches, 252 requests per method. Corrected allocator and original matcher assigned all in this low-load case; zero shared-edge violations and maximum utilization about 5.405%. Corrected versus shortest: −0.001207% modeled dose and +0.001324% travel time. Axes intentionally span ±0.5%. This is modeled dose, not measured exposure reduction or classical matching stability.

Source artifacts:
- `final_blr_results/final_routing_closure/v2t/ROUTING_COMPARISON_RESULTS.csv` (SHA-256 `4da5edcfc79d04e41ed42b4b30d408d7f810f9c2578e866c1871b5fb3f3cec47`)
- `final_blr_results/final_routing_closure/v2t/PAIRED_COMPARISONS.csv` (SHA-256 `fbdf12efbb406dde6ca6bbedb477f0caeec4524949f3cbbec4cc9d3c1e9f0401`)

Derived source data: `source_data/F08_assignment.csv; F08_tradeoff.csv`.

Regenerate: `python final_blr_results/ieee_publication_assets/scripts/build_assets.py`.
