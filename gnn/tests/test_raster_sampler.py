import numpy as np

from gnn.graph_builder import build_demo_graph
from gnn.raster_sampler import sample_edge_concentration


def test_sample_edge_concentration_returns_value_per_edge() -> None:
	g = build_demo_graph()
	grid = np.ones((6, 6), dtype=float) * 20.0
	sampled = sample_edge_concentration(g, grid)
	assert len(sampled) == g.number_of_edges()
	assert all(v == 20.0 for v in sampled.values())

