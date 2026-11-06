# v2o frozen citywide estimation protocol

Frozen before new v2o spatial scores or road estimates. This extension uses the exposed Bengaluru dataset and cannot produce independent confirmation. Preserve v2j–v2n artifacts.

## Path ordering and classification

A: inspect corrected ST-PIGNN checkpoint, graph, node-hour features and scaler lineage. Do not use shape compatibility alone. If matching weights or honest features are missing, classify original-model road inference BLOCKED. B: use same-time observed station PM2.5 as an explicit retrospective spatial bridge. Primary IDW uses Euclidean EPSG:32643 distance and fixed power 2; nearest observed station is the mandatory simple comparator. No test-tuned power, range, variogram or spatial covariate coefficient. C: document requirements for any new supervised road-graph model; do not train one.

## Station-isolated validation

Use the v2m array's observed PM2.5 and UTC test mask (the observed targets/masks are byte-identical to v2j). For each of 15 held-out station IDs, remove that station from every same-hour support set. Score only its genuinely observed test targets. IDW requires at least two other contemporaneously observed stations; nearest requires one. Do not fill unavailable predictions. The fixed train-station-mean comparator is fit using training observations from other stations only. No held-out station target or target-derived channel enters interpolation, fitting or selection. Same-hour readings from *other* stations are inference-time support and make this retrospective reconstruction, not h-step forecasting. Report each method's n, coverage, MAE, RMSE, R², and pooled matched-IDW/nearest comparisons; no test result selects a method. The prior corrected W6 ST-PIGNN LOSS to ridge remains separately reported; populations and information sets are not pooled.

## Full road execution

Choose first, median and last UTC test hours with at least four observed PM2.5 support stations, using masks only. Use sorted raw road-node order and preserve `(row_index, osmid, utm_x_m, utm_y_m)`. Run first 1,000 nodes, first 10,000 nodes, then all 154,902 nodes at each chosen time. Compare prefix output exactly to the full calculation (max absolute difference ≤1e-6 µg/m³). IDW output must be finite and nonnegative. Do not add copied station values as road observations. Use vectorized chunking at 16,384 nodes and record elapsed wall time, nodes/s and peak process RAM; GPU metrics are inapplicable. Node elevation is the verified SRTM-derived `nodes_elevation_true.parquet` and is recorded as a covariate only, not fitted into IDW. Do not invent differentiated wind. Preserve the raw one-coordinate weather limitation.

Record nearest-support distance in metres, number of supporting stations and whether the road node lies outside the support-station convex hull. These are *support diagnostics*, not calibrated intervals. A station-level leave-one-out absolute residual by distance bin may be reported as empirical retrospective error, never as an independent/calibrated road interval. Maps must label output "retrospective IDW estimate from same-hour monitors" and mark poor support (outside hull or nearest monitor >5 km). The 5 km map marker is a descriptive display threshold fixed here, not an accuracy guarantee. If any fixed snapshot lacks four eligible monitors or numerical checks fail, stop the dependent full-city execution and report the blocker. Successful computation does not validate unsensed roads.

The output is **INTERPOLATED ESTIMATES**, not neural forecasts, observed road concentrations or validated ST-PIGNN inference. Road topology is used for node locations only; partition halo equivalence is inapplicable to IDW. Compare chunked/full prefix output instead.
