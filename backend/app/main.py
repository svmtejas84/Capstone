from fastapi import FastAPI

from app.api.routes_health import router as health_router
from app.api.routes_route import router as route_router
from app.api.routes_demo import router as demo_router

app = FastAPI(
    title="Urban Toxicity Orchestrator API",
    version="0.1.0",
    description="Phase-1 backend for live toxicity-aware routing.",
)

app.include_router(health_router, prefix="/health", tags=["health"])
app.include_router(route_router, prefix="/route", tags=["route"])
app.include_router(demo_router, prefix="/demo", tags=["demo"])
