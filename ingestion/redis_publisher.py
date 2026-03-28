import json

from shared.redis_client import RedisStore

# Legacy stream (kept for backwards compatibility)
STREAM_NAME = "toxicity:global_truth"

# New data pipeline streams
WEATHER_STREAM = "weather:live"
AIRQUALITY_STREAM = "airquality:live"
SENSORS_STREAM = "sensors:live"


def publish_state(store: RedisStore, payload: dict[str, object]) -> None:
	"""Publish to legacy global truth stream for backwards compatibility."""
	store.xadd(STREAM_NAME, {"payload": json.dumps(payload)}, maxlen=30)


def get_latest_state(store: RedisStore) -> dict[str, object] | None:
	"""Retrieve from legacy global truth stream for backwards compatibility."""
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


def publish_weather(store: RedisStore, data: dict[str, object]) -> None:
	"""Publish weather data (wind, temperature, humidity, pressure, boundary layer height)."""
	store.xadd(WEATHER_STREAM, {"payload": json.dumps(data)}, maxlen=30)


def publish_airquality(store: RedisStore, data: dict[str, object]) -> None:
	"""Publish air quality data (NO2, SO2, PM2.5, PM10, CO)."""
	store.xadd(AIRQUALITY_STREAM, {"payload": json.dumps(data)}, maxlen=30)


def publish_sensors(store: RedisStore, data: dict[str, object]) -> None:
	"""Publish ground-level sensor validation data from AQICN."""
	store.xadd(SENSORS_STREAM, {"payload": json.dumps(data)}, maxlen=30)


def get_latest_weather(store: RedisStore) -> dict[str, object] | None:
	"""Get latest weather data."""
	client = store.client
	if client is None:
		return None
	rows = client.xrevrange(WEATHER_STREAM, count=1)
	if not rows:
		return None
	_, fields = rows[0]
	raw = fields.get("payload")
	if not raw:
		return None
	return json.loads(raw)


def get_latest_airquality(store: RedisStore) -> dict[str, object] | None:
	"""Get latest air quality data."""
	client = store.client
	if client is None:
		return None
	rows = client.xrevrange(AIRQUALITY_STREAM, count=1)
	if not rows:
		return None
	_, fields = rows[0]
	raw = fields.get("payload")
	if not raw:
		return None
	return json.loads(raw)


def get_latest_sensors(store: RedisStore) -> dict[str, object] | None:
	"""Get latest sensor validation data."""
	client = store.client
	if client is None:
		return None
	rows = client.xrevrange(SENSORS_STREAM, count=1)
	if not rows:
		return None
	_, fields = rows[0]
	raw = fields.get("payload")
	if not raw:
		return None
	return json.loads(raw)


