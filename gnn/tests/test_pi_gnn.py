import numpy as np

from gnn.graph_builder import build_demo_graph
from gnn.pi_gnn import PIGNN


def test_pignn_forward_scales_values() -> None:
	g = build_demo_graph()
	model = PIGNN()
	out = model.forward(
		graph=g,
		edge_values={(1, 2): 10.0},
		wind_u=np.ones((4, 4), dtype=float),
		wind_v=np.zeros((4, 4), dtype=float),
	)
	assert (1, 2) in out
	assert out[(1, 2)] > 0.0


def test_pignn_multihop_steps_change_state() -> None:
	g = build_demo_graph()
	model = PIGNN()
	seed = {(1, 2): 15.0, (2, 3): 10.0, (1, 4): 8.0, (4, 5): 6.0, (5, 3): 5.0}

	one_step = model.forward(
		graph=g,
		edge_values=seed,
		wind_u=np.ones((4, 4), dtype=float),
		wind_v=np.zeros((4, 4), dtype=float),
		steps=1,
	)
	two_step = model.forward(
		graph=g,
		edge_values=seed,
		wind_u=np.ones((4, 4), dtype=float),
		wind_v=np.zeros((4, 4), dtype=float),
		steps=2,
	)

	assert two_step[(2, 3)] != one_step[(2, 3)]


def test_pignn_temporal_damping_reduces_update_magnitude() -> None:
	g = build_demo_graph()
	seed = {(1, 2): 15.0, (2, 3): 10.0, (1, 4): 8.0, (4, 5): 6.0, (5, 3): 5.0}

	low_damp_model = PIGNN(temporal_damping=0.2)
	high_damp_model = PIGNN(temporal_damping=1.0)

	low = low_damp_model.forward(
		graph=g,
		edge_values=seed,
		wind_u=np.ones((4, 4), dtype=float),
		wind_v=np.zeros((4, 4), dtype=float),
		steps=3,
	)
	high = high_damp_model.forward(
		graph=g,
		edge_values=seed,
		wind_u=np.ones((4, 4), dtype=float),
		wind_v=np.zeros((4, 4), dtype=float),
		steps=3,
	)

	low_delta = abs(low[(2, 3)] - seed[(2, 3)])
	high_delta = abs(high[(2, 3)] - seed[(2, 3)])
	assert low_delta < high_delta


def test_pignn_long_horizon_stays_bounded() -> None:
	g = build_demo_graph()
	model = PIGNN()
	seed = {(1, 2): 120.0, (2, 3): 110.0, (1, 4): 90.0, (4, 5): 80.0, (5, 3): 70.0}

	out = model.forward(
		graph=g,
		edge_values=seed,
		wind_u=np.ones((4, 4), dtype=float),
		wind_v=np.zeros((4, 4), dtype=float),
		steps=10,
	)

	assert all(0.0 <= value <= 500.0 for value in out.values())

