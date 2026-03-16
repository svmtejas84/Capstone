from __future__ import annotations

import json
from typing import Any

import numpy as np

from gnn.edge_weights import compute_edge_weights
from ingestion.gee_pipeline import build_next_payload
from ingestion.redis_publisher import get_latest_state
from shared.redis_client import RedisStore

_store = RedisStore()


def init_store() -> None:
	_store.connect()


def redis_store() -> RedisStore:
	return _store


def latest_plume_state() -> dict[str, Any]:
	state = get_latest_state(_store)
	if state is None:
		return build_next_payload(seed=42)
	return state


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

