from __future__ import annotations


from collections import deque


def _default_commuter_preferences(commuter_ids: list[str], route_ids: list[str]) -> dict[str, list[str]]:
	return {cid: list(route_ids) for cid in commuter_ids}


def _default_segment_preferences(commuter_ids: list[str], route_ids: list[str]) -> dict[str, list[str]]:
	return {rid: list(commuter_ids) for rid in route_ids}


def _segment_rank_maps(segment_preferences: dict[str, list[str]], commuter_ids: list[str]) -> dict[str, dict[str, int]]:
	default_rank = len(commuter_ids) + 1
	rank_maps: dict[str, dict[str, int]] = {}
	for route_id, ordered_commuters in segment_preferences.items():
		rank_maps[route_id] = {cid: idx for idx, cid in enumerate(ordered_commuters)}
		rank_maps[route_id]["__default__"] = default_rank
	return rank_maps


def _best_fallback_route(
	commuter_id: str,
	route_ids: list[str],
	assignments_per_route: dict[str, list[str]],
	route_distances: dict[str, dict[str, float]] | None,
) -> str:
	if route_distances and commuter_id in route_distances:
		dist = route_distances[commuter_id]
		candidates: list[tuple[float, int, str]] = []
		for idx, rid in enumerate(route_ids):
			if rid in dist:
				candidates.append((dist[rid], idx, rid))
		if candidates:
			return min(candidates)[2]

	# Distance-unaware fallback balances load deterministically.
	loads = [
		(len(assignments_per_route.get(rid, [])), idx, rid)
		for idx, rid in enumerate(route_ids)
	]
	return min(loads)[2]


def batch_match(
	commuter_ids: list[str],
	route_ids: list[str],
	*,
	commuter_preferences: dict[str, list[str]] | None = None,
	segment_preferences: dict[str, list[str]] | None = None,
	segment_capacities: dict[str, int] | None = None,
	route_distances: dict[str, dict[str, float]] | None = None,
	max_iterations: int | None = None,
) -> dict[str, str]:
	"""Run capacity-aware batch Gale-Shapley matching.

	Commuters (side A) propose to routes (side B) in preference order.
	Routes hold up to `segment_capacities[route]` tentative matches based on
	`segment_preferences`. If the loop reaches `max_iterations`, remaining
	unmatched commuters are assigned to nearest-distance route when available.
	"""
	if not commuter_ids:
		return {}
	if not route_ids:
		return {cid: "" for cid in commuter_ids}

	commuter_prefs = commuter_preferences or _default_commuter_preferences(commuter_ids, route_ids)
	segment_prefs = segment_preferences or _default_segment_preferences(commuter_ids, route_ids)
	capacities = {rid: max(1, int((segment_capacities or {}).get(rid, 1))) for rid in route_ids}

	rank_maps = _segment_rank_maps(segment_prefs, commuter_ids)
	assignments_per_route: dict[str, list[str]] = {rid: [] for rid in route_ids}
	assigned_route: dict[str, str] = {cid: "" for cid in commuter_ids}
	next_pref_index: dict[str, int] = {cid: 0 for cid in commuter_ids}
	unmatched: deque[str] = deque(commuter_ids)

	iteration_cap = max_iterations
	if iteration_cap is None:
		iteration_cap = max(1, len(commuter_ids) * max(1, len(route_ids)))
	iterations = 0

	while unmatched and iterations < iteration_cap:
		iterations += 1
		cid = unmatched.popleft()
		prefs = commuter_prefs.get(cid, route_ids)
		accepted = False

		while next_pref_index[cid] < len(prefs):
			rid = prefs[next_pref_index[cid]]
			next_pref_index[cid] += 1

			if rid not in assignments_per_route:
				continue

			current = assignments_per_route[rid]
			capacity = capacities[rid]
			rank_map = rank_maps.get(rid, {"__default__": len(commuter_ids) + 1})
			default_rank = rank_map["__default__"]
			new_rank = rank_map.get(cid, default_rank)

			if len(current) < capacity:
				current.append(cid)
				assigned_route[cid] = rid
				accepted = True
				break

			worst_current = max(current, key=lambda c: rank_map.get(c, default_rank))
			worst_rank = rank_map.get(worst_current, default_rank)

			if new_rank < worst_rank:
				current.remove(worst_current)
				current.append(cid)
				assigned_route[cid] = rid
				assigned_route[worst_current] = ""
				accepted = True
				if next_pref_index[worst_current] < len(commuter_prefs.get(worst_current, route_ids)):
					unmatched.append(worst_current)
				break

		if not accepted and next_pref_index[cid] < len(prefs):
			unmatched.append(cid)

	remaining = [cid for cid, rid in assigned_route.items() if not rid]
	for cid in remaining:
		fallback_rid = _best_fallback_route(cid, route_ids, assignments_per_route, route_distances)
		assignments_per_route.setdefault(fallback_rid, []).append(cid)
		assigned_route[cid] = fallback_rid

	return assigned_route

