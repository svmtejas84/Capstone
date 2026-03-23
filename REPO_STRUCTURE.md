# toxicity-nav — GitHub Repository Structure

> Cross-Scale Geospatial Logic for Real-Time Urban Toxicity Orchestration  
> Major Project, Academic Year 2025–26 · NMIT, VTU

---

## Top-Level Layout

```
toxicity-nav/
├── README.md
├── docker-compose.yml
├── pyproject.toml
├── .env.example
├── .gitignore
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── deploy.yml
│
├── ingestion/          # Module 1 — Live Environmental Component (GEE + Redis)
├── gnn/                # Module 2 — Physics-Informed GNN
├── matcher/            # Module 3 — Equilibrium Matcher (Gale-Shapley)
├── router/             # Module 4 — Deployment Stack (FastAPI + Rust/WASM A*)
├── shared/             # Cross-module utilities, config, schemas
├── frontend/           # React + Leaflet/Deck.gl demo UI
├── data/               # Cached fixtures, raw downloads, simulation seeds
└── notebooks/          # Jupyter EDA, training, and demo notebooks
```

---

## Root Files

### `README.md`
Project overview, architecture summary, quickstart guide, and links to each module's own README.

### `docker-compose.yml`
Orchestrates all services locally:
- `redis` — Redis 7 (Streams enabled)
- `ingestion` — Python ingestion worker
- `api` — FastAPI routing server
- `frontend` — React dev server

### `pyproject.toml`
Single Python project config (PEP 517). Lists all workspace packages (`ingestion`, `gnn`, `matcher`, `router`, `shared`) and shared dev dependencies (`pytest`, `ruff`, `mypy`).

### `.env.example`
Template for required environment variables:
```
GEE_SERVICE_ACCOUNT=
GEE_KEY_FILE=
TOMTOM_API_KEY=
MOSDAC_USERNAME=
MOSDAC_PASSWORD=
MOSDAC_PRODUCT=INSAT_AMV
REDIS_URL=redis://localhost:6379
ERA5_CACHE_DIR=./data/era5_cache
INSAT_REFRESH_MINUTES=15
TRAFFIC_ANOMALY_ALPHA=1.5
```

### `.github/workflows/ci.yml`
Runs on every pull request:
1. `ruff` lint
2. `pytest` for all modules
3. `cargo test` for the Rust A* engine
4. `wasm-pack build` to verify WASM compilation

---

## Module 1 — `ingestion/`

**Purpose:** Creates the "Live State" of the atmosphere. Pulls Sentinel-5P and ERA5 base data, applies INSAT-style intra-day wind updates, injects threshold-gated traffic spikes, and pushes the result to Redis Streams as the shared "Global Truth" Physics Plane.

```
ingestion/
├── README.md
├── __init__.py
├── gee_pipeline.py          # Main ingestion: Sentinel-5P + ERA5 base + INSAT-like wind refresh
├── nowcaster.py             # Multi-latency nowcasting: advects pollution mass using current wind field
├── traffic_spike.py         # Threshold-gated traffic anomaly injection (D > alpha*B)
├── physics_plane.py         # Builds 100m × 100m UTM grid (Graster) for Bangalore
├── redis_publisher.py       # Pushes Physics Plane to Redis Streams as Global Truth
├── bias_correction.py       # TROPOMI underestimation correction layer (East et al. 2022)
├── config.py                # Module-level config (GEE project, grid bounds, refresh interval)
└── tests/
    ├── __init__.py
    ├── test_gee_pipeline.py      # Mock GEE calls, validate NO₂ array shape and dtype
    ├── test_nowcaster.py         # Validate wind advection with known vectors
    ├── test_traffic_spike.py     # Verify threshold gating and anomalous-excess injection
    ├── test_physics_plane.py     # Validate 100m UTM grid bounds over Bangalore
    └── fixtures/
        ├── era5_sample.nc        # Small ERA5 cached NetCDF for offline base-state testing
        └── sentinel5p_sample.nc  # Small TROPOMI NO₂ sample for offline testing
```

### Key Files — Explained

**`gee_pipeline.py`**
- Authenticates with GEE using a service account key
- Pulls Sentinel-5P TROPOMI `NO2_column_number_density` and `SO2_column_number_density`
- Uses ERA5 for base initialization and INSAT AMV feed for intra-day wind refresh
- Returns numpy arrays clipped to Bangalore bounding box
- Refresh interval: every 5–15 minutes (configurable via `INGESTION_REFRESH_MINUTES`)

**`nowcaster.py`**
- Since satellite passes are daily, uses refreshed intra-day winds to "push" the existing pollution mass forward in time
- Implements a 2D Eulerian advection step: `C(x,y,t+dt) = C(x,y,t) - u*dC/dx - v*dC/dy`
- Accepts the current `physics_plane` array and wind vectors `(u, v)` as inputs
- Returns the nowcast concentration array `C(x, y, t)` ready for Redis

**`traffic_spike.py`**
- Queries TomTom Traffic Flow API for current congestion across the Bangalore road network
- Maps road-level congestion to the 100m grid by rasterizing OSMnx edge geometries
- Computes anomaly gate `D(l,t) > alpha * B(l,t)` per segment/time-of-day baseline
- Injects source term `S(x, y, t) = k * (D(l,t) - B(l,t))` only when threshold is exceeded
- Injects `S` into the concentration grid before wind advection begins

**`physics_plane.py`**
- Defines the `Graster` grid: 100m × 100m UTM squares over a configurable bounding box
- Coordinate reference: UTM Zone 43N (EPSG:32643) — appropriate for Bangalore
- Provides `grid_to_latlon()` and `latlon_to_grid()` conversion utilities
- Returns a `GrasterState` dataclass: `{concentration: np.ndarray, wind_u: np.ndarray, wind_v: np.ndarray, source_spike: np.ndarray, timestamp: datetime}`

**`redis_publisher.py`**
- Serializes `GrasterState` to MessagePack (compact binary) and pushes to `XADD toxicity:global_truth`
- Retains last 30 frames (`MAXLEN 30`) for rollback and debugging
- Exposes `get_latest_state()` helper used by Module 2 and Module 3

**`bias_correction.py`**
- Applies a linear correction to TROPOMI vertical column densities before gridding
- Correction factors from East et al. (2022): TROPOMI systematically underestimates urban NO₂
- Configurable multiplier and offset (defaults tuned for Bangalore urban corridor)

---

## Module 2 — `gnn/`

**Purpose:** The predictive "brain." Models Bangalore's road network as a directed graph and propagates pollution wakes between nodes using Gaussian Plume physics, urban canyon corrections, and angularly weighted diffusion. Outputs dynamic edge weights `Cedge`.

```
gnn/
├── README.md
├── __init__.py
├── graph_builder.py         # OSMnx → NetworkX directed graph G=(V,E) for Bangalore
├── raster_sampler.py        # Bilinear interpolation: samples C(x,y,t) for each road edge
├── plume_physics.py         # Gaussian Plume Model + Urban Canyon Correction
├── angular_diffusion.py     # Angularly weighted message passing constrained by wind θ
├── pi_gnn.py                # Spatio-Temporal GNN model (PyTorch Geometric)
├── edge_weights.py          # Computes and caches Cedge per road segment
├── wake_predictor.py        # Predicts 10-minute downwind pollution wake for high-traffic nodes
├── model_weights/           # Saved PyTorch model checkpoints
│   └── pi_gnn_v1.pt
└── tests/
    ├── __init__.py
    ├── test_graph_builder.py        # Validate node/edge count for known Bangalore sub-area
    ├── test_raster_sampler.py       # Check bilinear interpolation against known values
    ├── test_plume_physics.py        # Validate Gaussian Plume output shape and physics
    ├── test_pi_gnn.py               # Forward pass smoke test with fixture data
    └── test_edge_weights.py         # Verify Cedge updates after simulated spike injection
```

### Key Files — Explained

**`graph_builder.py`**
- Uses `osmnx.graph_from_place("Bangalore, India", network_type="drive")` to extract the road network
- Converts to NetworkX `DiGraph` where nodes `V` are intersections and edges `E` are road segments
- Attaches metadata per edge: `length`, `geometry`, `road_type`, `building_density` (from OSM building footprints)
- For Phase 1: uses a cached GraphML file for a 20km × 20km area centred on Hebbal (`data/graphs/bangalore_hebbal.graphml`)

**`raster_sampler.py`**
- For each road edge `eij`, finds the grid cells that the edge geometry intersects
- Performs bilinear interpolation of `C(x, y, t)` from `GrasterState` at the edge midpoint
- Returns a dict `{edge_id: sampled_concentration}` for all edges in the graph

**`plume_physics.py`**
- Implements the Gaussian Plume Model for urban dispersion (Clements et al. 2024)
- `gaussian_plume(Q, x, y, u, sigma_y, sigma_z)` → concentration at downwind point
- `urban_canyon_correction(concentration, building_density, wind_speed)` → applies vertical profile scaling: narrow streets reduce effective wind speed and increase toxicity persistence
- Both functions operate on numpy arrays for vectorised execution over the graph

**`angular_diffusion.py`**
- Implements angularly weighted message passing
- For each node `i`, computes downwind neighbour set `Ni` by filtering edges whose bearing falls within angle `θ ± 45°` of the ERA5 wind direction
- Weight `w_ij = exp(-Δθ² / (2σ²))` where `Δθ` is the bearing deviation from wind direction
- Produces a sparse weight matrix used by the GNN message passing layer

**`pi_gnn.py`**
- `class PIGNN(torch.nn.Module)` built on PyTorch Geometric
- Architecture: 3-layer Spatio-Temporal GNN with `MessagePassing` base class
- `message()`: computes toxicity messages as Gaussian Plume predictions weighted by `angular_diffusion`
- `update()`: aggregates neighbour messages, applies GRU cell for temporal state update
- `forward(data, wind_state)` → returns updated node feature tensor used to derive `Cedge`
- Training labels: ground-truth KSPCB station readings where available; TROPOMI-derived values elsewhere

**`edge_weights.py`**
- Subscribes to Redis Streams (`XREAD` on `toxicity:global_truth`)
- On each new frame, runs `raster_sampler` + `PIGNN.forward()` to produce updated `Cedge` dict
- Writes results back to Redis hash `toxicity:edge_weights:{timestamp}` for consumption by Module 4
- Also updates `wake_predictor` with the new node states

**`wake_predictor.py`**
- For high-traffic source nodes (e.g. Hebbal Flyover — identified by `traffic_spike` values above threshold), runs a 10-minute forward projection of the Gaussian Plume
- Returns `{node_id: predicted_wake_polygon}` — a GeoJSON geometry of the predicted pollution wake downwind
- Used by the frontend for the "Live Plume Demo" visualization

---

## Module 3 — `matcher/`

**Purpose:** Solves the "herd behaviour" problem. Uses Batch Gale-Shapley Stable Matching to distribute commuters across multiple green corridors, preventing any single clean route from becoming overcongested and toxic.

```
matcher/
├── README.md
├── __init__.py
├── commuter_model.py        # Side A: commuter preferences (IDmin, distance tolerance, mode)
├── segment_model.py         # Side B: segment capacity and vulnerability preference
├── quota_manager.py         # Dynamic quota: Quota ∝ 1/Cedge (wind-driven capacity)
├── gale_shapley.py          # Core Batch GS algorithm
├── equilibrium_checker.py   # Validates stability: no blocking pair exists in final allocation
├── route_pool.py            # Assembles candidate "stable routes" from edge-weight graph
└── tests/
    ├── __init__.py
    ├── test_commuter_model.py        # Validate preference list construction
    ├── test_segment_model.py         # Validate capacity and vulnerability ranking
    ├── test_gale_shapley.py          # Correctness: 10-commuter, 3-route scenario
    ├── test_equilibrium_checker.py   # Verify no blocking pair in stable allocation
    └── test_quota_manager.py         # Validate quota update on Cedge change
```

### Key Files — Explained

**`commuter_model.py`**
- `class Commuter(BaseModel)`: fields `id`, `origin`, `destination`, `mode` (`jogger` | `cyclist` | `car`), `id_min` (max tolerable inhaled dose), `distance_tolerance_m`
- `build_preference_list(commuter, route_pool, edge_weights)` → ranks candidate routes by combined score: `α * inhaled_dose_estimate + (1-α) * distance_ratio`
- `α` is mode-specific: higher for joggers (health-first) than for car users

**`segment_model.py`**
- `class Segment(BaseModel)`: fields `id`, `edge_ids`, `current_capacity`, `cedge_mean`, `vulnerability_preference`
- `build_preference_list(segment, commuters)` → segments prefer more vulnerable users (cyclists > car users) when `cedge_mean` is borderline, reserving cleanest corridors for those whose physiology requires it most
- Preference is computed as: `vulnerability_score(mode) / (1 + congestion_penalty)`

**`quota_manager.py`**
- Maintains dynamic capacity for each segment: `Quota ∝ 1 / Cedge_mean`
- When wind is strong (low concentration), capacity opens; stagnant air restricts it
- Updates quotas after each new `edge_weights` frame from Redis
- Enforces minimum quota of 1 per segment to prevent deadlock in the matching

**`gale_shapley.py`**
- Implements Batch Gale-Shapley: commuters (Side A) propose to their most-preferred unrejected segment
- Segment holds tentative match if proposer ranks better than current tentative; else rejects
- Runs until no commuter is unmatched (or until `max_iterations` is hit — fallback assigns remaining commuters to their nearest-distance route)
- Returns `StableAllocation`: `{commuter_id: assigned_route_id}` for all commuters in the batch
- Complexity: `O(n²)` worst case; acceptable for Phase 1 batch size of ≤ 100 simultaneous commuters

**`equilibrium_checker.py`**
- Post-matching validation: iterates over all unmatched commuter-segment pairs
- A "blocking pair" exists if commuter `c` prefers segment `s` over their assignment AND `s` prefers `c` over one of its current assignees
- Returns `is_stable: bool` and a list of any blocking pairs found (should be empty)
- Used in tests and logged to Redis as a health metric

**`route_pool.py`**
- Constructs the set of candidate routes (Side B entries) from the edge-weight graph
- Runs a k-shortest-paths algorithm (`k=5`) from each origin cluster to destination
- Groups physically adjacent paths into "corridor" segments for the matching
- Assigns initial capacity from `quota_manager`

---

## Module 4 — `router/`

**Purpose:** The deployment stack. A FastAPI backend with async workers and a Rust/WASM A* pathfinding engine that computes personalised, mode-aware routes with sub-100ms latency. Every route is cryptographically audited via the "Stake" system.

```
router/
├── README.md
├── __init__.py
│
├── api/
│   ├── main.py              # FastAPI app entry point, lifespan hooks, CORS
│   ├── routes.py            # Endpoint definitions: /route, /plume, /audit, /health
│   ├── dependencies.py      # Shared FastAPI dependencies: Redis client, edge weight cache
│   └── middleware.py        # Request logging, latency tracking
│
├── rust_astar/              # Rust crate — compiled to WASM via wasm-pack
│   ├── Cargo.toml
│   └── src/
│       ├── lib.rs           # WASM entry point, exports route_find() to Python/JS
│       ├── astar.rs         # A* search implementation with custom heuristic
│       ├── graph.rs         # Graph representation (adjacency list, edge weights)
│       └── types.rs         # Shared structs: Node, Edge, RouteResult
│
├── inhalation_rates.py      # IRmode constants and lookup: jogger / cyclist / car
├── edge_cost.py             # W = Σ(Cedge × te × IRmode) computation per path
├── stake_audit.py           # Hash route + env seed for provable routing
└── tests/
    ├── __init__.py
    ├── test_routes.py               # API endpoint integration tests (TestClient)
    ├── test_astar.py                # Rust A* correctness: known graph, known optimal path
    ├── test_edge_cost.py            # Verify W formula for jogger vs car on same route
    ├── test_stake_audit.py          # Verify audit hash is deterministic and unique per state
    └── test_inhalation_rates.py     # Confirm IRmode values match literature (Cui 2021)
```

### Key Files — Explained

**`api/main.py`**
- Creates the FastAPI `app` instance
- Lifespan context manager: on startup connects to Redis, loads latest edge weights into memory, initialises the Rust/WASM module
- CORS configured to allow the React frontend origin

**`api/routes.py`**

*`POST /route`* — Main routing endpoint
```json
Request:  { "origin": [lat, lon], "destination": [lat, lon], "mode": "jogger" }
Response: { "route": [[lat,lon], ...], "total_cost_W": 0.42, "stake_hash": "abc123...", "stable_corridor_id": "c3" }
```

*`GET /plume`* — Returns current GrasterState as GeoJSON for map visualisation
```json
Response: { "grid": { "type": "FeatureCollection", "features": [...] }, "timestamp": "...", "wind_vector": [u, v] }
```

*`GET /audit/{stake_hash}`* — Verifies a past route recommendation
```json
Response: { "valid": true, "route_at_time": [...], "env_seed": "sha256:...", "timestamp": "..." }
```

*`GET /health`* — Liveness probe: checks Redis connectivity and last ingestion timestamp

**`rust_astar/src/astar.rs`**
- Standard A* with a haversine-distance heuristic (admissible for geographic graphs)
- Edge weight: `W = Cedge × te × IRmode` — passed in as a pre-computed weight map
- Returns the optimal path as a vector of node IDs plus the total accumulated cost
- Compiled to `wasm32-unknown-unknown` via `wasm-pack build --target bundler`

**`rust_astar/src/lib.rs`**
- Exposes `#[wasm_bindgen] pub fn route_find(graph_json: &str, weights_json: &str, origin_id: u64, dest_id: u64, ir_mode: f64) -> JsValue`
- Python calls this via `wasmtime` (WASI runtime): `router = WasmRouter("rust_astar/pkg/rust_astar_bg.wasm")`

**`inhalation_rates.py`**
- Constants derived from Cui et al. (2021) and Bigazzi et al. (2015):
  ```python
  IR_MODE = {
      "jogger":  2.75,   # m³/hour — high exertion rate
      "cyclist": 1.80,   # m³/hour — moderate exertion
      "car":     0.65,   # m³/hour — low; add κ (cabin penalty factor) for open windows
  }
  CABIN_PENALTY_FACTOR = 1.41  # Panchal et al. 2022: NO₂ 41-48% higher inside cars
  ```

**`edge_cost.py`**
- `compute_edge_weight(cedge, travel_time_s, mode)` → `W = cedge × (travel_time_s / 3600) × IR_MODE[mode]`
- `compute_path_cost(path_edges, cedge_map, graph, mode)` → `Σ W` over all edges in path
- Travel time `te` derived from edge length / free-flow speed, adjusted by TomTom congestion factor

**`stake_audit.py`**
- On route recommendation: `hash = SHA256(route_node_ids + redis_state_checksum + ISO_timestamp)`
- Stores `{hash: {route, env_seed, timestamp}}` in Redis hash `toxicity:audit_log` (TTL 7 days)
- `verify_audit(hash)` → retrieves and returns the stored record; returns `{"valid": false}` if not found

---

## `shared/`

**Purpose:** Common utilities imported by all four modules. Centralises config, Redis access, Pydantic schemas, and logging.

```
shared/
├── __init__.py
├── config.py              # Loads .env into a Pydantic Settings model; single source of truth
├── redis_client.py        # Async Redis client wrapper; XREAD consumer for Global Truth
├── schemas.py             # Shared Pydantic models: GrasterState, RouteRequest, RouteResponse, AuditRecord
├── logging_utils.py       # Structured JSON logging; attaches request_id to every log line
└── geo_utils.py           # Haversine distance, UTM ↔ WGS84 conversion, bbox helpers
```

### Key Files — Explained

**`config.py`**
```python
class Settings(BaseSettings):
    gee_service_account: str
    gee_key_file: Path
    tomtom_api_key: str
    redis_url: str = "redis://localhost:6379"
    grid_bbox: tuple[float, float, float, float] = (12.834, 77.461, 13.144, 77.781)  # Bangalore
    ingestion_refresh_minutes: int = 15
    astar_timeout_ms: int = 100
```

**`schemas.py`**
- `GrasterState`: `concentration: np.ndarray`, `wind_u: np.ndarray`, `wind_v: np.ndarray`, `source_spike: np.ndarray`, `timestamp: datetime`
- `RouteRequest`: `origin: tuple[float,float]`, `destination: tuple[float,float]`, `mode: Literal["jogger","cyclist","car"]`
- `RouteResponse`: `route: list[tuple[float,float]]`, `total_cost_W: float`, `stake_hash: str`, `stable_corridor_id: str`
- `AuditRecord`: `route: list`, `env_seed: str`, `timestamp: datetime`

---

## `frontend/`

**Purpose:** React demo application for the three demonstration milestones. Uses Leaflet for 2D map and Deck.gl for 3D heatmap layers.

```
frontend/
├── package.json
├── vite.config.ts
├── src/
│   ├── App.tsx
│   ├── api/
│   │   └── client.ts          # Typed wrappers around /route, /plume, /audit endpoints
│   ├── components/
│   │   ├── PlumeMap.tsx        # Demo 1: 3D Deck.gl GridLayer showing 100m Physics Plane shifting with wind
│   │   ├── RoutePanel.tsx      # Demo 1+2: Mode selector (jogger/cyclist/car), origin/dest picker, route result overlay
│   │   ├── AgentSim.tsx        # Demo 2: Animated "Cyclist" agent replanning in real-time as GNN pushes wake
│   │   ├── AuditViewer.tsx     # Demo 3 (partial): Input a stake hash → display route + atmospheric state at time
│   │   └── EquilibriumViz.tsx  # Demo 3: Multiple user origins → visualise GS-distributed green corridors
│   ├── hooks/
│   │   ├── usePlumeStream.ts   # Polls /plume every 15s, returns GeoJSON state
│   │   └── useRouteResult.ts   # Calls /route, returns route + stake hash
│   └── styles/
│       └── index.css
```

### Component Descriptions

**`PlumeMap.tsx`** — "Live Plume" Demo
- Renders a `Deck.gl GridLayer` over Bangalore using the `/plume` GeoJSON response
- Cell colour encodes NO₂ concentration (low=green → high=red)
- Wind vector arrows overlaid using a `ScatterplotLayer`
- Auto-refreshes every 15 seconds via `usePlumeStream`

**`RoutePanel.tsx`** — Route UI
- Leaflet map with clickable origin/destination pin placement
- Mode toggle: Jogger / Cyclist / Car
- On submit: calls `/route`, draws polyline coloured by per-edge `Cedge`
- Shows `total_cost_W` and `stake_hash` in a side panel

**`AgentSim.tsx`** — "Dynamic Reroute" Demo
- Simulates a cycling agent moving along the recommended route
- Subscribes to `/plume` stream; when a new pollution wake intersects the current path, calls `/route` again and animates the agent pivoting to the new path
- Displays a "Pollution Wake Alert" banner triggered by the GNN wake prediction

**`EquilibriumViz.tsx`** — "Equilibrium Proof" Demo
- Places 10 simulated users at the same origin
- Calls `/route` in batch, then visualises each assigned corridor with a distinct colour
- Shows a histogram: "users per corridor" to demonstrate that no single green path is overloaded

**`AuditViewer.tsx`** — "Stake" Audit UI
- Text input for a `stake_hash`
- Calls `/audit/{hash}` and renders the stored route on the map alongside the atmospheric state (concentration + wind) that was active at that timestamp

---

## `data/`

```
data/
├── README.md
├── era5_cache/              # Downloaded ERA5 .nc files (gitignored; use DVC or LFS)
├── sentinel5p_cache/        # Downloaded TROPOMI .nc files (gitignored)
├── fixtures/                # Small pre-processed samples committed to repo for offline testing
│   ├── bangalore_20km_era5.nc
│   ├── bangalore_20km_no2.nc
│   └── hebbal_traffic_spike_sim.json
└── graphs/
    ├── bangalore_hebbal.graphml    # Pre-built OSMnx graph for 20km × 20km Hebbal area
    └── bangalore_full.graphml      # Full city graph (gitignored — too large; regenerate with graph_builder.py)
```

---

## `notebooks/`

```
notebooks/
├── 01_eda_physics_plane.ipynb      # Visualise Sentinel-5P + ERA5/INSAT hybrid over Bangalore; validate 100m grid
├── 02_gnn_training.ipynb           # Full PyTorch Geometric training loop for PI-GNN; loss curves
├── 03_plume_validation.ipynb       # Compare Gaussian Plume predictions vs KSPCB station readings
├── 04_gale_shapley_demo.ipynb      # Interactive GS matching on 20 simulated commuters; equilibrium proof
├── 05_astar_benchmark.ipynb        # Benchmark Rust/WASM A* latency vs Python NetworkX Dijkstra
└── 06_route_comparison.ipynb       # Side-by-side: standard (shortest) route vs toxicity-minimised route; dose delta
```

---

## Technology Stack Summary

| Layer | Technology | Purpose |
|---|---|---|
| Satellite data | Sentinel-5P TROPOMI via GEE | NO₂, SO₂ base toxicity |
| Atmospheric driver | ERA5 base + INSAT-3D/3DR AMV updates | Wind vectors, BLH cadence |
| Traffic proxy | TomTom Traffic Flow API + baseline profiler | Threshold-gated source spike |
| Road network | OSMnx (OpenStreetMap) | Graph G=(V,E) |
| State layer | Redis 7 Streams | Global Truth (GrasterState) |
| GNN framework | PyTorch Geometric | PI-GNN message passing |
| Physics | Gaussian Plume + canyon corrections | Edge weight prediction |
| Matching | Gale-Shapley (Python) | Equilibrium route distribution |
| API backend | FastAPI + asyncio | Routing server |
| Pathfinding | Rust compiled to WASM | Sub-100ms A* |
| WASM runtime | wasmtime (Python bindings) | Rust→Python bridge |
| Frontend | React + Vite + Leaflet + Deck.gl | Demo UI |
| Containerisation | Docker Compose | Local dev orchestration |

---

## Phase 1 Simulation Mode

For Major Project Phase 1, all modules support a simulation mode using cached data instead of live APIs:

- `ingestion`: set `SIMULATION_MODE=true` — reads from `data/fixtures/` instead of calling GEE
- The simulation area is a 20km × 20km bounding box centred on **Hebbal, Bangalore**
- A synthetic traffic spike at Hebbal Flyover is pre-injected to demonstrate the Live Plume and Dynamic Reroute demos
- The GS matcher is seeded with 10 simulated commuters from Hebbal to MG Road

---

## Functional Requirement Mapping

| FR ID | Requirement | Files Responsible |
|---|---|---|
| FR1 | 100m Physics Plane, refreshed every 15 min | `ingestion/physics_plane.py`, `ingestion/gee_pipeline.py`, `ingestion/redis_publisher.py` |
| FR2 | PI-GNN dynamic Cedge for 10km × 10km sub-graph | `gnn/pi_gnn.py`, `gnn/edge_weights.py`, `gnn/plume_physics.py` |
| FR3 | Mode-aware A* routing, W = Σ(Cedge × te × IRmode), sub-200ms | `router/rust_astar/`, `router/edge_cost.py`, `router/inhalation_rates.py` |
| FR4 | GS matching: 10 commuters → ≥2 distinct stable routes | `matcher/gale_shapley.py`, `matcher/route_pool.py`, `matcher/quota_manager.py` |

---

*Generated for toxicity-nav · Major Project Phase 1 · NMIT VTU 2025-26*
