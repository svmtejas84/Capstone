from pydantic import BaseModel, Field


class RouteRequest(BaseModel):
    origin_lat: float
    origin_lon: float
    destination_lat: float
    destination_lon: float
    mode: str = Field(description="jogger|cyclist|car")


class RouteResponse(BaseModel):
    route_id: str
    total_weight: float
    eta_seconds: int
    note: str
