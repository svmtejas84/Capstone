from __future__ import annotations

import json
from typing import Any

import numpy as np
import networkx as nx

from gnn.edge_weights import graph_edge_toxicity_values, update_graph_toxicity_from_streams
from gnn.graph_builder import load_utm_graph
from shared.redis_client import RedisStore

_store = RedisStore()
_utm_graph: nx.MultiDiGraph | None = None


def init_store() -> None:
	global _utm_graph
	_store.connect()
	if _utm_graph is None:
		_utm_graph = load_utm_graph()


def redis_store() -> RedisStore:
	return _store


def road_graph() -> nx.MultiDiGraph:
	global _utm_graph
	if _utm_graph is None:
		_utm_graph = load_utm_graph()
	return _utm_graph


def latest_plume_state() -> dict[str, Any]:
	graph = update_graph_toxicity_from_streams(_store)
	edges: list[dict[str, float]] = []
	for u, v, k, attrs in graph.edges(keys=True, data=True):
		x1 = float(graph.nodes[u].get("x", 0.0))
		y1 = float(graph.nodes[u].get("y", 0.0))
		x2 = float(graph.nodes[v].get("x", 0.0))
		y2 = float(graph.nodes[v].get("y", 0.0))
		edges.append(
			{
				"u": int(u),
				"v": int(v),
				"k": int(k),
				"x": (x1 + x2) / 2.0,
				"y": (y1 + y2) / 2.0,
				"toxicity": float(attrs.get("toxicity", 0.0)),
			}
		)

	return {
		"edges": edges,
		"timestamp": "live",
	}


def latest_edge_weight_values() -> list[float]:
	graph = update_graph_toxicity_from_streams(_store)
	values = graph_edge_toxicity_values(graph)
	if not values:
		values = [22.0, 16.0]

	_store.hset("toxicity:edge_weights", "latest", json.dumps(values))
	return values


def env_seed_from_state(state: dict[str, Any]) -> str:
	vals = np.array([float(e.get("toxicity", 0.0)) for e in state.get("edges", [])], dtype=float)
	mean = float(vals.mean()) if vals.size > 0 else 0.0
	return f"ts={state.get('timestamp', 'live')};mean={mean:.6f}"

