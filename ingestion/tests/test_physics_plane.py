from ingestion.config import load_ingestion_config
from ingestion.physics_plane import simulate_base_state, to_payload


def test_simulate_base_state_has_expected_dimensions() -> None:
	cfg = load_ingestion_config()
	state = simulate_base_state(cfg)
	assert state.concentration.shape == (cfg.grid_rows, cfg.grid_cols)
	assert state.wind_u.shape == (cfg.grid_rows, cfg.grid_cols)


def test_to_payload_serializable_types() -> None:
	cfg = load_ingestion_config()
	state = simulate_base_state(cfg)
	payload = to_payload(state)
	assert isinstance(payload["concentration"], list)
	assert isinstance(payload["timestamp"], str)

