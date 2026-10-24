"""Capacity-constrained deferred-acceptance routing versus distance A*.

Input: directed OSMnx GraphML whose edges have length (m) and predicted_pm25
(micrograms/m3), or a CSV of u,v,key,predicted_pm25 joined to that GraphML.
Run: python scripts/evaluate_routing_gs.py --graph data/graphs/bangalore_utm.graphml
     --predictions path/to/edge_predictions.csv
"""
from __future__ import annotations

import argparse
import json
from collections import deque
from pathlib import Path

import networkx as nx
import numpy as np
import osmnx as ox
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/processed/evaluations"
SPEED_M_H = 15_000.0
RMV_M3_H = 3.5


def load_graph(path: Path, predictions: Path | None) -> nx.DiGraph:
    raw = ox.load_graphml(path)
    lookup = {}
    if predictions:
        table = pd.read_csv(predictions)
        required = {"u", "v", "key", "predicted_pm25"}
        if not required <= set(table):
            raise ValueError(f"Prediction CSV requires {sorted(required)}")
        if table.duplicated(["u", "v", "key"]).any():
            raise ValueError("Duplicate edge prediction keys")
        lookup = {(int(r.u), int(r.v), int(r.key)): float(r.predicted_pm25)
                  for r in table.itertuples(index=False)}
    graph = nx.DiGraph()
    for node, data in raw.nodes(data=True):
        graph.add_node(int(node), x=float(data.get("x", 0)), y=float(data.get("y", 0)))
    missing = 0
    for u, v, key, data in raw.edges(keys=True, data=True):
        pm = lookup.get((int(u), int(v), int(key)), data.get("predicted_pm25"))
        if pm is None or not np.isfinite(float(pm)):
            missing += 1
            continue
        length = float(data["length"])
        pm = float(pm)
        if length <= 0 or pm < 0:
            raise ValueError("Edges require positive length and nonnegative predicted_pm25")
        # A DiGraph uses the shortest parallel edge. Its PM2.5 belongs to
        # that same physical edge; never mix distance from one edge with PM
        # from another.
        if not graph.has_edge(int(u), int(v)) or length < graph[u][v]["length"]:
            graph.add_edge(int(u), int(v), length=length, predicted_pm25=pm,
                           key=int(key), time_h=length / SPEED_M_H,
                           dose=pm * RMV_M3_H * length / SPEED_M_H)
    if missing:
        raise ValueError(f"{missing} directed edges lack predicted_pm25; supply complete --predictions")
    ratios = []
    for u, v, data in graph.edges(data=True):
        a, b = graph.nodes[u], graph.nodes[v]
        straight = float(np.hypot(a["x"] - b["x"], a["y"] - b["y"]))
        if straight > 0:
            ratios.append(data["length"] / straight)
    graph.graph["astar_heuristic_scale"] = min(1.0, min(ratios)) if ratios else 0.0
    return graph


def route_stats(graph: nx.DiGraph, path: list[int]) -> dict:
    edges = list(zip(path[:-1], path[1:]))
    return {"path": path, "edges": edges,
            "distance_m": sum(graph[u][v]["length"] for u, v in edges),
            "time_min": 60 * sum(graph[u][v]["time_h"] for u, v in edges),
            "dose_ug": sum(graph[u][v]["dose"] for u, v in edges)}


def candidate_routes(graph: nx.DiGraph, source: int, target: int, max_routes: int) -> list[dict]:
    # Scale Euclidean distance by the minimum length/straight-line edge ratio.
    # The triangle inequality then guarantees an admissible A* lower bound.
    def heuristic(u: int, v: int) -> float:
        a, b = graph.nodes[u], graph.nodes[v]
        return graph.graph["astar_heuristic_scale"] * float(np.hypot(a["x"] - b["x"], a["y"] - b["y"]))
    shortest = nx.astar_path(graph, source, target, heuristic=heuristic, weight="length")
    paths = [shortest]
    # Add a small Pareto-like choice set using exposure and blended weights.
    for weight in ("dose", lambda u, v, d: d["length"] + 300 * d["dose"]):
        try:
            path = nx.shortest_path(graph, source, target, weight=weight)
            if path not in paths:
                paths.append(path)
        except nx.NetworkXNoPath:
            pass
    # One extra distance alternative is useful when capacity is tight.
    if len(paths) < max_routes:
        try:
            for path in nx.shortest_simple_paths(graph, source, target, weight="length"):
                if path not in paths:
                    paths.append(path)
                if len(paths) >= max_routes:
                    break
        except nx.NetworkXNoPath:
            pass
    return sorted((route_stats(graph, p) for p in paths), key=lambda r: (r["dose_ug"], r["time_min"]))[:max_routes]


def edge_quotas(graph: nx.DiGraph, reference_quota: int = 12) -> dict:
    """Quota = clip(floor(Qref*median(C)/max(C,0.01)), 1, 4*Qref)."""
    reference_pm25 = float(np.median([d["predicted_pm25"] for _, _, d in graph.edges(data=True)]))
    return {(u, v): int(np.clip(np.floor(reference_quota * reference_pm25 /
                                          max(d["predicted_pm25"], 0.01)), 1, reference_quota * 4))
            for u, v, d in graph.edges(data=True)}


def deferred_acceptance(options: list[list[dict]], quota: dict) -> dict[int, dict]:
    """Commuters propose in dose order; each edge retains its best applicants.

    Edge preference is lower route dose, then shorter trip, then commuter ID.
    A rejected route releases all its edge reservations before reproposal.
    Paths require several resources, so this is a deferred-acceptance heuristic;
    global pairwise stability is not mathematically guaranteed for bundles.
    """
    held: dict[int, dict] = {}
    edge_users: dict[tuple[int, int], set[int]] = {}
    next_choice = [0] * len(options)
    queue = deque(range(len(options)))

    def release(commuter: int) -> None:
        old = held.pop(commuter, None)
        if old is not None:
            for edge in old["edges"]:
                edge_users[edge].remove(commuter)

    while queue:
        commuter = queue.popleft()
        if next_choice[commuter] >= len(options[commuter]):
            continue
        route = options[commuter][next_choice[commuter]]
        next_choice[commuter] += 1
        held[commuter] = route
        for edge in route["edges"]:
            edge_users.setdefault(edge, set()).add(commuter)
        rejected = set()
        for edge in route["edges"]:
            users = edge_users[edge]
            if len(users) > quota[edge]:
                ranked = sorted(users, key=lambda i: (held[i]["dose_ug"], held[i]["time_min"], i))
                rejected.update(ranked[quota[edge]:])
        for loser in sorted(rejected):
            release(loser)
            queue.append(loser)
    assert all(len(users) <= quota[edge] for edge, users in edge_users.items())
    return held


def simulate(graph: nx.DiGraph, n_trips: int, seed: int, max_routes: int) -> dict:
    rng = np.random.default_rng(seed)
    largest = max(nx.strongly_connected_components(graph), key=len)
    nodes = np.array(sorted(largest), dtype=np.int64)
    if len(nodes) < 2:
        raise ValueError("Need a strongly connected directed road network")
    options, astar = [], []
    for _ in range(n_trips):
        source, target = rng.choice(nodes, size=2, replace=False)
        routes = candidate_routes(graph, int(source), int(target), max_routes)
        # Distance A* is measured separately, even when its route is not the
        # first (lowest-dose) preference in the deferred-acceptance process.
        astar_path = nx.astar_path(graph, int(source), int(target),
                                  heuristic=lambda u, v: graph.graph["astar_heuristic_scale"] *
                                  np.hypot(graph.nodes[u]["x"] - graph.nodes[v]["x"],
                                           graph.nodes[u]["y"] - graph.nodes[v]["y"]),
                                  weight="length")
        astar.append(route_stats(graph, astar_path))
        options.append(routes)
    quotas = edge_quotas(graph)
    held = deferred_acceptance(options, quotas)
    if not held:
        raise ValueError("No routes were admitted under capacity constraints")
    rows = []
    for i, gs in held.items():
        baseline = astar[i]
        rows.append({"trip": i, "astar_dose_ug": baseline["dose_ug"],
                     "gs_dose_ug": gs["dose_ug"], "astar_time_min": baseline["time_min"],
                     "gs_time_min": gs["time_min"]})
    data = pd.DataFrame(rows).sort_values("trip")
    OUT.mkdir(parents=True, exist_ok=True)
    data.to_csv(OUT / "routing_trip_results.csv", index=False)
    a_dose, g_dose = data.astar_dose_ug.mean(), data.gs_dose_ug.mean()
    a_time, g_time = data.astar_time_min.mean(), data.gs_time_min.mean()
    result = {"requested_trips": n_trips, "admitted_trips": len(data), "unmatched_trips": n_trips - len(data),
              "astar_mean_dose_ug": float(a_dose), "gs_mean_dose_ug": float(g_dose),
              "dose_reduction_pct": float(100 * (a_dose - g_dose) / a_dose),
              "astar_mean_time_min": float(a_time), "gs_mean_time_min": float(g_time),
              "time_tradeoff_pct": float(100 * (g_time - a_time) / a_time),
              "comparison_population": "admitted trips only", "seed": seed,
              "quota_min": min(quotas.values()), "quota_median": float(np.median(list(quotas.values()))),
              "quota_max": max(quotas.values()),
              "edge_pm25_min": float(min(d["predicted_pm25"] for _, _, d in graph.edges(data=True))),
              "edge_pm25_median": float(np.median([d["predicted_pm25"] for _, _, d in graph.edges(data=True)])),
              "edge_pm25_max": float(max(d["predicted_pm25"] for _, _, d in graph.edges(data=True)))}
    (OUT / "routing_results.json").write_text(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--graph", type=Path, default=ROOT / "data/graphs/bangalore_utm.graphml")
    parser.add_argument("--predictions", type=Path, help="CSV with u,v,key,predicted_pm25")
    parser.add_argument("--trips", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max-routes", type=int, default=4)
    args = parser.parse_args()
    print(json.dumps(simulate(load_graph(args.graph, args.predictions), args.trips, args.seed, args.max_routes), indent=2))
