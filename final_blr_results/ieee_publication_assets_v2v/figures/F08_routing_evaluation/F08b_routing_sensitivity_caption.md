# Routing sensitivity to modeled concentration perturbations

The saved routing study contains four fields: one original concentration field plus three prespecified perturbations (uniform scaling, spatial sine, and support-distance perturbation). Each perturbation has 252 requests. Bars show route identity stability, not calibrated exposure uncertainty. Assignment stability was 100% and declared edge-capacity violations zero in these low-load scenarios. No measured human exposure validation.

Source artifacts:
- `final_blr_results/final_routing_closure/v2t/SENSITIVITY_STABILITY.csv` (SHA-256 `8fe8e0b8ff03f10df6d60db0274af6d938c3e2cc84a424c49b3994e9f5077855`)

Derived source data: `source_data/F08_sensitivity_stability.csv`.

Regenerate: `python final_blr_results/ieee_publication_assets_v2v/scripts/build_assets.py`.
