from dataclasses import dataclass

from shared.config import get_settings


@dataclass(frozen=True)
class IngestionConfig:
	refresh_minutes: int
	simulation_mode: bool
	grid_bbox: tuple[float, float, float, float]
	insat_refresh_minutes: int
	era5_base_refresh_hours: int
	traffic_baseline_window_days: int
	traffic_anomaly_alpha: float
	traffic_emission_factor_k: float
	grid_rows: int = 50
	grid_cols: int = 50


def load_ingestion_config() -> IngestionConfig:
	s = get_settings()
	return IngestionConfig(
		refresh_minutes=s.ingestion_refresh_minutes,
		simulation_mode=s.simulation_mode,
		grid_bbox=s.grid_bbox_tuple,
		insat_refresh_minutes=s.insat_refresh_minutes,
		era5_base_refresh_hours=s.era5_base_refresh_hours,
		traffic_baseline_window_days=s.traffic_baseline_window_days,
		traffic_anomaly_alpha=s.traffic_anomaly_alpha,
		traffic_emission_factor_k=s.traffic_emission_factor_k,
	)

