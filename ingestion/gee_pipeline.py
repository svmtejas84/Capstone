from __future__ import annotations

import time
from datetime import datetime, timezone

import numpy as np

from ingestion.bias_correction import apply_bias_correction
from ingestion.config import load_ingestion_config
from ingestion.nowcaster import advect
from ingestion.physics_plane import simulate_base_state, to_payload
from ingestion.redis_publisher import publish_state
from ingestion.traffic_spike import inject_spike
from shared.logging_utils import get_logger, log_json
from shared.redis_client import RedisStore


def _simulate_insat_wind_update(
	wind_u: np.ndarray,
	wind_v: np.ndarray,
	seed: int,
) -> tuple[np.ndarray, np.ndarray]:
	"""Apply a small deterministic perturbation as a stand-in for INSAT AMV updates."""
	rng = np.random.default_rng(seed + 10_000)
	u_delta = rng.normal(loc=0.0, scale=0.15, size=wind_u.shape)
	v_delta = rng.normal(loc=0.0, scale=0.15, size=wind_v.shape)
	return wind_u + u_delta, wind_v + v_delta


def _simulate_traffic_density(shape: tuple[int, int], seed: int) -> tuple[np.ndarray, np.ndarray]:
	"""Return baseline and observed densities with sparse anomalies for threshold gating."""
	rng = np.random.default_rng(seed + 20_000)
	baseline = rng.uniform(0.4, 1.2, size=shape)
	observed = baseline + rng.normal(loc=0.0, scale=0.08, size=shape)

	# Create a few local congestion anomalies to emulate spike periods.
	for _ in range(3):
		r = int(rng.integers(0, shape[0]))
		c = int(rng.integers(0, shape[1]))
		observed[r, c] = baseline[r, c] * rng.uniform(1.45, 1.9)

	return np.clip(baseline, 0.0, None), np.clip(observed, 0.0, None)


def build_next_payload(seed: int) -> dict[str, object]:
	cfg = load_ingestion_config()
	# Keep ERA5-like state as the base climatological layer.
	state = simulate_base_state(cfg, seed=seed)
	# Refresh with INSAT-like intra-day AMV perturbations.
	state.wind_u, state.wind_v = _simulate_insat_wind_update(state.wind_u, state.wind_v, seed)
	state.concentration = apply_bias_correction(state.concentration)
	baseline_density, observed_density = _simulate_traffic_density(state.concentration.shape, seed)
	state.concentration, state.source_spike = inject_spike(
		state.concentration,
		observed_density=observed_density,
		baseline_density=baseline_density,
		alpha=cfg.traffic_anomaly_alpha,
		emission_factor_k=cfg.traffic_emission_factor_k,
	)
	state.concentration = advect(state.concentration, state.wind_u, state.wind_v)
	state.timestamp = datetime.now(timezone.utc)
	return to_payload(state)


def main() -> None:
	logger = get_logger("ingestion")
	cfg = load_ingestion_config()
	store = RedisStore()
	store.connect()

	seed = 42
	log_json(logger, "ingestion_start", simulation_mode=cfg.simulation_mode)

	while True:
		payload = build_next_payload(seed)
		publish_state(store, payload)
		log_json(logger, "ingestion_tick", timestamp=payload["timestamp"])
		seed += 1
		time.sleep(max(5, cfg.refresh_minutes * 60))


if __name__ == "__main__":
	main()

