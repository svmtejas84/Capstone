# Volume 13 — Dose-aware routes and constrained preference allocation

<a id="volume-13"></a>

## Editorial reconstruction and evidentiary boundary

The original serving matcher and offline evaluator are distinct. The serving API used route quotas and a forced fallback; it did not represent shared road-edge capacities. The offline evaluator reserved directed edges and generated the earlier 1,000-request report: 444 assigned, admitted-only modeled dose +0.1211%, travel time +0.1463%. v2t retained the historical implementations and added a preference-based deferred-acceptance allocator with directed-edge reservations, atomic route release and explicit UNASSIGNED. Twenty focused tests passed, and 6,048 method-request outputs contained no invalid path or declared-capacity violation. In the 1,008-request scenario the original and corrected serving paths were identical and max edge utilization only 5.405%; dose changed −0.001207% versus shortest, time +0.001324%. This is not evidence of measured human exposure reduction, universal matching stability or operational traffic capacity. [EVIDENCE: v2t verdict | final_blr_results/final_routing_closure/v2t/ROUTING_FINAL_VERDICT.md | snapshot 1c46a4b]

## Full round-specific source exhibits

The exhibits reproduce the cited local reports as source evidence. Their original round-specific conclusions may be narrower than later findings; read the editorial reconstruction and final synthesis before treating one exhibit as the final verdict.

## Source exhibit 1: `final_blr_results/final_three_pillars/routing/ROUTING_IMPLEMENTATION.md`

[EVIDENCE: `final_blr_results/final_three_pillars/routing/ROUTING_IMPLEMENTATION.md` | SHA-256 `55d330edb066bb63a899467342909eb62ef10ee889e036dcd196d6f4d400c36e` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Routing implementation recovery

#### Components and provenance

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

#### Route continuity and disconnections

API `_candidate_paths` returns an empty set on a no-path A* request. `scripts/evaluate_routing_gs.py::simulate` samples both endpoints in the largest strongly connected component, so its trial set intentionally avoids disconnected OD demands. Route costs sum edge length/time/dose; the toy diagnostics independently checked endpoint/edge continuity and that a disconnected destination raises `NetworkXNoPath`.

## Source exhibit 2: `final_blr_results/final_routing_closure/original_gale_shapley_audit/GALE_SHAPLEY_IMPLEMENTATION.md`

[EVIDENCE: `final_blr_results/final_routing_closure/original_gale_shapley_audit/GALE_SHAPLEY_IMPLEMENTATION.md` | SHA-256 `9b6f4f3ce9d23b79b6ec269f93bcfbd663f605d92e2b99bd9a092fe7242dc8fb` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Recovered Gale–Shapley implementations

Two distinct allocation mechanisms exist. Their properties must not be combined.

#### Serving API: route-capacitated one-to-many deferred acceptance

`router/api/routes.py::route` creates a candidate set and one `Segment` object per candidate route. `matcher/gale_shapley.py::batch_match` treats each commuter as a proposer and each route ID as a receiver with capacity. It is not a road-edge matching algorithm.

1. **Proposer:** commuter. The API includes the real `requester`; optional `commuter_counts` adds synthetic cohort members for load simulation.
2. **Receiver / participant:** candidate route ID (despite variable names `segment_*`).
3. **Commuter ranking:** `score = α·(dose/max_candidate_dose) + (1−α)·(distance/distance_tolerance)`, ascending; ties use input route order. Mode α: jogger .75, cyclist .60, two-wheeler/car .35. Dose is edge concentration × RMV × traversal time summed along path; route dose and distances are computed before matching.
4. **Route ranking:** `score = (mode_vulnerability_weight + 1/id_min)/(1+max(0, congestion_penalty))`, descending then commuter ID. Current API leaves congestion penalty at 0; `cedge_mean` is not used. If a route preference list omits a commuter, the matcher assigns an equal default rank rather than treating that pair as unacceptable.
5. **Capacity:** `route_capacity` computes an integer quota for each whole candidate route, using its minimum modeled road class/lane/congestion capacity and route-duration discount. Each route has a separate quota. No edge set is passed to the matcher.
6. **Displacement:** a route at capacity replaces its worst current member if the new proposer has a better route ranking. The displaced commuter is queued to propose to its next listed route.
7. **Fallback:** after the loop, every unmatched commuter is assigned by nearest route distance (if available) or least-loaded route. The fallback does not check quota and can assign outside the commuter's listed preferences.

The API sets `matching_applied` only when `commuter_counts` is provided. With no cohort, the requester alone is matched and retains their top preference. Candidate recommendations are not evidence of operational group allocation.

#### Offline evaluator: route-bundle edge deferred acceptance

`scripts/evaluate_routing_gs.py::deferred_acceptance` is separate from `batch_match`. A commuter proposes whole paths in ascending `(dose_ug, time_min)` order. Every directed edge in a proposed route is reserved for that commuter. For each over-quota edge, applicants are ranked by their currently proposed route's `(dose, time, commuter index)`; all commuters rejected by any edge have their entire path reservation released and are requeued to their next path. Exhausted commuters remain unassigned. A final assertion checks every retained edge occupancy against its per-edge quota.

Thus this evaluator **does account for overlapping directed edges and preserves ex-post quota feasibility** for its returned allocation. It has no route-independent receiver preferences: each edge compares applicants by the total score of their current route. A path is a bundle of complementary resources. Rejection at one edge releases all resources in the bundle. Classical resident-proposing/commuter-proposing Gale–Shapley theorems do not directly apply to these bundle choice functions; no general stability, strategy-proofness or welfare optimality was shown.

#### A* and candidate generation

Serving API `_candidate_paths` creates up to `k=3` choices by dose-weighted A* (`heuristic=_heuristic`, Euclidean projected metres, edge weight µg), dose-weighted `shortest_simple_paths`, and distance-weighted `shortest_simple_paths`; candidate paths are deduplicated, scored and truncated. Since the API dose-A* heuristic is distance in metres against a dose-in-µg path cost, admissibility/optimality is not established. The offline evaluator instead obtains the distance route with A* and a scaled Euclidean lower bound; dose and blended alternatives use `shortest_path`, not dose A*.

The offline evaluator's exact recorded command used `--max-routes 3`; although the script default is four, the saved additional-evaluation report confirms the override. A previous v2r protocol summary saying “up to four” described the default, not this historical run; use three for the run-specific account.

## Source exhibit 3: `final_blr_results/final_routing_closure/original_gale_shapley_audit/MATCHING_MATHEMATICAL_FORMULATION.md`

[EVIDENCE: `final_blr_results/final_routing_closure/original_gale_shapley_audit/MATCHING_MATHEMATICAL_FORMULATION.md` | SHA-256 `4d45178723429aa29807f3fd12d89952d8d7bf12edbf0b66cf1ed65d02b89645` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Matching formulation and guarantees

#### Serving route matching

Let commuters be (C), route candidates (R), route capacity (q_r\in\mathbb{Z}_{\ge1}), and each commuter (c) rank a finite ordered list of routes. Each route (r) ranks commuters. The implementation is the usual commuter-proposing deferred-acceptance loop for a many-to-one market: an unmatched commuter proposes to their next route; a route holds the best (q_r) applicants so far and rejects/displaces the rest.

For the API, commuter route utility is ranked by

\[
s_{cr}=\alpha_m\frac{D_r}{\max_{j\in R}D_j}+(1-\alpha_m)\frac{L_r}{\ell_c},
\]

where (D_r\) is modeled inhaled mass, (L_r\) route length, ℓ_c is distance tolerance, and α_m is mode dependent. Lower is preferred. The route receiver score is

\[
v_{rc}=\frac{w_{m(c)}+1/\mathrm{idmin}_c}{1+\max(0,\gamma_r)},
\]

ranked higher first (ties broken by commuter ID); current API uses γ_r=0. The route quota is independently estimated from the minimum edge class/lane capacity, a 900 s window and route-duration discount; it is not a shared-link allocation model.

#### Classical theorem boundary

For finite commuters and routes, complete strict preferences over mutually acceptable pairs, fixed route quotas, responsive route preferences (a route chooses its top (q_r) applicants), and no post-processing fallback, commuter-proposing deferred acceptance terminates after at most ∑_c |P_c| proposals. The result is feasible and stable in the standard many-to-one sense: no commuter-route pair both prefers each other to their assignment, with unmatched below every acceptable listed route. It is commuter-optimal among stable outcomes under those assumptions. These guarantees are limited to the abstract route quota, not physical road-edge capacity.

The API implementation's default (n\times |R|) loop bound is enough for unique complete preference lists, but the current fallback then assigns all remaining commuters without enforcing quota/acceptability. Therefore the actual function does **not** guarantee feasible or stable output when unmatched proposers remain. Equal default receiver ranks for omitted commuters also break the complete strict-preference assumptions unless lists are complete.

#### Offline path-bundle allocator

For each route choice (p\), let (E(p)) be its set of directed road arcs and (q_e) the quota on arc (e). The allocator maintains selected commuters (x_c\in P_c\cup\{\varnothing\}) with

\[
\sum_c\mathbf 1[e\in E(x_c)]\le q_e\quad\forall e.
\]

This explicit set constraint provides ex-post feasibility because every overfull edge rejects enough applicants and each rejected path releases all its edge reservations before termination. Each commuter proposes to each finite option at most once, so the procedure terminates. It is not standard many-to-one matching: commuters demand bundles of edges, while each edge's ranking of a commuter depends on the commuter's current whole-route dose/time. The conditions required for standard deferred-acceptance stability—particularly substitutable choice—are not established. Feasibility does not imply pairwise stability, a core outcome, or social-welfare optimality.

#### What is and is not guaranteed

| Property | API `batch_match` | Offline `deferred_acceptance` |
|---|---|---|
| Termination | Finite proposal list / n×m guard; finite in current API. | Finite options, each proposal advances a pointer. |
| Route quota feasibility | Only before fallback; fallback can overflow. | Edge quota feasibility enforced by path release and final assertion. |
| Shared-edge feasibility | Not representable. | Yes for the directed arcs and quotas supplied. |
| Individual rationality | Not guaranteed after fallback. | A selected route is a listed proposal; exhausted demand stays unmatched. |
| Standard matching stability | Only under complete strict preferences, responsive route choices and no fallback. | Not established for complementary path bundles. |
| Welfare / dose optimality | Not guaranteed; proposer-optimality only within stable outcomes under theorem assumptions. | Not guaranteed; local edge rankings are not a global objective. |

## Source exhibit 4: `final_blr_results/final_routing_closure/original_gale_shapley_audit/CAPACITY_AND_OVERLAP_AUDIT.md`

[EVIDENCE: `final_blr_results/final_routing_closure/original_gale_shapley_audit/CAPACITY_AND_OVERLAP_AUDIT.md` | SHA-256 `741a2951ffd5a41bb3bf6b89aab3f05e61a89a25336a3ff84756c59057007a9f` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Capacity and shared-edge overlap audit

#### Serving API

`matcher.gale_shapley.batch_match` receives `route_ids`, preferences and one integer capacity per route. It receives no `route_edges` or edge-capacity map. `router.api.routes::route` computes each path's quota independently via `matcher.road_capacity.route_capacity`. If path A and path B share edge (e), the route quota calculation can count the same physical arc once in each route. The matching call cannot discover or prevent ∑ assigned users across A/B exceeding a shared edge's quota.

The fallback creates a second independent failure: after all normal proposals are rejected or the iteration cap is reached, `_best_fallback_route` adds every unmatched commuter to a route without checking route capacity. Existing `matcher/tests/test_gale_shapley.py::test_batch_match_fallback_assigns_when_iterations_cap_hit` intentionally verifies complete assignment but does not assert quota feasibility; the new deterministic counterexample shows two assigned to a route quota of one.

#### Offline path-bundle evaluator

The `scripts/evaluate_routing_gs.py` evaluator does represent shared directed arcs. It uses `edge_users[(u,v)]` sets; proposing a route reserves all its arcs. An overfull arc sorts users by route `(dose_ug, time_min, trip index)` and places all excess users in a rejection set. A rejection releases every arc of that user's current route. It terminates when every queued commuter is exhausted or held, and asserts `len(edge_users[e]) <= quota[e]` for each occupied directed edge. The new overlapping-route toy example passes: two paths share a quota-one arc, one user shifts to an alternative, and all retained edge counts remain within quota.

This is a genuine computational mechanism for edge-wise feasibility in the offline allocation. It is not present in API `batch_match`, and the quota values are not validated traffic capacities. The saved benchmark summary has no retained route paths/edge occupancy table or independently recomputable violation count; hence the historical terminal assertion is not an external audit artifact.

#### Quota provenance

- API `route_capacity`: road-class constants (e.g. primary 1200, residential 450 vehicles/hour/lane), lane/width parsing/defaults, optional congestion discount, 900-second window, route time penalty, minimum one. These are code assumptions.
- Offline evaluator: (q_e=\mathrm{clip}(\lfloor 12\cdot\mathrm{median}(C)/\max(C_e,0.01)\rfloor,1,48)), where (C_e) is static modeled PM2.5 on each directed arc. This makes assigned capacity inversely proportional to modeled pollution. Historical observed quotas were 9–12. This is a pollution-allocation heuristic, not a traffic engineering capacity model.

#### Finding

The repository did not have one unified matching implementation that both served the API and enforced shared-edge resources. The offline evaluator solved a narrower bookkeeping problem (edge quota feasibility for its current allocation); the production serving matcher does not. Neither supports a claim of validated capacity satisfaction in actual traffic.

## Source exhibit 5: `final_blr_results/final_routing_closure/original_gale_shapley_audit/PREVIOUS_BENCHMARK_RECONCILIATION.md`

[EVIDENCE: `final_blr_results/final_routing_closure/original_gale_shapley_audit/PREVIOUS_BENCHMARK_RECONCILIATION.md` | SHA-256 `7e403abb8096709feb9c33eeddbdda7986cca01856296aed8f8a5ec0bf74b9b5` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Reconciliation of the 1,000-trip benchmark

The prior three-pillar summary's numbers are correct, but the implementation identity needs precision.

#### What ran

The command in `ST_PIGNN_additional_eval_23oct2026.md` invokes `scripts/evaluate_routing_gs.py --trips 1000 --max-routes 3 --seed 42`. Its allocation call is `scripts/evaluate_routing_gs.py::deferred_acceptance`, **not** `matcher.gale_shapley.batch_match` and not the FastAPI `router.api.routes::route` pathway. The evaluator does perform a custom route-bundle deferred-acceptance procedure with directed-edge quota bookkeeping and asserts final per-edge feasibility. Thus it was more than a per-route-only simplified matcher for the specific simulated allocation, but it did not evaluate the serving API's complete end-to-end routing/matching system or provide formal classical Gale–Shapley stability.

#### Demand, costs and comparator

- **Demand:** 1,000 pseudo-random OD pairs (no replacement within each pair) sampled from nodes in the largest strongly connected component of a 1.5-km central Bengaluru OSM graph; seed 42. They are synthetic requests, not observed commuter flows.
- **Candidate choice:** up to three routes, generated from distance A*, minimum-dose path and blended/shortest-simple-path alternatives. Deferred-acceptance proposal order is ascending modeled route dose then travel time.
- **Capacity:** each directed edge quota is pollution-inverse `floor(12 × median edge PM / max(edge PM, 0.01))`, clipped 1–48; observed 9–12. This is not traffic flow capacity.
- **Pollution field:** legacy root citywide checkpoint on its latest 12-hour feature window; road-node estimate clipped to 0–120 then averaged at edge endpoints. The v2q audit identified target-hour/input validity concerns. It is static, model-derived and not roadside-validated.
- **Dose/time:** fixed 15 km/h and 3.5 m³/hour RMV; (D=\sum_e C_e\,RMV\,L_e/v). This produces modeled inhaled mass in µg. Since speed and RMV are constant, fastest and shortest length co-rank.
- **Comparator:** distance-minimizing A* on the same OD pairs, evaluated on the 444 pairs admitted by the bundle allocator. Dose and time differences are conditional on admission, not an all-request comparison. There is no separately reported unconstrained minimum-dose baseline.

#### Results and limitations

Admission was 444/1,000 (44.4%); 556 remained unmatched. On admitted trips, mean modeled dose changed `0.2714978885 → 0.2718266394 µg` (+0.1210878%); time changed `3.53588536 → 3.54105928 min` (+0.1463261%). These values recompute from the saved 444-row trip CSV and agree with `routing_results.json`.

The result does **not** show an API matcher shared-edge defect in operation: the offline evaluator independently tracks shared edges. Conversely, it does **not** validate the API route-quota matcher, since that implementation was not called. Its successful final assertion is evidence only that the offline allocator returned a quota-feasible set for this run; edge occupancy/path records were not saved for independent re-audit. No matching stability, route diversity, runtime, scaling, per-trip distance overhead, or real exposure result is available.

An earlier audit protocol said “up to four candidates,” based on the script default. The exact recorded command overrides this with `--max-routes 3`; this reconciliation uses three. No files in the old benchmark were changed or rerun.

## Source exhibit 6: `final_blr_results/final_routing_closure/v2t/ROUTING_PROTOCOL.md`

[EVIDENCE: `final_blr_results/final_routing_closure/v2t/ROUTING_PROTOCOL.md` | SHA-256 `70eb0543188d7204552dc8a6b87f1060e2bcca454723d89004cbd61d8575693e` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Frozen v2t routing protocol — 2026-11-07

This is exploratory computational validation on an exposed Bengaluru scenario. No road concentration or commuter flow is independently observed. Freeze before code changes or result inspection.

#### Inputs and methods

Use `data/processed/evaluations/routing_snapshot.graphml` (SHA-256 `38e2a46792e9209af57e9c71fb17f6768e0117016e978ebc280ba96241647810`; 1,428 nodes/3,459 raw directed arcs; EPSG:32643). It comes from the historical citywide checkpoint and latest 12-hour input; it is a static experimental scenario. `scripts/evaluate_routing_gs.py::load_graph` collapses parallel arcs retaining the shortest edge and its PM. Demand samples only the sorted largest strongly connected component, with two distinct nodes per OD. Freeze batch sizes 12, 24, 48; seeds 11, 23, 37. Use the same generated OD and concentration field for all methods. Three candidates per OD via existing offline `candidate_routes` plus distance A*, and fixed speed 15 km/h, RMV 3.5 m³/h; distance in m, time in min, modeled inhaled mass in µg.

Methods: shortest distance; fastest time (identical to distance at fixed speed, report explicitly); unconstrained minimum modeled dose; original serving `matcher.gale_shapley.batch_match` on each batch's candidate-route labels and capacities; corrected preference DA with shared directed-edge and route quotas. The historical offline `deferred_acceptance` is an additional capacity control, not the serving baseline. Preserve the original API behavior as a separately callable historical control.

For each OD, rank routes by the original API commuter score `alpha*normalized_dose+(1-alpha)*distance/tolerance`; use cycling alpha .60 and tolerance 8,000 m. Since all commuters use the same mode in this controlled scenario, RMV is 3.5. Receiver priority is the original `Segment` score with cycling mode and `id_min=2.4`; deterministic commuter ID breaks ties. Across different routes sharing an edge, compare the rank in that route's original receiver list, then commuter ID. This cross-route rule is a declared extension; ordinary GS stability is not presumed.

Route quota: existing `route_capacity` computed on each path's edge attributes and total route time. Edge quota: the same function on each single directed edge and its travel time, with a 900-s window, default road-class/lane assumptions and no invented observed traffic. If `route_capacity` creates quotas larger than demand, report that shared-edge constraint is unstressed; toy tests provide the critical capacity gate. Directed `(u,v)` resources are distinct from `(v,u)`. Unit demand is one commuter per traversed edge. Original serving matcher gets only route quotas; corrected gets route and shared-edge quotas. No post-loop forced assignment in corrected mode.

#### Concentration stress scenarios

Primary original field. Prespecified stress tests: uniform ×1.25; spatially varying `C_e*(1+0.25*sin(x_mid/1000))` clipped at zero; support-dependent `C_e*(1+0.25*min(d_nearest_station/5000,1))` if verified station coordinates are available, otherwise mark this scenario NOT RUN. All perturbations are synthetic stress tests, not calibrated uncertainty. OD batches and capacities are fixed from the original field so sensitivity isolates route/cost changes, not altered traffic-resource budgets. Recompute candidate routes, preferences and doses for each field.

#### Outputs and statistics

For every method/scenario/batch, retain request IDs and OD, assigned/unassigned, path and edge list, distance/time/dose, route score, capacity use, runtime, invalid-route count, route diversity, saturated-edge count. Report all requests, each method's admitted set, and the common admitted set for allocator contrasts. Pair dose/time differences on common IDs. Treat each of 9 demand batches as one replicate; report mean and range/percentile intervals across batches without claiming independent commuter-level inference. Keep negative outcomes.

#### Gates and limits

Before benchmark: deterministic tests for 15 requested correctness cases, independent exhaustive feasibility check on small instances, no zero-capacity assignment, atomic release and nonnegative residuals. Any failure blocks benchmark until repaired. Bound benchmark to the 1,428-node snapshot, at most 48 requests per batch and 3 candidates per OD, nine batches and four concentration scenarios; stop at 45 minutes wall or 4 GB peak RAM. Use the repository supervised runner for long execution, with logs/locks/markers. No new model fit, citywide forecast or historical artifact overwrite. A completed benchmark is computational scenario evidence, never measured exposure reduction.

## Source exhibit 7: `final_blr_results/final_routing_closure/v2t/CAPACITY_ALLOCATOR_SPECIFICATION.md`

[EVIDENCE: `final_blr_results/final_routing_closure/v2t/CAPACITY_ALLOCATOR_SPECIFICATION.md` | SHA-256 `cdc41556dd01d6a1f82fd2b477b1a43bd72784ab6cd46141564fc8280a8ee683` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Corrected preference allocator

`matcher/edge_capacity_da.py::allocate_shared_edges` is an additive implementation. The historical `matcher.gale_shapley.batch_match` and `scripts.evaluate_routing_gs.deferred_acceptance` remain callable. The serving endpoint defaults to corrected mode; `TOXICITY_ROUTE_ALLOCATOR=original` reproduces the historical matcher behavior.

Commuters propose route IDs in the original `matcher.commuter_model` order. Each route retains its original `matcher.segment_model` receiver ranking and has an integer route quota. Each route also consumes one unit of capacity on every directed `(u,v)` edge it traverses. `(v,u)` is a distinct resource. When a proposal overloads a route or edge, the lowest ranked user(s) are rejected. For two different routes sharing an edge, priority is the rank of each commuter in their proposed route's receiver list, then commuter ID. This cross-route ordering is an explicit extension; no classical stability theorem follows from it.

All rejections remove the user's whole route bundle before occupancy is checked again. Rejected users may propose the next route. An exhausted user returns `None`; the serving API reports `UNASSIGNED` and an empty route. The allocator validates unique IDs, directed route continuity, nonempty/nonrepeated edges, nonnegative capacities, and capacity metadata. It asserts route and edge occupancy after each proposal. It does not assign a route outside a commuter's preferences.

For each edge (e), the enforced invariant is \(\sum_c 1[e\in R_c]\le K_e\). Unit consumption is one simultaneous commuter per directed edge. The API obtains `K_e` from the existing `route_capacity` method applied to each physical edge's available OSM attributes and traversal time; route capacities remain computed from the whole path. These are assumed allocation ceilings, not measured traffic counts. Candidate routes remain limited to the existing three generated alternatives.

The algorithm terminates because each proposal advances that commuter's finite route-preference pointer. Feasibility is checked during every iteration and at the returned assignment. Global preference stability and welfare optimality are unproved for overlapping route bundles.

## Source exhibit 8: `final_blr_results/final_routing_closure/v2t/ROUTING_CORRECTNESS_TESTS.md`

[EVIDENCE: `final_blr_results/final_routing_closure/v2t/ROUTING_CORRECTNESS_TESTS.md` | SHA-256 `e5643492a2688aea2c15118a2066f654e1188f54975457e1f026cc1fba3fdc20` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Correctness gate

Command: `python -m pytest -q tests/test_edge_capacity_da_v2t.py matcher/tests/test_gale_shapley.py router/tests/test_edge_cost.py`. The focused pre-benchmark run passed **19/19** after one test expectation was corrected to specify an actual receiver-preference tie. The initial failed test expected lexical ID priority while its fixture had explicitly ranked the other commuter first; the implementation correctly followed the supplied ranking. A subsequent disconnected-OD test initially exposed `NodeNotFound` when the collapsed graph had no edges. The candidate generator now returns no candidates in that case, and the focused suite passed **20/20**. These failures and repairs remain documented here.

The new tests cover route competition, shared bottleneck, atomic release and reproposal, independent routes, zero capacity, excess demand, overlapping bundles, missing candidates, empty/noncontinuous/missing-capacity routes, duplicate commuter IDs, deterministic equal-rank tie, directed-edge distinction, and comparison to an exhaustive feasible-assignment enumerator on a small instance. The allocator asserts all supplied route and edge capacity invariants after every proposal. Units are verified by the existing `router/tests/test_edge_cost.py` suite. Historical original matcher tests also passed; they do not prove its capacity correctness.

One broader FastAPI route test command was interrupted after its initial tests passed but the process stalled without a final summary. It is not counted as a completed test run. The benchmark's one-request dry run completed on the real snapshot for all six compared methods before the full supervised job. The first supervised launch failed at import before any batch output; the run's attempt logs are preserved. A second run uses the fixed entry point and per-batch atomic files.

The audit-only tests under `final_routing_closure/original_gale_shapley_audit/` remain the counterexamples for the historical matcher. They are expected findings, not regressions in the new allocator.

## Source exhibit 9: `final_blr_results/final_routing_closure/v2t/ROUTING_METHODOLOGY.md`

[EVIDENCE: `final_blr_results/final_routing_closure/v2t/ROUTING_METHODOLOGY.md` | SHA-256 `96ef3f1632dd283a57b14b061017d39131545584cd222fab5a72725b03c2f5c8` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### v2t routing methodology and reproduction

Protocol frozen and pushed at `d85e81c9055f95fa5b900c29e50124d1c985c963` before code modification or benchmark. The complete frozen definitions are in `ROUTING_PROTOCOL.md`; this document records their execution. The original serving matcher, historical offline allocator and corrected allocator have separate entry points.

#### Sources and inputs

- Graph/concentration: `data/processed/evaluations/routing_snapshot.graphml`, SHA-256 `38e2a46792e9209af57e9c71fb17f6768e0117016e978ebc280ba96241647810`; 1,428 nodes, 3,459 raw directed arcs, EPSG:32643. `scripts.evaluate_routing_gs.load_graph` collapses parallel arcs to the shortest selected arc with matching PM. The field was built from the legacy city model and has no roadside accuracy validation.
- Station coordinates for the support stress factor: `results/stations_v2.csv`, transformed from WGS84 to EPSG:32643. Distance is a diagnostic, not uncertainty calibration.
- Demand: sorted largest strongly connected component, NumPy PCG64 seeds 11/23/37, 12/24/48 requests per batch, two distinct nodes per request; same OD list across all four concentration scenarios and methods. Total 36 batches, 1,008 scenario-request instances, 6,048 method-request rows.
- Candidate limit three; fixed cycling speed 15 km/h, RMV 3.5 m³/h. Edge dose (C\,[\mu g/m^3]\times3.5\,[m^3/h]\times L\,[m]/15000\,[m/h]) in µg. API preference uses cycling α=.60 and 8,000 m tolerance; receiver ranking uses cyclist vulnerability and `id_min=2.4`. This constant-mode design isolates path/allocation behavior.
- Route and directed-edge capacities from existing `matcher.road_capacity.route_capacity` with OSM road class/lane tags and 900-s window; one commuter consumes one unit on each traversed directed edge. Capacities stay fixed from the original field across perturbations.

#### Execution and verification

`run_benchmark.py` writes one atomic parquet per frozen batch/scenario, then the aggregate parquet and three required CSVs. The supervised runner logs are under `runs/benchmark_fixed/`; the initial `runs/benchmark/` failed before output because Python could not import the repository package. The repaired run completed all 36 cells. Its first attempt returned code 0 but wrote the completion marker in the result directory rather than the supervisor run directory; two restart attempts re-read all saved cells without redoing route generation. After verifying complete outputs, the supervisor completion marker was copied into its run directory. `run_supervised.sh status` reports COMPLETE. The failed attempts and recovery are retained.

Reproduction, subject to the historical local inputs: `PYTHONPATH=. MPLCONFIGDIR=/tmp/stpignn-v2t-mpl python final_blr_results/final_routing_closure/v2t/run_benchmark.py`; then `python final_blr_results/final_routing_closure/v2t/analyze_results.py`; then `PYTHONPATH=. python final_blr_results/final_routing_closure/v2t/verify_outputs.py`. Existing batch parquet files make reruns idempotent; remove none without a new authorized protocol. `python -m pytest -q tests/test_edge_capacity_da_v2t.py matcher/tests/test_gale_shapley.py router/tests/test_edge_cost.py` passed 20/20. No GPU or neural fit was used.

#### Comparisons and uncertainty

`ROUTING_PER_REQUEST_RESULTS.parquet` retains every submitted request and all six method outcomes. Every method assigned every request, so all submitted, admitted-only and common-admitted populations coincide in this bounded scenario. `PAIRED_COMPARISONS.csv` contains matched request differences by batch; `SENSITIVITY_STABILITY.csv` compares the same IDs with the original concentration scenario. Reported uncertainty is a range/2.5–97.5 percentile of nine batch-level values, not a confidence claim over independent commuters. No post-hoc subset was selected.

Runtime is measured for an entire batch including graph scenario construction, candidate generation and all six methods; it must not be assigned to a single method. Peak RAM was not recorded; GPU memory is 0 because CPU execution was used. The static concentration field, assumed RMV/speed, heuristic traffic quotas, small central area and synthetic OD demand limit external interpretation.

## Source exhibit 10: `final_blr_results/final_routing_closure/v2t/MATCHING_GUARANTEES.md`

[EVIDENCE: `final_blr_results/final_routing_closure/v2t/MATCHING_GUARANTEES.md` | SHA-256 `5a57ce5498a8ade745b58cc5e1709c761676178585e615ef62b16d26abcb3f55` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Mathematical claim audit

**Capacity feasibility:** The corrected allocator checks both route quotas and shared directed-edge quotas after every proposal. It releases all edges of a displaced route atomically and returns `None` if no candidate can be held. The test gate passed and an independent scan of all 6,048 saved rows found 0 invalid paths and 0 declared directed-edge quota violations across 216 method/batch/scenario groups. These quotas are assumed traffic capacities; they are not measured road flow limits. The frozen benchmark reached at most 5.405% utilization and saturated no edge, so the city scenario did not stress the correction.

**Preference stability:** Classical many-to-one Gale–Shapley stability applies to route-only quotas with complete strict responsive preferences and no fallback. The corrected allocator uses route bundles that share road edges; a commuter's assignment consumes complementary resources. Cross-route edge priority is declared by the rank in each route's receiver list then commuter ID. There is no theorem or exhaustive proof that this output is globally stable for the bundle market. Verdict: **UNPROVEN**. The two-person exhaustive test verifies feasibility, not general preference stability.

**Welfare optimality:** Neither the corrected allocator nor the historical one solves a global dose/time or social-welfare objective. Unconstrained minimum-dose paths are separate controls. Verdict: **UNSUPPORTED**.

**Scalability:** On the frozen 1,428-node central snapshot, full batch generation plus six method evaluations averaged 1.236 s (12 requests), 2.738 s (24), and 4.734 s (48) in the original concentration scenario. The four-scenario 36-batch job was about 104 s of measured batch work. Per-method runtime and full-city operational latency were not isolated. Verdict: **SUPPORTED only as bounded 1,428-node computational execution**.

## Source exhibit 11: `final_blr_results/final_routing_closure/v2t/ROUTING_FINAL_VERDICT.md`

[EVIDENCE: `final_blr_results/final_routing_closure/v2t/ROUTING_FINAL_VERDICT.md` | SHA-256 `384b88ea1b58ebca57c9c725d309e2bea40101c2257cd99e1fc39883c307966b` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### v2t final routing verdict

**Software correction: SUPPORTED within the declared model. Exposure effectiveness: UNSUPPORTED as an empirical claim.** The corrected additive allocator preserves the serving system's commuter and route preference builders, enforces route and shared directed-edge quotas, atomically releases displaced routes, and returns `UNASSIGNED` when no feasible route remains. The historical matcher and offline bundle evaluator remain callable. The critical focused suite passed 20/20, and an independent scan of saved outputs found zero invalid routes and zero declared-capacity violations.

The frozen scenario used a 1,428-node central Bengaluru graph and four static concentration scenarios. There were 252 requests per scenario (1,008 scenario-request instances). All methods assigned all requests; original and corrected serving allocators returned the **same path in all 1,008 cases**. Maximum edge utilization was 5.405%, with no saturated edge. Thus the city scenario does not demonstrate a capacity-driven improvement; the defect correction is supported by explicit stress tests on deterministic toy graphs.

For the original field, the corrected allocator's mean across nine batch-level paired dose differences versus shortest/fastest was **−0.001207%**, with batch range −0.006322% to 0; mean travel-time overhead was **+0.001324%**. Versus unconstrained minimum dose, its mean dose was +0.000413%. These differences are numerically tiny and should not be described as meaningful exposure benefit. The original and corrected allocators were identical here. The offline bundle control had different path preferences and matched the unconstrained minimum-dose route in this unstressed scenario.

Uniform +25% concentration preserved all route choices and assignments. Spatial sine perturbation preserved corrected assignments but changed 11.11% of its route paths; support-distance perturbation changed 1.59%. All corrected scenario outputs remained feasible and fully assigned. These are synthetic sensitivity probes, not calibrated uncertainty intervals.

The new algorithm does **not** establish classical preference stability or global welfare optimality for overlapping path bundles. The road concentration field comes from an historically invalid/unvalidated city model, and traffic capacities, OD demands, speed and RMV are assumptions. No measured human exposure, operational congestion, actual edge capacity, full 154,902-node network routing latency, or roadside accuracy was evaluated.
