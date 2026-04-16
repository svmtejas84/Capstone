import numpy as np


def advect(concentration: np.ndarray, u: np.ndarray, v: np.ndarray, dt_seconds: float = 300.0) -> np.ndarray:
	dx = 100.0
	dy = 100.0

	dcdx = np.gradient(concentration, axis=1) / dx
	dcdy = np.gradient(concentration, axis=0) / dy

	advected = concentration - dt_seconds * (u * dcdx + v * dcdy)
	return np.clip(advected, 0.0, None)

