from __future__ import annotations

import numpy as np
import networkx as nx

from gnn.graph_builder import load_utm_graph, to_gnn_digraph
from gnn.pi_gnn import PIGNN
from ingestion.data_fusion import fuse_weather_and_airquality
from ingestion.redis_publisher import get_latest_airquality, get_latest_sensors, get_latest_weather
from shared.redis_client import RedisStore


def _wind_components(weather: dict[str, object] | None) -> tuple[np.ndarray, np.ndarray]:
	wind_speed = float((weather or {}).get("wind_speed_10m") or 0.2)
	wind_dir = float((weather or {}).get("wind_direction_10m") or 0.0)
	rad = np.radians(wind_dir)
	u = wind_speed * np.sin(rad)
	v = wind_speed * np.cos(rad)
	return np.array([[u]], dtype=float), np.array([[v]], dtype=float)


def update_graph_toxicity_from_streams(store: RedisStore) -> nx.MultiDiGraph:
	"""Compute toxicity weights from live Redis streams and write to UTM graph edges."""
	graph = load_utm_graph()
	weather = get_latest_weather(store)
	airquality = get_latest_airquality(store)
	sensors = get_latest_sensors(store)

	edge_obs = fuse_weather_and_airquality(weather, airquality, sensors, graph=graph)
	gnn_graph = to_gnn_digraph(graph)
	seed_values = {(u, v): vals["toxicity"] for (u, v), vals in edge_obs.items() if gnn_graph.has_edge(u, v)}

	model = PIGNN()
	wind_u, wind_v = _wind_components(weather)
	pred = model.forward(gnn_graph, seed_values, wind_u=wind_u, wind_v=wind_v, steps=2)

	for u, v, k in graph.edges(keys=True):
		toxicity = float(pred.get((int(u), int(v)), seed_values.get((int(u), int(v)), 0.0)))
		graph[u][v][k]["toxicity"] = toxicity

	return graph


def graph_edge_toxicity_values(graph: nx.MultiDiGraph) -> list[float]:
	values: list[float] = []
	for u, v, k in graph.edges(keys=True):
		values.append(float(graph[u][v][k].get("toxicity", 0.0)))
	return values


def compute_edge_weights(
	concentration_grid: np.ndarray,
	wind_u: np.ndarray | None = None,
	wind_v: np.ndarray | None = None,
	steps: int = 2,
) -> dict[tuple[int, int], float]:
	"""Compatibility helper for existing call sites.

	Maps a scalar concentration proxy to current UTM graph edges and runs PIGNN.
	"""
	graph = load_utm_graph()
	gnn_graph = to_gnn_digraph(graph)
	base = float(np.mean(concentration_grid)) if concentration_grid.size > 0 else 0.0
	seed = {(int(u), int(v)): base for u, v in gnn_graph.edges()}

	model = PIGNN()
	if wind_u is None:
		wind_u = np.array([[0.2]], dtype=float)
	if wind_v is None:
		wind_v = np.array([[0.0]], dtype=float)
	return model.forward(gnn_graph, seed, wind_u=wind_u, wind_v=wind_v, steps=steps)
