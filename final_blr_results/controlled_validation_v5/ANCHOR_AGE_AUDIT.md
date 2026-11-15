# Saved-prediction anchor-age audit

`scripts/audit_saved.py` aligned every available saved ensemble/deterministic prediction with the V3 unregularized reference by truth, target-hour index and station index. The resulting `ANCHOR_AGE_ALL_METHODS.csv` contains **602 rows**: all **16 V3 methods × five horizons × seven prespecified age buckets**, plus six V4 six-hour controls × seven buckets. All nonempty buckets have MAE, RMSE, count and source prediction path. Every method at a given horizon is scored on the same **14,583 observed target pairs**. These are exposed-test descriptive results, not independent validation. The source array SHA-256 is `bd08d733f924387da82e758d1060703dfcdd121f360b7e8765189d8b7446e202`.

An anchor is the latest **genuinely observed** station PM2.5 row strictly before forecast issue `c=T−h`; age is `c−source_row` in hours. A station with no earlier observed row uses a training-mean fallback and is placed in `no_observed_anchor`. This is different from the fraction of imputed pollutant **input slots** in the full 12-hour all-station tensor. It is also different from the fact that each scored target at T is observed.

| Horizon | Scored pairs | One-hour genuine anchors | Fraction fresh | No-prior-observation fallback |
|---:|---:|---:|---:|---:|
| 1 h | 14,583 | 13,908 | 95.37% | 12 |
| 3 h | 14,583 | 13,634 | 93.49% | 24 |
| 6 h | 14,583 | 13,340 | 91.48% | 42 |
| 12 h | 14,583 | 12,875 | 88.29% | 78 |
| 24 h | 14,583 | 12,311 | 84.42% | 149 |

These proportions describe the *scored-target population*. They do not show that the system can maintain equal accuracy across unsensed hours. At six hours, V3 all-station historical pollutant input slots were approximately 84.9% imputed in training and 76.7% imputed in test. The apparent contrast arises because scoring selects observed targets, many of which have nearby prior observations. The per-bucket MAE patterns vary by site and period; they are descriptive associations, not a causal effect of anchor age. [SOURCE: V3 repaired array `observed_mask` and `input_observed_mask`; V4 `ANCHOR_AGE_AND_ERROR_AUDIT.md`; V5 `ANCHOR_AGE_ALL_METHODS.csv`.]
