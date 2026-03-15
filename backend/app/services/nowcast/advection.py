import numpy as np


def advect_grid(grid: np.ndarray, u: float, v: float) -> np.ndarray:
    shift_x = int(round(u))
    shift_y = int(round(v))
    advected = np.roll(grid, shift=(shift_y, shift_x), axis=(0, 1))
    return advected
