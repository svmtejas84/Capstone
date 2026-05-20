"""Compute a global linear scaler from latest station observations vs persistence baseline,
and store scaler in Redis under key 'scaler:__global__'.

This script is intended to be run locally to produce an initial scaler without retraining.
"""
from __future__ import annotations

import json
from pathlib import Path
from statistics import mean

import pandas as pd

import sys
from pathlib import Path as _P
REPO_ROOT = _P(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from shared.redis_client import RedisStore
from gnn.persistence_baseline import _load_static_artifacts, predict_route_edge_concentrations_persistence


def main():
    # Load latest station observations (choose most recent file in data/processed/stations)
    p = Path("data/processed/stations")
    files = sorted(p.glob("*.parquet"))
    if not files:
        print("No station files found under data/processed/stations")
        return
    df = pd.read_parquet(files[-1])
    # Expect columns: time, station_id, value or similar - try common names
    col_candidates = [c for c in df.columns if "pm25" in c.lower() or "value" in c.lower()]
    if not col_candidates:
        print("No PM2.5/value column found in stations parquet")
        return
    val_col = col_candidates[0]

    # Use the latest timestamp's observed station values
    ts_col = "time" if "time" in df.columns else ("timestamp" if "timestamp" in df.columns else df.columns[0])
    df[ts_col] = pd.to_datetime(df[ts_col])
    latest_ts = df[ts_col].max()
    latest = df[df[ts_col] == latest_ts]

    # (We do not require per-station->node mapping for this simple global scaler.)


    # Fallback simpler approach: compute multiplicative scaler using means
    # Observed mean across latest station values
    obs_mean = float(latest["value"].mean())

    # Persistence mean from graph station feature (station_pm25) where present
    graph, node_to_index, station_idx, city_idx = _load_static_artifacts()
    node_x = graph.x
    station_vals = []
    for i in range(node_x.shape[0]):
        try:
            v = float(node_x[i][station_idx])
        except Exception:
            v = 0.0
        if v > 0.0:
            station_vals.append(v)
    persistence_mean = float(sum(station_vals) / len(station_vals)) if station_vals else 0.0

    if persistence_mean <= 0.0:
        print("Persistence mean is zero; cannot fit multiplicative scaler")
        return

    a = obs_mean / persistence_mean
    b = 0.0
    print(f"Computed multiplicative scaler a={a:.6f}, b={b:.6f}, obs_mean={obs_mean:.6f}, persistence_mean={persistence_mean:.6f}")

    # Store in Redis
    store = RedisStore()
    store.connect()
    if store.client is None:
        print("Redis not available; scaler not stored")
        return
    key = "scaler:__global__"
    mapping = {"a": float(a), "b": float(b), "version": "auto_fit", "min_samples": int(len(latest))}
    # RedisStore.hset accepts key, field, value; we store as JSON under field 'meta'
    store.hset(key, "a", mapping["a"])
    store.hset(key, "b", mapping["b"])
    store.hset(key, "version", mapping["version"])
    store.hset(key, "min_samples", mapping["min_samples"])
    print("Stored scaler in Redis at key", key)


if __name__ == "__main__":
    main()
