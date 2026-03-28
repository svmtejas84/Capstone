from __future__ import annotations

from fastapi import APIRouter

from matcher.commuter_model import Commuter, build_preference_list as build_commuter_preferences
from gnn.wake_predictor import predict_wake_polygon
from matcher.gale_shapley import batch_match
from matcher.quota_manager import quotas_from_route_cedge
from matcher.route_pool import build_route_metrics, candidate_corridors
from matcher.segment_model import Segment, build_preference_list as build_segment_preferences
from ingestion.data_fusion import fuse_weather_and_airquality
from ingestion.redis_publisher import get_latest_airquality, get_latest_sensors, get_latest_weather
from router.api.dependencies import env_seed_from_state, latest_edge_weight_values, redis_store
from router.edge_cost import compute_path_cost
from router.stake_audit import create_audit, verify_audit
from shared.config import get_settings
from shared.schemas import RouteRequest, RouteResponse

router = APIRouter()


def _id_min_for_mode(mode: str) -> float:
	if mode == "jogger":
		return 1.8
	if mode == "cyclist":
		return 2.4
	return 3.0


def _build_batch_commuters(requester: Commuter) -> list[Commuter]:
	"""Build a deterministic cohort to emulate concurrent demand pressure."""
	cohort: list[Commuter] = [requester]
	modes = ["jogger", "cyclist", "car", "cyclist", "car", "jogger", "car", "cyclist", "jogger"]
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


def _stream_backed_state() -> dict[str, object]:
	store = redis_store()
	settings = get_settings()
	weather = get_latest_weather(store)
	airquality = get_latest_airquality(store)
	sensors = get_latest_sensors(store)
	return fuse_weather_and_airquality(weather, airquality, sensors, settings)


@router.get("/health")
def health() -> dict[str, str]:
	return {"status": "ok"}


@router.get("/plume")
def plume() -> dict[str, object]:
	state = _stream_backed_state()
	return {
		"grid": state["concentration"],
		"wind_u": state["wind_u"],
		"wind_v": state["wind_v"],
		"timestamp": state["timestamp"],
		"wake": predict_wake_polygon(),
	}


@router.post("/route", response_model=RouteResponse)
def route(req: RouteRequest) -> RouteResponse:
	route_line = [req.origin, ((req.origin[0] + req.destination[0]) / 2, (req.origin[1] + req.destination[1]) / 2), req.destination]
	edge_values = latest_edge_weight_values()
	if len(edge_values) > 2:
		edge_values = edge_values[:2]
	total_cost = compute_path_cost(edge_values, req.mode)

	corridors = candidate_corridors()
	route_metrics = build_route_metrics(corridors, edge_values=edge_values)
	route_cedge = {rid: route_metrics[rid]["cedge_mean"] for rid in corridors}
	route_distance_m = {rid: route_metrics[rid]["distance_m"] for rid in corridors}

	requester = Commuter(id="requester", mode=req.mode, id_min=2.0, distance_tolerance_m=8000.0)
	all_commuters = _build_batch_commuters(requester)
	commuter_preferences = {
		c.id: build_commuter_preferences(
			c,
			corridors,
			route_dose=route_cedge,
			route_distance_m=route_distance_m,
		)
		for c in all_commuters
	}

	segment_capacities = quotas_from_route_cedge(route_cedge, scale=24.0, min_quota=2, max_quota=6)
	segment_preferences = {
		rid: build_segment_preferences(
			Segment(id=rid, cedge_mean=route_cedge[rid], capacity=segment_capacities[rid]),
			all_commuters,
		)
		for rid in corridors
	}

	allocation = batch_match(
		[c.id for c in all_commuters],
		corridors,
		commuter_preferences=commuter_preferences,
		segment_preferences=segment_preferences,
		segment_capacities=segment_capacities,
		route_distances={c.id: route_distance_m for c in all_commuters},
		max_iterations=len(corridors) * len(all_commuters),
	)
	corridor_id = allocation["requester"]

	state = _stream_backed_state()
	env_seed = env_seed_from_state(state)
	stake_hash, _ = create_audit(route_line, env_seed=env_seed, store=redis_store())
	return RouteResponse(
		route=route_line,
		total_cost_w=round(total_cost, 6),
		stake_hash=stake_hash,
		stable_corridor_id=corridor_id,
	)


@router.get("/audit/{stake_hash}")
def audit(stake_hash: str) -> dict[str, object]:
	return verify_audit(stake_hash, store=redis_store())

