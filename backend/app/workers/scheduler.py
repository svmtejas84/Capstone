import time

from app.services.ingestion.gee_ingestor import build_mock_grid
from app.services.nowcast.advection import advect_grid
from app.services.state.redis_streams import publish_grid_snapshot


def run_once() -> str:
    grid = build_mock_grid()
    grid = advect_grid(grid, u=1.0, v=0.0)
    payload = {
        "timestamp": int(time.time()),
        "shape": list(grid.shape),
        "mean": float(grid.mean()),
        "max": float(grid.max()),
    }
    return publish_grid_snapshot("physics.grid", payload)
