# Directional regularization statistical audit

## Directional versus Laplacian paired comparison

Saved five-seed predictions were aligned by target timestamp and station, averaged within each model to form the same five-seed ensemble convention used in the v2l source tables, and compared by paired absolute error. A seven-calendar-day moving-block percentile bootstrap used 2,000 replicates per horizon, preserving missing calendar days in the block calendar. The sign is directional minus Laplacian; negative favors directional regularization.

| Horizon | Pairs | ΔMAE (µg/m³) | 95% 7-day block CI |
|---:|---:|---:|---:|
| 1 h | 14,583 | −0.0725 | [−0.1160, −0.0337] |
| 3 h | 14,583 | +0.1775 | [+0.0714, +0.3034] |
| 6 h | 14,583 | −0.1297 | [−0.2293, −0.0416] |
| 12 h | 14,583 | +0.0026 | [−0.1753, +0.1889] |
| 24 h | 14,583 | −0.1026 | [−0.1999, −0.0095] |

The results vary by horizon. These are post-hoc test-set sensitivity intervals, not prospective confirmation. The block method and the original v2l moving-block analysis both sample contiguous seven-calendar-day blocks; the v2v calculation is recomputed from aligned five-seed predictions for directional versus Laplacian specifically.

## Five-of-five sign result

At six hours, directional ST-PIGNN has lower saved seed-level MAE than the zero-regularization model for all five seeds. The exact two-sided sign test has (p=2/2^5=0.0625). This is a five-seed consistency count on one exposed test period, not an independent-dataset test.

## Holm values near 0.0175

The original day-level sign-flip test used 2,000 Monte Carlo draws and the correction formula `(1 + number at least as extreme) / 2001`, so the minimum raw p-value is (1/2001\approx0.00049975). The original Holm family has 35 contrasts. When a minimum-resolution p-value is the smallest family member, its first Holm adjusted value is approximately (35/2001=0.01749), displayed as 0.0175. Repeated 0.0175 values therefore reflect the discrete resampling floor plus a 35-test Holm family, not identical evidence strength. The original adjusted values are retained; this audit does not replace the frozen comparison family.

## Wind-cone diagnostics availability and boundary

Valid post-hoc **station-space** diagnostics are available at `physics_audit/physical_diagnostics/physical_metrics.csv` and `spatial_behavior.csv`. They define a directed edge (u\to v) using source-to-destination bearing clockwise from north; convert wind-from to transport-to by adding 180°; and select edges within 37.5°. The PVR at threshold (	au) is the share of active observed-endpoint station-edge pairs with ((\hat y_v-\hat y_u)/s_{train}>\tau), where (s_{train}=22.994\) µg/m³. For the six-hour ensemble, saved directional PVR is approximately 29.41% at (	au=0), 27.11% at 0.01, 25.08% at 0.05, and 22.44% at 0.1. This is a normalized monotonicity proxy, not a violation rate for atmospheric conservation. The diagnostic covers the station graph and selected observed endpoints only; the centered weather pipeline also has the documented +30-minute availability issue. The original manuscript's 1.404% PVR is historical and not substantiated by this corrected diagnostic.

## Reproduction

Run `python final_blr_results/ieee_publication_assets_v2v/scripts/build_assets.py` to recreate the paired CIs and figure from local saved prediction Parquets. Run `python final_blr_results/ieee_publication_assets_v2v/scripts/analyze_saved_evidence.py` to recreate the seed-level sign summary and source tables.
