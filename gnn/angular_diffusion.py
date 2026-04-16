from __future__ import annotations

from math import exp

from shared.physics_config import UrbanCanyon


def angle_difference_deg(a_deg: float, b_deg: float) -> float:
	"""Smallest absolute difference between two directions in degrees."""
	delta = (a_deg - b_deg + 180.0) % 360.0 - 180.0
	return abs(delta)


def angular_weight(delta_theta_deg: float, sigma_deg: float = 45.0) -> float:
	return exp(-((delta_theta_deg ** 2) / (2.0 * sigma_deg ** 2)))


def is_downwind(edge_bearing_deg: float, wind_dir_deg: float, cone_deg: float = 75.0) -> bool:
	return angle_difference_deg(edge_bearing_deg, wind_dir_deg) <= cone_deg


def directional_diffusion_weight(
	edge_bearing_deg: float,
	wind_dir_deg: float,
	sigma_deg: float = 35.0,
	cone_deg: float = 75.0,
	building_density: float = 0.0,
) -> float:
	"""Directional diffusion weight with street canyon tunneling correction.

	In high-density urban areas, wind is deflected to align with street bearing.

	Args:
		edge_bearing_deg: Street/edge direction in degrees (0-360).
		wind_dir_deg: Wind direction in degrees (0-360).
		sigma_deg: Gaussian width for angular diffusion (degrees).
		cone_deg: Downwind cone angle (degrees).
		building_density: Fraction of area covered by buildings (0-1).

	Returns:
		Angular weight (0-1).
	"""
	# Canyon tunneling: strong buildings deflect wind to street alignment
	effective_wind_dir = wind_dir_deg
	if building_density > UrbanCanyon.HIGH_DENSITY_THRESHOLD:
		# Blend wind direction towards street bearing
		blend = UrbanCanyon.CANYON_DEFLECTION_STRENGTH
		delta_to_bearing = angle_difference_deg(wind_dir_deg, edge_bearing_deg)
		if delta_to_bearing != 0:
			# Move wind direction towards street bearing proportionally
			if angle_difference_deg(wind_dir_deg, edge_bearing_deg) < 180:
				effective_wind_dir = wind_dir_deg + blend * angle_difference_deg(wind_dir_deg, edge_bearing_deg)
			else:
				effective_wind_dir = wind_dir_deg - blend * (360 - angle_difference_deg(wind_dir_deg, edge_bearing_deg))
		effective_wind_dir = effective_wind_dir % 360

	if not is_downwind(edge_bearing_deg, effective_wind_dir, cone_deg=cone_deg):
		return 0.0
	delta = angle_difference_deg(edge_bearing_deg, effective_wind_dir)
	return angular_weight(delta, sigma_deg=sigma_deg)

