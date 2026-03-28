from __future__ import annotations

from math import atan2, cos, radians, sin
from typing import Any

import networkx as nx
import numpy as np
from pyproj import Transformer

from gnn.graph_builder import load_utm_graph
from shared.config import get_settings

_WGS84_TO_UTM43 = Transformer.from_crs("EPSG:4326", "EPSG:32643", always_xy=True)
_UTM43_TO_WGS84 = Transformer.from_crs("EPSG:32643", "EPSG:4326", always_xy=True)


def _safe_float(value: object, default: float = 0.0) -> float:
	try:
		if value is None:
			return default
		return float(value)
	except (TypeError, ValueError):
		return default


def _extract_sensor_points(
	weather_data: dict[str, object] | None,
	aq_data: dict[str, object] | None,
	sensors_data: dict[str, object] | None,
) -> list[dict[str, float]]:
	settings = get_settings()
	points: list[dict[str, float]] = []

	base_lat = _safe_float((aq_data or {}).get("lat"), settings.bangalore_lat)
	base_lon = _safe_float((aq_data or {}).get("lon"), settings.bangalore_lon)
	points.append(
		{
			"lat": base_lat,
			"lon": base_lon,
			"no2": _safe_float((aq_data or {}).get("nitrogen_dioxide")),
			"so2": _safe_float((aq_data or {}).get("sulphur_dioxide")),
			"pm2_5": _safe_float((aq_data or {}).get("pm2_5")),
		}
	)

	sensor_lat = _safe_float((sensors_data or {}).get("lat"), settings.bangalore_lat)
	sensor_lon = _safe_float((sensors_data or {}).get("lon"), settings.bangalore_lon)
	if sensors_data:
		points.append(
			{
				"lat": sensor_lat,
				"lon": sensor_lon,
				"no2": _safe_float(sensors_data.get("no2")),
				"so2": _safe_float(sensors_data.get("so2")),
				"pm2_5": _safe_float(sensors_data.get("pm2_5")),
			}
		)

	if weather_data and not aq_data and not sensors_data:
		points.append(
			{
				"lat": _safe_float(weather_data.get("lat"), settings.bangalore_lat),
				"lon": _safe_float(weather_data.get("lon"), settings.bangalore_lon),
				"no2": 0.0,
				"so2": 0.0,
				"pm2_5": 0.0,
			}
		)

	return points


def _edge_midpoint_xy(graph: nx.MultiDiGraph, u: int, v: int, data: dict[str, object]) -> tuple[float, float]:
	geom = data.get("geometry")
	if geom is not None:
		try:
			coords = list(geom.coords)
			if len(coords) >= 2:
				mx = (coords[0][0] + coords[-1][0]) / 2.0
				my = (coords[0][1] + coords[-1][1]) / 2.0
				return float(mx), float(my)
		except Exception:
			pass

	x1 = _safe_float(graph.nodes[u].get("x"))
	y1 = _safe_float(graph.nodes[u].get("y"))
	x2 = _safe_float(graph.nodes[v].get("x"))
	y2 = _safe_float(graph.nodes[v].get("y"))
	return (x1 + x2) / 2.0, (y1 + y2) / 2.0


def _idw_pollution(edge_x: float, edge_y: float, sensor_points: list[dict[str, float]]) -> tuple[float, float, float]:
	if not sensor_points:
		return 0.0, 0.0, 0.0

	weighted_no2 = 0.0
	weighted_so2 = 0.0
	weighted_pm = 0.0
	weight_sum = 0.0

	for p in sensor_points:
		sx, sy = _WGS84_TO_UTM43.transform(p["lon"], p["lat"])
		dx = edge_x - sx
		dy = edge_y - sy
		d2 = dx * dx + dy * dy
		w = 1.0 / (d2 + 1.0)
		weighted_no2 += w * p["no2"]
		weighted_so2 += w * p["so2"]
		weighted_pm += w * p["pm2_5"]
		weight_sum += w

	if weight_sum <= 0.0:
		return 0.0, 0.0, 0.0

	return weighted_no2 / weight_sum, weighted_so2 / weight_sum, weighted_pm / weight_sum


def _wind_factor(weather_data: dict[str, object] | None, edge_bearing_deg: float) -> float:
	wind_speed = _safe_float((weather_data or {}).get("wind_speed_10m"), 0.2)
	wind_dir = _safe_float((weather_data or {}).get("wind_direction_10m"), 0.0)
	delta = abs(((edge_bearing_deg - wind_dir + 180.0) % 360.0) - 180.0)
	angular = np.exp(-((delta / 45.0) ** 2))
	return float(max(0.2, (1.0 + 0.15 * wind_speed) * angular))


def fuse_weather_and_airquality(
	weather_data: dict[str, object] | None,
	aq_data: dict[str, object] | None,
	sensors_data: dict[str, object] | None,
	settings: Any | None = None,
	graph: nx.MultiDiGraph | None = None,
) -> dict[tuple[int, int], dict[str, float]]:
	"""Interpolate pollution onto UTM road-graph edges using IDW from nearest sensor points."""
	if settings is None:
		settings = get_settings()
	if graph is None:
		graph = load_utm_graph()

	sensor_points = _extract_sensor_points(weather_data, aq_data, sensors_data)
	edge_payload: dict[tuple[int, int], dict[str, float]] = {}

	for u, v, _k, data in graph.edges(keys=True, data=True):
		emx, emy = _edge_midpoint_xy(graph, u, v, data)
		no2, so2, pm2_5 = _idw_pollution(emx, emy, sensor_points)

		x1 = _safe_float(graph.nodes[u].get("x"))
		y1 = _safe_float(graph.nodes[u].get("y"))
		x2 = _safe_float(graph.nodes[v].get("x"))
		y2 = _safe_float(graph.nodes[v].get("y"))
		edge_bearing = (np.degrees(atan2((y2 - y1), (x2 - x1))) + 360.0) % 360.0

		base_pollution = max(0.0, no2 + so2 + pm2_5)
		toxicity = base_pollution * _wind_factor(weather_data, edge_bearing)

		edge_payload[(int(u), int(v))] = {
			"no2": float(no2),
			"so2": float(so2),
			"pm2_5": float(pm2_5),
			"toxicity": float(toxicity),
			"x": float(emx),
			"y": float(emy),
		}

	return edge_payload


def edge_midpoint_latlon(graph: nx.MultiDiGraph, u: int, v: int, data: dict[str, object]) -> tuple[float, float]:
	x, y = _edge_midpoint_xy(graph, u, v, data)
	lon, lat = _UTM43_TO_WGS84.transform(x, y)
	return float(lat), float(lon)
