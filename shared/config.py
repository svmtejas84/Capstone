from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
	model_config = SettingsConfigDict(env_file=".env", extra="ignore")

	simulation_mode: bool = True
	gee_service_account: str = ""
	gee_key_file: str = ""
	tomtom_api_key: str = ""
	mosdac_username: str = ""
	mosdac_password: str = ""
	mosdac_product: str = "INSAT_AMV"
	redis_url: str = "redis://localhost:6379"
	era5_cache_dir: str = "./data/era5_cache"
	sentinel_cache_dir: str = "./data/sentinel5p_cache"
	ingestion_refresh_minutes: int = 15
	insat_refresh_minutes: int = 15
	era5_base_refresh_hours: int = 24
	traffic_baseline_window_days: int = 30
	traffic_anomaly_alpha: float = 1.5
	traffic_emission_factor_k: float = 1.0
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

