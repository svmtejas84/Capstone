from __future__ import annotations

import re
from collections.abc import Iterable


# Conservative directional capacities in vehicles per hour per lane. They are
# used as an allocation ceiling, not as a replacement for the dose objective.
_CAPACITY_PER_LANE_VPH = {
	"motorway": 1800.0,
	"trunk": 1500.0,
	"primary": 1200.0,
	"secondary": 1000.0,
	"tertiary": 800.0,
	"unclassified": 600.0,
	"residential": 450.0,
	"service": 250.0,
}
_DEFAULT_LANES = {"motorway": 3.0, "trunk": 2.0, "primary": 2.0, "secondary": 2.0, "tertiary": 1.0}


def _number(value: object, default: float) -> float:
	match = re.search(r"\d+(?:\.\d+)?", str(value))
	return float(match.group()) if match else default


def _road_type(attrs: dict[str, object]) -> str:
	value = attrs.get("highway", "unclassified")
	if isinstance(value, (list, tuple)):
		value = value[0] if value else "unclassified"
	return str(value).lower()


def _lane_count(attrs: dict[str, object], road_type: str) -> float:
	if "lanes" in attrs:
		return max(1.0, _number(attrs["lanes"], 1.0))
	if "width" in attrs:
		return max(1.0, _number(attrs["width"], 3.2) / 3.2)
	return _DEFAULT_LANES.get(road_type, 1.0)


def _congestion_ratio(attrs: dict[str, object]) -> float:
	for key in ("congestion", "congestion_ratio", "traffic_ratio"):
		if key in attrs:
			return min(0.9, max(0.0, _number(attrs[key], 0.0)))
	# If both speeds exist, derive congestion from the live/free-flow ratio.
	if "speed_kph" in attrs and "maxspeed" in attrs:
		free_flow = _number(attrs["maxspeed"], 0.0)
		current = _number(attrs["speed_kph"], free_flow)
		if free_flow > 0.0:
			return min(0.9, max(0.0, 1.0 - current / free_flow))
	return 0.0


def route_capacity(
	edge_attrs: Iterable[dict[str, object]],
	*,
	travel_time_s: float,
	allocation_window_s: float = 900.0,
) -> int:
	"""Estimate a route's allocation capacity from its bottleneck road segment.

	The estimate uses road class and usable width/lanes, discounts live traffic
	congestion when supplied, and reduces capacity for routes occupied longer
	than the allocation window. The result is a directional commuter count for
	the current simulation window.
	"""
	edges = list(edge_attrs)
	if not edges:
		return 1

	edge_capacities = []
	for attrs in edges:
		road_type = _road_type(attrs)
		base = _CAPACITY_PER_LANE_VPH.get(road_type, _CAPACITY_PER_LANE_VPH["unclassified"])
		edge_capacities.append(base * _lane_count(attrs, road_type) * (1.0 - _congestion_ratio(attrs)))

	bottleneck_vph = min(edge_capacities)
	window_capacity = bottleneck_vph * allocation_window_s / 3600.0
	travel_time_penalty = 1.0 + max(0.0, travel_time_s) / allocation_window_s
	return max(1, int(window_capacity / travel_time_penalty))
