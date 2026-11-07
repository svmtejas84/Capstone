# Volume 4 — Road, partition and station graphs

<a id="volume-04"></a>

## Editorial reconstruction and evidentiary boundary

Two graph objects must never be conflated. The road network has 154,902 nodes, 393,089 raw directed edge rows and 424,550 processed message arcs. The corrected forecasting graph has 15 observed station nodes and 60 directed kNN edges. The 64 geographical road partitions omit 7,134 cross-partition arcs, so a partition forward pass is not automatically equivalent to whole-graph message passing. The larger processed arc count follows reverse-arc construction and deduplication after self-loop handling, not extra monitors. Structural integrity supports graph engineering; it supplies no road-node label or independent roadside accuracy. [EVIDENCE: v2k road audit | final_blr_results/road_graph/road_graph_integrity.md | snapshot 1c46a4b]

## Full round-specific source exhibits

The exhibits reproduce the cited local reports as source evidence. Their original round-specific conclusions may be narrower than later findings; read the editorial reconstruction and final synthesis before treating one exhibit as the final verdict.

## Source exhibit 1: `final_blr_results/road_graph/road_graph_integrity.md`

[EVIDENCE: `final_blr_results/road_graph/road_graph_integrity.md` | SHA-256 `3d374e2a670fdb0596c6e5a9dba47e75a120cfc581b7ad2886a75c9a76dcd9bd` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Bengaluru road graph integrity

Read-only structural audit: `inspect_graph_v2k.py` and exact machine-readable `graph_measurements_v2k.json`; source `scripts/build_graph_tensors.py`, `data/graphs/bangalore_utm_{nodes,edges}.parquet`, `data/processed/graph/topology_graph.pt`, `topology_graph_pyg_inference.pt`, and `partitioned_manifold_64_clusters.pt` at source commit `128dd0324deeb23310a93cb2aaa98f2032efb648`.

The raw OSM-derived, UTM-zone-43N graph has **154,902 unique nodes and 393,089 directed edge rows**. Coordinates are all finite and transform to 12.8353–13.1422°N and 77.45999–77.77664°E. All endpoints resolve. Raw edges include 117 self-loops and 938 repeated directed `(u,v)` pairs, but no repeated `(u,v,key)` rows. All lengths are finite and positive (0.521–6884.931 m; median 42.472 m). All rows have a highway category; optional lanes, width, speed, bridge and similar tags are often missing (counts in JSON). The raw `oneway` attribute is False in 376,626 and True in 16,463 rows; the tensor builder symmetrizes edges for message passing, so the tensor does **not** preserve legal travel direction.

The processed topology tensor has **154,902 nodes and 424,550 directed edges**, `x=[154902,17]`, `edge_attr=[424550,16]`; all features and edge indices are finite/in range, with zero self-loops. It has 16,156 repeated directed endpoint pairs after conversion, representing different length/road-category parallel edges. NetworkX finds one weak and one strong component, both spanning all nodes. The PyG inference tensor has identical node features and edge indices and marks 23 station nodes for training. Station mapping has 23 rows, 23 distinct mapped road nodes, and no missing mapped index. SRTM elevation is present for all 154,902 nodes.

The raw and tensor edge counts refer to different constructions: `scripts/build_graph_tensors.py` drops 117 raw self-loops (393,089→392,972), adds reverse message-passing arcs (→785,944), then deduplicates by directed endpoints, length and highway category (→424,550). The older 393,089 figure describes raw serialized OSM edge rows; 424,550 describes processed tensor arcs. The difference is construction and counting convention, not a missing-node defect. A manuscript citation should name which object it counted; this round did not edit it.

There are 64 disjoint partitions covering every node, sizes 1,238–3,746 (individual sizes in JSON). Their internal directed edges sum to 417,416. Exactly 7,134 directed topology edges cross partition boundaries and are omitted by the stored induced partitions. Partition inputs have shape `[12,16]`, which also differs from the graph static `x` width 17 and corrected v2j station input width 18. Structural validity does not establish model compatibility or predictive validity.

## Source exhibit 2: `final_blr_results/road_graph/full_graph_compatibility.md`

[EVIDENCE: `final_blr_results/road_graph/full_graph_compatibility.md` | SHA-256 `a6ad466168b2593acef607293e5491ffc15bf321964019382d2a58a05d554c9b` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Corrected ST-PIGNN full-graph compatibility

**Verdict: direct full-road-graph inference is BLOCKED.** This is an engineering compatibility verdict, not a prediction-quality result. No training or full-graph forward pass was executed.

The v2j original ST-PIGNN was trained on the 15-station, four-neighbor distance graph with 18 time-varying input channels, a 12-hour window, station-specific observed/imputed history, a causal residual anchor, and distance edge attributes. The raw road tensor has 154,902 nodes, static `x=[154902,17]` and length/category `edge_attr=[424550,16]`; partitions store `[12,16]` features and omit 7,134 cross-boundary arcs. The v2j benchmark saved predictions but no trained neural checkpoints. An older `citywide_stpignn_best.pt` belongs to a legacy/shifted-weather pathway and cannot be declared a corrected v2j checkpoint. Model B additionally has 15-node learned graph parameters, so its node count is structurally fixed. Running any v2j weights on this road tensor would require new inputs, graph/edge adaptation, and checkpoint verification; none was silently supplied.

The road graph lacks complete hourly features for 154,880 nodes and lacks observed road-node PM2.5 truth. The source meteorology is one known coordinate, with no verified multi-cell citywide mapping. These are distribution and provenance blockers even if tensor shapes were made to match. Copying station concentrations or imputed concentrations across road nodes would create artificial truth.

Approximate float32 memory before model activations: `[12,154902,18]` input ≈134 MB, `[424550,16]` edge attributes ≈27 MB, and one `[12,154902,64]` hidden activation ≈476 MB. Multiple graph layers, temporary messages, PyTorch allocator overhead and batching could require multiple GB; a V100 32 GB may hold a bounded forward pass, but capacity has **not** been profiled. The 64 existing partitions reduce local graph size yet lose boundary messages and use a different feature width, so they are not a validated drop-in solution. Successful synthetic shape profiling would only establish engineering feasibility, never street-level accuracy. No citywide production inference was authorized or run.

## Source exhibit 3: `final_blr_results/city_scale/graph/graph_provenance.md`

[EVIDENCE: `final_blr_results/city_scale/graph/graph_provenance.md` | SHA-256 `e430ca2c12133cf827b95670bc9efbfe8faccc90f337b7d08680aede0f53df55` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Road graph provenance and integrity

The canonical raw OSM-derived road graph is `data/graphs/bangalore_utm_nodes.parquet` (SHA-256 `d42b9551a84e64727fa61d6825e8310d3a540276c220299bbfddb4ae7776989f`) and `data/graphs/bangalore_utm_edges.parquet` (`c5d3aa5bb37c9be5f08349dfabf2d8e3a8fae85acd34ecd13b93dce0f4512b79`). Coordinates are EPSG:32643 UTM metres, inferred from preprocessing and checked by transformation to 12.8353–13.1422°N, 77.45999–77.77664°E. Raw rows: 154,902 unique nodes and 393,089 directed edges, with all endpoints present and positive finite lengths. The raw `oneway` field is true for 16,463 and false for 376,626 rows.

`scripts/build_graph_tensors.py` removes 117 self-loops, adds reverse message arcs and deduplicates by directed endpoints, length and road category: 393,089 → 392,972 → 785,944 → **424,550** processed arcs. `data/processed/graph/topology_graph.pt` SHA-256 is `a6454d9a46e42fc30831cc6ed3dae2f0e91e18661c596cc0a8c56334ef9c552f`; its 154,902 × 17 node tensor and 424,550 × 16 edge tensor are finite and in range. Both weak and strong graph connectivity scans found one component. Message arcs are symmetric for learning and do not encode legal driving direction. Sixteen thousand one hundred fifty-six repeated directed endpoint pairs retain different road length/category attributes.

The 64-partition file SHA-256 is `7c04b2507fd951f6874d14d411d9b2c097ebb429883e672e1d20547fc64f4cfa`. It covers every node exactly once, with partition sizes 1,238–3,746. The 417,416 internal arcs omit 7,134 cross-boundary directed arcs. Any two-layer message passing needs at least a two-hop halo, with induced edges preserved, and a numerical comparison against a full overlapping subgraph before a partition result can be called equivalent. The stored partition feature shape `[12,16]` differs from both road `x` and corrected station model inputs.

The PyG inference tensor has the same node/edge topology and marks 23 station nodes. The station mapping has 23 rows and 23 distinct valid road indices; snapping is a mapping, not observation of the remaining nodes. Only 22 mapped nodes have stored node-hour rows. Full measurements and construction provenance are in `final_blr_results/road_graph/road_graph_integrity.md` and `graph_measurements_v2k.json`, audited at source commit `128dd0324deeb23310a93cb2aaa98f2032efb648`. v2n reused this completed audit and independently hashed the source objects; no graph was rebuilt.

## Source exhibit 4: `final_blr_results/city_scale/graph/graph_compatibility.md`

[EVIDENCE: `final_blr_results/city_scale/graph/graph_compatibility.md` | SHA-256 `7040c4c5f464632764d108d6355a1c1836a2e0c665c349cad1c251e1c747a846` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Graph compatibility verdict

| Pairing | Verdict | Reason |
|---|---|---|
| Raw OSM graph to processed road topology | COMPATIBLE | Counts reconcile by loop removal, reverse arcs and deduplication; all indices and lengths valid. |
| Road topology to 64 stored partitions | APPROXIMATE WITH ASSUMPTIONS | Every node is assigned, but 7,134 directed cross-boundary arcs disappear; two-hop halo equivalence has not been demonstrated. |
| 15-station corrected forecast graph to 154,902-node road graph | BLOCKED | Different nodes, graph construction, distance edge features, dynamic input schema and target population. |
| Road graph to monitored road-node PM2.5 validation | UNVERIFIABLE | The 23 station snaps do not provide independent concentration labels at all roads. |

The corrected ST-PIGNN was evaluated on a 15-station directed four-neighbor distance kNN graph, not this OSM graph. A loaded tensor of matching shape would not establish transfer. Full-city predictive inference remains gated by checkpoint and node-hour feature compatibility in `../features/feature_validation.md`. No full-road model forward pass was made.

## Source exhibit 5: `final_blr_results/ieee_paper_evidence/methodology/GRAPH_CONSTRUCTION.md`

[EVIDENCE: `final_blr_results/ieee_paper_evidence/methodology/GRAPH_CONSTRUCTION.md` | SHA-256 `8d0930b6d78b50a6ceddc24246ed217b120cd2c4c9f72964d2489e7f15651bf8` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Graph construction

Two graphs must remain distinct. The canonical OSM road graph contains 154,902 nodes; 393,089 raw directed edge rows; 424,550 processed message arcs; 64 geographical partitions; and 7,134 directed cross-partition arcs absent from the historical partition representation. Structural integrity is documented in `final_blr_results/city_scale/graph/`.

Corrected station forecasting instead uses a 15-monitor directed kNN graph with 60 directed edges. No corrected ST-PIGNN message passing was run directly across all road nodes. Original notebook partitioning is historical and omits cross-partition arcs. A valid road graph is not evidence of concentration accuracy.
