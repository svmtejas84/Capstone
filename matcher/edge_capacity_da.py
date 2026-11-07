"""Preference-based deferred acceptance with atomic directed-edge quotas.

This additive allocator does not alter matcher.gale_shapley.batch_match.
Route IDs are global within a batch; a route consumes one route slot and one
unit on every directed edge it traverses. No forced fallback is performed.
"""
from __future__ import annotations

from collections import deque


def allocate_shared_edges(
    commuter_ids: list[str],
    commuter_preferences: dict[str, list[str]],
    route_edges: dict[str, list[tuple[int, int]]],
    route_capacities: dict[str, int],
    edge_capacities: dict[tuple[int, int], int],
    route_preferences: dict[str, list[str]],
) -> dict[str, str | None]:
    """Return one route or None per commuter, with all supplied quotas respected.

    Incumbents and proposers compete on a shared edge using their rank in their
    own route's receiver list, then commuter ID. This cross-route ordering is
    deterministic but has no classical stable-matching guarantee.
    """
    if len(set(commuter_ids)) != len(commuter_ids):
        raise ValueError("duplicate commuter IDs")
    for rid, edges in route_edges.items():
        if not edges or len(set(edges)) != len(edges):
            raise ValueError(f"route {rid} has empty or repeated edges")
        if any(edges[i][1] != edges[i + 1][0] for i in range(len(edges) - 1)):
            raise ValueError(f"route {rid} is not directed-continuous")
        if rid not in route_capacities or any(e not in edge_capacities for e in edges):
            raise ValueError(f"route {rid} lacks capacity metadata")
    if any(v < 0 for v in route_capacities.values()) or any(v < 0 for v in edge_capacities.values()):
        raise ValueError("negative capacity")

    rank = {r: {c: i for i, c in enumerate(route_preferences.get(r, sorted(commuter_ids)))}
            for r in route_edges}
    held: dict[str, str] = {}
    next_index = {c: 0 for c in commuter_ids}
    queue = deque(commuter_ids)

    def priority(c: str) -> tuple[int, str]:
        r = held[c]
        return (rank[r].get(c, len(commuter_ids) + 1), c)

    def occupancy():
        by_route = {r: [] for r in route_edges}
        by_edge = {e: [] for e in edge_capacities}
        for c, r in held.items():
            by_route[r].append(c)
            for e in route_edges[r]:
                by_edge[e].append(c)
        return by_route, by_edge

    while queue:
        c = queue.popleft()
        prefs = commuter_preferences.get(c, [])
        if next_index[c] >= len(prefs):
            continue
        r = prefs[next_index[c]]
        next_index[c] += 1
        if r not in route_edges:
            if next_index[c] < len(prefs):
                queue.append(c)
            continue
        held[c] = r
        by_route, by_edge = occupancy()
        rejected = set()
        for rid, users in by_route.items():
            cap = route_capacities[rid]
            if len(users) > cap:
                rejected.update(sorted(users, key=priority)[cap:])
        for edge, users in by_edge.items():
            cap = edge_capacities[edge]
            if len(users) > cap:
                rejected.update(sorted(users, key=priority)[cap:])
        for loser in sorted(rejected):
            del held[loser]  # atomically releases every edge of the path
            if next_index[loser] < len(commuter_preferences.get(loser, [])):
                queue.append(loser)
        by_route, by_edge = occupancy()
        assert all(len(users) <= route_capacities[rid] for rid, users in by_route.items())
        assert all(len(users) <= edge_capacities[e] for e, users in by_edge.items())
    return {c: held.get(c) for c in commuter_ids}
