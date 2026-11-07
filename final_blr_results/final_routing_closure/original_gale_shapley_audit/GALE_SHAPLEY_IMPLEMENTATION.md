# Recovered Gale–Shapley implementations

Two distinct allocation mechanisms exist. Their properties must not be combined.

## Serving API: route-capacitated one-to-many deferred acceptance

`router/api/routes.py::route` creates a candidate set and one `Segment` object per candidate route. `matcher/gale_shapley.py::batch_match` treats each commuter as a proposer and each route ID as a receiver with capacity. It is not a road-edge matching algorithm.

1. **Proposer:** commuter. The API includes the real `requester`; optional `commuter_counts` adds synthetic cohort members for load simulation.
2. **Receiver / participant:** candidate route ID (despite variable names `segment_*`).
3. **Commuter ranking:** `score = α·(dose/max_candidate_dose) + (1−α)·(distance/distance_tolerance)`, ascending; ties use input route order. Mode α: jogger .75, cyclist .60, two-wheeler/car .35. Dose is edge concentration × RMV × traversal time summed along path; route dose and distances are computed before matching.
4. **Route ranking:** `score = (mode_vulnerability_weight + 1/id_min)/(1+max(0, congestion_penalty))`, descending then commuter ID. Current API leaves congestion penalty at 0; `cedge_mean` is not used. If a route preference list omits a commuter, the matcher assigns an equal default rank rather than treating that pair as unacceptable.
5. **Capacity:** `route_capacity` computes an integer quota for each whole candidate route, using its minimum modeled road class/lane/congestion capacity and route-duration discount. Each route has a separate quota. No edge set is passed to the matcher.
6. **Displacement:** a route at capacity replaces its worst current member if the new proposer has a better route ranking. The displaced commuter is queued to propose to its next listed route.
7. **Fallback:** after the loop, every unmatched commuter is assigned by nearest route distance (if available) or least-loaded route. The fallback does not check quota and can assign outside the commuter's listed preferences.

The API sets `matching_applied` only when `commuter_counts` is provided. With no cohort, the requester alone is matched and retains their top preference. Candidate recommendations are not evidence of operational group allocation.

## Offline evaluator: route-bundle edge deferred acceptance

`scripts/evaluate_routing_gs.py::deferred_acceptance` is separate from `batch_match`. A commuter proposes whole paths in ascending `(dose_ug, time_min)` order. Every directed edge in a proposed route is reserved for that commuter. For each over-quota edge, applicants are ranked by their currently proposed route's `(dose, time, commuter index)`; all commuters rejected by any edge have their entire path reservation released and are requeued to their next path. Exhausted commuters remain unassigned. A final assertion checks every retained edge occupancy against its per-edge quota.

Thus this evaluator **does account for overlapping directed edges and preserves ex-post quota feasibility** for its returned allocation. It has no route-independent receiver preferences: each edge compares applicants by the total score of their current route. A path is a bundle of complementary resources. Rejection at one edge releases all resources in the bundle. Classical resident-proposing/commuter-proposing Gale–Shapley theorems do not directly apply to these bundle choice functions; no general stability, strategy-proofness or welfare optimality was shown.

## A* and candidate generation

Serving API `_candidate_paths` creates up to `k=3` choices by dose-weighted A* (`heuristic=_heuristic`, Euclidean projected metres, edge weight µg), dose-weighted `shortest_simple_paths`, and distance-weighted `shortest_simple_paths`; candidate paths are deduplicated, scored and truncated. Since the API dose-A* heuristic is distance in metres against a dose-in-µg path cost, admissibility/optimality is not established. The offline evaluator instead obtains the distance route with A* and a scaled Euclidean lower bound; dose and blended alternatives use `shortest_path`, not dose A*.

The offline evaluator's exact recorded command used `--max-routes 3`; although the script default is four, the saved additional-evaluation report confirms the override. A previous v2r protocol summary saying “up to four” described the default, not this historical run; use three for the run-specific account.
