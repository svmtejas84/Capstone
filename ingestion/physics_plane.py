from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import numpy as np


@dataclass
class GrasterState:
	concentration: np.ndarray
	wind_u: np.ndarray
	wind_v: np.ndarray
	source_spike: np.ndarray
	timestamp: datetime


def build_empty_state(cfg: Any) -> GrasterState:
	rows = int(getattr(cfg, "grid_rows", 50))
	cols = int(getattr(cfg, "grid_cols", 50))
	shape = (rows, cols)
	return GrasterState(
		concentration=np.zeros(shape, dtype=float),
		wind_u=np.zeros(shape, dtype=float),
		wind_v=np.zeros(shape, dtype=float),
		source_spike=np.zeros(shape, dtype=float),
		timestamp=datetime.now(timezone.utc),
	)


def simulate_base_state(cfg: Any, seed: int = 42) -> GrasterState:
	rng = np.random.default_rng(seed)
	state = build_empty_state(cfg)
	state.concentration = rng.uniform(12.0, 40.0, size=state.concentration.shape)
	state.wind_u = rng.uniform(0.2, 2.5, size=state.wind_u.shape)
	state.wind_v = rng.uniform(-1.2, 1.2, size=state.wind_v.shape)
	return state


def to_payload(state: GrasterState) -> dict[str, object]:
	return {
		"concentration": state.concentration.round(4).tolist(),
		"wind_u": state.wind_u.round(4).tolist(),
		"wind_v": state.wind_v.round(4).tolist(),
		"source_spike": state.source_spike.round(4).tolist(),
		"timestamp": state.timestamp.isoformat(),
	}

