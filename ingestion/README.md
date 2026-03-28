# ingestion

Live environmental ingestion package.

## Responsibilities

- Fetch live observations asynchronously for Bangalore.
- Publish point observations to Redis streams.
- Fuse stream observations into grid-form state for downstream consumers.

## Main Files

- `ingestor.py`: async worker loop.
- `data_fusion.py`: point-to-grid conversion.
- `redis_publisher.py`: stream read/write helpers.
- `physics_plane.py`: grid utilities.
- `pull_gnn_training_data.py`: tensor generation from stream-backed state.

## Stream Keys

- `weather:live`
- `airquality:live`
- `sensors:live`

## Run

```bash
python -m ingestion.ingestor
```

## Notes

- Keep secrets in root `.env`.
- All env-backed settings are loaded in `shared/config.py`.
