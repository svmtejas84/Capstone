from fastapi import APIRouter

from app.services.ingestion.gee_ingestor import build_mock_grid
from app.services.nowcast.advection import advect_grid
from app.services.traffic.spike_injector import inject_traffic_spike

router = APIRouter()


@router.post("/tick")
def demo_tick() -> dict[str, float]:
    grid = build_mock_grid()
    grid = inject_traffic_spike(grid, x=10, y=10, intensity=3.0)
    grid = advect_grid(grid, u=1.2, v=0.3)
    return {
        "grid_mean": float(grid.mean()),
        "grid_max": float(grid.max()),
    }
