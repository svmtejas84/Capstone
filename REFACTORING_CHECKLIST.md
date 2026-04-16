# Refactoring Checklist

## Completed

- [x] Environment values standardized in root `.env`.
- [x] Root `.env.example` aligned with placeholder values.
- [x] `shared/config.py` reduced to active settings only.
- [x] Deprecated ingestion files removed.
- [x] Router state retrieval wired to live Redis streams.
- [x] Training data utility updated to stream-backed payload generation.
- [x] Markdown docs updated to current data stack language.

## Stream Contracts

- `weather:live`: weather observations
- `airquality:live`: pollutant observations
- `sensors:live`: sensor validation observations

## Final Sanity Checks

1. `python -m ingestion.ingestor` runs with valid token.
2. Router starts and `/plume` returns grid + wind arrays.
3. Router `/route` returns stable corridor and audit hash.
4. `.env` remains git-ignored.
