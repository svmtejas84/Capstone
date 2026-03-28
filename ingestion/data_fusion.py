"""
Data fusion layer that converts point-based observations from Open-Meteo and AQICN
into grid-based representations compatible with the GNN and downstream modules.

Handles interpolation and spatial discretization of real-time sensor data.
"""

from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import Optional

import numpy as np
from scipy.interpolate import griddata

from shared.config import get_settings
from shared.logging_utils import get_logger

logger = get_logger(__name__)

# IST timezone offset
IST = timezone(timedelta(hours=5, minutes=30))


class GridInterpolator:
	"""Converts point observations to grid representation."""

	def __init__(
		self,
		min_lat: float,
		min_lon: float,
		max_lat: float,
		max_lon: float,
		grid_rows: int = 50,
		grid_cols: int = 50,
	):
		"""
		Initialize grid interpolator with bounding box and grid dimensions.

		Args:
			min_lat, min_lon: Southwest corner of grid
			max_lat, max_lon: Northeast corner of grid
			grid_rows, grid_cols: Number of grid cells
		"""
		self.min_lat = min_lat
		self.min_lon = min_lon
		self.max_lat = max_lat
		self.max_lon = max_lon
		self.grid_rows = grid_rows
		self.grid_cols = grid_cols

		# Create regular grid for interpolation targets
		lat_vals = np.linspace(min_lat, max_lat, grid_rows)
		lon_vals = np.linspace(min_lon, max_lon, grid_cols)
		self.grid_lat, self.grid_lon = np.meshgrid(lat_vals, lon_vals, indexing="ij")
		self.grid_points = np.column_stack([self.grid_lat.ravel(), self.grid_lon.ravel()])

	def interpolate_scalar(
		self,
		value: float | None,
		lat: float,
		lon: float,
		method: str = "constant",
	) -> np.ndarray:
		"""
		Interpolate a scalar observation to grid.

		For point data, uses nearest-neighbor or constant value fill if only one point.

		Args:
			value: Scalar observation value
			lat: Latitude of observation
			lon: Longitude of observation
			method: Interpolation method ('constant', 'nearest', 'linear')

		Returns:
			Grid array of interpolated values
		"""
		if value is None:
			return np.zeros((self.grid_rows, self.grid_cols))

		if method == "constant":
			# Fill entire grid with constant value
			return np.full((self.grid_rows, self.grid_cols), value, dtype=float)

		# For single-point data, use nearest-neighbor interpolation
		points = np.array([[lat, lon]])
		values = np.array([value])

		try:
			interpolated = griddata(
				points,
				values,
				self.grid_points,
				method="nearest",
				fill_value=value,
			)
			return interpolated.reshape((self.grid_rows, self.grid_cols))
		except Exception as e:
			logger.warning(f"Interpolation failed: {e}, using constant fill")
			return np.full((self.grid_rows, self.grid_cols), value, dtype=float)

	def wind_to_components(
		self,
		wind_speed: float | None,
		wind_direction: float | None,
	) -> tuple[np.ndarray, np.ndarray]:
		"""
		Convert wind speed and direction to u,v components on grid.

		Args:
			wind_speed: Wind speed in m/s
			wind_direction: Wind direction in degrees (0=North, 90=East, 180=South, 270=West)

		Returns:
			Tuple of (wind_u, wind_v) grids
		"""
		if wind_speed is None or wind_direction is None:
			return (
				np.zeros((self.grid_rows, self.grid_cols)),
				np.zeros((self.grid_rows, self.grid_cols)),
			)

		# Convert direction to radians (meteorological convention: 0=N, 90=E)
		rad = np.radians(wind_direction)
		u = wind_speed * np.sin(rad)
		v = wind_speed * np.cos(rad)

		# Fill grid with constant wind vectors (reasonable for small area)
		wind_u = np.full((self.grid_rows, self.grid_cols), u, dtype=float)
		wind_v = np.full((self.grid_rows, self.grid_cols), v, dtype=float)

		return wind_u, wind_v


def fuse_weather_and_airquality(
	weather_data: dict | None,
	aq_data: dict | None,
	sensors_data: dict | None,
	settings=None,
) -> dict[str, object]:
	"""
	Fuse point-based weather and air quality observations into grid format.

	Creates GrasterState-compatible dictionary with grids for:
	- concentration (from air quality measurements)
	- wind_u, wind_v (from weather wind vectors)
	- source_spike (placeholder for now; could use traffic data)

	Args:
		weather_data: Dictionary from Open-Meteo Forecast API
		aq_data: Dictionary from Open-Meteo Air Quality API
		sensors_data: Dictionary from AQICN API
		settings: Configuration object (default: get from shared.config)

	Returns:
		Dictionary with grid-based state compatible with existing GNN pipelines
	"""
	if settings is None:
		settings = get_settings()

	# Parse grid bounds
	min_lat, min_lon, max_lat, max_lon = settings.grid_bbox_tuple

	# Create interpolator
	interp = GridInterpolator(min_lat, min_lon, max_lat, max_lon, grid_rows=50, grid_cols=50)

	# Extract measurements (use air quality primary source, fall back to sensors)
	concentration_value = None
	if aq_data and aq_data.get("pm2_5"):
		concentration_value = aq_data["pm2_5"]
	elif sensors_data and sensors_data.get("pm2_5"):
		concentration_value = sensors_data["pm2_5"]

	# Use NO2 if PM2.5 unavailable
	if concentration_value is None:
		if aq_data and aq_data.get("nitrogen_dioxide"):
			concentration_value = aq_data["nitrogen_dioxide"]
		elif sensors_data and sensors_data.get("no2"):
			concentration_value = sensors_data["no2"]

	# Extract wind data
	wind_speed = weather_data.get("wind_speed_10m") if weather_data else None
	wind_direction = weather_data.get("wind_direction_10m") if weather_data else None

	# Interpolate to grids
	concentration = interp.interpolate_scalar(
		concentration_value,
		settings.bangalore_lat,
		settings.bangalore_lon,
		method="constant",
	)

	wind_u, wind_v = interp.wind_to_components(wind_speed, wind_direction)

	# Source spike (placeholder: can be enhanced with traffic data)
	source_spike = np.zeros((50, 50), dtype=float)

	# Determine timestamp from data sources (prefer weather as primary)
	timestamp_str = None
	if weather_data:
		timestamp_str = weather_data.get("timestamp")
	elif aq_data:
		timestamp_str = aq_data.get("timestamp")
	elif sensors_data:
		timestamp_str = sensors_data.get("timestamp")

	if not timestamp_str:
		timestamp_str = datetime.now(IST).isoformat()

	return {
		"concentration": concentration.round(4).tolist(),
		"wind_u": wind_u.round(4).tolist(),
		"wind_v": wind_v.round(4).tolist(),
		"source_spike": source_spike.round(4).tolist(),
		"timestamp": timestamp_str,
		"metadata": {
			"source": "open-meteo+aqicn",
			"concentration_source": "pm2_5" if concentration_value else "no2",
			"concentration_value": float(concentration_value) if concentration_value else None,
			"wind_speed_ms": float(wind_speed) if wind_speed else None,
			"wind_direction_deg": float(wind_direction) if wind_direction else None,
		},
	}


if __name__ == "__main__":
	"""
	Test data fusion locally.

	Usage:
		python -m ingestion.data_fusion
	"""
	import json

	# Mock data for testing
	weather = {
		"wind_speed_10m": 2.5,
		"wind_direction_10m": 45.0,
		"temperature_2m": 28.5,
		"timestamp": datetime.now(IST).isoformat(),
	}

	aq = {
		"pm2_5": 35.2,
		"nitrogen_dioxide": 42.1,
		"timestamp": datetime.now(IST).isoformat(),
	}

	sensors = {
		"pm2_5": 38.0,
		"no2": 40.5,
		"timestamp": datetime.now(IST).isoformat(),
	}

	result = fuse_weather_and_airquality(weather, aq, sensors)
	print(json.dumps({k: v for k, v in result.items() if k != "concentration" and k != "wind_u" and k != "wind_v" and k != "source_spike"}, indent=2))
	print(f"Grid shapes: concentration={np.array(result['concentration']).shape}, wind_u={np.array(result['wind_u']).shape}")
