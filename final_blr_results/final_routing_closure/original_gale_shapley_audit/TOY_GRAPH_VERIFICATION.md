# Deterministic toy graph verification

Command:

```sh
PYTHONPATH=. python final_blr_results/final_routing_closure/original_gale_shapley_audit/toy_graph_verification.py
```

This audit-only script imports the repository implementations without changing them. It writes `TOY_GRAPH_RESULTS.json`. The expected defect cases are reported as `pass: false` because the observed output violates the requested invariant; the script itself exits successfully only after reproducing each expected finding. An independent exhaustive enumerator checks all (3^2=9) assignments for two commuters and two routes, filters capacity-feasible outcomes, and tests blocking pairs under standard responsive route preferences.

| Scenario | Result | Finding |
|---|---|---|
| Two commuters compete for route A (capacity 1), route B alternative; rejection/displacement | PASS | c2 displaces c1 at A; c1 proposes to B. |
| Preference stability, 2 commuters × 2 routes | PASS | Returned `{c1:B,c2:A}` matches the sole stable assignment found by exhaustive enumeration. |
| Multiple independent corridors | PASS | Independent quota-one routes each receive one commuter. |
| Two candidate routes share a quota-one edge in API matcher | EXPECTED FAILURE | API assigns one commuter to each route; aggregate shared-edge occupancy is 2 because paths are not an input. |
| Demand exceeds supply in API matcher | EXPECTED FAILURE | Two commuters assigned to a single route with quota 1 because fallback ignores quota. |
| Shared bottleneck in offline bundle evaluator | PASS | One proposal is rejected at shared arc; the displaced commuter proposes to its alternate path; all edge occupancies satisfy supplied quotas. |
| Demand exceeds a single offline edge's capacity | PASS AS CAPACITY-SAFE BEHAVIOR | One of two commuters is assigned to quota-one edge; one remains unallocated. |

This establishes a narrow standard Gale–Shapley result for one small ordinary matching instance and an implementation counterexample for API feasibility. It does not prove general stability of the bundle evaluator, real traffic capacity, commuter welfare, exposure effectiveness, or scalability.
