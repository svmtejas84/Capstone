# router

FastAPI serving mode-aware toxicity routing endpoints.

## Endpoints

- GET /health
- GET /plume
- POST /route
- GET /audit/{stake_hash}

## Run

```powershell
uvicorn router.api.main:app --reload --port 8000
```

