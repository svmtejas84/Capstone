# Original routing verdict

## Decision: D — Contains an identifiable correctness defect

The serving `matcher.gale_shapley.batch_match` is a recognizable commuter-proposing, route-capacitated deferred-acceptance procedure in its main proposal/displacement loop. Under fixed route quotas and complete strict preferences, with responsive route choices and **without** its post-loop fallback, ordinary many-to-one deferred acceptance has the standard termination, feasibility and stability guarantees. A bounded toy case agrees with an independent exhaustive stable-assignment enumeration.

The shipped function does not preserve those conditions for all inputs. Its fallback assigns any remaining commuter to nearest/least-loaded route without checking capacity or acceptability. A two-commuter, one-route/quota-one example returns two assigned commuters. It also lacks shared-edge resource data; two different routes sharing a bottleneck can independently fill their quotas beyond that edge's limit. These are concrete allocation-feasibility defects in the serving matcher. No production correction is made in this audit.

`matcher/README.md` describes fallback as complete assignment “under capacity constraints” and says equilibrium is validated; the implementation and tests contradict the capacity assertion when supply is exceeded, and no runtime stability check is called by `batch_match`. Treat those README statements as documentation claims, not verified properties.

Separately, the offline evaluator does account for shared directed-edge quotas and asserts ex-post feasibility for its allocation. This narrow mechanism is real and was exercised by the prior 1,000-trip simulation. However, it is not the API matcher and does not establish formal stability for multi-edge route bundles, validated traffic capacities, dose reduction, or operational performance.

## Classification by component

- **API route-based deferred acceptance:** D (identifiable fallback capacity/acceptability defect; shared-edge capacities unmodeled).
- **Offline route-bundle allocation:** B (edge-feasible under its supplied directed-edge quotas and finite listed options, subject to heuristic quota assumptions; formal stability/welfare unproved).
- **Historical quantitative exposure/routing claim:** C (an implementation and one saved simulation exist, but quantitative evidence is exploratory, admission-conditioned and based on invalid/unvalidated road concentration inputs; effectiveness not supported).
- **Notebook-contained routing:** E as a notebook claim (no routing/matching implementation in the named production notebook); repository-level routing code remains recoverable from modules and scripts.

## Minimum future work (approval required before implementation/large runs)

1. Decide whether the serving contract should allow unassigned demand. Remove or redesign capacity-bypassing fallback only after supervisor approval; report unmatched requests rather than silently exceeding quota.
2. For physical shared-edge enforcement, pass route edge bundles and shared directed-edge capacities to allocation or solve a specified constrained assignment problem; use measured/justified capacity data. Keep stability and feasibility as separate properties.
3. Add independent tests for all path/capacity edge cases, preference acceptability and the no-blocking-pair condition for the exact restricted API model.
4. Before an effectiveness benchmark, use validated forecast-time concentrations and OD demand, freeze capacity definitions and comparator population, retain paths/edge occupancies, record runtime, and report unallocated demand. This audit did not run that benchmark.

Primary report set: this directory. Prior routing evidence remains in `final_blr_results/final_three_pillars/routing/` and the IEEE evidence package, without alteration.
