# Data Directory

This directory contains all raw and processed data for the Bangalore urban toxicity navigation project.
Do not commit files in `raw/` except `stations/meta.parquet` and checkpoint files.

## Structure

```
data/
	raw/
		weather/              # Open-Meteo Historical Forecast API
			2022.parquet        # 8,760 rows — wind, temp, pressure, humidity (hourly)
			2023.parquet
			2024.parquet
			2025.parquet
			2026_partial.parquet
		airquality/           # Open-Meteo Air Quality API (CAMS Global, 45km resolution)
			2022.parquet        # 8,760 rows — NO2, SO2, PM2.5, PM10, CO background context
			2023.parquet
			2024.parquet
			2025.parquet
			2026_partial.parquet
		stations/             # OpenAQ CPCB ground sensors (station-level resolution)
			meta.parquet        # 23 stations — ID, name, lat, lon, available sensors
			2022.parquet        # ~1.3M rows — NO2, SO2, PM2.5, PM10, CO per station
			2023.parquet
			2024.parquet
			2025.parquet
			2026_partial.parquet
	graphs/                 # OSMnx road network (generated, not committed)
		bangalore_utm.graphml
		bangalore_utm_nodes.parquet
		bangalore_utm_edges.parquet
	gnn/
		training/             # Joined training datasets (generated, not committed)
		checkpoints/          # Saved GNN model weights (not committed)
```

## Sources

| Source | API | Variables | Resolution | Key Required |
|---|---|---|---|---|
| Open-Meteo Forecast | archive-api.open-meteo.com | wind_speed_10m, wind_direction_10m, wind_gusts_10m, temperature_2m, relative_humidity_2m, surface_pressure | 2-11km | No |
| Open-Meteo Air Quality | air-quality-api.open-meteo.com | nitrogen_dioxide, sulphur_dioxide, pm2_5, pm10, carbon_monoxide | 45km (CAMS Global) | No |
| OpenAQ CPCB | api.openaq.org/v3 | no2, so2, pm25, pm10, co | Station-level (23 stations) | Yes — OPENAQ_API_KEY |

## Bangalore Stations (OpenAQ)

23 unique CPCB/KSPCB stations within bounding box `12.834,77.461,13.144,77.781`:
- Hebbal, Peenya, Silk Board, BTM Layout, Jayanagar 5th Block
- BWSSB Kadabesanahalli, City Railway Station, Sanegurava Halli
- Bapuji Nagar, Hombegowda Nagar, RVCE-Mailasandra
- Kasturi Nagar, Shivapura Peenya, Koramangala, Bellandur
- And others — see `stations/meta.parquet` for full list with coordinates

## Pull Scripts

```bash
# Pull all weather data (2022-2026)
python scripts/pull_weather.py

# Pull all air quality data (2022-2026)
python scripts/pull_airquality.py

# Pull all station data (2022-2026) — takes several hours
python scripts/pull_stations.py

# Resume any interrupted pull
python scripts/pull_weather.py --resume
python scripts/pull_airquality.py --resume
python scripts/pull_stations.py --resume

# Pull a single year only
python scripts/pull_stations.py --year 2023
```

## Notes

- Weather and air quality data has zero missing values from 2023 onwards
- 2022 air quality has ~25,000 missing values due to CAMS data availability starting mid-2022
- Station data is at 15-minute intervals, resampled to hourly at training time
- Duplicate stations (same coordinates, different provider names) are deduplicated during discovery
- All timestamps stored in IST (Asia/Kolkata, UTC+5:30)
- Parquet files use Snappy compression via pyarrow
