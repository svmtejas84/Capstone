# toxicity-nav Repository Structure

## Top Level

```text
toxicity-nav/
├── README.md
├── docker-compose.yml
├── pyproject.toml
├── .env
├── .env.example
├── .gitignore
├── ingestion/
├── gnn/
├── matcher/
├── router/
├── shared/
├── frontend/
├── data/
└── notebooks/
```

## Key Packages

### ingestion/
- ingestor.py: async worker that fetches live observations.
- data_fusion.py: converts point observations to grid-form payloads.
- redis_publisher.py: stream publisher/getter helpers.
- physics_plane.py: grid state utilities.
- pull_gnn_training_data.py: builds model tensors from stream-backed state.

### gnn/
- Graph toxicity and wake modeling components.

### matcher/
- Stable assignment logic and quota/preference tools.

### router/
- FastAPI endpoints for health, plume, route, and audit.
- Uses stream-backed state and computed toxicity values.

### shared/
- config.py: central settings loaded from environment.
- redis_client.py: Redis store wrapper.
- schemas.py: request/response models.

## Redis Streams

- weather:live
- airquality:live
- sensors:live

## Data Layout

- data/raw/: raw snapshots and intermediate artifacts.
- data/gnn/: training dataset outputs.
- data/fixtures/: local fixtures for tests and demos.
