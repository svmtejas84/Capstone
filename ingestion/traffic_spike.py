import numpy as np


def inject_spike(
	concentration: np.ndarray,
	spike_center: tuple[int, int] = (25, 25),
	intensity: float = 20.0,
	radius_cells: int = 3,
) -> tuple[np.ndarray, np.ndarray]:
	spike = np.zeros_like(concentration)
	r0, c0 = spike_center
	for r in range(max(0, r0 - radius_cells), min(concentration.shape[0], r0 + radius_cells + 1)):
		for c in range(max(0, c0 - radius_cells), min(concentration.shape[1], c0 + radius_cells + 1)):
			dist2 = float((r - r0) ** 2 + (c - c0) ** 2)
			gain = intensity / (1.0 + dist2)
			spike[r, c] = gain
	return concentration + spike, spike

