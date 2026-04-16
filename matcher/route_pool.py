from __future__ import annotations


def candidate_corridors() -> list[str]:
	return ["corridor_a", "corridor_b", "corridor_c"]


def build_route_metrics(route_ids: list[str], edge_values: list[float] | None = None) -> dict[str, dict[str, float]]:
	"""Create simple per-route metrics used by matcher preference builders."""
	if not route_ids:
		return {}

	values = edge_values[:] if edge_values else [22.0, 17.0, 12.0]
	if not values:
		values = [22.0]

	metrics: dict[str, dict[str, float]] = {}
	for idx, rid in enumerate(route_ids):
		cedge = float(values[idx % len(values)])
		# Slightly increasing length mimics realistic alternate-corridor detours.
		distance_m = float(1800 + idx * 700)
		metrics[rid] = {
			"cedge_mean": cedge,
			"distance_m": distance_m,
		}

	return metrics

