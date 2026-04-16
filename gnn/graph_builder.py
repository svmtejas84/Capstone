from __future__ import annotations

from math import atan2, degrees
from pathlib import Path

import networkx as nx
import osmnx as ox

from shared.geo_utils import haversine_m

_UTM_GRAPH_PATH = Path("data/graphs/bangalore_utm.graphml")


def _bearing_deg(x1: float, y1: float, x2: float, y2: float) -> float:
	return (degrees(atan2(y2 - y1, x2 - x1)) + 360.0) % 360.0


def load_utm_graph() -> nx.MultiDiGraph:
	"""Load or fetch Bangalore road graph and ensure UTM Zone 43N projection."""
	if _UTM_GRAPH_PATH.exists():
		return ox.load_graphml(_UTM_GRAPH_PATH)

	raw = ox.graph_from_place(
		"Bangalore, India",
		simplify=True,
		retain_all=False,
		network_type="drive",
	)
	projected = ox.projection.project_graph(raw, to_crs="EPSG:32643")
	_UTM_GRAPH_PATH.parent.mkdir(parents=True, exist_ok=True)
	ox.save_graphml(projected, _UTM_GRAPH_PATH)
	return projected


def to_gnn_digraph(graph: nx.MultiDiGraph) -> nx.DiGraph:
	"""Convert MultiDiGraph to DiGraph with attributes expected by PIGNN."""
	di = nx.DiGraph()
	for nid, attrs in graph.nodes(data=True):
		di.add_node(int(nid), **attrs)

	for u, v, _k, attrs in graph.edges(keys=True, data=True):
		x1 = float(graph.nodes[u].get("x", 0.0))
		y1 = float(graph.nodes[u].get("y", 0.0))
		x2 = float(graph.nodes[v].get("x", 0.0))
		y2 = float(graph.nodes[v].get("y", 0.0))
		length_m = float(attrs.get("length", attrs.get("length_m", 100.0)))
		bearing = float(attrs.get("bearing_deg", _bearing_deg(x1, y1, x2, y2)))
		building_density = float(attrs.get("building_density", 0.5))

		if not di.has_edge(int(u), int(v)):
			di.add_edge(
				int(u),
				int(v),
				length_m=length_m,
				bearing_deg=bearing,
				building_density=building_density,
			)

	return di


def build_demo_graph() -> nx.DiGraph:
	"""Small deterministic graph kept for unit tests of GNN internals."""
	g = nx.DiGraph()
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
			bearing_deg=(degrees(atan2(lat2 - lat1, lon2 - lon1)) + 360.0) % 360.0,
			building_density=building_density,
		)

	add_edge(1, 2, 0.72)
	add_edge(2, 3, 0.58)
	add_edge(1, 4, 0.44)
	add_edge(4, 5, 0.67)
	add_edge(5, 3, 0.51)
	return g
