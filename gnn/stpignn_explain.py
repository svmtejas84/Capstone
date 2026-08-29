from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache

import torch
import torch.nn as nn

from gnn.stpignn_inference import _build_temporal_x_seq, _load_static_artifacts, _route_subgraph


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
class STPIGNNIntegratedGradientsExplanation:
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
		return pred.mean(dim=1)


def explain_route_edges_with_integrated_gradients(
	route_edges: list[tuple[int, int]],
	*,
	window: int = 12,
	max_route_nodes: int = 32,
	top_k: int = 8,
	departure_time: datetime | None = None,
) -> STPIGNNIntegratedGradientsExplanation:
	"""Explain route-local ST-PIGNN predictions with Captum Integrated Gradients.

	This mirrors the evaluated wind-advection notebook: a zero baseline,
	25 integration steps, and sequential internal batches to bound memory use.
	"""
	if not route_edges:
		return STPIGNNIntegratedGradientsExplanation(
			available=False,
			method="captum.integrated_gradients",
			target="route_mean_stpignn_prediction",
			feature_attributions={},
			reason="route has no edges",
		)

	try:
		from captum.attr import IntegratedGradients

		model, graph, node_to_index = _load_static_artifacts()
	except Exception as exc:
		return STPIGNNIntegratedGradientsExplanation(
			available=False,
			method="captum.integrated_gradients",
			target="route_mean_stpignn_prediction",
			feature_attributions={},
			reason=f"Integrated Gradients unavailable: {type(exc).__name__}: {exc}",
		)

	route_node_indices: set[int] = set()
	for u, v in route_edges:
		if int(u) in node_to_index and int(v) in node_to_index:
			route_node_indices.add(node_to_index[int(u)])
			route_node_indices.add(node_to_index[int(v)])

	if not route_node_indices:
		return STPIGNNIntegratedGradientsExplanation(
			available=False,
			method="captum.integrated_gradients",
			target="route_mean_stpignn_prediction",
			feature_attributions={},
			reason="route nodes are absent from the ST-PIGNN node map",
		)

	if len(route_node_indices) > max_route_nodes:
		route_node_indices = set(sorted(route_node_indices)[:max_route_nodes])

	try:
		nodes, sub_edge_index, sub_edge_attr, _local = _route_subgraph(graph, route_node_indices, max_extra_neighbors=0)
	except Exception as exc:
		return STPIGNNIntegratedGradientsExplanation(
			available=False,
			method="captum.integrated_gradients",
			target="route_mean_stpignn_prediction",
			feature_attributions={},
			reason=f"route-local subgraph unavailable: {type(exc).__name__}: {exc}",
		)

	model.eval()
	try:
		x_seq = _build_temporal_x_seq(graph, nodes, departure_time=departure_time, window=window)
	except Exception:
		x_static = graph.x[nodes, : len(FEATURE_NAMES)].float()
		x_seq = x_static.unsqueeze(0).repeat(window, 1, 1).unsqueeze(0)
	baseline = torch.zeros_like(x_seq)
	wrapper = _RouteMeanWrapper(model, sub_edge_index, sub_edge_attr.float())
	wrapper.eval()

	try:
		explainer = IntegratedGradients(wrapper)
		values, delta = explainer.attribute(
			x_seq,
			baselines=baseline,
			n_steps=25,
			internal_batch_size=1,
			return_convergence_delta=True,
		)
	except Exception as exc:
		return STPIGNNIntegratedGradientsExplanation(
			available=False,
			method="captum.integrated_gradients",
			target="route_mean_stpignn_prediction",
			feature_attributions={},
			reason=f"Integrated Gradients computation failed: {type(exc).__name__}: {exc}",
		)

	values_t = torch.as_tensor(values, dtype=torch.float32)
	if values_t.dim() != 4:
		return STPIGNNIntegratedGradientsExplanation(
			available=False,
			method="captum.integrated_gradients",
			target="route_mean_stpignn_prediction",
			feature_attributions={},
			reason=f"unexpected Integrated Gradients tensor shape: {tuple(values_t.shape)}",
		)

	feature_scores = values_t.abs().mean(dim=(0, 1, 2))
	ranked = sorted(
		((FEATURE_NAMES[idx], round(float(score), 9)) for idx, score in enumerate(feature_scores.tolist())),
		key=lambda item: item[1],
		reverse=True,
	)
	return STPIGNNIntegratedGradientsExplanation(
		available=True,
		method="captum.integrated_gradients",
		target="route_mean_stpignn_prediction",
		feature_attributions=dict(ranked[:top_k]),
		reason=f"mean convergence delta={float(torch.as_tensor(delta).abs().mean()):.6g}",
	)


# Compatibility alias for callers that used the previous runtime name.
explain_route_edges_with_stpignn = explain_route_edges_with_integrated_gradients
