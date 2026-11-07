# Routing final verdict

**Classification: MIXED implementation, UNSUPPORTED effectiveness claim.** Route candidate generation and µg dose arithmetic exist. Offline A* uses a geometric lower-bound scale computed as the minimum edge-length/straight-line ratio (then capped at one); under nonzero Euclidean edges and nonnegative length weights this is an admissible distance lower bound. Dose-only shortest paths use nonnegative PM estimates and fixed positive mode-wide factors. API route time is derived from fixed mode speed. The Rust A* crate is a stub, not the production path.

Historical quantitative scenario: seed 42, 1,000 requests, 444 assigned, 556 unassigned; admitted-only modeled dose increased by 0.1211%, and time increased by 0.1463%. The route field is a legacy static prediction snapshot with weak provenance and no roadside validation. Distance summary, runtime and separate minimum-dose comparator were not retained. No v2r route benchmark was run; no citywide real exposure result is inferred.

Shared-edge handling exists in the offline path-bundle heuristic and is checked by a terminal assertion. The serving API's Gale–Shapley routine only constrains per-route counts, has an over-capacity fallback, and cannot express overlapping edge resources. The toy counterexample demonstrates this gap. Neither route implementation provides a general stability/welfare guarantee; road-class capacities are heuristic.

Allowed claim: “the repository implements dose-weighted route selection and a bounded allocation simulation; the saved assigned-only scenario showed no dose reduction.” Do not claim exposure reduction, travel-time benefits, citywide route optimality, matching stability, real capacity satisfaction, or operational safety.
