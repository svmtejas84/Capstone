# Urban Toxicity Navigation (Bangalore v1)

Real-time urban toxicity-aware navigation for vulnerable commuters in Bangalore.
The system combines weather, pollutant, sensor, graph, and routing components to produce safer travel corridors instead of shortest-distance-only routes.

**Roadmap**: v1 (Bangalore) → v2 (multi-city with Delhi, Mumbai, etc.)  
**Physics**: City-agnostic models (Gaussian plume, canyon effects, RMV). See [docs/PHYSICS.md](docs/PHYSICS.md).  
**Architecture**: Data-agnostic design. Details in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Documentation

Start here for system-level understanding:
- **[PHYSICS.md](docs/PHYSICS.md)** — Detailed physics model (Gaussian plume, Pasquill stability, urban canyon, RMV, dosimetry) with EPA sourcing.
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** — Multi-city structure, data flow, physics portability, startup automation scripts.
- **[TRAINING_ST_PIGNN.md](docs/TRAINING_ST_PIGNN.md)** — End-to-end ST-PIGNN training playbook (windows, masked loss, AMP, V100 guidance).

## Project Overview

This project models street-level toxicity risk and uses that risk in route and corridor selection.
It is designed for people who are more sensitive to air pollution exposure, including people with respiratory conditions, elderly users, and children.

## Architecture (Text Diagram)

Data Sources -> Ingestor -> Redis Streams -> GNN -> Gale-Shapley -> FastAPI -> Frontend

Flow details:

1. Data Sources provide weather, air quality context, station observations, and graph topology.
2. Ingestor normalizes and publishes live data.
3. Redis Streams hold near-real-time weather/air/sensor streams.
4. GNN computes toxicity-aware edge weights using physics + graph learning.
5. Gale-Shapley matching allocates commuters to equilibrium corridors.
6. FastAPI exposes route, plume, health, and audit APIs.
7. Frontend renders map overlays, route options, and exposure metrics.

## Data Sources

1. **Open-Meteo Forecast API**
   - Provides weather variables: wind speed, direction, temperature, pressure, humidity.
   - No API key required.
   - URL: `archive-api.open-meteo.com` or `api.open-meteo.com`

2. **Open-Meteo Air Quality API**
   - Provides regional background pollutant context (CAMS Global, 45 km resolution).
   - Variables: NO2, SO2, PM2.5, PM10, CO.
   - No API key required.
   - URL: `air-quality-api.open-meteo.com`

3. **AQICN API**
   - Live validation signal from 23 CPCB/KSPCB ground stations in Bangalore.
   - Station-level observations for NO2, SO2, PM2.5, PM10, CO.
   - Requires `AQICN_TOKEN` (set in `.env`).
   - URL: `api.waqi.info`

4. **OpenStreetMap via OSMnx**
   - Road network extraction and graph construction.
   - Graph is projected to UTM Zone 43N (EPSG:32643) and cached at `data/graphs/bangalore_utm.graphml`.

## Data Folder Structure

```
data/
  raw/
    weather/
    airquality/
    stations/
  graphs/
  gnn/
    training/
    checkpoints/
  sensors/
    aqicn_live/
```

## Setup

1. Clone the repository.
2. Create environment file from template:
   ```bash
   cp .env.example .env
   ```
3. Add your AQICN token in `.env`:
   ```
   AQICN_TOKEN=your_token_here
   ```
4. Install dependencies:
   ```bash
   pip install -e .
   ```
5. Start Redis:
   ```bash
   redis-server
   ```
6. Start live ingestion (fetches from Open-Meteo + AQICN):
   ```bash
   python -m ingestion.ingestor
   ```
7. In another terminal, start the API:
   ```bash
   uvicorn router.api.main:app --reload --port 8000
   ```
8. Visit `http://localhost:8000/docs` for interactive API documentation.

### Data Processing Pipeline

After pulling historical data, prepare the training dataset:

```bash
# Step 1: Repair 2022 gaps using IDW + pollutant ratio imputation (run once)
python scripts/finalize_data_layer.py
# Output: Zero missing values in 2022, station_node_map.parquet

# Step 2: Build PyTorch graph tensors from road network (run once per city)
python scripts/build_graph_tensors.py
# Output: data/instances/bangalore/static_graph.pt, node_index_map.parquet

# Step 3: Merge data sources and sync on entry (runs at startup)
python scripts/sync_on_entry.py
# Logic: If new weather/AQ data detected, rebuild training master. Else skip.

# Step 4: Finalize ST-PIGNN assets (temporal repair + train mask + PyG serialization)
python scripts/finalize_gnn_assets.py
# Outputs: gnn_training_tensor_final.parquet, static_graph_pyg.pt
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for script details.

### Recent Hardening (March 2026)

- `scripts/sync_on_entry.py` now persists `data/processed/2023_ratios.parquet` and ensures helper artifacts exist even when sync is skipped.
- New sync logging: `[SYNC] Applying pollutant ratio logic...` on real merge runs.
- Idempotency verified: repeated runs show checkpoint skip when horizon is unchanged.
- `shared/physics_config.py` now defines `PHYSICS_LOSS_LAMBDA = 0.1` for physics-informed training.
- New `scripts/finalize_gnn_assets.py` produces V100-ready artifacts:
   - `data/processed/gnn_training_tensor_final.parquet` (continuous hourly spine)
   - `data/processed/static_graph_pyg.pt` (PyG `Data` with `train_mask` and `physics_lambda`)
- New `gnn/model.py` adds ST-PIGNN (`GINEConv` + `GRU`) with:
   - Masked MSE on sensor nodes only (`train_mask`)
   - Physics penalty term weighted by `PHYSICS_LOSS_LAMBDA`
   - AMP-ready train step for CUDA/V100.

Note: On PyTorch 2.6+, load PyG artifacts with:

```python
torch.load("data/processed/static_graph_pyg.pt", weights_only=False)
```

```bash
# Weather archive (Light, hourly 2022-2026)
python scripts/pull_weather.py

# Air quality archive (CAMS, hourly 2022-2026)
python scripts/pull_airquality.py

# Station archive (CPCB, 15-minute 2022-2026; takes ~2 hours)
python scripts/pull_stations.py
```

Data is stored in `data/raw/` as Parquet files.

## GNN Layer

The GNN layer combines **physics-informed priors** with **learned spatio-temporal patterns**.

### Physics (City-Agnostic)

1. **Gaussian Plume Model**
   - Models pollutant dispersion from street sources.
   - **Pasquill-Gifford stability classes (A–F)** dynamically determined from wind speed, solar radiation, and hour.
   - Distance-decay concentration with stability-dependent dispersion σy and σz.

2. **Urban Canyon Tunneling**
   - Building density (0–1) tunes wind deflection toward street bearing.
   - High-density streets: 85% of wind assumes street direction (canyon effect).
   - Low-density streets: diffusion spreads perpendicular to wind.

3. **Respiratory Minute Volume (RMV)**
   - **Walking**: 1.2 m³/hr (light activity)
   - **Cycling**: 3.5 m³/hr (heavy; ~2.9× than walking)
   - **Driving**: 0.6 m³/hr (cabin protection)
   - **Basis**: EPA Exposure Factors Handbook (2023)

### Learning (Data-Driven)

1. **Spatio-Temporal GNN** (graph neural network)
   - Fuses physics priors with 2022–2026 historical archive.
   - Learns dynamic edge toxicity weights over graph structure.
   - Accounts for time-of-day, seasonality, wind patterns by location.

2. **Training Data**
   - Merged tensor: weather (Open-Metoe) + CAMS regional AQ + CPCB station observations.
   - 23 ground stations snapped to road nodes via KDTree (avg. 84.57 m snap distance).
   - Hourly resolution, IST timezone, interpolated for gaps via IDW from neighbors.

### Model State

Trained weights stored in `gnn/model_weights/pi_gnn_v1.pt` (PyTorch format).
Checkpoints can be updated from stream-backed training tensors.

## Routing Layer

Routing is computed on a **UTM-projected OSMnx graph** (EPSG:32643, UTM Zone 43N) with bidirectional edges.

1. **Edge Cost Computation (Inhaled Dose)**
   - GNN predicts street-level concentration (µg/m³).
   - Multiplied by **Respiratory Minute Volume** and travel time to get biological dose.
   - Formula: `Dose = Concentration × RMV × Travel_Time`
   - Mode-dependent RMV (walking 1.2, cycling 3.5, driving 0.6 m³/hr) accounts for activity intensity.
   - Result: Cyclists show 2.9–6× higher exposure than drivers/pedestrians at same air quality.

2. **A* Search**
   - Pathfinding with toxicity-aware heuristics.
   - Rust/WASM acceleration available for large graphs.
   - Returns top K routes (typically 3) balancing safety and practical constraints.

3. **Route Comparison**
   - Cumulative exposure (µg) for each route.
   - Time and distance penalties.
   - User vulnerability profile adjustments (elderly, respiratory, child).

## Matching Layer

The matcher allocates commuters to equilibrium corridors using **Gale-Shapley stable matching**:

1. **Preference Ranking**
   - Users rank available corridors by toxicity, distance, and time.
   - Derived from GNN edge weights and recent stream state.

2. **Capacity Constraints**
   - Each corridor has a maximum capacity.
   - Prevents demand collapse into a single route.

3. **Segment-Level Control**
   - Enforce special preferences on specific segments.
   - Support isolation-focused behavior during pollution spikes.

4. **Equilibrium Guarantee**
   - No pair (user, corridor) can improve by swapping.
   - Fallback to nearest route if capacity exhausted.

## Deployment

### Local Development

See [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) for step-by-step local setup.

### Docker Compose

Full stack (Redis + ingestion worker + FastAPI):

```bash
docker-compose up
```

API available at `http://localhost:8000`.

### Runtime Components

1. **Redis** (state transport layer)
   - Holds weather:live, airquality:live, sensors:live streams.
   - Provides low-latency state exchange.

2. **Ingestion Worker** (ingestor.py)
   - Async process fetching from Open-Meteo and AQICN.
   - Publishes to Redis streams every 5–15 minutes.

3. **FastAPI Service** (router.api.main)
   - Exposes REST endpoints: /health, /plume, /route, /audit/{hash}.
   - Reads from Redis streams, computes routes, returns results.

4. **Rust/WASM A*** (optional acceleration)
   - Compiled in router/rust_astar/.
   - Speeds up pathfinding on large graphs.

## Multi-City Support (v2 Roadmap)

Physics modules are **city-agnostic**. Only data differs by location.

**Current**: Bangalore v1 (physics + data)  
**Target**: Delhi, Mumbai, Pune, etc. (same physics, new data)

### Extending to New Cities

All physics (Gaussian plume, canyon tunneling, RMV) is universal. To add a new city:

1. Fetch raw data (weather, AQ, sensors) for the city.
2. Run `scripts/finalize_data_layer.py` to repair gaps.
3. Run `scripts/build_graph_tensors.py` to build road graph tensors.
4. Register city in `shared/physics_config.py` (one entry in `CITY_INSTANCES` dict).
5. Train GNN on your city's data; physics modules work unchanged.

See [docs/ARCHITECTURE.md § City Addition Workflow](docs/ARCHITECTURE.md) for detailed steps.

## Audit

The **Stake Audit hash** provides an immutable accountability marker for route generation:

- **Purpose**: Reproducibility, traceability, and compliance review.
- **Contents**: Request, model version, graph snapshot, stream state, timestamps.
- **Endpoint**: `GET /audit/{stake_hash}` returns decision context.

Example:
```bash
curl http://localhost:8000/audit/0xa1b2c3d4... | jq .
```
