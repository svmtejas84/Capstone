# Resume

- Branch: `audit/canonical-notebook-20261023`.
- S4 complete and pushed at `006ba94`; S4 verdict LOSS versus ordinary kriging. Earlier outputs remain unchanged.
- W1 input repair committed/pushed at `d935f64`; original W1 AR fit to raw targets scored test MAE/R² 11.894099/0.374211 versus persistence 8.116095/0.532089 and triggered the fixed stop rule.
- X1–X5 input diagnostic complete: `scripts/input_diagnosis_v2g2.py`, `results/input_diagnosis_v2g2.md`, seed 42, config `configs/data_v2.yaml`. Observed-lag-only AR fitted in the shared train-fitted log1p target space scores all-test MAE/R² 8.509631/0.559943; persistence 8.116095/0.532089. Cause found: transform mismatch in the original W1 AR fitting. The repaired lag/target scaling and sampled one-hour timestamp alignment check pass. W1 PASSED by the fixed 0.5 µg/m³ margin.
- Required input rule for future neural models: train-fitted shared log1p lag/target scaling and zero training-loss weight for target pairs with an imputed immediate lag. This is a diagnostic rule; no neural model has been trained under it.
- This turn ends after committing/pushing X1–X5. W2–W8 are NOT RUN. No routing, IG, or Gate M.
- ACTIONS, DECISIONS, QUOTA, and `runs/x_input_diagnosis_v2g2.log` were appended; only RESUME.md was overwritten.
