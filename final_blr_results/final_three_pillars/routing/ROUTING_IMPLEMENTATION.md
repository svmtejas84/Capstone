# Routing implementation recovery

## Components and provenance

| Component | Code | Behavior and limitations |
|---|---|---|
| Network | `data/graphs/bangalore_utm.graphml`; also OSMnx APIs in `router/api/routes.py` | Directed road MultiDiGraph, length in meters, OSM road tags/coordinates. Road geometry is not air-flow geometry. |
| Candidate route generation | `router/api/routes.py::_candidate_paths` | Converts edge PM to inhaled dose, creates dose-weighted and distance-weighted simple paths; API uses an approximate geometric heuristic. The returned top-k are ranked with mode-level dose/distance score. |
| Historical fixed snapshot | `scripts/prepare_routing_snapshot.py` | Uses latest available historical feature window and root legacy road checkpoint, then averages endpoint PM to edges. v2q found its underlying original model inputs can include target-hour leakage/duplicated station histories; treat snapshot as historical simulation input only. |
| Offline comparison | `scripts/evaluate_routing_gs.py` | `length` (m); fixed `SPEED_M_H=15000` (15 km/h); fixed `RMV_M3_H=3.5` (m³/h); edge dose `C(µg/m³) × RMV(m³/h) × length/speed(m/h)`, yielding µg. Distance A* and dose-weighted alternatives share endpoint demands. |
| Serving API dose | `router/edge_cost.py`, `shared/physics_config.py` | `C × RMV × travel_time`; RMV values: walking 1.2, cycling 3.5, two-wheeler 0.6 m³/h; aliases map jogger→walking and cyclist→cycling. API derives travel time from a fixed mode speed; result is modeled inhaled mass, not absorbed dose. |
| Capacity | `matcher/road_capacity.py` | Road class lane-flow constants (vehicles/hour/lane), parsed lanes/width and optional congestion, divided into a 900-s allocation window and duration penalty. These are assumed operational capacities, not measured Bengaluru flow capacities. |
| Serving matching | `matcher/gale_shapley.py::batch_match` | Route proposer/route receiver with per-route quotas only. Fallback assigns leftover commuters without rechecking capacity, so hard route capacity is not guaranteed when preferences/iterations are exhausted. It cannot represent an edge shared by overlapping routes. |
| Offline bundle allocator | `scripts/evaluate_routing_gs.py::deferred_acceptance` | Tracks reservations on each directed edge, rejects overflow users, releases all route-edge reservations, then reproposes. A final assertion checks edge quotas. Multi-edge bundle preferences do not satisfy general substitutability; algorithm is not a general stable matching or welfare optimizer. |
| Rust path crate | `router/rust_astar` | Current `astar.rs::astar_cost` returns `0.0`; no production A* implementation is present there. NetworkX is used in the active API/evaluator. |

The serving API catches ST-PIGNN inference errors and falls back to persistence. Successful endpoint output does not prove ST-PIGNN edge inference was used. Its API `matching_applied` is false absent a commuter-count simulation. The original notebook itself did not implement the routing optimizer; it lives in separate repository modules/scripts.

## Route continuity and disconnections

API `_candidate_paths` returns an empty set on a no-path A* request. `scripts/evaluate_routing_gs.py::simulate` samples both endpoints in the largest strongly connected component, so its trial set intentionally avoids disconnected OD demands. Route costs sum edge length/time/dose; the toy diagnostics independently checked endpoint/edge continuity and that a disconnected destination raises `NetworkXNoPath`.
