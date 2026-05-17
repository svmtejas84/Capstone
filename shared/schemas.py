from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class GrasterState(BaseModel):
	concentration: list[list[float]]
	wind_u: list[list[float]]
	wind_v: list[list[float]]
	source_spike: list[list[float]]
	timestamp: datetime


class RouteRequest(BaseModel):
	origin: tuple[float, float]
	destination: tuple[float, float]
	mode: Literal["jogger", "cyclist", "two_wheeler", "car"]


class RouteScoreExplanation(BaseModel):
	base_score: float
	dose_contribution: float
	distance_contribution: float
	final_score: float


class NeuralModelExplanation(BaseModel):
	available: bool
	method: str
	target: str
	feature_attributions: dict[str, float] = Field(default_factory=dict)
	reason: str | None = None


class RouteExplanation(BaseModel):
	route_score: RouteScoreExplanation
	neural_model: NeuralModelExplanation | None = None


class RouteCandidate(BaseModel):
	id: str
	route: list[tuple[float, float]]
	node_ids: list[int]
	distance_m: float
	travel_time_s: float
	mean_concentration_ug_m3: float
	dose_ug: float
	preference_rank: int
	recommended: bool
	explanation: RouteExplanation


class RouteResponse(BaseModel):
	route: list[tuple[float, float]]
	total_cost_w: float
	stake_hash: str
	stable_corridor_id: str
	candidates: list[RouteCandidate] = Field(default_factory=list)


class AuditRecord(BaseModel):
	route: list[tuple[float, float]]
	env_seed: str
	timestamp: datetime
