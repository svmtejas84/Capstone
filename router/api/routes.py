from __future__ import annotations

import networkx as nx
import os
from fastapi import APIRouter
from pyproj import Transformer

from gnn.edge_weights import update_graph_toxicity_from_streams
from gnn.persistence_baseline import predict_route_edge_concentrations_persistence
from gnn.stpignn_explain import explain_route_edges_with_stpignn
from gnn.stpignn_inference import predict_route_edge_concentrations
from gnn.wake_predictor import predict_wake_polygon
from matcher.commuter_model import MODE_ALPHA, Commuter, build_preference_list as build_commuter_preferences
from matcher.gale_shapley import batch_match
from matcher.quota_manager import quotas_from_route_cedge
from matcher.segment_model import Segment, build_preference_list as build_segment_preferences
from router.api.dependencies import env_seed_from_state, redis_store
from router.edge_cost import compute_edge_weight, compute_path_cost
from router.stake_audit import create_audit, verify_audit
from shared.schemas import NeuralModelExplanation, RouteCandidate, RouteExplanation, RouteRequest, RouteResponse, RouteScoreExplanation
from router.prediction_scaler import ScalerStore

router = APIRouter()
_WGS84_TO_UTM43 = Transformer.from_crs("EPSG:4326", "EPSG:32643", always_xy=True)
_UTM43_TO_WGS84 = Transformer.from_crs("EPSG:32643", "EPSG:4326", always_xy=True)


def _id_min_for_mode(mode: str) -> float:
	if mode == "jogger":
		return 1.8
	if mode == "cyclist":
		return 2.4
	if mode == "two_wheeler":
		return 3.0
	if mode == "car":  # legacy alias
		return 3.0
	return 3.0


def _build_batch_commuters(requester: Commuter) -> list[Commuter]:
	cohort: list[Commuter] = [requester]
	modes = ["jogger", "cyclist", "two_wheeler", "cyclist", "two_wheeler", "jogger", "car", "cyclist", "jogger"]
	for idx, mode in enumerate(modes, start=1):
		cohort.append(
			Commuter(
				id=f"sim_{idx}",
				mode=mode,
				id_min=_id_min_for_mode(mode),
				distance_tolerance_m=6800.0 + idx * 350.0,
			)
		)
	return cohort


def _nearest_node(graph: nx.MultiDiGraph, lat: float, lon: float) -> int:
	x, y = _WGS84_TO_UTM43.transform(lon, lat)
	best = None
	best_d2 = float("inf")
	for nid, attrs in graph.nodes(data=True):
		nxv = float(attrs.get("x", 0.0))
		nyv = float(attrs.get("y", 0.0))
		d2 = (nxv - x) ** 2 + (nyv - y) ** 2
		if d2 < best_d2:
			best_d2 = d2
			best = int(nid)
	return int(best)


def _heuristic(graph: nx.MultiDiGraph, a: int, b: int) -> float:
	ax = float(graph.nodes[a].get("x", 0.0))
	ay = float(graph.nodes[a].get("y", 0.0))
	bx = float(graph.nodes[b].get("x", 0.0))
	by = float(graph.nodes[b].get("y", 0.0))
	return ((ax - bx) ** 2 + (ay - by) ** 2) ** 0.5


def _tox_weight(graph: nx.MultiDiGraph, u: int, v: int) -> float:
	edge_data = graph.get_edge_data(u, v, default={})
	if isinstance(edge_data, dict):
		attrs0 = edge_data.get(0)
		if isinstance(attrs0, dict):
			return float(attrs0.get("toxicity", 0.5))
		for attrs in edge_data.values():
			if isinstance(attrs, dict):
				return float(attrs.get("toxicity", 0.5))
	return 0.5


def _speed_mps_for_mode(mode: str) -> float:
	if mode == "jogger":
		return 1.4
	if mode == "cyclist":
		return 6.0
	if mode == "two_wheeler":
		return 15.0
	if mode == "car":
		return 15.0
	return 1.4


def _first_edge_attrs(graph: nx.MultiDiGraph, u: int, v: int) -> dict[str, object]:
	edge_data = graph.get_edge_data(u, v, default={})
	if isinstance(edge_data, dict):
		attrs0 = edge_data.get(0)
		if isinstance(attrs0, dict):
			return attrs0
		for attrs in edge_data.values():
			if isinstance(attrs, dict):
				return attrs
	return {}


def _edge_length_m(attrs: dict[str, object]) -> float:
	return max(1.0, float(attrs.get("length", attrs.get("length_m", 1.0))))


def _edge_travel_time_s(attrs: dict[str, object], mode: str) -> float:
	speed_mps = _speed_mps_for_mode(mode)
	return _edge_length_m(attrs) / max(0.1, speed_mps)


def _edge_dose_weight(graph: nx.MultiDiGraph, u: int, v: int, mode: str, tox_val: float | None = None) -> float:
	attrs = _first_edge_attrs(graph, u, v)
	concentration = tox_val if tox_val is not None else float(attrs.get("toxicity", 0.5))
	travel_time_s = _edge_travel_time_s(attrs, mode)
	return compute_edge_weight(concentration_ug_m3=concentration, travel_time_s=travel_time_s, mode=mode)


def _path_edges(path: list[int]) -> list[tuple[int, int]]:
	return [(path[i], path[i + 1]) for i in range(len(path) - 1)]


def _route_model_concentrations(route_edges: dict[str, list[tuple[int, int]]]) -> dict[tuple[int, int], float]:
	model_name = os.environ.get("TOXICITY_ROUTE_MODEL", "persistence").lower()
	all_edges: list[tuple[int, int]] = []
	for edges in route_edges.values():
		all_edges.extend(edges)
	try:
		if model_name == "stpignn":
			return predict_route_edge_concentrations(all_edges)
		if model_name == "stream":
			return {}
		return predict_route_edge_concentrations_persistence(all_edges)
	except Exception:
		if model_name == "stpignn":
			try:
				return predict_route_edge_concentrations_persistence(all_edges)
			except Exception:
				return {}
		return {}


def _include_neural_explanation() -> bool:
	return os.environ.get("TOXICITY_INCLUDE_NEURAL_EXPLANATION", "0").lower() in {"1", "true", "yes"}


def _path_to_latlon(graph: nx.MultiDiGraph, path: list[int]) -> list[tuple[float, float]]:
	coords: list[tuple[float, float]] = []
	for nid in path:
		x = float(graph.nodes[nid].get("x", 0.0))
		y = float(graph.nodes[nid].get("y", 0.0))
		lon, lat = _UTM43_TO_WGS84.transform(x, y)
		coords.append((float(lat), float(lon)))
	return coords


def _candidate_paths(
	graph: nx.MultiDiGraph,
	source: int,
	target: int,
	mode: str,
	k: int = 3,
	tox_preds: dict[tuple[int, int], float] | None = None,
) -> list[list[int]]:
	if tox_preds is None:
		tox_preds = {}
	digraph = nx.DiGraph()
	for u, v, _k, _data in graph.edges(keys=True, data=True):
		tox_val = tox_preds.get((int(u), int(v)))
		w = _edge_dose_weight(graph, int(u), int(v), mode, tox_val=tox_val)
		if not digraph.has_edge(int(u), int(v)) or w < float(digraph[int(u)][int(v)]["dose"]):
			digraph.add_edge(int(u), int(v), dose=w)

	paths: list[list[int]] = []
	try:
		base = nx.astar_path(
			digraph,
			source,
			target,
			heuristic=lambda a, b: _heuristic(graph, a, b),
			weight="dose",
		)
		paths.append(base)
	except nx.NetworkXNoPath:
		return []

	try:
		for p in nx.shortest_simple_paths(digraph, source, target, weight="dose"):
			if p not in paths:
				paths.append(p)
			if len(paths) >= k:
				break
	except (nx.NetworkXNoPath, nx.NodeNotFound):
		pass

	return paths


def _route_score_explanations(
	route_ids: list[str],
	route_dose: dict[str, float],
	route_distance_m: dict[str, float],
	mode: str,
	distance_tolerance_m: float,
) -> dict[str, RouteScoreExplanation]:
	"""Explain the same dose/distance preference score used for route ranking.

	The terms are additive around the mean candidate route. They are SHAP-style
	attributions for this linear route score, not model-internal neural SHAP.
	"""
	if not route_ids:
		return {}

	alpha = MODE_ALPHA.get(mode, 0.5)
	finite_doses = [
		max(0.0, route_dose.get(rid, float("inf")))
		for rid in route_ids
		if route_dose.get(rid, float("inf")) != float("inf")
	]
	max_dose = max(finite_doses) if finite_doses else 1.0
	if max_dose <= 0.0:
		max_dose = 1.0

	norm_dose = {rid: route_dose.get(rid, float("inf")) / max_dose for rid in route_ids}
	distance_ratio = {rid: route_distance_m.get(rid, float("inf")) / distance_tolerance_m for rid in route_ids}
	mean_norm_dose = sum(norm_dose.values()) / len(route_ids)
	mean_distance_ratio = sum(distance_ratio.values()) / len(route_ids)
	base_score = alpha * mean_norm_dose + (1.0 - alpha) * mean_distance_ratio

	explanations: dict[str, RouteScoreExplanation] = {}
	for rid in route_ids:
		dose_contribution = alpha * (norm_dose[rid] - mean_norm_dose)
		distance_contribution = (1.0 - alpha) * (distance_ratio[rid] - mean_distance_ratio)
		explanations[rid] = RouteScoreExplanation(
			base_score=round(float(base_score), 9),
			dose_contribution=round(float(dose_contribution), 9),
			distance_contribution=round(float(distance_contribution), 9),
			final_score=round(float(base_score + dose_contribution + distance_contribution), 9),
		)
	return explanations


@router.get("/health")
def health() -> dict[str, str]:
	return {"status": "ok"}


@router.get("/plume")
def plume() -> dict[str, object]:
	graph = update_graph_toxicity_from_streams(redis_store())
	edges = []
	for u, v, k, attrs in graph.edges(keys=True, data=True):
		x1 = float(graph.nodes[u].get("x", 0.0))
		y1 = float(graph.nodes[u].get("y", 0.0))
		x2 = float(graph.nodes[v].get("x", 0.0))
		y2 = float(graph.nodes[v].get("y", 0.0))
		mx = (x1 + x2) / 2.0
		my = (y1 + y2) / 2.0
		lon, lat = _UTM43_TO_WGS84.transform(mx, my)
		edges.append({"u": int(u), "v": int(v), "k": int(k), "lat": float(lat), "lon": float(lon), "toxicity": float(attrs.get("toxicity", 0.0))})

	return {
		"edges": edges,
		"timestamp": "live",
		"wake": predict_wake_polygon(),
	}


@router.get("/_debug_scaler")
def debug_scaler() -> dict[str, object]:
	try:
		vals = {k: {"a": v.a, "b": v.b, "version": v.version, "last_updated": v.last_updated} for k, v in (_scaler_store._cache.items() if _scaler_store is not None else {})}
	except Exception:
		vals = {}
	return {"scaler_cache": vals}


@router.post("/route", response_model=RouteResponse)
def route(req: RouteRequest) -> RouteResponse:
	graph = update_graph_toxicity_from_streams(redis_store())

	# Initialize scaler store lazily to avoid import-time Redis connection
	global _scaler_store
	try:
		_scaler_store
	except NameError:
		_scaler_store = None
	if _scaler_store is None:
		try:
			_store = redis_store()
			_scaler_store = ScalerStore(redis_client=_store.client if _store is not None else None)
			_scaler_store.refresh_from_redis()
		except Exception:
			_scaler_store = ScalerStore()
	source = _nearest_node(graph, req.origin[0], req.origin[1])
	target = _nearest_node(graph, req.destination[0], req.destination[1])

	# Predict concentrations for all edges in the graph for the ST-PIGNN model
	all_edges = list(graph.edges())
	tox_preds = {}
	model_name = os.environ.get("TOXICITY_ROUTE_MODEL", "persistence").lower()
	if model_name == "stpignn":
		try:
			tox_preds = predict_route_edge_concentrations(all_edges)
		except Exception:
			# Fallback to persistence if ST-PIGNN fails
			tox_preds = predict_route_edge_concentrations_persistence(all_edges)
	elif model_name != "stream":
		tox_preds = predict_route_edge_concentrations_persistence(all_edges)


	candidate_paths = _candidate_paths(graph, source, target, mode=req.mode, k=3, tox_preds=tox_preds)
	candidates: list[RouteCandidate] = []
	if not candidate_paths:
		route_line = [req.origin, req.destination]
		total_cost = 0.0
		corridor_id = "route_0"
	else:
		route_ids = [f"route_{i}" for i in range(len(candidate_paths))]
		route_edges = {rid: _path_edges(path) for rid, path in zip(route_ids, candidate_paths, strict=False)}
		
		# The concentrations are already predicted. Apply post-prediction scaling (per-edge/zone) if available.
		route_model_concentrations: dict[tuple[int, int], float] = {}
		# Refresh scaler parameters from Redis so runtime updates take effect.
		try:
			if _scaler_store is not None:
				_scaler_store.refresh_from_redis()
		except Exception:
			pass

		for rid in route_ids:
			for edge in route_edges[rid]:
				raw = tox_preds.get(edge, 0.0)
				zone_id = f"{edge[0]}_{edge[1]}"
				try:
					scaled = _scaler_store.apply(zone_id, raw) if _scaler_store is not None else raw
				except Exception:
					scaled = raw
				route_model_concentrations[edge] = float(scaled)

		route_dose: dict[str, float] = {}
		route_distance_m: dict[str, float] = {}
		for rid, edges in route_edges.items():
			tox_vals = []
			edge_times_s = []
			dist_m = 0.0
			for u, v in edges:
				attrs = _first_edge_attrs(graph, u, v)
				tox_vals.append(float(route_model_concentrations.get((u, v), attrs.get("toxicity", 0.0))))
				edge_times_s.append(_edge_travel_time_s(attrs, req.mode))
				dist_m += _edge_length_m(attrs)
			route_dose[rid] = float(compute_path_cost(tox_vals, req.mode, edge_times_s=edge_times_s))
			route_distance_m[rid] = float(dist_m)

		requester = Commuter(id="requester", mode=req.mode, id_min=2.0, distance_tolerance_m=8000.0)
		all_commuters = _build_batch_commuters(requester)
		commuter_preferences = {
			c.id: build_commuter_preferences(c, route_ids, route_dose=route_dose, route_distance_m=route_distance_m)
			for c in all_commuters
		}
		segment_capacities = quotas_from_route_cedge(route_dose, scale=24.0, min_quota=2, max_quota=6)
		segment_preferences = {
			rid: build_segment_preferences(
				Segment(id=rid, cedge_mean=route_dose[rid], capacity=segment_capacities[rid]),
				all_commuters,
			)
			for rid in route_ids
		}

		allocation = batch_match(
			[c.id for c in all_commuters],
			route_ids,
			commuter_preferences=commuter_preferences,
			segment_preferences=segment_preferences,
			segment_capacities=segment_capacities,
			route_distances={c.id: route_distance_m for c in all_commuters},
			max_iterations=len(route_ids) * len(all_commuters),
		)
		corridor_id = allocation["requester"]
		chosen_path = candidate_paths[int(corridor_id.split("_")[-1])]
		route_line = _path_to_latlon(graph, chosen_path)
		total_cost = route_dose[corridor_id]
		explanations = _route_score_explanations(
			route_ids,
			route_dose=route_dose,
			route_distance_m=route_distance_m,
			mode=req.mode,
			distance_tolerance_m=requester.distance_tolerance_m,
		)
		neural_explanations: dict[str, NeuralModelExplanation] = {}
		if _include_neural_explanation():
			for rid, edges in route_edges.items():
				neural = explain_route_edges_with_stpignn(edges)
				neural_explanations[rid] = NeuralModelExplanation(
					available=neural.available,
					method=neural.method,
					target=neural.target,
					feature_attributions=neural.feature_attributions,
					reason=neural.reason,
				)
		for rid, path in zip(route_ids, candidate_paths, strict=False):
			edges = route_edges[rid]
			total_time_s = 0.0
			weighted_concentration = 0.0
			for u, v in edges:
				attrs = _first_edge_attrs(graph, u, v)
				length_m = _edge_length_m(attrs)
				concentration = float(route_model_concentrations.get((u, v), attrs.get("toxicity", 0.0)))
				total_time_s += _edge_travel_time_s(attrs, req.mode)
				weighted_concentration += concentration * length_m
			distance_m = route_distance_m[rid]
			mean_concentration = weighted_concentration / distance_m if distance_m > 0.0 else 0.0
			candidates.append(
				RouteCandidate(
					id=rid,
					route=_path_to_latlon(graph, path),
					node_ids=[int(node_id) for node_id in path],
					distance_m=round(distance_m, 3),
					travel_time_s=round(total_time_s, 3),
					mean_concentration_ug_m3=round(mean_concentration, 6),
					dose_ug=round(route_dose[rid], 6),
					preference_rank=commuter_preferences["requester"].index(rid) + 1,
					recommended=rid == corridor_id,
					explanation=RouteExplanation(
						route_score=explanations[rid],
						neural_model=neural_explanations.get(rid),
					),
				)
			)

	state = {
		"timestamp": "live",
		"edges": [
			{"toxicity": float(data.get("toxicity", 0.0))}
			for _u, _v, _k, data in graph.edges(keys=True, data=True)
		],
	}
	env_seed = env_seed_from_state(state)
	# include scaler cache versions in audit metadata for reproducibility
	meta = {}
	try:
		if _scaler_store is not None:
			meta = {"scaler_versions": {k: getattr(v, "version", None) for k, v in _scaler_store._cache.items()}}
	except Exception:
		meta = {}

	stake_hash, _ = create_audit(route_line, env_seed=env_seed, store=redis_store(), meta=meta)
	return RouteResponse(
		route=route_line,
		total_cost_w=round(total_cost, 6),
		stake_hash=stake_hash,
		stable_corridor_id=corridor_id,
		candidates=sorted(candidates, key=lambda candidate: candidate.preference_rank),
	)


@router.get("/audit/{stake_hash}")
def audit(stake_hash: str) -> dict[str, object]:
	return verify_audit(stake_hash, store=redis_store())
