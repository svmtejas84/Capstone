from __future__ import annotations

from datetime import datetime
from functools import lru_cache
from pathlib import Path

import pandas as pd
import torch

from gnn.checkpoint import load_stpignn_checkpoint

TARGET_SCALE = 342.9356
TARGET_PM25_MAX = 120.0
DEFAULT_GRAPH_PATH = Path("data/processed/graph/topology_graph_pyg_inference.pt")
DEFAULT_NODE_MAP_PATH = Path("data/processed/graph/topology_nodeid_to_index_map.parquet")
DEFAULT_TEMPORAL_FEATURES_PATH = Path("data/processed/model_input/model_input_node_hourly_features.parquet")
DEFAULT_CHECKPOINT_PATH = Path("citywide_stpignn_best.pt")
# This is the evaluated checkpoint loaded by
# notebooks/production/evaluated_wind_advection.ipynb.
EVALUATED_WIND_ADVECTION_NOTEBOOK = Path("notebooks/production/evaluated_wind_advection.ipynb")
FEATURE_COLUMNS = [
	"station_pm10",
	"station_pm25",
	"station_no2",
	"station_so2",
	"station_co",
	"weather_wind_speed_10m",
	"weather_wind_direction_10m",
	"weather_wind_gusts_10m",
	"weather_temperature_2m",
	"weather_relative_humidity_2m",
	"weather_surface_pressure",
	"city_nitrogen_dioxide",
	"city_sulphur_dioxide",
	"city_pm2_5",
	"city_pm10",
	"city_carbon_monoxide",
]

_TEMPORAL_GLOBAL_COLUMNS = [
	"weather_wind_speed_10m",
	"weather_wind_direction_10m",
	"weather_wind_gusts_10m",
	"weather_temperature_2m",
	"weather_relative_humidity_2m",
	"weather_surface_pressure",
	"city_nitrogen_dioxide",
	"city_sulphur_dioxide",
	"city_pm2_5",
	"city_pm10",
	"city_carbon_monoxide",
]


@lru_cache(maxsize=1)
def _load_static_artifacts(
	graph_path: str = str(DEFAULT_GRAPH_PATH),
	node_map_path: str = str(DEFAULT_NODE_MAP_PATH),
	checkpoint_path: str = str(DEFAULT_CHECKPOINT_PATH),
) -> tuple[torch.nn.Module, object, dict[int, int]]:
	import pandas as pd

	model, _info = load_stpignn_checkpoint(checkpoint_path, device="cpu", eval_mode=True)
	graph = torch.load(graph_path, map_location="cpu", weights_only=False)
	node_map = pd.read_parquet(node_map_path)
	node_to_index = {
		int(node_id): int(node_index)
		for node_id, node_index in zip(node_map["node_id"].values, node_map["node_index"].values, strict=False)
	}
	return model, graph, node_to_index


@lru_cache(maxsize=1)
def _load_node_id_map(node_map_path: str = str(DEFAULT_NODE_MAP_PATH)) -> dict[int, int]:
	node_map = pd.read_parquet(node_map_path)
	return {
		int(node_index): int(node_id)
		for node_id, node_index in zip(node_map["node_id"].values, node_map["node_index"].values, strict=False)
	}


@lru_cache(maxsize=1)
def _load_temporal_feature_frame(
	features_path: str = str(DEFAULT_TEMPORAL_FEATURES_PATH),
) -> pd.DataFrame:
	df = pd.read_parquet(features_path, columns=["node_id", "timestamp", *FEATURE_COLUMNS])
	if "node_id" not in df.columns or "timestamp" not in df.columns:
		raise ValueError("temporal feature source must contain node_id and timestamp columns")
	df = df.copy()
	df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.floor("h")
	return df


def _normalize_departure_time(departure_time: datetime | None) -> pd.Timestamp | None:
	if departure_time is None:
		return None
	timestamp = pd.Timestamp(departure_time)
	if timestamp.tzinfo is not None:
		timestamp = timestamp.tz_convert(None)
	return timestamp.floor("h")


def _resolve_temporal_window(
	available_timestamps: pd.Index,
	departure_time: datetime | None,
	window: int,
) -> list[pd.Timestamp]:
	if available_timestamps.empty:
		return []
	ordered = pd.Index(pd.to_datetime(available_timestamps).sort_values().unique())
	anchor = _normalize_departure_time(departure_time)
	if anchor is None:
		anchor = pd.Timestamp(ordered[-1])
	else:
		position = ordered.searchsorted(anchor, side="right") - 1
		if position < 0:
			position = 0
		anchor = pd.Timestamp(ordered[position])
	end_position = ordered.searchsorted(anchor, side="right") - 1
	start_position = max(0, end_position - max(1, window) + 1)
	return [pd.Timestamp(ts) for ts in ordered[start_position : end_position + 1]]


def _build_temporal_x_seq(
	graph: object,
	nodes: torch.Tensor,
	departure_time: datetime | None,
	window: int,
) -> torch.Tensor:
	temporal_df = _load_temporal_feature_frame()
	available_timestamps = pd.Index(temporal_df["timestamp"].unique())
	selected_timestamps = _resolve_temporal_window(available_timestamps, departure_time, window)
	if not selected_timestamps:
		raise ValueError("no temporal timestamps are available for ST-PIGNN inference")

	index_to_node_id = _load_node_id_map()
	node_ids = [index_to_node_id.get(int(node_index)) for node_index in nodes.tolist()]
	if any(node_id is None for node_id in node_ids):
		raise ValueError("route-local node map is incomplete for temporal inference")
	node_ids = [int(node_id) for node_id in node_ids if node_id is not None]

	static_x = graph.x[nodes, : len(FEATURE_COLUMNS)].float()
	steps: list[torch.Tensor] = []
	global_column_indices = [FEATURE_COLUMNS.index(column) for column in _TEMPORAL_GLOBAL_COLUMNS]
	for timestamp in selected_timestamps:
		frame = temporal_df[temporal_df["timestamp"] == timestamp].set_index("node_id")
		step_df = frame.reindex(node_ids)[FEATURE_COLUMNS]
		step_df = step_df.apply(pd.to_numeric, errors="coerce")
		step_x = static_x.clone()

		if not frame.empty:
			global_row = frame[_TEMPORAL_GLOBAL_COLUMNS].mean(axis=0, skipna=True)
			global_values = torch.tensor(global_row.to_numpy(), dtype=static_x.dtype)
			step_x[:, global_column_indices] = global_values

		step_values = torch.tensor(step_df.to_numpy(), dtype=static_x.dtype)
		covered_mask = ~torch.isnan(step_values).any(dim=1)
		if int(covered_mask.sum().item()) > 0:
			covered_rows = torch.nonzero(covered_mask, as_tuple=True)[0]
			step_x[covered_rows] = torch.where(
				torch.isnan(step_values[covered_rows]),
				step_x[covered_rows],
				step_values[covered_rows],
			)
		steps.append(step_x)

	return torch.stack(steps, dim=0).unsqueeze(0)


def _route_subgraph(
	graph: object,
	node_indices: set[int],
	max_extra_neighbors: int = 256,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, dict[int, int]]:
	edge_index = graph.edge_index.cpu()
	edge_attr = graph.edge_attr.cpu().float()
	selected = set(node_indices)

	if max_extra_neighbors > 0:
		touching = torch.isin(edge_index[0], torch.tensor(sorted(selected), dtype=torch.long)) | torch.isin(
			edge_index[1], torch.tensor(sorted(selected), dtype=torch.long)
		)
		extra = torch.unique(edge_index[:, touching]).tolist()
		for node in extra[:max_extra_neighbors]:
			selected.add(int(node))

	nodes = torch.tensor(sorted(selected), dtype=torch.long)
	local = {int(node): idx for idx, node in enumerate(nodes.tolist())}
	keep = torch.isin(edge_index[0], nodes) & torch.isin(edge_index[1], nodes)
	sub_edges_global = edge_index[:, keep]
	sub_edge_attr = edge_attr[keep]
	if sub_edges_global.numel() == 0:
		raise ValueError("Route-local ST-PIGNN subgraph has no edges")
	sub_edge_index = torch.tensor(
		[[local[int(value)] for value in row.tolist()] for row in sub_edges_global],
		dtype=torch.long,
	)
	return nodes, sub_edge_index, sub_edge_attr, local


def predict_route_edge_concentrations(
	route_edges: list[tuple[int, int]],
	window: int = 12,
	departure_time: datetime | None = None,
) -> dict[tuple[int, int], float]:
	"""Predict unscaled PM2.5-like concentrations for route edges with the trained ST-PIGNN."""
	if not route_edges:
		return {}

	model, graph, node_to_index = _load_static_artifacts()
	route_node_indices: set[int] = set()
	edge_index_pairs: dict[tuple[int, int], tuple[int, int]] = {}
	for u, v in route_edges:
		if int(u) not in node_to_index or int(v) not in node_to_index:
			continue
		gu = node_to_index[int(u)]
		gv = node_to_index[int(v)]
		route_node_indices.add(gu)
		route_node_indices.add(gv)
		edge_index_pairs[(int(u), int(v))] = (gu, gv)

	if not route_node_indices:
		return {}

	nodes, sub_edge_index, sub_edge_attr, local = _route_subgraph(graph, route_node_indices)
	try:
		x_seq = _build_temporal_x_seq(graph, nodes, departure_time=departure_time, window=window)
	except Exception:
		x_static = graph.x[nodes, : len(FEATURE_COLUMNS)].float()
		x_seq = x_static.unsqueeze(0).repeat(window, 1, 1).unsqueeze(0)

	with torch.no_grad():
		pred_scaled = model(x_seq=x_seq, edge_index=sub_edge_index, edge_attr=sub_edge_attr)[0].cpu()

	pred: dict[tuple[int, int], float] = {}
	for edge, (gu, gv) in edge_index_pairs.items():
		if gu in local and gv in local:
			edge_scaled = float((pred_scaled[local[gu]] + pred_scaled[local[gv]]) / 2.0)
			pred[edge] = max(0.0, min(edge_scaled * TARGET_SCALE, TARGET_PM25_MAX))
	return pred
