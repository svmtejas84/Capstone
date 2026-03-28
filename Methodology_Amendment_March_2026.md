# Methodology Amendment (March 2026)

## Scope

This amendment standardizes the project on a live API + stream-first architecture for urban toxicity-aware routing.

## Active Inputs

- Open-Meteo forecast observations
- Open-Meteo air-quality observations
- AQICN station observations
- OpenStreetMap road graph via OSMnx

## Processing Sequence

1. Fetch observations in an async worker.
2. Push observations to Redis streams.
3. Build fused grid-form state for downstream components.
4. Use stream-backed state for route and corridor decisions.

## Data Integrity

- Keep stream payloads timestamped.
- Keep environment access centralized in `shared/config.py`.
- Avoid direct environment reads in feature modules.

## Operational Target

- Refresh interval: every 5 to 15 minutes.
- City focus: Bangalore coordinates configured in root env.

## Expected Outcome

A consistent, low-latency state layer that supports safer, exposure-aware routing decisions for vulnerable commuters.
