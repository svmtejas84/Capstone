from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Any

import torch
import torch.nn as nn

from gnn.stpignn_inference import _load_static_artifacts, _route_subgraph


FEATURE_NAMES = [
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


@dataclass(frozen=True)
class STPIGNNShapExplanation:
	available: bool
	method: str
	target: str
	feature_attributions: dict[str, float]
	reason: str | None = None


class _RouteMeanWrapper(nn.Module):
	def __init__(self, model: nn.Module, edge_index: torch.Tensor, edge_attr: torch.Tensor) -> None:
		super().__init__()
		self.model = model
		self.edge_index = edge_index
		self.edge_attr = edge_attr

	def forward(self, x_seq: torch.Tensor) -> torch.Tensor:
		pred = self.model(x_seq=x_seq, edge_index=self.edge_index, edge_attr=self.edge_attr)
		return pred.mean(dim=1, keepdim=True)


@lru_cache(maxsize=1)
def _import_shap() -> Any:
	import shap

	return shap


def explain_route_edges_with_stpignn(
	route_edges: list[tuple[int, int]],
	*,
	window: int = 12,
	max_route_nodes: int = 32,
	top_k: int = 8,
) -> STPIGNNShapExplanation:
	"""Compute neural SHAP attributions for route-local ST-PIGNN inference.

	The explainer wraps the trained ST-PIGNN checkpoint with fixed route-local
	edges and explains the mean predicted concentration over route nodes with
	respect to the 16 node/time input features.
	"""
	if not route_edges:
		return STPIGNNShapExplanation(
			available=False,
			method="shap.gradient",
			target="route_mean_stpignn_prediction",
			feature_attributions={},
			reason="route has no edges",
		)

	try:
		shap = _import_shap()
		model, graph, node_to_index = _load_static_artifacts()
	except Exception as exc:
		return STPIGNNShapExplanation(
			available=False,
			method="shap.gradient",
			target="route_mean_stpignn_prediction",
			feature_attributions={},
			reason=f"ST-PIGNN SHAP dependencies unavailable: {type(exc).__name__}: {exc}",
		)

	route_node_indices: set[int] = set()
	for u, v in route_edges:
		if int(u) in node_to_index and int(v) in node_to_index:
			route_node_indices.add(node_to_index[int(u)])
			route_node_indices.add(node_to_index[int(v)])

	if not route_node_indices:
		return STPIGNNShapExplanation(
			available=False,
			method="shap.gradient",
			target="route_mean_stpignn_prediction",
			feature_attributions={},
			reason="route nodes are absent from the ST-PIGNN node map",
		)

	if len(route_node_indices) > max_route_nodes:
		route_node_indices = set(sorted(route_node_indices)[:max_route_nodes])

	try:
		nodes, sub_edge_index, sub_edge_attr, _local = _route_subgraph(graph, route_node_indices, max_extra_neighbors=0)
	except Exception as exc:
		return STPIGNNShapExplanation(
			available=False,
			method="shap.gradient",
			target="route_mean_stpignn_prediction",
			feature_attributions={},
			reason=f"route-local subgraph unavailable: {type(exc).__name__}: {exc}",
		)

	model.eval()
	x_static = graph.x[nodes, : len(FEATURE_NAMES)].float()
	x_seq = x_static.unsqueeze(0).repeat(window, 1, 1).unsqueeze(0)
	background = torch.zeros_like(x_seq)
	wrapper = _RouteMeanWrapper(model, sub_edge_index, sub_edge_attr.float())
	wrapper.eval()

	try:
		explainer = shap.GradientExplainer(wrapper, background)
		shap_values = explainer.shap_values(x_seq)
	except Exception as exc:
		return STPIGNNShapExplanation(
			available=False,
			method="shap.gradient",
			target="route_mean_stpignn_prediction",
			feature_attributions={},
			reason=f"SHAP computation failed: {type(exc).__name__}: {exc}",
		)

	values = shap_values[0] if isinstance(shap_values, list) else shap_values
	values_t = torch.as_tensor(values, dtype=torch.float32)
	if values_t.dim() == 5 and values_t.shape[-1] == 1:
		values_t = values_t.squeeze(-1)
	if values_t.dim() != 4:
		return STPIGNNShapExplanation(
			available=False,
			method="shap.gradient",
			target="route_mean_stpignn_prediction",
			feature_attributions={},
			reason=f"unexpected SHAP tensor shape: {tuple(values_t.shape)}",
		)

	feature_scores = values_t.abs().mean(dim=(0, 1, 2))
	ranked = sorted(
		((FEATURE_NAMES[idx], round(float(score), 9)) for idx, score in enumerate(feature_scores.tolist())),
		key=lambda item: item[1],
		reverse=True,
	)
	return STPIGNNShapExplanation(
		available=True,
		method="shap.gradient",
		target="route_mean_stpignn_prediction",
		feature_attributions=dict(ranked[:top_k]),
	)
