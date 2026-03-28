# Data Pipeline Architecture

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
