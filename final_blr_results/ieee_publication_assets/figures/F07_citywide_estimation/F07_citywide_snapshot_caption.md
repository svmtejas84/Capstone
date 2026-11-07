# Experimental neural-assisted road-node estimates and support

Earliest frozen origin, 2025-10-08 07:00 UTC, six-hour forecast; 154,902 saved node values without added smoothing. Station forecaster uses 15-station graph; road values use separate 1,249-parameter decoder. Decoder underperformed simple spatial controls; roadside accuracy is unvalidated. 19.45% of nodes lie >5 km from a monitor; 60.58% are outside the monitor convex hull.

Source artifacts:
- `final_blr_results/final_research_v2r/citywide/road_predictions/road_predictions_20251008T0700Z.parquet` (SHA-256 `f58fab904af5261ee7b831347afed5414c5c059e7d76608351a622c090ba55f7`)
- `results/stations_v2.csv` (SHA-256 `1566c0238101643a4b90b1e1937d457a86a534492464b771ae18f403f40368d9`)

Derived source data: `source_data/F07_snapshot_node_data.csv`.

Regenerate: `python final_blr_results/ieee_publication_assets/scripts/build_assets.py`.
