# Historical routing evidence inventory

## Recovered quantified scenario

Source command recorded in `ST_PIGNN_additional_eval_23oct2026.md`:

```sh
python scripts/prepare_routing_snapshot.py
python scripts/evaluate_routing_gs.py --graph data/processed/evaluations/routing_snapshot.graphml --trips 1000 --max-routes 3 --seed 42
python scripts/write_additional_eval_report.py
```

Input snapshot: `data/processed/evaluations/routing_snapshot.graphml`; generated from a 1.5 km central OSM area, its largest strongly connected component, the legacy root `citywide_stpignn_best.pt` and latest available 12-hour feature window. The script predicts a value at each road node and writes edge (C) as the mean of endpoint predictions, clipped to 0–120 µg/m³. v2q documents that the historical input can include target-hour information; this is not a forecast-valid, calibrated roadside field. Graph has no independent ground-truth road-node labels.

Demand: 1,000 synthetic random OD pairs sampled without replacement per pair from the selected strongly connected component, NumPy seed 42. No observed commuter OD demand or population representativeness. The evaluator constructs up to 3 candidate simple paths per pair. A fixed 15 km/h speed and RMV 3.5 m³/hour are used. Both reference-distance A* and allocated paths are scored on the **same 444 admitted trips only**.

| Measure | Saved result | Interpretation |
|---|---:|---|
| Requests / admitted / unassigned | 1000 / 444 / 556 | Admission success 44.4%; 55.6% unallocated. |
| Quotas | min 9, median 12, max 12 | Pollution-inverse edge quotas, not measured traffic capacity. |
| Edge concentration | min 1.2825, median 1.3073, max 1.6286 µg/m³ | Legacy static model-derived range. |
| Mean modeled dose, distance A* | 0.2714978885 µg | Admitted subset. |
| Mean modeled dose, allocated | 0.2718266394 µg | Admitted subset; +0.1210878%, no reduction. |
| Mean travel time, distance A* | 3.53588536 min | Fixed speed. |
| Mean travel time, allocated | 3.54105928 min | +0.1463261%. |
| Matching stability | NOT MEASURED | No blocking-pair/path-bundle audit. |
| Runtime, path diversity, distance overhead, edge occupancy report | NOT SAVED / UNVERIFIABLE | Not recoverable from retained JSON and 444-row CSV. |

Raw files: `data/processed/evaluations/routing_results.json` (17 summary fields), `routing_trip_results.csv` (444 rows; dose/time only; no paths/distances). Snapshot SHA-256 is `38e2a46792e9209af57e9c71fb17f6768e0117016e978ebc280ba96241647810`; result JSON SHA-256 `5662d776a1a2a68adc7dcca1425efec3a949b7df2c8c8f4342bdb55379a869df`; trip CSV SHA-256 `54ba1dedef16af9b28aba32863a975dff05176a5d71355fee618da12134044fe`. Snapshot has 1,428 nodes, 3,459 directed arcs, CRS EPSG:32643 and OSMnx 2.1.0 metadata. `ST_PIGNN_additional_eval_23oct2026.md` is the run report. `scripts/write_additional_eval_report.py` is its report generator. The saved result exactly matches means recomputed from per-trip CSV to floating-point precision.

## Other artifacts

The primary production notebook has no routing implementation or saved routing output. The matching demo and route-comparison draft notebooks are empty. `matcher/tests/` provides small API unit tests, including the fallback assignment behavior, but no shared-edge or stable-matching exhaustive test. `data/processed/evaluations/` is gitignored; do not mistake ignored status for missing local artifacts. No other archived route assignment table, matching-stability score, OD dataset, route runtime/scalability benchmark, or independent commuter allocation study was located in the indexed local ZIP members or current repository search.

The original manuscript's more ambitious routing/capacity claims are not supported by these saved artifacts. See the reviewer/source evidence package for exact review-text availability; this audit adds code facts, not claims about reviewer wording.
