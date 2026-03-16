from math import exp, pi


def dispersion_sigmas(distance_m: float) -> tuple[float, float]:
	"""Simple urban dispersion parameterization for sigma_y and sigma_z."""
	d = max(1.0, distance_m)
	sigma_y = max(2.0, 0.22 * d)
	sigma_z = max(1.0, 0.12 * d)
	return sigma_y, sigma_z


def effective_wind_speed(wind_speed: float, building_density: float) -> float:
	bd = max(0.0, min(1.0, building_density))
	return max(0.2, wind_speed * (1.0 - 0.55 * bd))


def gaussian_plume(
	q: float,
	x_downwind_m: float,
	y_crosswind_m: float,
	wind_speed: float,
	sigma_y: float,
	sigma_z: float,
	release_height_m: float = 2.0,
) -> float:
	if wind_speed <= 0.0 or sigma_y <= 0.0 or sigma_z <= 0.0:
		return 0.0
	cross = exp(-(y_crosswind_m ** 2) / (2.0 * sigma_y ** 2))
	vertical = exp(-(release_height_m ** 2) / (2.0 * sigma_z ** 2))
	return (q / (2.0 * pi * wind_speed * sigma_y * sigma_z)) * cross * vertical


def urban_canyon_correction(concentration: float, building_density: float, wind_speed: float) -> float:
	bd = max(0.0, min(1.0, building_density))
	stagnation = max(0.0, 1.0 - min(1.0, wind_speed / 3.0))
	# Denser canyons and stagnation increase persistence near breathing zone.
	multiplier = 1.0 + 0.6 * bd + 0.15 * stagnation
	return concentration * multiplier

