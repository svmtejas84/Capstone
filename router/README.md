# router

FastAPI serving toxicity-aware routing endpoints with diagnostics and audit support.

## Responsibilities

- Expose REST API for route computation and diagnostics.
- Serve plume visibility and exposure metrics.
- Implement Rust/WASM A* acceleration for path search on toxicity-weighted graphs.
- Provide audit trail and stake hashing for decision reproducibility.
- Compute edge costs using GNN-derived toxicity weights and physical constraints.

## Endpoints

### Health Check

```
GET /health
```

Returns API and stream status.

**Response:**
```json
{
  "status": "ok",
  "streams": {
    "weather:live": 42,
    "airquality:live": 41,
    "sensors:live": 39
  }
}
```

### Plume (Diagnostics)

```
GET /plume?lat=12.95&lon=77.55
```

Returns toxicity snapshot and grid state at given location.

**Query Params:**
- `lat`, `lon`: WGS84 coordinates.
- Optional: `grid_res` (default 100 m).

**Response:**
```json
{
  "location": {"lat": 12.95, "lon": 77.55},
  "toxicity_level": 42.5,
  "nearby_sources": [
    {"distance_m": 150, "concentration": 25.3, "pollutant": "NO2"}
  ],
  "grid_cells": [...]
}
```

### Route (Main Endpoint)

```
POST /route
```

Compute toxicity-aware route(s) from origin to destination.

**Request:**
```json
{
  "start": {"lat": 12.93, "lon": 77.61},
  "end": {"lat": 12.97, "lon": 77.57},
  "user_profile": "vulnerable",
  "num_routes": 3
}
```

**Response:**
```json
{
  "routes": [
    {
      "path": [{"lat": 12.93, "lon": 77.61}, ...],
      "distance_m": 2500,
      "estimated_exposure": 145.2,
      "estimated_time_s": 420,
      "toxicity_percentile": 35
    }
  ],
  "plume_state": {...},
  "stake_hash": "0xa1b2c3d4..."
}
```

**Optional Query Params:**
- `mode`: "fastest", "safest", or "balanced" (default: "balanced").

### Audit Trail

```
GET /audit/{stake_hash}
```

Retrieve decision context for a specific route (for reproducibility and compliance).

**Response:**
```json
{
  "stake_hash": "0xa1b2c3d4...",
  "timestamp": "2026-03-29T12:34:56Z",
  "graph_state": {...},
  "edge_weights": {...},
  "model_version": "pi_gnn_v1",
  "request_context": {...}
}
```

## Core Modules

### A* Pathfinding

- Base algorithm in `router/edge_cost.py`.
- Rust/WASM acceleration available in `router/rust_astar/`.
- Edge costs computed as **inhaled dose** (concentration × RMV × time), not just distance.

### Edge Cost Computation

- File: `router/edge_cost.py`
- Computes biological dose intake using **EPA-standard RMV values** from `shared/physics_config.py`:
  - Walking: 1.2 m³/hr (light activity)
  - Cycling: 3.5 m³/hr (heavy activity, ~2.9× pedestrian)
  - Two wheeler (`two_wheeler`): 0.6 m³/hr (current motorized baseline)
  - Legacy aliases: `driving`, `car` (kept for compatibility/reference)
- Formula: `Dose = Concentration (µg/m³) × RMV (m³/hr) × Travel_Time (hr)`
- Result: cyclists' routes weighted ~3× higher exposure than two-wheeler riders/pedestrians on same streets
- **Deprecated**: `inhalation_rates.py` (replaced by centralized physics_config)

### Stake Audit

- Immutable hash of route-generation context.
- File: `router/stake_audit.py`.
- Includes: request, model state, graph snapshot, timestamps.

## Configuration

Router settings from `shared/config.py`:

- Redis URL (stream source).
- API origin (CORS).
- Grid bounding box (Bangalore UTM extent).
- Frontend origin for CORS.

## Run Locally

```bash
# Ensure Redis and ingestion worker are running
redis-server
python -m ingestion.ingestor

# Start API server
uvicorn router.api.main:app --reload --port 8000
```

Then visit `http://localhost:8000/docs` for interactive Swagger UI.

## Running with Docker

See `docker-compose.yml` for full stack (Redis + ingestion + API):

```bash
docker-compose up
```

API will be available at `http://localhost:8000`.

## Testing

Unit tests in `tests/`:

```bash
pytest router/tests/
```

Requires FastAPI test client dependencies. If unavailable, run matcher/gnn tests separately.

## Performance Notes

- Plume computation: ~10–50 ms depending on grid resolution.
- Route search (A*): ~50–200 ms depending on graph size and destination.
- Full request latency (typical): 100–300 ms with warm cache.
- Latency degrades if stream lag exceeds 2 minutes.

