# Capacity and shared-edge overlap audit

## Serving API

`matcher.gale_shapley.batch_match` receives `route_ids`, preferences and one integer capacity per route. It receives no `route_edges` or edge-capacity map. `router.api.routes::route` computes each path's quota independently via `matcher.road_capacity.route_capacity`. If path A and path B share edge (e), the route quota calculation can count the same physical arc once in each route. The matching call cannot discover or prevent ∑ assigned users across A/B exceeding a shared edge's quota.

The fallback creates a second independent failure: after all normal proposals are rejected or the iteration cap is reached, `_best_fallback_route` adds every unmatched commuter to a route without checking route capacity. Existing `matcher/tests/test_gale_shapley.py::test_batch_match_fallback_assigns_when_iterations_cap_hit` intentionally verifies complete assignment but does not assert quota feasibility; the new deterministic counterexample shows two assigned to a route quota of one.

## Offline path-bundle evaluator

The `scripts/evaluate_routing_gs.py` evaluator does represent shared directed arcs. It uses `edge_users[(u,v)]` sets; proposing a route reserves all its arcs. An overfull arc sorts users by route `(dose_ug, time_min, trip index)` and places all excess users in a rejection set. A rejection releases every arc of that user's current route. It terminates when every queued commuter is exhausted or held, and asserts `len(edge_users[e]) <= quota[e]` for each occupied directed edge. The new overlapping-route toy example passes: two paths share a quota-one arc, one user shifts to an alternative, and all retained edge counts remain within quota.

This is a genuine computational mechanism for edge-wise feasibility in the offline allocation. It is not present in API `batch_match`, and the quota values are not validated traffic capacities. The saved benchmark summary has no retained route paths/edge occupancy table or independently recomputable violation count; hence the historical terminal assertion is not an external audit artifact.

## Quota provenance

- API `route_capacity`: road-class constants (e.g. primary 1200, residential 450 vehicles/hour/lane), lane/width parsing/defaults, optional congestion discount, 900-second window, route time penalty, minimum one. These are code assumptions.
- Offline evaluator: (q_e=\mathrm{clip}(\lfloor 12\cdot\mathrm{median}(C)/\max(C_e,0.01)\rfloor,1,48)), where (C_e) is static modeled PM2.5 on each directed arc. This makes assigned capacity inversely proportional to modeled pollution. Historical observed quotas were 9–12. This is a pollution-allocation heuristic, not a traffic engineering capacity model.

## Finding

The repository did not have one unified matching implementation that both served the API and enforced shared-edge resources. The offline evaluator solved a narrower bookkeeping problem (edge quota feasibility for its current allocation); the production serving matcher does not. Neither supports a claim of validated capacity satisfaction in actual traffic.
