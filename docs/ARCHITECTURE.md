# Multi-City GNN Architecture

This document describes the current structure for **Bangalore v1** and the path to **multi-city support (v2+)**.

For detailed physics foundations (Gaussian plume, Pasquill stability, urban canyon, RMV), see [PHYSICS.md](PHYSICS.md).
For model training workflow, see [TRAINING_ST_PIGNN.md](TRAINING_ST_PIGNN.md).

## Current Directory Structure (v1 — Bangalore)

```
├── gnn/                              # Core GNN & physics modules
│   ├── plume_physics.py              # Gaussian plume, Pasquill stability, canyon effects
│   ├── angular_diffusion.py          # Wind directional diffusion with canyon tunneling
│   ├── edge_weights.py               # Graph edge weight computation
│   ├── graph_builder.py              # Load & prepare graphs
│   ├── pi_gnn.py                     # Core GNN training & inference
│   ├── wake_predictor.py             # Wake field predictions
│   ├── model_weights/
│   │   └── pi_gnn_v1.pt              # Trained weights
│   ├── tests/                        # Unit tests
│   └── core/                         # [v2+] Will hold refactored modules
│   
├── shared/                           # City-agnostic config & utilities
│   ├── physics_config.py             # ← NEW: Pasquill stability, RMV, roughness, city registry
│   ├── config.py                     # General app config
│   ├── schemas.py                    # Data models
│   ├── geo_utils.py                  # Coordinate transforms (WGS84 ↔ UTM43N)
│   ├── logging_utils.py
│   └── redis_client.py
│   
├── router/
│   ├── edge_cost.py                  # ← REFACTORED: Inhaled dose via physics_config RMV
│   ├── inhalation_rates.py           # [Deprecated]
│   ├── api/
│   ├── rust_astar/                   # C++ Dijkstra/A* backend
│   └── tests/
│   
├── matcher/                          # Corridor matching algorithms
│   ├── gale_shapley.py
│   ├── equilibrium_checker.py
│   ├── quota_manager.py
│   └── tests/
│   
├── ingestion/                        # Data fusion & real-time updates
│   ├── data_fusion.py
│   ├── nowcaster.py
│   ├── pull_gnn_training_data.py
│   ├── redis_publisher.py
│   └── tests/
│   
├── scripts/
│   ├── finalize_data_layer.py        # ← NEW: Repair 2022, IDW + ratio imputation
│   ├── build_graph_tensors.py        # ← NEW: Node indexing, bidirectional edges, PyTorch tensors
│   ├── sync_on_entry.py              # ← NEW: Welcome gate with checkpoint logic
│   ├── pull_weather.py
│   ├── pull_airquality.py
│   ├── pull_stations.py
│   └── quickstart.sh
│   
├── data/
│   ├── instances/
│   │   └── bangalore/
│   │       ├── graph/
│   │       │   ├── topology_graph.pt       # PyTorch Geometric graph tensor (edges + attributes)
│   │       │   ├── topology_graph_pyg_inference.pt # PyG-ready graph object
│   │       │   ├── topology_nodeid_to_index_map.parquet # OSM osmid → node index mapping
│   │       │   └── station_to_topology_node_map.parquet # Station-to-node lookup
│   │       └── model_input/
│   │           └── model_input_node_hourly_features.parquet # Merged training data (weather + AQ + sensors)
│   ├── processed/                    # Processed workspace root
│   ├── graphs/ (read-only)           # Raw OSM road network
│   │   ├── bangalore_utm.graphml
│   │   ├── bangalore_utm_nodes.parquet
│   │   └── bangalore_utm_edges.parquet
│   ├── raw/ (read-only)              # Data pulls (weather, AQ, sensors)
│   │   ├── weather/
│   │   ├── airquality/
│   │   └── stations/
│   ├── gnn/
│   │   ├── training/
│   │   └── checkpoints/
│   ├── README.md                     # Data documentation & sync-gate notes
│   ├── check_data.py
│   └── fixtures/
│   
├── docs/
│   ├── PHYSICS.md                    # Physics model (Gaussian, Pasquill, canyon, RMV, dose)
│   └── ARCHITECTURE.md               # This file
│   
└── notebooks/
    ├── 01_eda_physics_plane.ipynb
    ├── 02_gnn_training.ipynb
    └── ...
```

## Physics Abstraction: City-Agnostic Computation

All **physics** is universal; only **data** is city-specific.

| Layer | Module | Universal? | Inputs | Outputs |
|-------|--------|---|---|---|
| **Atmospheric** | `gnn/plume_physics.py` | ✓ | Wind, stability class, distance, pollutant conc. | Dispersed concentration (µg/m³) |
| **Urban** | `gnn/angular_diffusion.py` | ✓ | Wind direction, street bearing, building density | Directional weight (canyon tunneling) |
| **Human** | `router/edge_cost.py` | ✓ | Concentration, travel time, transport mode | Inhaled dose (µg) |
| **Config** | `shared/physics_config.py` | ✓ | (Constants only) | Pasquill params, RMV, stability lookup |
| **Data** | — | ✗ | Graph, weather, air quality, sensors | Training master tensor |

### Key Refactoring (March 2026)

#### 1. Stability-Aware Dispersion

Previously: hardcoded dispersion coefficients.  
Now: `dispersion_sigmas(distance_m, stability)` uses **Pasquill-Gifford classes A–F**:

```python
from gnn.plume_physics import dispersion_sigmas
from shared.physics_config import StabilityClass

# Class A (unstable, sunny afternoon, high wind)
σy, σz = dispersion_sigmas(100, StabilityClass.A)  # → σy=25.8m, σz=18.3m

# Class D (neutral, overcast, medium wind) — most common
σy, σz = dispersion_sigmas(100, StabilityClass.D)  # → σy=20.0m, σz=6.0m

# Class F (stable, night, low wind)
σy, σz = dispersion_sigmas(100, StabilityClass.F)  # → σy=10.0m, σz=1.6m
```

Stability is computed dynamically from weather:
```python
from shared.physics_config import get_pasquill_stability

stability = get_pasquill_stability(
    wind_speed_ms=2.5, 
    solar_radiation_wm2=150,  # W/m² at ground
    is_night=False
)  # → StabilityClass.B
```

#### 2. Canyon Tunneling

Previously: no urban canyon effects.  
Now: `directional_diffusion_weight(..., building_density)` applies **wind deflection**:

- **Low density (0.5)**: Wind freely spreads perpendicular. Weight ≈ 1.0 if aligned with street.
- **High density (0.8)**: Wind funnels along streets. Blends 85% toward street bearing regardless of meteorological wind.

```python
from gnn.angular_diffusion import directional_diffusion_weight

# Street runs north, wind is west. Low density → low weight.
weight_low = directional_diffusion_weight(
    edge_bearing=0,      # north
    wind_direction=270,  # west
    building_density=0.5
)  # → 0.2 (perpendicular, poor mix)

# Same street, high density → high weight (canyon funneling).
weight_high = directional_diffusion_weight(
    edge_bearing=0,
    wind_direction=270,
    building_density=0.8
)  # → 0.85 (canyon forces downwind flow despite cross-wind)
```

#### 3. Respiratory Minute Volume (RMV) — EPA Standard

Previously: single hardcoded rate.  
Now: mode-dependent from `shared/physics_config.RespiratoryCostant`:

| Mode | RMV (m³/hr) | Activity Level | Biological Basis |
|------|---|---|---|
| Walking | 1.2 | Light | 2.5 L/min @ 60 breaths/min × vol |
| Cycling | 3.5 | Heavy | 5.8 L/min @ 60 breaths/min (Ernst et al., 2015) |
| Driving | 0.6 | Light (cabin effect) | ~50% baseline due to HVAC |

**Result**: Cyclists' inhaled dose = 2.9–6× pedestrians at same air quality.

```python
from shared.physics_config import get_respiratory_minute_volume

rmv_walking = get_respiratory_minute_volume("walking")   # 1.2 m³/hr
rmv_cycling = get_respiratory_minute_volume("cycling")   # 3.5 m³/hr

# Example: 50 µg/m³, 300s journey
dose_walking = 50 * 1.2 * (300/3600)  # 5.0 µg
dose_cycling = 50 * 3.5 * (300/3600)  # 14.58 µg

print(dose_cycling / dose_walking)  # 2.916× (EPA ratio holds)
```

## Startup Automation

### Welcome Gate: `scripts/sync_on_entry.py`

Runs **once per session start**, checks data freshness:

```bash
python scripts/sync_on_entry.py
```

**Logic**:
1. Scan `data/raw/` for latest hour (UTC, then normalize to local IST)
2. Compare to `processed/model_input/model_input_node_hourly_features.parquet` horizon
3. **If no new data**: `[CHECKPOINT] Data is up to date` → exit
4. **If new data**: print `[SYNC] Applying pollutant ratio logic...`, merge weather + AQ + stations, apply ratio-based pollutant imputation, save to `processed/`, append README with sync timestamp
5. **Idempotent**: Safe to run multiple times; only appends new timestamps

**Helper persistence guarantees**:
- `data/processed/graph/station_to_topology_node_map.parquet` is required and validated at runtime.
- `data/processed/2023_ratios.parquet` is cached and persisted for ratio reuse.
- Ratio cache is ensured even during checkpoint skip paths.

Used as a **post-pull hook**:
```bash
# After pulling new data from Open-Metoe/CAMS/OpenAQ
python scripts/sync_on_entry.py  # ← Auto-runs; builds merged training tensor
```

### Data Repair: `scripts/finalize_data_layer.py`

Run **once during setup** to clean 2022 gaps (59% missing before repair):

```bash
python scripts/finalize_data_layer.py
```

**Steps**:
1. Compute 2023 station **pollutant ratio fingerprint** (PM2.5/NO2/CO) per station
2. Impute missing 2022 pollutants in PM10-only records using 2023 ratios
3. **IDW interpolation** from 23 ground stations to fill remaining gaps in merged data
4. **Station-to-node mapping**: KDTree snap each station to nearest road node (avg 84.57m) for training
5. Output: Zero missing values, station_to_topology_node_map.parquet for node attachment

### Graph Tensor Build: `scripts/build_graph_tensors.py`

Run **once per city** to convert OSM network → PyTorch Geometric:

```bash
python scripts/build_graph_tensors.py
```

**Output**:
- `data/processed/graph/topology_nodeid_to_index_map.parquet`: OSM osmid → continuous node index
- `data/processed/graph/topology_graph.pt`: Torch tensor with:
    - `x` [num_nodes, 17]: sanitized node features aligned to road nodes via UTM KDTree nearest-neighbor join
  - `edge_index` [2, num_edges]: bidirectional edges
    - `edge_attr` [num_edges, 1+num_highways]: length (m) + case-insensitive one-hot highway type
    - Validation: 0 isolated nodes, 2.74 edges/node density, 0.52–6884 m edge range
    - Data-quality checks: `graph.x` has zero NaNs, zero all-zero rows, and physically clamped PM2.5/humidity/temperature/elevation ranges

**To adjust for local physics** (e.g., higher air mixing in coastal cities), tune the single parameters in `UrbanCanyon` or `RespiratoryCostant`.

### Final GNN Asset Build: `scripts/finalize_gnn_assets.py`

Run after sync to finalize model-ready assets:

```bash
python scripts/finalize_gnn_assets.py
```

**What it does in one pass**:
1. Repairs temporal continuity on `model_input/model_input_node_hourly_features.parquet` by building a complete hourly spine per `node_id`.
2. Interpolates AQ columns (`station_*`, `city_*`) and forward/backward fills weather columns (`weather_*`).
3. Creates `train_mask` from station-to-topology mapping using `graph/topology_nodeid_to_index_map.parquet`.
4. Converts `graph/topology_graph.pt` dict payload into PyG `Data` and stores:
    - `edge_index`
    - `edge_attr`
    - `num_nodes`
    - `train_mask` (23 labeled sensor nodes)
    - `physics_lambda` (from `PHYSICS_LOSS_LAMBDA`)
5. Runs `data.validate(raise_on_error=True)` and prints isolated/self-loop checks.

**Outputs**:
- `data/processed/model_input/model_input_node_hourly_features.parquet`
- `data/processed/graph/topology_graph_pyg_inference.pt`

**Current validation snapshot**:
- Temporal continuity: `bad_steps=0`
- `train_mask` true count: `23`
- Isolated nodes: `False`
- Self loops: `False`

On PyTorch 2.6+, load with:

```python
data = torch.load("data/processed/graph/topology_graph_pyg_inference.pt", weights_only=False)
```

## ST-PIGNN Model

`gnn/model.py` now provides a Spatio-Temporal Physics-Informed GNN:

- **Spatial encoder**: `GINEConv` stack over `edge_index` + `edge_attr`.
- **Temporal encoder**: `GRU` over node embeddings from a 12-hour sliding window.
- **Output head**: one scalar per node (predicted PM2.5 concentration).

### Training Loss

Total loss:

$$
\mathcal{L} = \mathcal{L}_{data} + \lambda_{physics} \cdot \mathcal{L}_{physics}
$$

- $\mathcal{L}_{data}$: MSE only on nodes where `train_mask == True`.
- $\mathcal{L}_{physics}$: upwind consistency penalty with Gaussian-plume-weighted edge severity.
- $\lambda_{physics}$: `PHYSICS_LOSS_LAMBDA` from `shared/physics_config.py` (default `0.1`).

### V100 Readiness

`train_step_amp(...)` in `gnn/model.py` includes:
- `.to(device)` tensor movement
- `autocast(...)` mixed precision
- `GradScaler` for stable AMP training on CUDA Tensor Cores.

## Future Enhancements

1. **City-Specific GNN Models**: Create `gnn/instances/{city}/model.py` if needed for custom architectures.
2. **Dynamic Stability Mapping**: Use local solar radiation & cloud climatology databases.
3. **Landuse Roughness**: Integrate landuse raster maps to compute spatial $z_0(x,y)$ for each node.
4. **Transport Mode Distribution**: Estimate local modal split (walking %, cycling %) to weight routes by real usage.

