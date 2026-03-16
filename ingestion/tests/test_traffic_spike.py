import numpy as np

from ingestion.traffic_spike import inject_spike


def test_inject_spike_increases_local_concentration() -> None:
	c = np.zeros((11, 11), dtype=float)
	out, spike = inject_spike(c, spike_center=(5, 5), intensity=12.0, radius_cells=2)
	assert spike[5, 5] > 0.0
	assert out[5, 5] > c[5, 5]

