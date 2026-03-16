import json

from shared.redis_client import RedisStore


STREAM_NAME = "toxicity:global_truth"


def publish_state(store: RedisStore, payload: dict[str, object]) -> None:
	store.xadd(STREAM_NAME, {"payload": json.dumps(payload)}, maxlen=30)


def get_latest_state(store: RedisStore) -> dict[str, object] | None:
	client = store.client
	if client is None:
		return None
	rows = client.xrevrange(STREAM_NAME, count=1)
	if not rows:
		return None
	_, fields = rows[0]
	raw = fields.get("payload")
	if not raw:
		return None
	return json.loads(raw)

