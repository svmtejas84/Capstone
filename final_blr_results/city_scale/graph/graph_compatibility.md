# Graph compatibility verdict

| Pairing | Verdict | Reason |
|---|---|---|
| Raw OSM graph to processed road topology | COMPATIBLE | Counts reconcile by loop removal, reverse arcs and deduplication; all indices and lengths valid. |
| Road topology to 64 stored partitions | APPROXIMATE WITH ASSUMPTIONS | Every node is assigned, but 7,134 directed cross-boundary arcs disappear; two-hop halo equivalence has not been demonstrated. |
| 15-station corrected forecast graph to 154,902-node road graph | BLOCKED | Different nodes, graph construction, distance edge features, dynamic input schema and target population. |
| Road graph to monitored road-node PM2.5 validation | UNVERIFIABLE | The 23 station snaps do not provide independent concentration labels at all roads. |

The corrected ST-PIGNN was evaluated on a 15-station directed four-neighbor distance kNN graph, not this OSM graph. A loaded tensor of matching shape would not establish transfer. Full-city predictive inference remains gated by checkpoint and node-hour feature compatibility in `../features/feature_validation.md`. No full-road model forward pass was made.
