# Routing and exposure implementation audit

## What exists

The repository contains an API/router stack (`router/api/routes.py`), edge dose cost (`router/edge_cost.py`), mode respiratory-volume constants (`shared/physics_config.py`), audit/stake hashing, Rust A* code, and route-pool/capacity code. `scripts/evaluate_routing_gs.py` implements an offline comparison between distance A* and a deferred-acceptance route allocation heuristic. It constructs candidate shortest-dose/blended routes, assigns edge quotas inversely to static PM2.5, and compares admitted trip dose/time.

## Saved quantitative diagnostic

The saved run requested 1,000 trips with seed 42; 444 were admitted and 556 were unmatched. Among admitted trips only, mean dose changed from 0.2714979 µg to 0.2718266 µg (reported dose reduction −0.1211%, i.e. slight increase), while mean travel time changed from 3.53589 to 3.54106 minutes (+0.1463%). Quotas were 9–12 (median 12). Edge PM2.5 values spanned only 1.2825–1.6286 µg/m³ in this snapshot. The raw run summary is `data/processed/evaluations/routing_results.json`; per-trip rows are `data/processed/evaluations/routing_trip_results.csv`.

## Interpretation

This is a bounded software/simulation demonstration, not independent route-effectiveness evidence. Metrics exclude unmatched trips, giving a selected admitted-only population; 55.6% of requested trips received no route under the stated quotas. The static concentration field is not road-validated and its provenance/calibration does not support an ambient exposure claim. Capacity constraints are heuristic allocations for sampled trips, not evidence of real-world capacity satisfaction or guaranteed matching stability for multi-edge route bundles. No human exposure dose, health outcome, route safety, welfare, user behavior or operational test was evaluated. Therefore no validated exposure reduction, travel-time trade-off, citywide route optimality, welfare guarantee, capacity guarantee or vulnerable-commuter safety claim is supportable.
