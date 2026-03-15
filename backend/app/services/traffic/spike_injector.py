import numpy as np


def inject_traffic_spike(grid: np.ndarray, x: int, y: int, intensity: float) -> np.ndarray:
    out = grid.copy()
    if 0 <= y < out.shape[0] and 0 <= x < out.shape[1]:
        out[y, x] += intensity
    return out
