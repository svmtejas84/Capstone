from __future__ import annotations

from fastapi import APIRouter

from gnn.wake_predictor import predict_wake_polygon
from matcher.gale_shapley import batch_match
from matcher.route_pool import candidate_corridors
from router.api.dependencies import env_seed_from_state, latest_edge_weight_values, latest_plume_state, redis_store
from router.edge_cost import compute_path_cost
from router.stake_audit import create_audit, verify_audit
from shared.schemas import RouteRequest, RouteResponse

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
	return {"status": "ok"}


@router.get("/plume")
def plume() -> dict[str, object]:
	state = latest_plume_state()
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
	allocation = batch_match(["requester"], corridors)
	corridor_id = allocation["requester"]

	state = latest_plume_state()
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

