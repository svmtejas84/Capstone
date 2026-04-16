import numpy as np


def compute_anomalous_excess(
	observed_density: np.ndarray,
	baseline_density: np.ndarray,
	alpha: float = 1.5,
) -> np.ndarray:
	if observed_density.shape != baseline_density.shape:
		raise ValueError("observed_density and baseline_density must have matching shapes")
	if alpha <= 0.0:
		raise ValueError("alpha must be > 0")

	gated = observed_density > (alpha * baseline_density)
	excess = np.where(gated, observed_density - baseline_density, 0.0)
	return np.clip(excess, 0.0, None)


def inject_spike(
	concentration: np.ndarray,
	observed_density: np.ndarray | None = None,
	baseline_density: np.ndarray | None = None,
	alpha: float = 1.5,
	emission_factor_k: float = 1.0,
	spike_center: tuple[int, int] = (25, 25),
	intensity: float = 20.0,
	radius_cells: int = 3,
) -> tuple[np.ndarray, np.ndarray]:
	if emission_factor_k < 0.0:
		raise ValueError("emission_factor_k must be >= 0")

	if observed_density is not None or baseline_density is not None:
		if observed_density is None or baseline_density is None:
			raise ValueError("observed_density and baseline_density must both be provided")
		excess = compute_anomalous_excess(observed_density, baseline_density, alpha=alpha)
		spike = emission_factor_k * excess
		return concentration + spike, spike

	# Fallback synthetic spike for pure simulation mode.
	spike = np.zeros_like(concentration)
	r0, c0 = spike_center
	for r in range(max(0, r0 - radius_cells), min(concentration.shape[0], r0 + radius_cells + 1)):
		for c in range(max(0, c0 - radius_cells), min(concentration.shape[1], c0 + radius_cells + 1)):
			dist2 = float((r - r0) ** 2 + (c - c0) ** 2)
			gain = intensity / (1.0 + dist2)
			spike[r, c] = gain
	return concentration + spike, spike

