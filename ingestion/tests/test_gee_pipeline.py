from ingestion.gee_pipeline import build_next_payload


def test_build_next_payload_shape_and_keys() -> None:
	payload = build_next_payload(seed=123)
	assert set(payload.keys()) == {"concentration", "wind_u", "wind_v", "source_spike", "timestamp"}
	assert len(payload["concentration"]) == 50
	assert len(payload["concentration"][0]) == 50

