from router.inhalation_rates import get_ir


def compute_edge_weight(cedge: float, travel_time_s: float, mode: str) -> float:
	ir = get_ir(mode)
	return cedge * (travel_time_s / 3600.0) * ir


def compute_path_cost(edge_weights: list[float], mode: str, edge_time_s: float = 60.0) -> float:
	return sum(compute_edge_weight(w, edge_time_s, mode) for w in edge_weights)

