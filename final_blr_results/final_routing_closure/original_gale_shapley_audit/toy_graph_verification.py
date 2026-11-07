"""Deterministic audit-only probes; imports but does not modify production matchers."""
from itertools import product
import json
from pathlib import Path

from matcher.gale_shapley import batch_match
from scripts.evaluate_routing_gs import deferred_acceptance


def exhaustive_stable_assignments(commuters, routes, prefs_c, prefs_r, caps):
    """Enumerate feasible assignments and check standard one-to-many blocking pairs."""
    result = []
    for choice in product([None, *routes], repeat=len(commuters)):
        assignment = dict(zip(commuters, choice))
        members = {r: [c for c in commuters if assignment[c] == r] for r in routes}
        if any(len(members[r]) > caps[r] for r in routes):
            continue
        blocked = False
        for c in commuters:
            for r in prefs_c[c]:
                if assignment[c] == r:
                    break
                if len(members[r]) < caps[r]:
                    blocked = True
                    break
                rank = {x: i for i, x in enumerate(prefs_r[r])}
                worst = max(members[r], key=lambda x: rank[x])
                if rank[c] < rank[worst]:
                    blocked = True
                    break
            if blocked:
                break
        if not blocked:
            result.append(assignment)
    return result


def main():
    rows = []
    # Classic two-sided DA case, with displacement and a stable final allocation.
    cs, rs = ["c1", "c2"], ["A", "B"]
    pc = {"c1": ["A", "B"], "c2": ["A", "B"]}
    pr = {"A": ["c2", "c1"], "B": ["c1", "c2"]}
    cap = {"A": 1, "B": 1}
    actual = batch_match(cs, rs, commuter_preferences=pc, segment_preferences=pr,
                         segment_capacities=cap, max_iterations=4)
    stable = exhaustive_stable_assignments(cs, rs, pc, pr, cap)
    assert actual == {"c1": "B", "c2": "A"}
    assert actual in stable
    rows.append({"case": "rejection_displacement_and_stability", "pass": True,
                 "assignment": actual, "exhaustive_stable_assignments": stable})

    # Independent corridors: both route capacities are respected by ordinary DA.
    independent = batch_match(["u1", "u2"], ["north", "south"],
        commuter_preferences={"u1": ["north", "south"], "u2": ["south", "north"]},
        segment_preferences={"north": ["u1", "u2"], "south": ["u2", "u1"]},
        segment_capacities={"north": 1, "south": 1}, max_iterations=4)
    assert independent == {"u1": "north", "u2": "south"}
    rows.append({"case": "independent_corridors", "pass": True, "assignment": independent})

    # API accepts two different route labels without seeing their common edge.
    api_shared = batch_match(["x", "y"], ["route_left", "route_right"],
        commuter_preferences={"x": ["route_left", "route_right"],
                              "y": ["route_right", "route_left"]},
        segment_preferences={"route_left": ["x", "y"], "route_right": ["y", "x"]},
        segment_capacities={"route_left": 1, "route_right": 1}, max_iterations=4)
    api_common_edge_occupancy = sum(api_shared[c] in {"route_left", "route_right"}
                                    for c in api_shared)
    assert api_common_edge_occupancy == 2  # Both paths contain bottleneck e=(1,2), cap 1.
    rows.append({"case": "API_overlapping_routes_shared_bottleneck", "pass": False,
                 "assignment": api_shared, "common_edge_capacity": 1,
                 "common_edge_occupancy": api_common_edge_occupancy,
                 "reason": "batch_match receives route IDs/capacities but no route-edge sets"})

    # API fallback assigns a second user even when a single corridor has quota one.
    overflow = batch_match(["a", "b"], ["only"],
        commuter_preferences={"a": ["only"], "b": ["only"]},
        segment_preferences={"only": ["a", "b"]}, segment_capacities={"only": 1},
        route_distances={"a": {"only": 1}, "b": {"only": 2}}, max_iterations=2)
    assert len(overflow) == 2
    rows.append({"case": "API_demand_exceeds_route_supply", "pass": False,
                 "assignment": overflow, "capacity": 1, "assigned": len(overflow),
                 "reason": "fallback appends unmatched commuters without quota recheck"})

    # Offline bundle allocator: shared edge is a resource. Loser moves to its next route.
    options = [
        [{"edges": [(1, 2), (2, 4)], "dose_ug": 1.0, "time_min": 2.0},
         {"edges": [(1, 3), (3, 4)], "dose_ug": 4.0, "time_min": 3.0}],
        [{"edges": [(1, 2), (2, 5)], "dose_ug": 2.0, "time_min": 2.2},
         {"edges": [(1, 6), (6, 5)], "dose_ug": 3.0, "time_min": 3.0}],
    ]
    bundle = deferred_acceptance(options, {(1, 2): 1, (2, 4): 1, (1, 3): 1,
                                           (3, 4): 1, (2, 5): 1, (1, 6): 1,
                                           (6, 5): 1})
    occupancy = {}
    for cid, route in bundle.items():
        for edge in route["edges"]:
            occupancy[edge] = occupancy.get(edge, 0) + 1
    assert len(bundle) == 2 and occupancy[(1, 2)] == 1
    assert all(n <= {(1, 2): 1, (2, 4): 1, (1, 3): 1, (3, 4): 1,
                     (2, 5): 1, (1, 6): 1, (6, 5): 1}[e] for e, n in occupancy.items())
    rows.append({"case": "offline_bundle_shared_edge_and_reproposal", "pass": True,
                 "selected_routes": {str(k): v["edges"] for k, v in bundle.items()},
                 "edge_occupancy": {str(k): v for k, v in occupancy.items()}})

    # Offline distinct corridors independently admit capacity-one routes.
    independent_bundle = deferred_acceptance(
        [[{"edges": [(1, 2)], "dose_ug": 1., "time_min": 1.}],
         [{"edges": [(3, 4)], "dose_ug": 1., "time_min": 1.}]],
        {(1, 2): 1, (3, 4): 1})
    assert len(independent_bundle) == 2
    rows.append({"case": "offline_independent_corridors", "pass": True,
                 "assigned_count": len(independent_bundle)})

    scarce = deferred_acceptance(
        [[{"edges": [(8, 9)], "dose_ug": 1., "time_min": 1.}],
         [{"edges": [(8, 9)], "dose_ug": 2., "time_min": 1.}]],
        {(8, 9): 1})
    assert len(scarce) == 1
    rows.append({"case": "offline_demand_exceeds_edge_supply", "pass": True,
                 "assigned_count": len(scarce), "unallocated_count": 2 - len(scarce),
                 "edge_capacity": 1})

    out = Path(__file__).with_name("TOY_GRAPH_RESULTS.json")
    out.write_text(json.dumps({"scope": "deterministic toy audit, not performance evidence",
                               "cases": rows,
                               "independent_reference": "exhaustive enumeration for 2 commuters x 2 routes under standard one-to-many responsive preferences",
                               "note": "Expected failure rows expose existing API limitations; production code unchanged."},
                              indent=2) + "\n")
    print(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()
