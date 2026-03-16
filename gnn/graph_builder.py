from __future__ import annotations

from math import atan2, degrees

import networkx as nx

from shared.geo_utils import haversine_m


def _bearing_deg(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
	# Local planar approximation is sufficient for this small demo subgraph.
	dx = lon2 - lon1
	dy = lat2 - lat1
	return (degrees(atan2(dy, dx)) + 360.0) % 360.0


def build_demo_graph() -> nx.DiGraph:
	g = nx.DiGraph()
	# Demo coordinates around Hebbal/Mekhri Circle corridor in Bangalore.
	nodes = {
		1: (13.0350, 77.5960),
		2: (13.0275, 77.6030),
		3: (12.9750, 77.6070),
		4: (13.0180, 77.5860),
		5: (12.9960, 77.5940),
	}
	for node_id, (lat, lon) in nodes.items():
		g.add_node(node_id, lat=lat, lon=lon)

	def add_edge(u: int, v: int, building_density: float) -> None:
		lat1, lon1 = nodes[u]
		lat2, lon2 = nodes[v]
		g.add_edge(
			u,
			v,
			length_m=haversine_m(lat1, lon1, lat2, lon2),
			bearing_deg=_bearing_deg(lat1, lon1, lat2, lon2),
			building_density=building_density,
		)

	add_edge(1, 2, 0.72)
	add_edge(2, 3, 0.58)
	add_edge(1, 4, 0.44)
	add_edge(4, 5, 0.67)
	add_edge(5, 3, 0.51)
	return g

