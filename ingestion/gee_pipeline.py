from __future__ import annotations

import time
from datetime import datetime, timezone

from ingestion.bias_correction import apply_bias_correction
from ingestion.config import load_ingestion_config
from ingestion.nowcaster import advect
from ingestion.physics_plane import simulate_base_state, to_payload
from ingestion.redis_publisher import publish_state
from ingestion.traffic_spike import inject_spike
from shared.logging_utils import get_logger, log_json
from shared.redis_client import RedisStore


def build_next_payload(seed: int) -> dict[str, object]:
	cfg = load_ingestion_config()
	state = simulate_base_state(cfg, seed=seed)
	state.concentration = apply_bias_correction(state.concentration)
	state.concentration, state.source_spike = inject_spike(state.concentration)
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

