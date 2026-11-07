# Frozen v2t routing protocol — 2026-11-07

This is exploratory computational validation on an exposed Bengaluru scenario. No road concentration or commuter flow is independently observed. Freeze before code changes or result inspection.

## Inputs and methods

Use `data/processed/evaluations/routing_snapshot.graphml` (SHA-256 `38e2a46792e9209af57e9c71fb17f6768e0117016e978ebc280ba96241647810`; 1,428 nodes/3,459 raw directed arcs; EPSG:32643). It comes from the historical citywide checkpoint and latest 12-hour input; it is a static experimental scenario. `scripts/evaluate_routing_gs.py::load_graph` collapses parallel arcs retaining the shortest edge and its PM. Demand samples only the sorted largest strongly connected component, with two distinct nodes per OD. Freeze batch sizes 12, 24, 48; seeds 11, 23, 37. Use the same generated OD and concentration field for all methods. Three candidates per OD via existing offline `candidate_routes` plus distance A*, and fixed speed 15 km/h, RMV 3.5 m³/h; distance in m, time in min, modeled inhaled mass in µg.

Methods: shortest distance; fastest time (identical to distance at fixed speed, report explicitly); unconstrained minimum modeled dose; original serving `matcher.gale_shapley.batch_match` on each batch's candidate-route labels and capacities; corrected preference DA with shared directed-edge and route quotas. The historical offline `deferred_acceptance` is an additional capacity control, not the serving baseline. Preserve the original API behavior as a separately callable historical control.

For each OD, rank routes by the original API commuter score `alpha*normalized_dose+(1-alpha)*distance/tolerance`; use cycling alpha .60 and tolerance 8,000 m. Since all commuters use the same mode in this controlled scenario, RMV is 3.5. Receiver priority is the original `Segment` score with cycling mode and `id_min=2.4`; deterministic commuter ID breaks ties. Across different routes sharing an edge, compare the rank in that route's original receiver list, then commuter ID. This cross-route rule is a declared extension; ordinary GS stability is not presumed.

Route quota: existing `route_capacity` computed on each path's edge attributes and total route time. Edge quota: the same function on each single directed edge and its travel time, with a 900-s window, default road-class/lane assumptions and no invented observed traffic. If `route_capacity` creates quotas larger than demand, report that shared-edge constraint is unstressed; toy tests provide the critical capacity gate. Directed `(u,v)` resources are distinct from `(v,u)`. Unit demand is one commuter per traversed edge. Original serving matcher gets only route quotas; corrected gets route and shared-edge quotas. No post-loop forced assignment in corrected mode.

## Concentration stress scenarios

Primary original field. Prespecified stress tests: uniform ×1.25; spatially varying `C_e*(1+0.25*sin(x_mid/1000))` clipped at zero; support-dependent `C_e*(1+0.25*min(d_nearest_station/5000,1))` if verified station coordinates are available, otherwise mark this scenario NOT RUN. All perturbations are synthetic stress tests, not calibrated uncertainty. OD batches and capacities are fixed from the original field so sensitivity isolates route/cost changes, not altered traffic-resource budgets. Recompute candidate routes, preferences and doses for each field.

## Outputs and statistics

For every method/scenario/batch, retain request IDs and OD, assigned/unassigned, path and edge list, distance/time/dose, route score, capacity use, runtime, invalid-route count, route diversity, saturated-edge count. Report all requests, each method's admitted set, and the common admitted set for allocator contrasts. Pair dose/time differences on common IDs. Treat each of 9 demand batches as one replicate; report mean and range/percentile intervals across batches without claiming independent commuter-level inference. Keep negative outcomes.

## Gates and limits

Before benchmark: deterministic tests for 15 requested correctness cases, independent exhaustive feasibility check on small instances, no zero-capacity assignment, atomic release and nonnegative residuals. Any failure blocks benchmark until repaired. Bound benchmark to the 1,428-node snapshot, at most 48 requests per batch and 3 candidates per OD, nine batches and four concentration scenarios; stop at 45 minutes wall or 4 GB peak RAM. Use the repository supervised runner for long execution, with logs/locks/markers. No new model fit, citywide forecast or historical artifact overwrite. A completed benchmark is computational scenario evidence, never measured exposure reduction.
