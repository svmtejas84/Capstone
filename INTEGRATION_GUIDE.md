# Integration Guide

## Prerequisites: Data Setup

Before running the live system, prepare training data (one-time setup):

```bash
# Pull historical data (weather, AQ, stations from 2022-2026)
python scripts/pull_weather.py
python scripts/pull_airquality.py
python scripts/pull_stations.py

# Repair gaps and build tensors
python scripts/finalize_data_layer.py  # IDW + station ratios
python scripts/build_graph_tensors.py   # PyTorch graph
python scripts/sync_on_entry.py         # Merge all sources
python scripts/finalize_gnn_assets.py   # Temporal repair + train_mask + PyG Data
```

See [data/README.md](data/README.md) for detailed data processing pipeline.
Training details: [docs/TRAINING_ST_PIGNN.md](docs/TRAINING_ST_PIGNN.md).

## ST-PIGNN Artifacts (Required Before Training)

`scripts/finalize_gnn_assets.py` generates the model-ready files:

- `data/processed/model_input/model_input_node_hourly_features.parquet`
- `data/processed/graph/topology_graph_pyg_inference.pt`

Quick verification:

```bash
python - <<'PY'
import torch
data = torch.load('data/processed/graph/topology_graph_pyg_inference.pt', weights_only=False)
data.validate(raise_on_error=True)
print('train_mask_true_count=', int(data.train_mask.sum().item()))
print('isolated_nodes=', data.has_isolated_nodes())
print('self_loops=', data.has_self_loops())
PY
```

Expected: `train_mask_true_count=23`, `isolated_nodes=False`, `self_loops=False`.

## Local Run (Live API)

1. Create environment file:
   - `cp .env.example .env`
2. Add your AQICN token in `.env`.
3. Start Redis:
   - `redis-server`
4. Start ingestion worker:
   - `python -m ingestion.ingestor`
5. Start API:
   - `uvicorn router.api.main:app --reload`

## Runtime Expectations

- Ingestion continuously publishes to:
  - `weather:live`
  - `airquality:live`
  - `sensors:live`
- Router endpoints derive current state from these streams.

## Health Checks

- API health endpoint:
  - `GET /health`
- Stream checks:
  - `XLEN weather:live`
  - `XLEN airquality:live`
  - `XLEN sensors:live`

## Docker Notes

If using compose, run Redis + API + ingestion as separate services. Keep `.env` mounted or injected into ingestion and API services.

## Troubleshooting

- No stream data:
  - verify Redis is reachable from worker.
  - verify internet access from worker host.
- Empty plume response:
  - confirm ingestion is running and publishing.
- Route response missing expected weights:
  - confirm stream data exists and contains recent timestamp.
