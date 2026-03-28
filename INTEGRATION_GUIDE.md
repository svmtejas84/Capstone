# Integration Guide

## Local Run

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
