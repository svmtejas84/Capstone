# Graph construction

Two graphs must remain distinct. The canonical OSM road graph contains 154,902 nodes; 393,089 raw directed edge rows; 424,550 processed message arcs; 64 geographical partitions; and 7,134 directed cross-partition arcs absent from the historical partition representation. Structural integrity is documented in `final_blr_results/city_scale/graph/`.

Corrected station forecasting instead uses a 15-monitor directed kNN graph with 60 directed edges. No corrected ST-PIGNN message passing was run directly across all road nodes. Original notebook partitioning is historical and omits cross-partition arcs. A valid road graph is not evidence of concentration accuracy.
