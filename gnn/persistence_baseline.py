from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import torch

DEFAULT_GRAPH_PATH = Path("data/processed/graph/topology_graph_pyg_inference.pt")
DEFAULT_NODE_MAP_PATH = Path("data/processed/graph/topology_nodeid_to_index_map.parquet")


@lru_cache(maxsize=1)
def _load_static_artifacts(
	graph_path: str = str(DEFAULT_GRAPH_PATH),
	node_map_path: str = str(DEFAULT_NODE_MAP_PATH),
) -> tuple[object, dict[int, int], int, int]:
	import pandas as pd

	graph = torch.load(graph_path, map_location="cpu", weights_only=False)
	node_map = pd.read_parquet(node_map_path)
	node_to_index = {
		int(node_id): int(node_index)
		for node_id, node_index in zip(node_map["node_id"].values, node_map["node_index"].values, strict=False)
	}
	schema = list(getattr(graph, "node_feature_schema", []))
	station_pm25_idx = schema.index("station_pm25") if "station_pm25" in schema else 1
	city_pm25_idx = schema.index("city_pm2_5") if "city_pm2_5" in schema else 13
	return graph, node_to_index, station_pm25_idx, city_pm25_idx


def _node_concentration(graph: object, node_idx: int, station_pm25_idx: int, city_pm25_idx: int) -> float:
	x = graph.x[int(node_idx)]
	station = float(x[station_pm25_idx])
	city = float(x[city_pm25_idx])
	if station > 0.0:
		return station
	if city > 0.0:
		return city
	return 0.0


def predict_route_edge_concentrations_persistence(
	route_edges: list[tuple[int, int]],
) -> dict[tuple[int, int], float]:
	"""Use the latest graph PM2.5 field as a persistence baseline for route edges."""
	if not route_edges:
		return {}

	graph, node_to_index, station_pm25_idx, city_pm25_idx = _load_static_artifacts()
	pred: dict[tuple[int, int], float] = {}
	for u, v in route_edges:
		if int(u) not in node_to_index or int(v) not in node_to_index:
			continue
		gu = node_to_index[int(u)]
		gv = node_to_index[int(v)]
		cu = _node_concentration(graph, gu, station_pm25_idx, city_pm25_idx)
		cv = _node_concentration(graph, gv, station_pm25_idx, city_pm25_idx)
		pred[(int(u), int(v))] = max(0.0, (cu + cv) / 2.0)
	return pred


def predict_route_edge_concentrations_true_persistence(
    route_edges: list[tuple[int, int]],
    current_time_step_tensor: torch.Tensor,
    node_to_index: dict[int, int],
    station_pm25_idx: int,
    city_pm25_idx: int
) -> dict[tuple[int, int], float]:
    """
    LEAK-FREE PERSISTENCE BASELINE: Replaces static graph lookups with 
    the actual feature states from the current operational time step.
    """
    if not route_edges or current_time_step_tensor is None:
        return {}

    pred: dict[tuple[int, int], float] = {}
    
    for u, v in route_edges:
        if int(u) not in node_to_index or int(v) not in node_to_index:
            continue
            
        gu = node_to_index[int(u)]
        gv = node_to_index[int(v)]
        
        # Pull features explicitly from the historical time-step tensor slicing matrix
        xu = current_time_step_tensor[gu]
        xv = current_time_step_tensor[gv]
        
        # Read the current step features to persist into the next evaluation window
        station_u = float(xu[station_pm25_idx])
        city_u = float(xu[city_pm25_idx])
        cu = station_u if station_u > 0.0 else (city_u if city_u > 0.0 else 0.0)
        
        station_v = float(xv[station_pm25_idx])
        city_v = float(xv[city_pm25_idx])
        cv = station_v if station_v > 0.0 else (city_v if city_v > 0.0 else 0.0)
        
        pred[(int(u), int(v))] = max(0.0, (cu + cv) / 2.0)
        
    return pred
