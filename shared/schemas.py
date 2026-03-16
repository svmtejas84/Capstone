from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class GrasterState(BaseModel):
	concentration: list[list[float]]
	wind_u: list[list[float]]
	wind_v: list[list[float]]
	source_spike: list[list[float]]
	timestamp: datetime


class RouteRequest(BaseModel):
	origin: tuple[float, float]
	destination: tuple[float, float]
	mode: Literal["jogger", "cyclist", "car"]


class RouteResponse(BaseModel):
	route: list[tuple[float, float]]
	total_cost_w: float
	stake_hash: str
	stable_corridor_id: str


class AuditRecord(BaseModel):
	route: list[tuple[float, float]]
	env_seed: str
	timestamp: datetime

