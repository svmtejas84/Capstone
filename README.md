Cross-scale geospatial logic for real-time urban toxicity-aware routing in Bangalore.

## Modules

- ingestion: Async live data collection and Redis stream publishing.
- gnn: Physics-informed graph toxicity estimation and wake prediction.
- matcher: Batch stable matching for corridor assignment.
- router: FastAPI service and path-cost orchestration.
- shared: Settings, schemas, logging, and Redis helpers.
- frontend: React + Vite client.

## Runtime Data Pipeline

1. ingestion pulls weather and pollutant observations for Bangalore.
2. ingestion publishes point observations to Redis streams:
   - weather:live
   - airquality:live
   - sensors:live
3. downstream modules consume live stream state.
4. router serves health, plume, route, and audit endpoints.

## Quickstart

1. Copy env template:
   - cp .env.example .env
2. Fill AQICN token in .env.
3. Start Redis:
   - docker compose up -d redis
4. Install Python dependencies:
   - pip install -e .
5. Start API:
   - uvicorn router.api.main:app --reload --port 8000
6. Start frontend in another terminal:
   - cd frontend
   - npm install
   - npm run dev

## Notes

- Environment values are centralized in shared/config.py.
- Keep secrets only in .env.
- Data/raw snapshots are ignored from source control.
