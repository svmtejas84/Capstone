# Routing benchmark protocol and evidence status

## Reused quantitative run

The only available city scenario benchmark is the saved run from `scripts/evaluate_routing_gs.py` with seed 42, 1,000 requests sampled from the largest strongly connected component, up to four candidates, and the historical `routing_snapshot.graphml` (1.5-km central area) with static predicted edge concentrations. Raw files: `data/processed/evaluations/routing_results.json` and `routing_trip_results.csv`. This run predates v2r and is not re-run or overwritten. It compares distance A* to a route-bundle deferred-acceptance heuristic on the common admitted-trip set.

The evaluator uses a constant speed of 15 km/h and RMV 3.5 m³/h, so in that scenario fastest route and shortest distance are exactly co-ranked. It does not export distance summaries in `routing_trip_results.csv`; distance comparison is **not numerically recoverable from the saved per-trip file**. Candidate routes include shortest-distance, minimum-dose and blended routes, but the result reports only the allocated choice versus shortest-distance A*. It does not report a separate unconstrained minimum-dose metric. The concentration field came from the legacy root road checkpoint and endpoint interpolation. It is not a corrected v2r forecast and is not roadside-validated.

## Fixed future benchmark protocol (not run)

For a valid follow-up using v2r only as a computational scenario: use the three already frozen targets in `final_research_v2r/citywide/road_predictions/`; derive OSM node values by joining exact `osmid` keys and edge concentration as the arithmetic mean of endpoint experimental estimates; freeze 20 OD pairs from a fixed pseudorandom seed before reading scenario concentration; use identical OD requests for all methods. Compare distance-min, fixed-mode fastest, concentration×time dose-min, and shared-edge capacity allocation. Report each timestamp separately and pooled with explicit method. Capacity must use a prespecified OSM-class/lane model only as a hypothetical constraint, with no operational interpretation. The decoder held-out site result is unfavorable, so any resulting route is merely a sensitivity/computational example.

This follow-up was **NOT RUN** in this closure. The prior saved scenario has a known legacy input-validity problem, and the task did not authorize replacement of that field with v2r road estimates and invented/synthetic capacity assumptions. No route outputs should be fabricated from the incomplete scenario. Existing record includes no per-route success/length distribution, capacity stress audit table, or runtime; these are UNVERIFIABLE from archived result rows.

## Selection and validity limits

The earlier run selects admission-conditioned metrics: 444 assigned, 556 unallocated. Thus route success is 44.4%; all dose/time averages are admitted-only and can be selection-biased. Concentration range was only 1.2825–1.6286 µg/m³. No calibrated concentration uncertainty or independent exposure measurement exists. No perturbation-based uncertainty analysis is reported. The historical edge quota `floor(12 × median(C)/max(C,0.01))`, clipped 1–48, decreases capacity as pollution rises; it is an allocation heuristic, not a traffic capacity law.
