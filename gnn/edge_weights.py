from __future__ import annotations

import numpy as np

from gnn.graph_builder import build_demo_graph
from gnn.pi_gnn import PIGNN
from gnn.raster_sampler import sample_edge_concentration


def compute_edge_weights(
	concentration_grid: np.ndarray,
	wind_u: np.ndarray | None = None,
	wind_v: np.ndarray | None = None,
	steps: int = 2,
) -> dict[tuple[int, int], float]:
	g = build_demo_graph()
	sampled = sample_edge_concentration(g, concentration_grid)
	model = PIGNN()
	if wind_u is None:
		wind_u = np.ones_like(concentration_grid)
	if wind_v is None:
		wind_v = np.zeros_like(concentration_grid)
	return model.forward(g, sampled, wind_u=wind_u, wind_v=wind_v, steps=steps)

