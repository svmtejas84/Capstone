import numpy as np

from gnn.edge_weights import compute_edge_weights


def test_compute_edge_weights_non_empty() -> None:
	weights = compute_edge_weights(np.ones((8, 8), dtype=float) * 15.0)
	assert len(weights) > 0
	assert min(weights.values()) > 0.0

