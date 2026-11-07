# Reconciliation of the 1,000-trip benchmark

The prior three-pillar summary's numbers are correct, but the implementation identity needs precision.

## What ran

The command in `ST_PIGNN_additional_eval_23oct2026.md` invokes `scripts/evaluate_routing_gs.py --trips 1000 --max-routes 3 --seed 42`. Its allocation call is `scripts/evaluate_routing_gs.py::deferred_acceptance`, **not** `matcher.gale_shapley.batch_match` and not the FastAPI `router.api.routes::route` pathway. The evaluator does perform a custom route-bundle deferred-acceptance procedure with directed-edge quota bookkeeping and asserts final per-edge feasibility. Thus it was more than a per-route-only simplified matcher for the specific simulated allocation, but it did not evaluate the serving API's complete end-to-end routing/matching system or provide formal classical Gale–Shapley stability.

## Demand, costs and comparator

- **Demand:** 1,000 pseudo-random OD pairs (no replacement within each pair) sampled from nodes in the largest strongly connected component of a 1.5-km central Bengaluru OSM graph; seed 42. They are synthetic requests, not observed commuter flows.
- **Candidate choice:** up to three routes, generated from distance A*, minimum-dose path and blended/shortest-simple-path alternatives. Deferred-acceptance proposal order is ascending modeled route dose then travel time.
- **Capacity:** each directed edge quota is pollution-inverse `floor(12 × median edge PM / max(edge PM, 0.01))`, clipped 1–48; observed 9–12. This is not traffic flow capacity.
- **Pollution field:** legacy root citywide checkpoint on its latest 12-hour feature window; road-node estimate clipped to 0–120 then averaged at edge endpoints. The v2q audit identified target-hour/input validity concerns. It is static, model-derived and not roadside-validated.
- **Dose/time:** fixed 15 km/h and 3.5 m³/hour RMV; (D=\sum_e C_e\,RMV\,L_e/v). This produces modeled inhaled mass in µg. Since speed and RMV are constant, fastest and shortest length co-rank.
- **Comparator:** distance-minimizing A* on the same OD pairs, evaluated on the 444 pairs admitted by the bundle allocator. Dose and time differences are conditional on admission, not an all-request comparison. There is no separately reported unconstrained minimum-dose baseline.

## Results and limitations

Admission was 444/1,000 (44.4%); 556 remained unmatched. On admitted trips, mean modeled dose changed `0.2714978885 → 0.2718266394 µg` (+0.1210878%); time changed `3.53588536 → 3.54105928 min` (+0.1463261%). These values recompute from the saved 444-row trip CSV and agree with `routing_results.json`.

The result does **not** show an API matcher shared-edge defect in operation: the offline evaluator independently tracks shared edges. Conversely, it does **not** validate the API route-quota matcher, since that implementation was not called. Its successful final assertion is evidence only that the offline allocator returned a quota-feasible set for this run; edge occupancy/path records were not saved for independent re-audit. No matching stability, route diversity, runtime, scaling, per-trip distance overhead, or real exposure result is available.

An earlier audit protocol said “up to four candidates,” based on the script default. The exact recorded command overrides this with `--max-routes 3`; this reconciliation uses three. No files in the old benchmark were changed or rerun.
