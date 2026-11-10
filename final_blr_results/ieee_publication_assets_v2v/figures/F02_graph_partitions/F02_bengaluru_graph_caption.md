# Bengaluru road topology, historical partitions, and monitors

Stored UTM graph and partition IDs; 154,902 nodes. The corrected forecasting model was evaluated on a separate 15-station, 60-edge kNN graph, not on the road graph. Arc and edge-row counts have different preprocessing semantics.

Source artifacts:
- `data/graphs/bangalore_utm_nodes.parquet` (SHA-256 `d42b9551a84e64727fa61d6825e8310d3a540276c220299bbfddb4ae7776989f`)
- `data/graphs/bangalore_utm_edges.parquet` (SHA-256 `c5d3aa5bb37c9be5f08349dfabf2d8e3a8fae85acd34ecd13b93dce0f4512b79`)
- `data/processed/graph/partitioned_manifold_64_clusters.pt` (SHA-256 `7c04b2507fd951f6874d14d411d9b2c097ebb429883e672e1d20547fc64f4cfa`)
- `results/stations_v2.csv` (SHA-256 `1566c0238101643a4b90b1e1937d457a86a534492464b771ae18f403f40368d9`)

Derived source data: `source_data/F02_graph_summary.csv`.

Regenerate: `python final_blr_results/ieee_publication_assets_v2v/scripts/build_assets.py`.
