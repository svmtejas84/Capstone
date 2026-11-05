# Physical specificity from existing predictions

`compute_physical_diagnostics.py` uses the corrected v2j wind direction at each target's forecast cutoff, the exact directed 4-neighbor station graph, and only test station pairs with observed targets at both edge ends. The wind-from direction is rotated 180° to transport-to, with a ±37.5° cone. Edge lengths are meters converted to kilometers inside the sigmoid resistance. `physical_metrics.csv` and `spatial_behavior.csv` contain each seed and five-seed ensemble at all five horizons, plus the observed-gradient reference on the same edges. The corrected weather flag is asserted from `results/data_v2j_fit.json`; temperature peak is 08:00 UTC. Active wind-edge observations number only 5,752–5,872 per horizon, so these are sparse station diagnostics, not citywide physics validation.

| h | Ensemble PVR>0 physics / λ0 / Laplacian (%) | Physics / λ0 / Laplacian mean spatial SD (µg/m³) | Physics−Laplacian MAE |
|---:|---:|---:|---:|
| 1 | 28.76 / 28.86 / 28.84 | 19.08 / 19.49 / 18.89 | −0.073 |
| 3 | 28.45 / 27.72 / 28.45 | 15.61 / 15.49 / 16.04 | +0.178 |
| 6 | 27.59 / 27.04 / 27.31 | 14.05 / 14.03 / 13.45 | −0.130 |
| 12 | 25.05 / 25.67 / 25.87 | 13.45 / 13.56 / 12.67 | +0.003 |
| 24 | 28.10 / 27.76 / 28.29 | 14.50 / 15.56 / 14.62 | −0.103 |

Observed PVR>0 is about 28.6–29.4% on the same active edges, and observed mean spatial SD is 21.66 µg/m³. Physics PVR is lower than λ0 at h=1/12 but higher at h=3/6/24. Magnitude-weighted squared hinge is lower for physics than λ0 at all horizons, yet generic Laplacian is equal or lower than physics at h=1/6/12/24. Absolute wind-aligned gradients are much larger than the 1 µg/m³ collapse threshold; near-constant spatial-hour frequency is around 1.5–3% for all variants. The pattern does not show a uniquely physical transport response. Lower hinge magnitude can arise from smoothing, and observed gradients often exceed predictions. No measured emissions Q or mass-balance constraint exists. PVR is a proxy, never proof of atmospheric consistency.

Predictive comparison with Laplacian is mixed: physics has lower ensemble MAE at h=1 and h=6 under the original 35-test Holm family, Laplacian is better at h=3, h=12 is indistinguishable, and h=24 is only nominally favorable to physics. Seed directions are 3/5, 2/5, 3/5, 3/5, 3/5 in favor of physics across h=1,3,6,12,24. This is insufficient for a specific upwind-mechanism claim. The saved predictions allow output proxies only; no v2j checkpoints exist to inspect internal fluxes or test counterfactual wind without retraining.
