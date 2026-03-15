import numpy as np


def build_mock_grid(size: int = 32) -> np.ndarray:
    # Prototype base toxicity field from low-frequency satellite baseline.
    y, x = np.mgrid[0:size, 0:size]
    center = size / 2
    base = np.exp(-((x - center) ** 2 + (y - center) ** 2) / (2 * (size / 5) ** 2))
    return base.astype(np.float32)
