# Coverage, missingness and shift in the V5 source population

The copied frozen V4 `data_manifests/COVERAGE_AND_SHIFT.csv` is computed from the repaired V3 array. It is a descriptive source-data audit, not a new V5 model result.

| Split | UTC hours | Possible station-hours (15 stations) | Observed target pairs | Raw observed-target coverage | Observed PM2.5 mean | Observed PM2.5 SD |
|---|---:|---:|---:|---:|---:|---:|
| Train | 30,624 | 459,360 | 32,638 | 7.105% | 34.136 µg/m³ | 22.994 µg/m³ |
| Validation | 1,992 | 29,880 | 7,203 | 24.106% | 24.970 µg/m³ | 12.810 µg/m³ |
| Exposed test | 4,488 | 67,320 | 14,583 | 21.662% | 44.426 µg/m³ | 37.071 µg/m³ |

For the six-hour model, the fraction of **all-station historical pollutant input slots** marked imputed is 84.895% in training and 76.719% in test. These slots are not target labels. Among *scored* six-hour test targets, 13,340/14,583 (91.48%) have a genuinely observed PM2.5 anchor just one hour before issue, because scored targets are a selected observed subset. For the genuine T−24 daily-lag signal, 12,375/14,583 (84.86%) scored pairs at h=1,3,6,12 have an eligible observed previous-day value; at h=24 none do under the strict-prior rule. See `ANCHOR_AGE_ALL_METHODS.csv` and `LAG24_ELIGIBILITY.csv` for exact definitions and per-method error.

Validation and test observed PM2.5 distributions differ sharply in mean and SD. The reported results are conditioned on observed target availability, which itself changes across splits. This limits extrapolation to unscored hours, unmonitored sites and new seasons. The weather archive and pollutant observations are timestamp causal in the V3 repaired array, but their operational delivery latencies were not measured. The test period is previously exposed. [SOURCE: V4 `COVERAGE_AND_SHIFT.csv`, V3 repaired array, V5 saved-data audits.]
