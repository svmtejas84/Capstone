# v2o citywide support diagnostics

The output records nearest same-hour eligible monitor distance, number of eligible support monitors, and whether each road node lies outside their convex hull. The display flag `poor_support` is outside-hull **or** nearest distance >5 km, fixed before scores; it is a map marker, not a calibrated uncertainty threshold.

| UTC snapshot | Supporting monitors | Median nearest distance | 90th percentile distance | Outside hull | Poor support |
|---|---:|---:|---:|---:|---:|
| 2025-10-08 13:00 | 4 | 5.01 km | 8.94 km | 75.0% | 86.1% |
| 2026-02-10 07:00 | 6 | 4.71 km | 9.25 km | 82.9% | 84.9% |
| 2026-03-28 23:00 | 4 | 6.18 km | 13.08 km | 85.9% | 90.6% |

These high fractions show that most road nodes require interpolation beyond the small contemporaneous monitor hull, especially at the last snapshot. Holding out one of eleven observed sites does not calibrate a prediction interval for all roads, and station representativeness differs from street microenvironments. No kriging/GP posterior or empirical road-node interval is claimed. A distance-to-monitor figure cannot be converted to a concentration error bar without independent observed sites and an appropriate calibration design. The raw weather archive has only one known coordinate; no street-level wind variation is introduced. The maps explicitly gray out poor-support areas.
