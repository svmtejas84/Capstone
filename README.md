
Cross-scale geospatial logic for real-time urban toxicity orchestration for healthier navigation of vulnerable commuters.

## Modules

- ingestion: Live Environmental Component (Sentinel-5P, ERA5, traffic spikes, Redis stream publish)
- gnn: Physics-Informed GNN and wake prediction for dynamic edge concentrations
- matcher: Batch Gale-Shapley stable matching for equilibrium route assignment
- router: FastAPI service plus Rust/WASM A* integration surface
- shared: Common settings, schemas, geo and Redis helpers
- frontend: React + Vite demo client

## Quickstart (simulation mode)

1. Copy environment file.
2. Start Redis with Docker Compose.
3. Install Python dependencies.
4. Run FastAPI backend.
5. Start frontend app.

Windows PowerShell:

```powershell
Copy-Item .env.example .env
docker compose up -d redis
pip install -e .
uvicorn router.api.main:app --reload --port 8000
```

In another terminal:

```powershell
Set-Location frontend
npm install
npm run dev
```

## API (starter)

- GET /health
- GET /plume
- POST /route
- GET /audit/{stake_hash}

## Notes

- This scaffold defaults to SIMULATION_MODE and does not require live GEE or TomTom calls.
- Data placeholders are committed for repository structure completeness.
