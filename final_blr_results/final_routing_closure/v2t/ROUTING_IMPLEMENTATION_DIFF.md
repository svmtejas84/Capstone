# Implementation difference from the recovered original

| Component | Historical | v2t change | Reason |
|---|---|---|---|
| Serving matcher | `matcher.gale_shapley.batch_match`; route quotas only; post-loop forced fallback | Original callable remains unchanged. New `matcher.edge_capacity_da.allocate_shared_edges` tracks route and shared directed-edge quotas; no forced fallback. | The audit demonstrated route quota overflow and shared-edge double booking. |
| Serving selector | Always invoked original matcher | `TOXICITY_ROUTE_ALLOCATOR=corrected` default; set `original` to invoke historical matcher. | Preserve a reproducible historical control and expose corrected behavior. |
| No feasible route | Historical matcher could force an over-capacity route; API could draw a straight origin–destination line on disconnected graphs | Explicit `UNASSIGNED`, empty route and zero modeled route cost. | Prevent a fabricated traversable route. |
| Python 3.9 execution | Two `zip(..., strict=False)` uses in `router/api/routes.py` raised TypeError | Plain `zip(...)` has the same non-strict behavior on Python 3.9. | Run the existing serving path in this environment. |
| Offline evaluator | Shared-edge bundle allocator in `scripts/evaluate_routing_gs.py` | Unchanged, used as a separate benchmark control. | Preserve historical method and results. |

The original commuter preference formula, route receiver ranking, dose cost, route generation and road-class capacity estimator remain in their existing modules. The correction adds only shared-edge accounting and an explicit failure status. Tests and benchmark entry points are under this v2t directory; no neural code or historical experiment was modified.
