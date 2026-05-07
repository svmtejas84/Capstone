from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import torch

from gnn.checkpoint import load_stpignn_checkpoint

TARGET_SCALE = 342.9356
DEFAULT_GRAPH_PATH = Path("data/processed/graph/topology_graph_pyg_inference.pt")
DEFAULT_NODE_MAP_PATH = Path("data/processed/graph/topology_nodeid_to_index_map.parquet")
DEFAULT_CHECKPOINT_PATH = Path("citywide_stpignn_best.pt")


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
	x_static = graph.x[nodes, :16].float()
	x_seq = x_static.unsqueeze(0).repeat(window, 1, 1).unsqueeze(0)

	with torch.no_grad():
		pred_scaled = model(x_seq=x_seq, edge_index=sub_edge_index, edge_attr=sub_edge_attr)[0].cpu()

	pred: dict[tuple[int, int], float] = {}
	for edge, (gu, gv) in edge_index_pairs.items():
		if gu in local and gv in local:
			edge_scaled = float((pred_scaled[local[gu]] + pred_scaled[local[gv]]) / 2.0)
			pred[edge] = max(0.0, edge_scaled * TARGET_SCALE)
	return pred
