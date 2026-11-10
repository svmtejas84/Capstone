# Spatio-temporal feature attribution: One-hour ST-PIGNN variant

Real saved attribution tensors, primary training-mean baseline, 45 attributed records, 12 input hours. Mean absolute and signed IG are separate. Maximum completeness |delta| 2.1e-05 µg/m³; wrapper error 4.6e-05 µg/m³. IG is baseline-relative sensitivity, not causality or physics proof. Integration-step count is documented in source methodology.

Source artifacts:
- `final_blr_results/final_three_pillars/captum/attribution_tensors.npz` (SHA-256 `bfa8cfc8e175e94d45c08feb791cfe196e7673df61bf3275ecf069b179d6b63e`)

Derived source data: `source_data/F06a_v2c_h1/`.

Regenerate: `python final_blr_results/ieee_publication_assets_v2v/scripts/build_assets.py`.
