# Spatio-temporal feature attribution: Six-hour station-isolated ST-PIGNN variant

Real saved attribution tensors, primary training-mean baseline, 9 attributed records, 12 input hours. Mean absolute and signed IG are separate. Maximum completeness |delta| 7.8e-06 µg/m³; wrapper error 7.6e-06 µg/m³. IG is baseline-relative sensitivity, not causality or physics proof. Integration-step count is documented in source methodology.

Source artifacts:
- `final_blr_results/final_three_pillars/captum/v2r_heldout_h6/attribution_tensors.npz` (SHA-256 `8383e322ca50d84a97743c8c68d900e831db731cc2b731b655c6e03e49ec13cd`)

Derived source data: `source_data/F06b_v2r_h6/`.

Regenerate: `python final_blr_results/ieee_publication_assets_v2v/scripts/build_assets.py`.
