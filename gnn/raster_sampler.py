from __future__ import annotations

import networkx as nx
import numpy as np


def sample_edge_concentration(g: nx.DiGraph, concentration_grid: np.ndarray) -> dict[tuple[int, int], float]:
	mean_c = float(np.mean(concentration_grid))
	out: dict[tuple[int, int], float] = {}
	for u, v in g.edges():
		out[(u, v)] = mean_c
	return out

