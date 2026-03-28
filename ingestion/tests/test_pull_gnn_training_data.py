import numpy as np

from ingestion.pull_gnn_training_data import build_gnn_dataset


def test_build_gnn_dataset_shapes() -> None:
	features, targets, edge_index = build_gnn_dataset(samples=3, seed_start=123)
	assert features.shape[0] == 3
	assert features.shape[1] == 4
	assert targets.shape[0] == 3
	assert edge_index.shape[1] == 2
	assert targets.shape[1] == edge_index.shape[0]
	assert np.isfinite(features).all()
	assert np.isfinite(targets).all()
