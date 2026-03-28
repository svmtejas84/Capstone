from dotenv import load_dotenv
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
	model_config = SettingsConfigDict(extra="ignore")

	# Open-Meteo API URLs (no key required)
	open_meteo_forecast_url: str = "https://api.open-meteo.com/v1/forecast"
	open_meteo_aq_url: str = "https://air-quality-api.open-meteo.com/v1/air-quality"

	# AQICN API
	aqicn_token: str = ""
	aqicn_url: str = "https://api.waqi.info/feed/bangalore/"

	# Bangalore coordinates
	bangalore_lat: float = 12.9716
	bangalore_lon: float = 77.5946

	# Ingestion configuration
	redis_url: str = "redis://localhost:6379"
	raw_data_dir: str = "./data/raw"
	ingestion_refresh_minutes: int = 15
	frontend_origin: str = "http://localhost:5173"

	grid_bbox: str = Field(default="12.834,77.461,13.144,77.781")

	@property
	def grid_bbox_tuple(self) -> tuple[float, float, float, float]:
		parts = [float(x.strip()) for x in self.grid_bbox.split(",")]
		if len(parts) != 4:
			raise ValueError("GRID_BBOX must contain 4 comma-separated floats")
		return (parts[0], parts[1], parts[2], parts[3])


@lru_cache(maxsize=1)
def get_settings() -> Settings:
	return Settings()

