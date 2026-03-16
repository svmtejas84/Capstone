from math import exp


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
) -> float:
	if not is_downwind(edge_bearing_deg, wind_dir_deg, cone_deg=cone_deg):
		return 0.0
	delta = angle_difference_deg(edge_bearing_deg, wind_dir_deg)
	return angular_weight(delta, sigma_deg=sigma_deg)

