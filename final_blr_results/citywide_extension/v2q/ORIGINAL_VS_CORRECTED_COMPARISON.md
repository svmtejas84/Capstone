# Original versus corrected Bengaluru model

| Property | Original notebook | Corrected v2j/v2m |
|---|---|---|
| Graph nodes | 154,902 road nodes partitioned into 64; 23 snapped graph mask nodes | 15 monitoring stations |
| Edges | 424,550 processed road arcs; 7,134 boundary arcs dropped in partitions | 60 directed station kNN edges |
| Inputs/window | 16 channels (11 + 5 duplicates), 12 hours; sparse station timeline copied to roads | 18 versioned channels, 12 hours, station-specific cutoff-safe history |
| Target/output | Direct `station_pm25 / 342.9356` at last input hour | Future observed PM2.5, log1p-compatible residual |
| Training | Road partitions, station mask plus physics-only batches, one historical split | Corrected chronological station-graph experiments |
| Wind/physics | Scaled wind channel treated as degrees; reverse-bearing hinge | Corrected directional hinge, still heuristic |
| Weather | Historical master/model-input tables with inconsistent aggregation/alignment | Distinct documented v2j and v2m protocols |
| Weights | Root legacy checkpoint present and strict-load compatible | Matching final v2j benchmark/LOSO weights absent; older station checkpoints have other protocols |
| Prediction locations | Road-partition output possible, observed validation at monitor snaps only | Monitored stations |

**DIRECTLY REUSABLE:** OSM node IDs/coordinates/topology and checkpoint loading for historical replay. **REUSABLE WITH CORRECTIONS:** architecture source, partition mechanics, geometry/bearing code, output-map plumbing. **HISTORICAL ONLY:** root weights, duplicated-feature schema, 64-partition maps and old replay. **SCIENTIFICALLY INVALID for new forecasting:** full pollutant timeline copy, modulo time lookup, target-hour pollutant input, unverified scaled-wind angle, zero-as-missing target rule and cross-partition truncation. **MISSING:** genuine road-node PM2.5 histories/targets, compatible corrected ST-PIGNN checkpoint, independent roadside observations and tested lead-time station-to-road decoder.

Original-model checkpoint shape compatibility does not repair the information set or establish road prediction accuracy. The earlier corrected W6 LOSO result remains MAE 22.314 for ST-PIGNN versus 20.624 for weather/static ridge on eleven scored sites; do not merge populations with the legacy replay.
