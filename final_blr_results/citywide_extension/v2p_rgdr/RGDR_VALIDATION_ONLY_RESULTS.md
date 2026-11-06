# Training/validation-only RGDR gate diagnostic

`gate_diagnostics.py` reads the existing station observed mask and raw wind direction at forecast cutoffs for all five fixed horizons, restricted to training and validation target hours. It does **not** inspect test targets, train a model, choose λ, or score PM2.5 predictions. The 15-station four-neighbor graph has 60 directed edges. Full per-horizon/split counts are in `gate_diagnostics.csv`.

| Horizon | Train retained directional edge instances | Train hours with zero gated edges | Validation retained edge instances | Validation hours with zero gated edges |
|---:|---:|---:|---:|---:|
| 1 h | 2.36% | 11,251/14,210 (79.2%) | 6.70% | 591/1,961 (30.1%) |
| 3 h | 2.34% | 11,276/14,209 (79.4%) | 6.68% | 597/1,961 (30.4%) |
| 6 h | 2.32% | 11,292/14,206 (79.5%) | 6.66% | 602/1,961 (30.7%) |
| 12 h | 2.31% | 11,320/14,200 (79.7%) | 6.69% | 592/1,961 (30.2%) |
| 24 h | 2.27% | 11,351/14,190 (80.0%) | 6.75% | 586/1,961 (29.9%) |

At h=6, the fixed wind mask has 197,297 training edge instances, but only 4,583 also have two immediately observed endpoint lags. Validation has 29,942 fixed-mask instances and 1,994 gated instances. The binary gate therefore removes most regularization exposure, especially in training. This is a **negative feasibility diagnostic** for the first gate definition. It is not a predictive-loss result, and there is no basis to relax the gate or choose fractional weights from Bengaluru test outcomes. Future work may investigate formally defined observed-data age or reliability categories using train/validation only, but such a change would be a new prespecified variant and needs separate approval before test evaluation.

No validation MAE/RMSE/R² for RGDR exists. The previous v2l physics MAE advantages cannot be assigned to this untrained variant. CUDA access in this sandbox was false; the training authorization remains limited and no CPU neural fit was substituted.
