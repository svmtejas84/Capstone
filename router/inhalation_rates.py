"""Deprecated inhalation-rate compatibility helpers.

The production routing path no longer uses this module. Route costs call
`router.edge_cost.compute_edge_weight`, which reads the EPA-aligned RMV values
from `shared.physics_config.get_respiratory_minute_volume`.

This file is retained for older notebooks/tests that imported `get_ir`
directly. Do not add new call sites here.
"""

from __future__ import annotations

import warnings

IR_MODE = {
	"jogger": 2.75,
	"cyclist": 1.80,
	"two_wheeler": 0.65,
}

# Legacy references retained for backward compatibility and comparison studies.
LEGACY_CAR_IR = 0.65
LEGACY_CAR_CABIN_PENALTY_FACTOR = 1.41

MODE_ALIASES = {
	"two-wheeler": "two_wheeler",
}


def get_ir(mode: str) -> float:
	warnings.warn(
		"router.inhalation_rates.get_ir is deprecated; use "
		"shared.physics_config.get_respiratory_minute_volume for routing dosimetry.",
		DeprecationWarning,
		stacklevel=2,
	)
	mode_key = MODE_ALIASES.get(mode.lower(), mode.lower())
	if mode_key == "car":
		return LEGACY_CAR_IR * LEGACY_CAR_CABIN_PENALTY_FACTOR
	base = IR_MODE.get(mode_key, IR_MODE["cyclist"])
	return base
