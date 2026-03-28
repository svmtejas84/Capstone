from matcher.route_pool import build_route_metrics, candidate_corridors


def test_candidate_corridors_default_set() -> None:
	routes = candidate_corridors()
	assert len(routes) >= 3


def test_build_route_metrics_contains_distance_and_cedge() -> None:
	routes = ["a", "b", "c"]
	metrics = build_route_metrics(routes, edge_values=[10.0, 20.0])
	assert set(metrics.keys()) == set(routes)
	assert metrics["a"]["cedge_mean"] == 10.0
	assert metrics["b"]["cedge_mean"] == 20.0
	assert metrics["c"]["cedge_mean"] == 10.0
	assert metrics["a"]["distance_m"] < metrics["b"]["distance_m"]
