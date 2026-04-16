from __future__ import annotations

from shared.physics_config import get_respiratory_minute_volume


def compute_edge_weight(concentration_ug_m3: float, travel_time_s: float, mode: str) -> float:
	"""Compute inhaled dose (mass of pollutant inhaled) for an edge traversal.

	Inhaled Dose = Concentration × RMV × Travel Time

	Args:
		concentration_ug_m3: Pollutant concentration in µg/m³.
		travel_time_s: Time spent on edge in seconds.
		mode: Transport mode ('walking', 'cycling', 'two_wheeler').
			Legacy aliases ('driving', 'car') are still accepted.

	Returns:
		Inhaled dose in µg.
	"""
	rmv = get_respiratory_minute_volume(mode)  # m³/hr
	travel_time_hr = travel_time_s / 3600.0  # Convert seconds to hours
	involved_volume = rmv * travel_time_hr  # m³ of air inhaled
	return concentration_ug_m3 * involved_volume


def compute_path_cost(edge_weights: list[float], mode: str, edge_time_s: float = 60.0) -> float:
	"""Compute cumulative inhaled dose along a path.

	Args:
		edge_weights: List of inhaled doses per edge in µg.
		mode: Transport mode (for completeness, already accounted in edge_weights).
		edge_time_s: Time per edge segment in seconds (not used if edge_weights are pre-computed).

	Returns:
		Total inhaled dose in µg.
	"""
	return sum(edge_weights)

