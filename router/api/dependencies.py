from __future__ import annotations

import json
from typing import Any

import numpy as np

from gnn.edge_weights import compute_edge_weights
from ingestion.data_fusion import fuse_weather_and_airquality
from ingestion.redis_publisher import get_latest_airquality, get_latest_sensors, get_latest_weather
from shared.config import get_settings
from shared.redis_client import RedisStore

_store = RedisStore()


def init_store() -> None:
	_store.connect()


def redis_store() -> RedisStore:
	return _store


def latest_plume_state() -> dict[str, Any]:
	settings = get_settings()
	weather = get_latest_weather(_store)
	airquality = get_latest_airquality(_store)
	sensors = get_latest_sensors(_store)
	return fuse_weather_and_airquality(weather, airquality, sensors, settings)


def latest_edge_weight_values() -> list[float]:
	state = latest_plume_state()
	grid = np.array(state["concentration"], dtype=float)
	wind_u = np.array(state["wind_u"], dtype=float)
	wind_v = np.array(state["wind_v"], dtype=float)
	edge_map = compute_edge_weights(grid, wind_u=wind_u, wind_v=wind_v)
	values = list(edge_map.values())
	if not values:
		values = [22.0, 16.0]

	_store.hset("toxicity:edge_weights", "latest", json.dumps(values))
	return values


def env_seed_from_state(state: dict[str, Any]) -> str:
	grid = np.array(state["concentration"], dtype=float)
	return f"ts={state['timestamp']};mean={grid.mean():.6f}"

