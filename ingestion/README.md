# ingestion

Live environmental data ingestion and stream-first architecture foundation.

## Responsibilities

- Fetch live observations asynchronously from Open-Meteo and AQICN APIs.
- Publish point observations to Redis streams (weather, air quality, sensors).
- Fuse stream observations into grid-form state for downstream consumers.
- Generate training tensors from stream-backed state for GNN updates.
- Support historical data archive (2022–2026) for bias correction and validation.

## Main Files

- `ingestor.py`: Async worker loop fetching and publishing to streams.
- `data_fusion.py`: Point-to-grid IDW conversion for physic-plane state.
- `redis_publisher.py`: Redis stream read/write helpers and stream management.
- `physics_plane.py`: Grid utilities and state initialization.
- `put_gnn_training_data.py`: Tensor generation from stream-backed state for model training.
- `bias_correction.py`: Calibration helpers for sensor data quality.
- `traffic_spike.py`: Commuter flow estimation from historical patterns.
- `nowcaster.py`: Short-term concentration prediction using recent stream state.

## Data Sources

### 1. Open-Meteo Forecast API

- **URL**: `archive-api.open-meteo.com` or `api.open-meteo.com`
- **API Key**: Not required.
- **Variables**: 
  - Wind speed (10m), wind direction, wind gust
  - Temperature (2m), relative humidity
  - Surface pressure
- **Resolution**: 2–11 km
- **Stream Key**: `weather:live`

### 2. Open-Meteo Air Quality API

- **URL**: `air-quality-api.open-meteo.com`
- **API Key**: Not required.
- **Variables**: NO2, SO2, PM2.5, PM10, CO (background CAMS Global context)
- **Resolution**: 45 km (CAMS Global)
- **Stream Key**: `airquality:live`

### 3. AQICN API (Station-Level Sensors)

- **URL**: `api.waqi.info`
- **API Key**: Required — set `AQICN_TOKEN` in `.env`.
- **Variables**: NO2, SO2, PM2.5, PM10, CO (live station observations).
- **Resolution**: Station-level (23 CPCB/KSPCB stations in Bangalore).
- **Stream Key**: `sensors:live`

## Redis Streams

Each stream holds timestamped JSON payloads:

```
weather:live      Example payload: {"timestamp": "2026-03-29T12:34:56Z", "wind_speed": 2.5, "wind_dir": 120, ...}
airquality:live   Example payload: {"timestamp": "...", "no2": 35, "so2": 12, "pm25": 45, ...}
sensors:live      Example payload: {"timestamp": "...", "station": "Hebbal", "no2": 38, "so2": 14, ...}
```

Stream readers always consume the latest available message (not historical backlog).

## Configuration

All environment access is centralized in `shared/config.py`. Required `.env` variables:

```
AQICN_TOKEN=your_token_here
BANGALORE_LAT=12.9352
BANGALORE_LON=77.6245
REDIS_URL=redis://localhost:6379
RAW_DATA_DIR=./data/raw
INGESTION_INTERVAL_MINUTES=5
GRID_BBOX=12.834,77.461,13.144,77.781
```

- Never hardcode secrets; keep them in `.env` (already excluded by `.gitignore`).

## Ingestion Workflow

1. **Fetch** observations from Open-Meteo and AQICN in parallel async tasks.
2. **Validate** timestamp freshness and missing-value handling.
3. **Publish** point payloads to corresponding Redis streams.
4. **Fuse** stream data into grid-form state using IDW on street segments.
5. **Update** GNN edge weights and downstream exposure estimates.

### Refresh Interval

Controlled by `INGESTION_INTERVAL_MINUTES` (default: 5 minutes).

## Data Fusion

Grid state is built by interpolating point observations onto street-segment edges:

- **Method**: Inverse Distance Weighted (IDW) from nearest stations/forecast points.
- **Spatial Scale**: Bangalore UTM extent at 100 m resolution.
- **Temporal Cadence**: Updated every 5–15 minutes as streams refresh.

## Training Data Pipeline

```python
from ingestion.pull_gnn_training_data import build_training_tensors

# Build tensors from stream snapshots + 2022-2026 archive
tensors = build_training_tensors(start_date='2024-01-01', end_date='2025-12-31')
# Output: node features, edge indices, edge weights, time dimension, labels
```

## Run

```bash
# Start the async ingestion worker
python -m ingestion.ingestor
```

Logs will show:
- API fetch status (success/latency/failures).
- Stream publish confirmations.
- Grid fusion completion.

## Fallback Behavior

- **No stream data**: Grid initialized with zero-safe shape (fused output = zeros).
- **Missing forecast**: Uses most recent cached forecast or static background context.
- **Station gap**: IDW falls back to regional CAMS forecast context.

## Testing

Unit tests in `tests/`:

```bash
pytest ingestion/tests/
```

Key test coverage:

- Data fusion correctness (IDW interpolation).
- Stream publish and consume.
- Timestamp handling and timezone normalization (UTC).
- Bias correction calibration.
- Nowcasting short-term predictions.

## Notes

- Keep stream payloads timestamped in ISO 8601 format (UTC).
- Redis connection must be established before worker starts.
- Timestamps are stored in UTC internally; convert to local time only at display boundaries if needed.

