# ingestion

Live environmental ingestion module.

## Responsibilities

- Build and update the 100m physics grid state.
- Inject threshold-gated traffic source spikes from anomalous congestion only.
- Advect plume concentrations with wind vectors.
- Publish the latest state to Redis stream `toxicity:global_truth`.

## Run

```powershell
python -m ingestion.gee_pipeline
```

## Notes

- Current scaffold uses simulation mode only.
- Amendment-ready design:
	- ERA5 is treated as the base climatological layer.
	- INSAT-3D/3DR AMV feed is the intended intra-day wind update source.
	- Traffic spike injection uses D(l, t) > alpha * B(l, t), and injects only k * (D - B).
- Replace `gee_pipeline.py` internals with live GEE, Mosdac, and traffic API integration in Phase 2.

