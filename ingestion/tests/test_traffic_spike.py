import numpy as np

from ingestion.traffic_spike import compute_anomalous_excess, inject_spike


def test_compute_anomalous_excess_threshold_gate() -> None:
	baseline = np.array([[1.0, 1.0], [1.0, 1.0]], dtype=float)
	observed = np.array([[1.2, 1.6], [1.49, 1.51]], dtype=float)
	excess = compute_anomalous_excess(observed, baseline, alpha=1.5)
	assert excess[0, 0] == 0.0
	assert excess[1, 0] == 0.0
	assert excess[0, 1] > 0.0
	assert excess[1, 1] > 0.0


def test_inject_spike_uses_only_anomalous_excess() -> None:
	c = np.zeros((2, 2), dtype=float)
	baseline = np.array([[1.0, 1.0], [1.0, 1.0]], dtype=float)
	observed = np.array([[1.4, 1.7], [1.0, 2.0]], dtype=float)
	out, spike = inject_spike(
		c,
		observed_density=observed,
		baseline_density=baseline,
		alpha=1.5,
		emission_factor_k=2.0,
	)
	assert spike[0, 0] == 0.0
	assert spike[1, 0] == 0.0
	assert np.isclose(spike[0, 1], 2.0 * (1.7 - 1.0))
	assert np.isclose(spike[1, 1], 2.0 * (2.0 - 1.0))
	assert np.array_equal(out, spike)

