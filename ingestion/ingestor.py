"""
Real-time data ingestion pipeline for urban air toxicity navigation.

Pulls live weather, air quality, and sensor data from Open-Meteo and AQICN APIs,
pushes to Redis Streams for downstream consumption by GNN, routing, and matching engines.

Data sources:
- Open-Meteo Forecast API: wind vectors, temperature, humidity, pressure, boundary layer height
- Open-Meteo Air Quality API: NO2, SO2, PM2.5, PM10, CO concentrations
- AQICN API: ground-level sensor validation for pollutants

All timestamps are emitted in UTC (ISO 8601).
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from pathlib import Path

import aiohttp
import osmnx as ox

from shared.config import get_settings
from shared.logging_utils import get_logger
from shared.redis_client import RedisStore
from ingestion.redis_publisher import (
	publish_state,
	publish_weather,
	publish_airquality,
	publish_sensors,
)
from ingestion.data_fusion import fuse_weather_and_airquality
from gnn.edge_weights import update_graph_toxicity_from_streams

logger = get_logger(__name__)

def _utc_now_iso() -> str:
	"""Return current UTC timestamp in ISO-8601 with explicit Z suffix."""
	return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class OpenMeteoIngestor:
	"""Async client for Open-Meteo APIs (Forecast + Air Quality)."""

	def __init__(self, settings):
		self.forecast_url = settings.open_meteo_forecast_url
		self.aq_url = settings.open_meteo_aq_url
		self.lat = settings.bangalore_lat
		self.lon = settings.bangalore_lon

	async def fetch_weather(self, session: aiohttp.ClientSession) -> dict[str, object] | None:
		"""
		Fetch weather data from Open-Meteo Forecast API.

		Returns:
			Dictionary with keys: wind_speed_10m, wind_direction_10m, wind_gusts_10m,
			boundary_layer_height, temperature_2m, relative_humidity_2m, surface_pressure,
			timestamp.
		"""
		params = {
			"latitude": self.lat,
			"longitude": self.lon,
			"hourly": (
				"wind_speed_10m,wind_direction_10m,wind_gusts_10m,temperature_2m,"
				"relative_humidity_2m,surface_pressure"
			),
			"current": (
				"wind_speed_10m,wind_direction_10m,wind_gusts_10m,temperature_2m,"
				"relative_humidity_2m,surface_pressure"
			),
			"wind_speed_unit": "ms",
			"timezone": "UTC",
			"forecast_days": "1",
		}

		try:
			async with session.get(self.forecast_url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
				if resp.status == 200:
					data = await resp.json()
					current = data.get("current", {})

					return {
						"wind_speed_10m": current.get("wind_speed_10m"),
						"wind_direction_10m": current.get("wind_direction_10m"),
						"wind_gusts_10m": current.get("wind_gusts_10m"),
						"boundary_layer_height": 500.0,
						"temperature_2m": current.get("temperature_2m"),
						"relative_humidity_2m": current.get("relative_humidity_2m"),
						"surface_pressure": current.get("surface_pressure"),
						"timestamp": _utc_now_iso(),
						"lat": self.lat,
						"lon": self.lon,
					}
				else:
					logger.error(f"Open-Meteo Forecast API error: {resp.status}")
					return None
		except Exception as e:
			logger.error(f"Failed to fetch weather from Open-Meteo: {e}")
			return None

	async def fetch_airquality(self, session: aiohttp.ClientSession) -> dict[str, object] | None:
		"""
		Fetch air quality data from Open-Meteo Air Quality API.

		Returns:
			Dictionary with keys: nitrogen_dioxide, sulphur_dioxide, pm2_5, pm10,
			carbon_monoxide, timestamp.
		"""
		params = {
			"latitude": self.lat,
			"longitude": self.lon,
			"current": "nitrogen_dioxide,sulphur_dioxide,pm2_5,pm10,carbon_monoxide",
			"timezone": "UTC",
		}

		try:
			async with session.get(self.aq_url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
				if resp.status == 200:
					data = await resp.json()
					current = data.get("current", {})

					return {
						"nitrogen_dioxide": current.get("nitrogen_dioxide"),
						"sulphur_dioxide": current.get("sulphur_dioxide"),
						"pm2_5": current.get("pm2_5"),
						"pm10": current.get("pm10"),
						"carbon_monoxide": current.get("carbon_monoxide"),
						"timestamp": _utc_now_iso(),
						"lat": self.lat,
						"lon": self.lon,
					}
				else:
					logger.error(f"Open-Meteo Air Quality API error: {resp.status}")
					return None
		except Exception as e:
			logger.error(f"Failed to fetch air quality from Open-Meteo: {e}")
			return None


class AQICNIngestor:
	"""Async client for AQICN ground-level sensor API."""

	def __init__(self, settings):
		resolved_settings = settings or get_settings()
		self.aqicn_url = resolved_settings.aqicn_url
		self.aqicn_token = resolved_settings.aqicn_token
		if not self.aqicn_token:
			logger.warning("AQICN token not set — skipping sensor fetch")

	async def fetch_sensors(self, session: aiohttp.ClientSession) -> dict[str, object] | None:
		"""
		Fetch ground-level sensor data from AQICN API.

		Returns:
			Dictionary with sensor measurements and metadata.
		"""
		if not self.aqicn_token:
			logger.warning("AQICN token not set — skipping sensor fetch")
			return None

		separator = "&" if "?" in self.aqicn_url else "?"
		request_url = f"{self.aqicn_url}{separator}token={self.aqicn_token}"

		try:
			async with session.get(request_url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
				if resp.status == 200:
					data = await resp.json()
					if data.get("status") == "ok":
						data_payload = data.get("data", {})
						return {
							"station": data_payload.get("station", {}).get("name"),
							"aqi": data_payload.get("aqi"),
							"no2": data_payload.get("iaqi", {}).get("no2", {}).get("v"),
							"so2": data_payload.get("iaqi", {}).get("so2", {}).get("v"),
							"pm2_5": data_payload.get("iaqi", {}).get("pm25", {}).get("v"),
							"o3": data_payload.get("iaqi", {}).get("o3", {}).get("v"),
							"timestamp": _utc_now_iso(),
							"lat": self.aqicn_url.split("bangalore")[0],  # Placeholder; extract from response
							"lon": self.aqicn_url.split("bangalore")[0],  # Placeholder; extract from response
						}
					else:
						logger.warning(f"AQICN API returned non-ok status: {data.get('status')}")
						return None
				else:
					logger.error(f"AQICN API error: {resp.status}")
					return None
		except Exception as e:
			logger.error(f"Failed to fetch sensors from AQICN: {e}")
			return None


class OSMGraphLoader:
	"""Lazy loader for OpenStreetMap road network graph."""

	_graph = None
	_cache_path = Path("data/graphs/bangalore_utm.graphml")

	@classmethod
	def load_road_graph(cls):
		"""Load/fetch Bangalore road graph and ensure UTM Zone 43N projection."""
		if cls._graph is not None:
			return cls._graph

		try:
			if cls._cache_path.exists():
				logger.info("Loading cached UTM graph from %s", cls._cache_path)
				cls._graph = ox.load_graphml(cls._cache_path)
				return cls._graph

			logger.info("Fetching Bangalore road network from OSM...")
			raw_graph = ox.graph_from_place(
				"Bangalore, India",
				simplify=True,
				retain_all=False,
				network_type="drive",
			)
			logger.info("Projecting road network to EPSG:32643")
			cls._graph = ox.projection.project_graph(raw_graph, to_crs="EPSG:32643")
			cls._cache_path.parent.mkdir(parents=True, exist_ok=True)
			ox.save_graphml(cls._graph, cls._cache_path)
			logger.info(
				"Cached projected graph at %s (%s nodes, %s edges)",
				cls._cache_path,
				len(cls._graph.nodes),
				len(cls._graph.edges),
			)
		except Exception as e:
			logger.error("Failed to load UTM road graph: %s", e)
			cls._graph = None

		return cls._graph

	@classmethod
	def get_graph(cls):
		"""Backward-compatible alias for load_road_graph."""
		return cls.load_road_graph()


async def ingest_once(
	redis_store: RedisStore,
	settings,
) -> None:
	"""
	Run a single ingestion cycle: fetch all data and push to Redis.

	Args:
		redis_store: Redis client for publishing data
		settings: Configuration object
	"""
	logger.info("Starting ingestion cycle...")

	# Initialize API clients
	open_meteo = OpenMeteoIngestor(settings)
	aqicn = AQICNIngestor(settings)

	async with aiohttp.ClientSession() as session:
		# Fetch all data in parallel
		weather_task = open_meteo.fetch_weather(session)
		aq_task = open_meteo.fetch_airquality(session)
		sensors_task = aqicn.fetch_sensors(session)

		weather_data, aq_data, sensors_data = await asyncio.gather(
			weather_task, aq_task, sensors_task, return_exceptions=False
		)

	# Publish raw point data to new streams
	if weather_data:
		publish_weather(redis_store, weather_data)
		logger.debug(f"Published weather: {weather_data}")
	else:
		logger.warning("Failed to fetch weather data")

	if aq_data:
		publish_airquality(redis_store, aq_data)
		logger.debug(f"Published air quality: {aq_data}")
	else:
		logger.warning("Failed to fetch air quality data")

	if sensors_data:
		publish_sensors(redis_store, sensors_data)
		logger.debug(f"Published sensor data: {sensors_data}")
	else:
		logger.info("No sensor data available (AQICN token may not be configured)")

	# Fuse data and create grid representation for GNN/routing
	fused_state = fuse_weather_and_airquality(
		weather_data,
		aq_data,
		sensors_data,
		settings,
		stringify_keys=True,
	)
	publish_state(redis_store, fused_state)  # Publish to legacy stream for backwards compatibility
	logger.debug("Published fused grid state to legacy stream")

	# Load OSM graph once (lazy load on first ingestion)
	graph = OSMGraphLoader.get_graph()
	if graph:
		logger.info("OSM graph ready for downstream use")
	else:
		logger.warning("OSM graph not available")

	logger.info("Ingestion cycle complete")


async def run_ingestor(
	redis_store: RedisStore,
	refresh_minutes: int = 15,
) -> None:
	"""
	Run the ingestor daemon in an infinite loop, pulling data every refresh_minutes.

	Args:
		redis_store: Redis client for publishing data
		refresh_minutes: Interval in minutes between API pulls
	"""
	settings = get_settings()

	async def _toxicity_refresh_loop(store: RedisStore) -> None:
		while True:
			try:
				update_graph_toxicity_from_streams(store)
			except Exception as e:
				logger.error(f"Toxicity refresh cycle failed: {e}", exc_info=True)
			await asyncio.sleep(300)

	toxicity_task = asyncio.create_task(_toxicity_refresh_loop(redis_store))

	try:
		while True:
			try:
				await ingest_once(redis_store, settings)
			except Exception as e:
				logger.error(f"Ingestion cycle failed: {e}", exc_info=True)

			logger.info(f"Sleeping for {refresh_minutes} minutes until next ingestion...")
			await asyncio.sleep(refresh_minutes * 60)
	finally:
		toxicity_task.cancel()


if __name__ == "__main__":
	"""
	Standalone entry point for testing the ingestor.

	Usage:
		python -m ingestion.ingestor
	"""
	from shared.redis_client import RedisStore

	logging.basicConfig(
		level=logging.INFO,
		format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
	)

	settings = get_settings()
	store = RedisStore()
	store.connect()

	try:
		asyncio.run(run_ingestor(store, refresh_minutes=settings.ingestion_refresh_minutes))
	except KeyboardInterrupt:
		logger.info("Ingestor stopped by user")
