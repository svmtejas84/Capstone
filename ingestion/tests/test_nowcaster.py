import numpy as np

from ingestion.nowcaster import advect


def test_advect_preserves_shape_and_non_negative() -> None:
	c = np.ones((5, 5), dtype=float) * 10.0
	u = np.ones((5, 5), dtype=float)
	v = np.zeros((5, 5), dtype=float)
	out = advect(c, u, v)
	assert out.shape == c.shape
	assert out.min() >= 0.0

