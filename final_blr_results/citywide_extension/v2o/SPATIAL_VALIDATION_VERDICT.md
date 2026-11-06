# v2o spatial validation verdict

**Retrospective IDW spatial accuracy: weak and incompletely covered.** `SPATIAL_VALIDATION_RESULTS.csv` and `spatial_validation_pairs.parquet` come from `run_spatial_bridge.py` using fixed power 2 and genuine held-out station isolation. For each target pair, the held-out station is removed from same-hour interpolation inputs; no model or weight is fitted on its test target. The train-other-station mean comparator uses training observations from other stations only. Eleven stations have test observations, four (5547, 5548, 6975, 2498781) have none and remain unscored. The 14,583 pairs are only eleven spatial sites and cannot be treated as independent locations.

| Method | Scored n / 14,583 | Coverage | Pooled MAE µg/m³ | RMSE µg/m³ | R² |
|---|---:|---:|---:|---:|---:|
| Fixed IDW p=2 | 12,328 | 84.54% | 23.133 | 42.606 | −0.176 |
| Nearest observed monitor | 13,616 | 93.37% | 26.640 | 46.743 | −0.510 |
| Training-only other-station mean | 14,583 | 100% | 20.563 | 38.480 | −0.078 |

On the **12,328 exact IDW-eligible pairs**, nearest-monitor MAE is 27.007 and training-only other-station mean MAE is 21.943, versus IDW 23.133. IDW improves on nearest on that matched population but is worse than the train-only mean. The pooled primary IDW figure is not compared causally with the nearest 13,616-pair row because coverage differs. Per-station IDW coverage ranges from 26.0% to 100%; station 3409388 has 56.9% and station 6119271 only 26.0%. Several per-station R² values are strongly negative, especially at low-variance sites. The full per-station table retains every scored site.

This is **same-time retrospective spatial reconstruction**: other monitors' observations at target hour t are used as inputs. It is not h-step forecasting and cannot be compared directly with corrected W6 forecast LOSO. The earlier W6 ST-PIGNN LOSS to weather/static ridge (MAE 22.314 vs 20.624, 11 scored stations) remains a separate negative result in `final_blr_results/city_scale/spatial_validation/SPATIAL_VALIDATION_VERDICT.md`. Both Bengaluru evaluations use an exposed test period; neither is independent spatial confirmation. No new IDW tuning was chosen after these results.
