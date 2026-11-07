"""Deterministic toy-graph checks for saved routing algorithms (not city benchmark)."""
from __future__ import annotations

import json
from pathlib import Path
import sys

import networkx as nx
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from matcher.gale_shapley import batch_match
from scripts.evaluate_routing_gs import candidate_routes, deferred_acceptance, route_stats


def main():
    g = nx.DiGraph()
    for node, xy in {1: (0.0, 0.0), 2: (1.0, 0.0), 3: (0.0, 2.0), 4: (2.0, 0.0)}.items():
        g.add_node(node, x=xy[0], y=xy[1])
    # Short/high-concentration path; longer/low-concentration path.
    for u, v, length, pm in [(1, 2, 1.0, 20.0), (2, 4, 1.0, 20.0),
                             (1, 3, 2.0, 1.0), (3, 4, 2.0, 1.0)]:
        g.add_edge(u, v, length=length, predicted_pm25=pm,
                   time_h=length / 15000.0,
                   dose=pm * 3.5 * length / 15000.0)
    ratios = [d["length"] / np.hypot(g.nodes[u]["x"]-g.nodes[v]["x"], g.nodes[u]["y"]-g.nodes[v]["y"])
              for u, v, d in g.edges(data=True)]
    g.graph["astar_heuristic_scale"] = min(1.0, min(ratios))
    routes = candidate_routes(g, 1, 4, 3)
    assert routes and all(r["path"][0] == 1 and r["path"][-1] == 4 for r in routes)
    assert all(all(g.has_edge(u, v) for u, v in r["edges"]) for r in routes)
    shortest = nx.shortest_path(g, 1, 4, weight="length")
    assert route_stats(g, shortest)["distance_m"] == 2.0
    fastest = nx.shortest_path(g, 1, 4, weight="time_h")
    assert fastest == shortest  # fixed 15 km/h in the offline scenario
    min_dose = nx.shortest_path(g, 1, 4, weight="dose")
    assert min_dose == [1, 3, 4]
    assert all(g[u][v]["dose"] >= 0 for u, v in g.edges)
    dose_expected = 2 * (1.0 * 3.5 * 2.0 / 15000.0)
    assert abs(route_stats(g, min_dose)["dose_ug"] - dose_expected) < 1e-15

    disconnected = nx.DiGraph([(1, 2)])
    disconnected.add_node(3)
    try:
        nx.shortest_path(disconnected, 1, 3)
        raise AssertionError("unreachable destination was not rejected")
    except nx.NetworkXNoPath:
        pass

    # Edge-bundle deferred acceptance honours overlapping per-edge quotas.
    a = {"edges": [(10, 11), (11, 12)], "dose_ug": 1.0, "time_min": 2.0}
    b = {"edges": [(10, 13), (13, 12)], "dose_ug": 2.0, "time_min": 2.0}
    choices = [[a, b], [a, b]]
    quotas = {(10, 11): 1, (11, 12): 2, (10, 13): 2, (13, 12): 2}
    held = deferred_acceptance(choices, quotas)
    shared_users = sum((10, 11) in item["edges"] for item in held.values())
    assert shared_users <= quotas[(10, 11)]

    # API matcher only sees route-level capacities, not edge membership.
    assigned = batch_match(["c1", "c2"], ["r1", "r2"],
        commuter_preferences={"c1": ["r1", "r2"], "c2": ["r2", "r1"]},
        segment_preferences={"r1": ["c1", "c2"], "r2": ["c2", "c1"]},
        segment_capacities={"r1": 1, "r2": 1})
    shared_api_usage = sum(assigned[c] in {"r1", "r2"} for c in assigned)
    assert shared_api_usage == 2

    result = {
        "scope": "deterministic synthetic correctness checks; not a Bengaluru performance evaluation",
        "checks_passed": ["route continuity and endpoints", "distance A* lower-bound result on toy graph",
                          "fastest equals shortest under constant-speed assumption", "minimum-dose route",
                          "nonnegative edge costs", "dose units/arithmetic", "disconnected path raises NetworkXNoPath",
                          "offline bundle allocator respects shared-edge quota", "API batch_match lacks edge-resource data"],
        "distance_shortest_path_nodes": shortest,
        "fastest_path_nodes_under_constant_15kmh": fastest,
        "minimum_modeled_dose_path_nodes": min_dose,
        "minimum_modeled_dose_ug": route_stats(g, min_dose)["dose_ug"],
        "offline_shared_edge_users": shared_users,
        "offline_shared_edge_quota": quotas[(10, 11)],
        "api_assigned_commuters_on_two_routes_sharing_one_edge": shared_api_usage,
        "api_route_capacities": {"r1": 1, "r2": 1},
        "api_shared_edge_capacity": "unrepresented; violation cannot be checked or prevented by batch_match",
    }
    out = Path(__file__).resolve().parent / "ROUTING_TOY_DIAGNOSTICS.json"
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
