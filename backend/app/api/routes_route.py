from fastapi import APIRouter

from app.models.schemas import RouteRequest, RouteResponse
from app.services.routing.router import score_route
from app.services.audit.stake import build_route_stake

router = APIRouter()


@router.post("/recommend", response_model=RouteResponse)
def recommend_route(request: RouteRequest) -> RouteResponse:
    weight, eta = score_route(request.mode)
    route_id = build_route_stake(request.mode, weight)
    return RouteResponse(
        route_id=route_id,
        total_weight=weight,
        eta_seconds=eta,
        note="Prototype response using mode-specific weighting.",
    )
