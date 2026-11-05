# Per-seed stability

Full paired seed rows, 2,000-replicate UTC-day intervals, relative differences and pair/day counts are in `per_seed_physics_comparisons.csv`. Difference is first model minus second; negative favors the first. All five seed models use exactly the same 14,583 test pairs. The table below summarizes physics minus λ=0 in µg/m³:

| h | Mean individual Δ | Median | Sample SD | Range | Seeds favoring physics |
|---:|---:|---:|---:|---:|---:|
| 1 | +0.009 | +0.022 | 0.084 | see CSV | 1/5 |
| 3 | −0.005 | −0.027 | 0.087 | see CSV | 3/5 |
| 6 | −0.566 | −0.744 | 0.461 | see CSV | 5/5 |
| 12 | −0.254 | −0.338 | 0.238 | see CSV | 4/5 |
| 24 | +0.155 | −0.056 | 0.499 | see CSV | 3/5 |

At h=6, the favorable direction is shared by all seeds; h=12 is mostly favorable but variable. At h=1 and h=3 the ensemble's favorable sign is weak or absent in the average individual fit. At h=24 the ensemble and average individual fit are unfavorable despite three favorable seeds, illustrating why sign counts alone do not establish an effect. The seed-level paired CIs describe uncertainty over UTC test days conditional on each trained run; the five seed draws are not independent test datasets. Physics–Laplacian and Laplacian–λ=0 seed rows and descriptive statistics are preserved in both CSVs, including unfavorable values.
