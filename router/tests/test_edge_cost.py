from router.edge_cost import compute_edge_weight, compute_path_cost


def test_compute_edge_weight_positive() -> None:
	assert compute_edge_weight(cedge=20.0, travel_time_s=60.0, mode="jogger") > 0.0


def test_compute_path_cost_mode_differs() -> None:
	jogger_cost = compute_path_cost([10.0, 10.0], "jogger")
	cyclist_cost = compute_path_cost([10.0, 10.0], "cyclist")
	assert jogger_cost > cyclist_cost

