import numpy as np


def apply_bias_correction(no2_grid: np.ndarray, multiplier: float = 1.15, offset: float = 0.0) -> np.ndarray:
	corrected = no2_grid * multiplier + offset
	return np.clip(corrected, 0.0, None)

