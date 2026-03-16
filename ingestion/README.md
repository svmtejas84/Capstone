# ingestion

Live environmental ingestion module.

## Responsibilities

- Build and update the 100m physics grid state.
- Inject traffic source spikes.
- Advect plume concentrations with wind vectors.
- Publish the latest state to Redis stream `toxicity:global_truth`.

## Run

```powershell
python -m ingestion.gee_pipeline
```

## Notes

- Current scaffold uses simulation mode only.
- Replace `gee_pipeline.py` internals with live GEE and traffic API integration in Phase 2.

