# Data Pipeline Architecture

## March 2026 Hardening Update

### Implemented

- Sync gate hardening in `scripts/sync_on_entry.py`:
   - Persists ratio cache: `data/processed/2023_ratios.parquet`
   - Validates helper map: `data/processed/graph/station_to_topology_node_map.parquet`
   - Emits explicit merge log: `[SYNC] Applying pollutant ratio logic...`
   - Preserves idempotency via checkpoint skip logic.
- Added physics-loss constant:
   - `shared/physics_config.py` now includes `PHYSICS_LOSS_LAMBDA = 0.1`.
- Added one-pass finalizer:
   - `scripts/finalize_gnn_assets.py` performs temporal repair, sensor masking, and PyG serialization.
- Added ST-PIGNN model module:
   - `gnn/model.py` with `GINEConv + GRU`, masked MSE, physics penalty, and AMP train step.

### Produced Artifacts

- `data/processed/model_input/model_input_node_hourly_features.parquet`
- `data/processed/graph/topology_graph_pyg_inference.pt`

### Validation Results

- Temporal continuity: hourly `bad_steps=0`
- Sensor supervision mask: `23` true nodes
- PyG graph validation: pass
- Isolated nodes: `False`
- Self loops: `False`

### Runtime Compatibility Note

On PyTorch 2.6+, load PyG `Data` artifacts with `weights_only=False`:

```python
data = torch.load("data/processed/graph/topology_graph_pyg_inference.pt", weights_only=False)
```

## Overview

The platform uses a live, stream-first architecture for urban toxicity-aware navigation in Bangalore.

## Active Data Stack

- Open-Meteo Forecast API
- Open-Meteo Air Quality API
- AQICN API
- OpenStreetMap graph loading via OSMnx

## Ingestion Flow

1. `ingestion/ingestor.py` fetches live observations asynchronously.
2. Point payloads are published to Redis streams:
   - `weather:live`
   - `airquality:live`
   - `sensors:live`
3. `ingestion/data_fusion.py` generates grid-form state used by downstream logic.

## Downstream Consumers

- gnn package: toxicity and wake estimation.
- matcher package: stable corridor allocation.
- router package: API endpoints for route decisions and auditing.

## Config Model

All environment access is centralized in `shared/config.py`.
Only the following settings are loaded:

- Open-Meteo URLs
- AQICN token and URL
- Bangalore latitude and longitude
- Redis URL
- Raw data directory
- Ingestion refresh interval
- Frontend origin
- Grid bounding box

## Reliability Notes

- API fetches are non-blocking.
- Stream readers use latest available values.
- Missing stream data falls back to zero-safe fused output shape.

## Quick Validation

1. Start Redis.
2. Run `python -m ingestion.ingestor`.
3. Verify stream length with Redis CLI for each live stream.
4. Run API and call `/plume` and `/route`.
