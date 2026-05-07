# Data/Processed Folder Structure & V100 Workflow Guide

## 📊 data/processed/ Organization

### Core Directories

#### `model_input/` ⭐ **START HERE FOR V100**
- **`model_input_node_hourly_features.parquet`**: Final ready-to-train temporal feature tensor
  - Hourly observations at each topology node
  - Columns: node_id, timestamp, pollutant_levels (PM2.5, NO2, O3, etc.), weather features
  - Time span: 2022 + 2024-2026 (note: 2023 intentionally absent)
  - **Shape**: ~hourly observations × ~115 nodes × ~12 features
  - **Use case**: Direct input to ST-PIGNN model training on V100

#### `graph/` ⭐ **CRITICAL FOR GNN TRAINING**
- **`topology_graph_pyg_inference.pt`**: PyTorch Geometric graph object (use this!)
  - Pre-built PyG Data object with node features, edges, and train/val/test masks
  - Ready for direct loading: `graph = torch.load('topology_graph_pyg_inference.pt')`
  - Includes physics metadata and node features
  
- **`topology_graph.pt`**: Base PyTorch tensor representation
  - Alternative format if PyG isn't needed
  
- **`station_to_topology_node_map.parquet`**: Station → node mapping
  - Maps each of ~40 stations to nearest topology grid node
  - Contains snap distance and spatial coordinates
  
- **`topology_nodeid_to_index_map.parquet`**: Node ID → contiguous index
  - Maps internal node IDs to 0..114 model indices (needed for embedding layers)

#### `stations/` **PROCESSED STATION DATA (YEAR-SPLIT)**
- **`2022.parquet`**: 269,462 rows of 2022 station observations
- **`2024.parquet`**: 194,615 rows of 2024 station observations  
- **`2025.parquet`**: 487,379 rows of 2025 station observations
- **`2026_partial.parquet`**: 122,351 rows (2026-01-01 to 2026-03-31)

**⚠️ NOTE: 2023 IS INTENTIONALLY ABSENT**
- OpenAQ station source yielded no observed 2023 data
- This is by design; don't assume a missing file indicates a broken build
- If you need 2023 data, see `gapfill/station_timeseries_observed_imputed.parquet` (imputed values)

**Content**: Station-level observations (pollutant concentrations, metadata)
**Use case**: Understanding raw station distributions, debugging, validation

#### `gapfill/` **IMPUTATION & METHODOLOGY**
- **`station_timeseries_observed_imputed.parquet`**: Full derived station layer
  - Combines observed + imputed values for missing periods
  - Includes 2023 imputed values (when observed are missing)
  - Source of truth for station data before node aggregation
  
- **`gapfill_selected_method_policy.parquet`**: Per-pollutant imputation policy
  - Which method (KNN, interpolation, forward-fill, etc.) used for each pollutant
  
- **`gapfill_benchmark_method_scores.parquet`**: Methodology benchmark results
  
- **`station_timeseries_imputation_summary.parquet`**: Imputation statistics
  - Count of observed vs imputed by pollutant/time period
  
- **`gapfill_benchmark_report.md`** & **`station_timeseries_imputation_build_report.md`**: Human-readable reports

**Use case**: Understanding data quality, imputation methodology, validation

#### `airquality/` & `weather/` **RAW PROCESSED COPIES**
- **`2022.parquet` through `2026_partial.parquet`**: Raw sensor/weather data (year-split)
- These are copies of raw/ data (UTC-normalized) inside processed/ for isolated V100 environments
- **Do NOT use directly for training**: Use `model_input/` and `graph/` instead

**Content**: Raw observations from AQICN (airquality) and Open-Meteo (weather)
**Use case**: Data exploration, debugging, re-derivation of processed layers

#### `checkpoints/` **RESUME STATE**
- **`.checkpoint_airquality.json`, `.checkpoint_weather.json`, etc.**
- Track completion status of ingestion pipelines
- Used by pull scripts to resume after interruption
- **Not needed for V100 training** (data already pulled)

#### `logs/` **OPERATION RECORDS**
- **`targeted_missing_pull_log.md`, `remap_2023_retry_log.md`**: Detailed recovery reports
- **`*_events.parquet`**: Event tables with timing, row counts, status
- **Use case**: Auditing data pipeline, understanding what was recovered

#### `audits/` **TRACEABILITY**
- **`processed_file_timestamps_2026-04-15.txt`**: Inventory snapshot
- Verifies recency of processed artifacts
- **Not critical for training**

#### `source_docs/` **CONTEXT**
- Copy of raw data README for reference
- **Not critical for training**

---

## 🔄 Recommended V100 Data Loading Pattern

```python
# 1. Load the graph
import torch
graph = torch.load('data/processed/graph/topology_graph_pyg_inference.pt')
# graph.x = node features, graph.edge_index = edges, graph.train_mask, etc.

# 2. Load node mappings
import pandas as pd
node_map = pd.read_parquet('data/processed/graph/topology_nodeid_to_index_map.parquet')

# 3. Load model input tensor
features = pd.read_parquet('data/processed/model_input/model_input_node_hourly_features.parquet')

# 4. (Optional) Load raw station data for validation
stations_2022 = pd.read_parquet('data/processed/stations/2022.parquet')
stations_2024 = pd.read_parquet('data/processed/stations/2024.parquet')
# ... etc

# 5. (Optional) Load imputation quality info
gapfill_policy = pd.read_parquet('data/processed/gapfill/gapfill_selected_method_policy.parquet')
```

---

## 📓 Notebooks & Recommended Workflow Order

### Notebook Overview

| # | Notebook | Status | Purpose | Depends On |
|---|---|---|---|---|
| 1 | `01_eda_physics_plane.ipynb` | Empty | EDA of physics/plume dynamics | (none) |
| 2 | `01_gnn_v100_training.ipynb` | **Has content** | ST-PIGNN training on V100 | `model_input/`, `graph/` |
| 3 | `02_gnn_training.ipynb` | Empty | Alternative GNN training setup | `model_input/`, `graph/` |
| 4 | `03_plume_validation.ipynb` | Empty | Validate plume predictions vs physics | GNN outputs |
| 5 | `04_gale_shapley_demo.ipynb` | Empty | Demo of Gale-Shapley matching | Router outputs |
| 6 | `05_astar_benchmark.ipynb` | Empty | A* routing algorithm benchmarks | Router outputs |
| 7 | `06_route_comparison.ipynb` | Empty | Compare routing strategies | Router + GNN outputs |

### Recommended Workflow Order for V100 Training

```
Start
  ↓
1. 01_gnn_v100_training.ipynb (existing template for training)
  │
  ├─→ Load graph + model_input data
  ├─→ Initialize ST-PIGNN model
  ├─→ Train on 2022 + 2024-2026 data
  ├─→ Save checkpoints to gnn/model_weights/
  └─→ Generate predictions
  ↓
2. 03_plume_validation.ipynb (validate outputs)
  │
  ├─→ Load GNN predictions
  ├─→ Compare against physics constraints
  ├─→ Visualize plume dynamics
  └─→ Refine model if needed
  ↓
3. 04_gale_shapley_demo.ipynb (matching algorithm)
  │
  ├─→ Use GNN predictions as emission estimates
  ├─→ Run Gale-Shapley commuter matching
  └─→ Output route assignments
  ↓
4. 05_astar_benchmark.ipynb (routing optimization)
  │
  ├─→ Benchmark A* with different heuristics
  ├─→ Compare to baseline routing
  └─→ Identify performance bottlenecks
  ↓
5. 06_route_comparison.ipynb (strategy comparison)
  │
  ├─→ Compare all routing strategies
  ├─→ Evaluate health impact metrics
  └─→ Generate final reports
  ↓
Done
```

### What Each Notebook Should Do (Current State)

#### `01_gnn_v100_training.ipynb` ✅ **READY TO USE**
- **Status**: Has 12 code cells with outputs
- **Purpose**: Train ST-PIGNN spatio-temporal GNN on Bangalore air quality data
- **Key Sections**:
  1. Load dependencies (torch, pytorch_geometric, pandas, etc.)
  2. Load graph from `topology_graph_pyg_inference.pt`
  3. Load model input from `model_input_node_hourly_features.parquet`
  4. Initialize ST-PIGNN model architecture
  5. Define loss & optimizer
  6. Training loop with validation
  7. Save model weights to `gnn/model_weights/`
  8. Generate predictions & metrics
- **Output**: Trained model, validation curves, inference results

#### `02_gnn_training.ipynb` (Empty)
- Alternative training notebook (e.g., different architecture, hyperparams)
- Can duplicate `01_gnn_v100_training.ipynb` as template and modify

#### `01_eda_physics_plane.ipynb` (Empty)
- Exploratory data analysis of plume/physics behavior
- Should load raw station + weather data and visualize
- Understand spatial/temporal patterns before training

#### `03_plume_validation.ipynb` (Empty)
- Validate GNN predictions against physics equations
- Load GNN model outputs and plume_physics.py constraints
- Compute constraint violations, compare forecast vs ground truth

#### `04_gale_shapley_demo.ipynb` (Empty)
- Demo of commuter-station matching algorithm
- Load emissions from GNN, run matcher.gale_shapley.py
- Visualize assignments

#### `05_astar_benchmark.ipynb` (Empty)
- Benchmark A* routing performance
- Load matched pairs, run router.rust_astar/ 
- Compare different heuristics

#### `06_route_comparison.ipynb` (Empty)
- Final comparison of all strategies (baseline, A*, matched)
- Aggregate health metrics, generate reports

---

## 🚀 Key Files to Give to Gemini/Collaborator

### For V100 Model Training:
1. **`data/processed/model_input/model_input_node_hourly_features.parquet`** — Main input tensor
2. **`data/processed/graph/topology_graph_pyg_inference.pt`** — PyG graph object
3. **`notebooks/01_gnn_v100_training.ipynb`** — Training template
4. **`gnn/model.py`** — ST-PIGNN architecture
5. **`gnn/pi_gnn.py`** — Core GNN logic
6. **`shared/config.py`** — Configuration & hyperparameters
7. **`docs/ARCHITECTURE.md`** — System overview

### For Data Understanding:
1. **`data/processed/data_processed_index.md`** — This file (what you're reading)
2. **`data/README.md`** — Raw data notes & timestamps
3. **`docs/PHYSICS.md`** — Plume physics constraints
4. **`gnn/README.md`** — GNN-specific documentation

---

## ⏱️ Timestamp Note (Critical for V100)

**All timestamps are UTC-naive ISO 8601 format (ending in Z when displayed)**

Example: `2022-01-15T14:30:00Z` (but stored as timezone-naive)

- No local time conversions applied
- All parquet datetime indexes are timezone-unaware
- Assumes UTC throughout the pipeline
- Do NOT re-localize to IST/Kolkata in V100 notebooks

---

## 📈 Data Shapes & Expected Volumes

| Dataset | Shape | Rows | Columns | Notes |
|---|---|---|---|---|
| `model_input_node_hourly_features.parquet` | ~35K hours × 115 nodes | 4.0M | timestamp, node_id, PM2.5, NO2, O3, temperature, humidity, wind_speed | Ready for training |
| `topology_graph_pyg_inference.pt` | Graph | 115 nodes | 10 features/node | PyG Data object |
| `station_timeseries_observed_imputed.parquet` | ~1.1M rows | 1,086,407 | station_id, timestamp, PM2.5, NO2, O3, imputation_method | Before node aggregation |
| Combined year files (stations/) | ~1.1M rows | 1,073,807 | station_id, timestamp, pollutant_levels | 2022, 2024, 2025, 2026 only |

---

## ✅ Data Quality Checklist for V100

- [ ] **No missing timestamps** in `model_input_node_hourly_features.parquet` within defined ranges
- [ ] **All node IDs** (0..114) present in graph and model input
- [ ] **Pollutant values** are numeric, non-NaN for observed rows
- [ ] **2023 is absent from `stations/` files** — this is correct (use gapfill for imputed 2023)
- [ ] **Graph edge indices** are valid (0 ≤ indices < 115)
- [ ] **Timestamps are UTC-naive** (no timezone metadata in parquet datetime)

---

## 🔗 Related Code Directories

| Dir | Purpose | For V100? |
|---|---|---|
| `gnn/` | ST-PIGNN model, graph builder, physics constraints | **YES** |
| `router/` | A* routing, cost functions, matching | **YES** (post-GNN) |
| `matcher/` | Gale-Shapley, equilibrium, quota | **YES** (post-GNN) |
| `ingestion/` | Real-time data fetching (weather, AQ, sensors) | NO (already in processed/) |
| `scripts/` | Pipeline orchestration, gap-filling, tensor building | NO (already executed) |
| `shared/` | Config, logging, schemas, physics constants | **YES** |
| `frontend/` | Web UI (not needed for V100 training) | NO |

---

## 💡 Pro Tips for V100 Training

1. **Use `model_input_node_hourly_features.parquet` directly** — it's already aggregated and ready
2. **Don't re-compute the graph** — load `topology_graph_pyg_inference.pt` as-is
3. **Batch by year** if memory is tight: load 2022 → 2024 → 2025 → 2026_partial separately
4. **2023 is missing by design** — skip year-specific filtering that assumes continuous years
5. **Check gnn/model_weights/** for existing checkpoints before training from scratch
6. **Use `shared/config.py`** for hyperparameters (don't hard-code)
7. **Log to `gnn/training/`** and save checkpoints regularly to `gnn/model_weights/`

