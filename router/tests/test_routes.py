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

	audit_res = client.get(f"/audit/{payload['stake_hash']}")
	assert audit_res.status_code == 200
	assert audit_res.json()["valid"] is True

