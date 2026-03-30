# Data Directory

This directory contains all raw and processed data for the Bangalore urban toxicity navigation project.
Do not commit files in `raw/` except `stations/meta.parquet` and checkpoint files.

**Multi-city roadmap**: v1 (Bangalore) → v2 (Delhi, Mumbai, etc.). Data structure supports city-specific instances in `data/instances/{city}/`.

## Structure

```
data/
	instances/                # City-specific data (v1: Bangalore only)
		bangalore/
			static_graph.pt         # PyTorch Geometric graph tensor (edges, node features)
			node_index_map.parquet  # OSM osmid → continuous node index
			gnn_training_master.parquet # Merged training data (joined hourly)
	processed/                # [Backward compat] Symlinks to data/instances/bangalore/
	raw/                      # Raw data pulls (read-only for sync_on_entry.py)
		weather/              # Open-Metoe Historical Forecast API
			2022.parquet        # 8,760 rows — wind, temp, pressure, humidity (hourly)
			2023.parquet
			...
		airquality/           # Open-Metoe Air Quality API (CAMS Global, 45km resolution)
			2022.parquet        # 8,760 rows — NO2, SO2, PM2.5, PM10, CO background context
			...
		stations/             # OpenAQ CPCB ground sensors (station-level resolution)
			meta.parquet        # 23 stations — ID, name, lat, lon, available sensors
			2022.parquet        # ~1.3M rows — NO2, SO2, PM2.5, PM10, CO per station
			...
	graphs/                   # OSMnx road network (read-only for build_graph_tensors.py)
		bangalore_utm.graphml
		bangalore_utm_nodes.parquet
		bangalore_utm_edges.parquet
	gnn/
		training/             # Generated training datasets (not committed)
		checkpoints/          # Saved GNN model weights (not committed)
	README.md                 # This file
	check_data.py             # Data completeness audit script
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

## Data Processing Pipeline

After raw data is pulled, run these scripts **once in order**:

### 1. Repair Historical Gaps (finalize_data_layer.py)

```bash
python scripts/finalize_data_layer.py
```

**What it does**:
- Computes station pollutant ratios from 2023 data (PM2.5/NO2/CO per station)
- Imputes missing 2022 station PM2.5, NO2, CO from PM10 using 2023 ratios
- Repairs city-level 2022 air quality gaps via IDW (Inverse Distance Weighting) from 23 ground stations
- Maps each station to nearest road node using KDTree (WGS84 → UTM43N)
- Outputs: `station_node_map.parquet` with snap distances

**Validation** (current state):
- Remaining 2022 missing count: 0
- Average snap distance: 84.57 m (expected ~80–150m for urban roads)

**Data caveat**: If 2023 has no data, ratio computation falls back to all available rows and logs warning.

### 2. Build Graph Tensors (build_graph_tensors.py)

```bash
python scripts/build_graph_tensors.py
```

**What it does**:
- Loads OSM road network parquets from `data/graphs/` (read-only)
- Creates continuous node indexing: OSM osmid → 0, 1, 2, ... (saved to `node_index_map.parquet`)
- Adds bidirectional edges: for each directed edge (u→v), add reverse edge (v→u)
- Encodes edge attributes as torch tensors:
  - `edge_index` [2, num_edges]: source/target node indices
  - `edge_attr` [num_edges, 1+num_highways]: edge length (m) + one-hot highway type
- Validates graph connectivity: degree distribution, isolated node count, edge length range
- Outputs: `static_graph.pt` (PyTorch tensor), `node_index_map.parquet` (node mapping)

**Validation** (current state):
- Isolated nodes: 0 (100% connectivity)
- Graph density: 2.74 edges per node
- Edge lengths: 0.52 m (min) to 6,884.93 m (max)

### 3. Sync on Entry (sync_on_entry.py)

```bash
python scripts/sync_on_entry.py
```

**What it does**:
- Checks if new weather/AQ/station data is available (read-only scan of `data/raw/`)
- If no new data: prints checkpoint message and exits quietly
- If new data: merges all sources hourly, applies station ratios, attaches node mapping, writes to `gnn_training_master.parquet`, updates README horizon timestamp
- Idempotent: safe to run multiple times (only appends new README notes)

**Auto-activation** (optional):
Add this to `.venv/bin/activate` to run automatically when environment loads:

```bash
if [ -f "$VIRTUAL_ENV/../scripts/sync_on_entry.py" ]; then
	"$VIRTUAL_ENV/bin/python" "$VIRTUAL_ENV/../scripts/sync_on_entry.py"
fi
```

**Example output** on successful sync:
```
[SYNC] Detected 24 new hours of data. Master tensor updated.
[STATUS] New Data Horizon: 2026-03-31 03:00:00 IST.
```

On skip (data already up-to-date):
```
[CHECKPOINT] Data is up to date (Horizon: 2026-03-30 03:00:00 IST). Skipping sync.
```

## Notes

- Weather and air quality data has zero missing values from 2023 onwards
- 2022 air quality has ~25,000 missing values resolved by repair script (IDW from stations)
- 2022 station data has ~22,515 missing pollutants resolved by ratio imputation
- Station data is at 15-minute intervals, resampled to hourly at training time
- All timestamps stored in IST (Asia/Kolkata, UTC+5:30)
- Parquet files use Snappy compression via pyarrow
- For multi-city expansion, duplicate this structure in `data/instances/{new_city}/`; same physics applies city-wide

## Multi-City Readiness

Physics modules (`gnn/plume_physics.py`, `gnn/angular_diffusion.py`, `router/edge_cost.py`) are *city-agnostic*.
All city-specific data lives in `data/instances/{city}/`.

To add a new city (e.g., Delhi):
1. Pull weather, AQ, station data for Delhi into `data/raw/`
2. Run `scripts/finalize_data_layer.py` (repairs gaps using same logic)
3. Run `scripts/build_graph_tensors.py` (builds tensors)
4. Run `scripts/sync_on_entry.py` (merges data)
5. Register city in `shared/physics_config.py` `CITY_INSTANCES` dict
6. Train GNN; physics models work unchanged

See [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) for full multi-city structure and workflow.
