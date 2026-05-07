from __future__ import annotations

from shared.physics_config import get_respiratory_minute_volume


def compute_edge_weight(
	concentration_ug_m3: float | None = None,
	travel_time_s: float = 60.0,
	mode: str = "walking",
	**kwargs: float,
) -> float:
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
	if concentration_ug_m3 is None:
		concentration_ug_m3 = float(kwargs.get("cedge", 0.0))
	rmv = get_respiratory_minute_volume(mode)  # m³/hr
	travel_time_hr = travel_time_s / 3600.0  # Convert seconds to hours
	involved_volume = rmv * travel_time_hr  # m³ of air inhaled
	return concentration_ug_m3 * involved_volume


def compute_path_cost(
	edge_weights: list[float],
	mode: str,
	edge_time_s: float = 60.0,
	edge_times_s: list[float] | None = None,
	weights_are_doses: bool = False,
) -> float:
	"""Compute cumulative inhaled dose along a path.

	Args:
		edge_weights: List of concentrations in µg/m³, or doses when weights_are_doses=True.
		mode: Transport mode used to select respiratory minute volume.
		edge_time_s: Fallback time per edge segment in seconds.
		edge_times_s: Optional per-edge traversal times in seconds.
		weights_are_doses: If true, sum edge_weights directly.

	Returns:
		Total inhaled dose in µg.
	"""
	if weights_are_doses:
		return sum(edge_weights)
	if edge_times_s is None:
		edge_times_s = [edge_time_s] * len(edge_weights)
	return sum(
		compute_edge_weight(concentration_ug_m3=concentration, travel_time_s=time_s, mode=mode)
		for concentration, time_s in zip(edge_weights, edge_times_s, strict=False)
	)
