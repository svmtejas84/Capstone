from fastapi.testclient import TestClient

from router.api.main import app


client = TestClient(app)


def test_health_endpoint() -> None:
	res = client.get("/health")
	assert res.status_code == 200
	assert res.json()["status"] == "ok"


def test_route_and_audit_flow() -> None:
	route_res = client.post(
		"/route",
		json={
			"origin": [13.03, 77.59],
			"destination": [12.98, 77.61],
			"mode": "jogger",
		},
	)
	assert route_res.status_code == 200
	payload = route_res.json()
	assert "stake_hash" in payload
	assert payload["candidates"]
	assert any(candidate["recommended"] for candidate in payload["candidates"])
	assert payload["stable_corridor_id"] in {candidate["id"] for candidate in payload["candidates"]}

	first = payload["candidates"][0]
	assert first["node_ids"]
	assert first["distance_m"] > 0.0
	assert first["travel_time_s"] > 0.0
	assert first["dose_ug"] >= 0.0
	assert set(first["explanation"]["route_score"]) == {
		"base_score",
		"dose_contribution",
		"distance_contribution",
		"final_score",
	}

	audit_res = client.get(f"/audit/{payload['stake_hash']}")
	assert audit_res.status_code == 200
	assert audit_res.json()["valid"] is True


def test_route_can_allocate_corridor_different_from_raw_rank_one() -> None:
	route_res = client.post(
		"/route",
		json={
			"origin": [13.03, 77.59],
			"destination": [12.98, 77.61],
			"mode": "cyclist",
		},
	)

	assert route_res.status_code == 200
	payload = route_res.json()
	recommended = [candidate for candidate in payload["candidates"] if candidate["recommended"]]

	assert len(recommended) == 1
	assert recommended[0]["id"] == payload["stable_corridor_id"]
	assert recommended[0]["preference_rank"] > 1
