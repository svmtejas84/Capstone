from __future__ import annotations

from math import exp, pi

from shared.physics_config import StabilityClass, get_stability_dispersion_params


def dispersion_sigmas(
	distance_m: float,
	stability: StabilityClass = StabilityClass.D,
) -> tuple[float, float]:
	"""Urban dispersion parameterization using Pasquill-Gifford stability classes.

	Args:
		distance_m: Downwind distance in meters.
		stability: Pasquill stability class (default: neutral D class).

	Returns:
		(sigma_y, sigma_z) in meters.
	"""
	d = max(1.0, distance_m)
	sigma_y_coeff, sigma_z_coeff = get_stability_dispersion_params(stability)
	sigma_y = max(2.0, sigma_y_coeff * d)
	sigma_z = max(1.0, sigma_z_coeff * d)
	return sigma_y, sigma_z


def effective_wind_speed(wind_speed: float, building_density: float) -> float:
	"""Effective wind speed at street level reduced by urban canyon sheltering.

	Args:
		wind_speed: Reference wind speed (m/s, typically at 10m height).
		building_density: Fraction of area covered by buildings (0-1).

	Returns:
		Effective wind speed at street level (m/s).
	"""
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
	"""Gaussian plume model for air pollutant concentration.

	Args:
		q: Source strength (µg/s).
		x_downwind_m: Downwind distance (m).
		y_crosswind_m: Crosswind distance (m).
		wind_speed: Mean wind speed (m/s).
		sigma_y: Lateral dispersion (m).
		sigma_z: Vertical dispersion (m).
		release_height_m: Release height (m, default 2.0 for breathing zone).

	Returns:
		Concentration in µg/m³.
	"""
	if wind_speed <= 0.0 or sigma_y <= 0.0 or sigma_z <= 0.0:
		return 0.0
	cross = exp(-(y_crosswind_m ** 2) / (2.0 * sigma_y ** 2))
	vertical = exp(-(release_height_m ** 2) / (2.0 * sigma_z ** 2))
	return (q / (2.0 * pi * wind_speed * sigma_y * sigma_z)) * cross * vertical


def urban_canyon_correction(concentration: float, building_density: float, wind_speed: float) -> float:
	"""Urban canyon amplification of pollutant concentration.

	Increase concentration due to stagnation in buildings canyons.

	Args:
		concentration: Ambient concentration (µg/m³).
		building_density: Fraction of area covered by buildings (0-1).
		wind_speed: Street-level wind speed (m/s).

	Returns:
		Corrected concentration (µg/m³).
	"""
	bd = max(0.0, min(1.0, building_density))
	stagnation = max(0.0, 1.0 - min(1.0, wind_speed / 3.0))
	# Denser canyons and stagnation increase persistence near breathing zone.
	multiplier = 1.0 + 0.6 * bd + 0.15 * stagnation
	return concentration * multiplier

