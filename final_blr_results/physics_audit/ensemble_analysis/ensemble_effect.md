# Ensemble contribution

For seed predictions pₛᵢ, `individual_mean=(1/5)Σₛ meanᵢ|pₛᵢ−yᵢ|`, `ensemble=meanᵢ|(1/5)Σₛpₛᵢ−yᵢ|`, and `gain=individual_mean−ensemble`. The same target and mask are used for every seed and model. `ensemble_decomposition.csv` supplies all three variants and horizons.

| h | Individual physics−λ0 MAE | Ensemble physics−λ0 MAE | Extra physics ensemble gain |
|---:|---:|---:|---:|
| 1 | +0.009 | −0.026 | +0.036 |
| 3 | −0.005 | −0.130 | +0.125 |
| 6 | −0.566 | −0.410 | −0.156 |
| 12 | −0.254 | −0.262 | +0.008 |
| 24 | +0.155 | +0.145 | +0.011 |

Positive extra gain means the physics ensemble benefits more from averaging than the λ=0 ensemble. Thus the h=1 favorable ensemble result **reverses** the mean individual direction; h=3 is almost entirely amplified by ensemble averaging. At h=6 and h=12 the benefit exists in individual fits; h=6 is attenuated by averaging. This does not by itself identify why predictions decorrelate across seeds.
