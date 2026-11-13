# Prespecified statistical implementation detail (before test unlock)

The frozen protocol defines 20 primary ensemble contrasts (true wind minus each of four controls at five horizons), seven-day moving-block bootstrap intervals and Holm adjustment. This addendum fixes implementation details before any v3 test metric is read.

- Pair predictions on exact UTC target timestamp and station index. Keep every observed target pair; no station-hour filtering based on error.
- For an ensemble contrast, compute mean absolute-error difference over paired station-hour rows; negative favors true wind.
- Form UTC-day units preserving all within-day station and hourly dependence. For the 95% interval, sample contiguous seven-day blocks of observed days with replacement until at least the original day count, truncate to that count, and recompute the observation-weighted paired difference. Use 2,000 replicates and RNG seed 4303+horizon×10+comparator index. The interval is exploratory and unadjusted.
- For an exploratory p-value, partition days into consecutive **nonoverlapping** seven-day blocks. Under a blockwise exchangeability null, flip the sign of every paired error difference in a block together. Use 100,000 Monte Carlo draws plus the observed statistic, two-sided absolute-value extremity, and seed 91273+horizon×10+comparator index. The p-value resolution floor is 1/100001. Apply Holm over all 20 predeclared contrasts. This is a different resampling object from the overlapping-block CI and must be labeled separately.
- For five seed-level matched pairs, report all differences and the exact two-sided sign test only if no ties; five same-sign seeds imply p=0.0625. Seeds are not independent geographic sites.
- No inferential p-value is confirmatory because the Bengaluru period was previously inspected. Report confidence intervals and p-values with the repeated-test limitation prominently.

This addendum does not alter models, hyperparameters, populations or frozen contrasts.
