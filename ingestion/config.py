from dataclasses import dataclass

from shared.config import get_settings


@dataclass(frozen=True)
class IngestionConfig:
	refresh_minutes: int
	simulation_mode: bool
	grid_bbox: tuple[float, float, float, float]
	grid_rows: int = 50
	grid_cols: int = 50


def load_ingestion_config() -> IngestionConfig:
	s = get_settings()
	return IngestionConfig(
		refresh_minutes=s.ingestion_refresh_minutes,
		simulation_mode=s.simulation_mode,
		grid_bbox=s.grid_bbox_tuple,
	)

