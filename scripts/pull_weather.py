"""
scripts/pull_weather.py

Pulls hourly historical weather data from Open-Meteo Archive API.
Covers Jan 2022 -> March 2026 for Bangalore.

Usage:
    python scripts/pull_weather.py
    python scripts/pull_weather.py --resume
    python scripts/pull_weather.py --year 2022
"""

from __future__ import annotations

import argparse
import json
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import requests

BANGALORE_LAT = 12.9716
BANGALORE_LON = 77.5946
BASE_URL = "https://archive-api.open-meteo.com/v1/archive"

VARIABLES = [
    "wind_speed_10m",
    "wind_direction_10m",
    "wind_gusts_10m",
    "temperature_2m",
    "relative_humidity_2m",
    "surface_pressure",
]

FULL_YEARS = [2022, 2023, 2024, 2025]
PARTIAL_YEAR = 2026
PARTIAL_END = "2026-03-28"
OUT_DIR = Path("data/raw/weather")
CHECKPOINT = Path("data/raw/.checkpoint_weather.json")
RETRY_LIMIT = 5
RETRY_DELAY = 10
RATE_DELAY = 2


def log(msg: str) -> None:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def log_milestone(msg: str) -> None:
    print(f"\n{'=' * 55}", flush=True)
    print(f"  *  {msg}", flush=True)
    print(f"{'=' * 55}\n", flush=True)


def load_checkpoint() -> dict:
    if CHECKPOINT.exists():
        data = json.loads(CHECKPOINT.read_text())
        log(f"Resuming - already pulled: {data.get('completed', [])}")
        return data
    return {"completed": [], "failed": []}


def save_checkpoint(state: dict) -> None:
    CHECKPOINT.parent.mkdir(parents=True, exist_ok=True)
    CHECKPOINT.write_text(json.dumps(state, indent=2))


def fetch_year(year: int, start: str, end: str) -> pd.DataFrame | None:
    params = {
        "latitude": BANGALORE_LAT,
        "longitude": BANGALORE_LON,
        "start_date": start,
        "end_date": end,
        "hourly": ",".join(VARIABLES),
        "wind_speed_unit": "ms",
        "timezone": "Asia/Kolkata",
    }
    for attempt in range(1, RETRY_LIMIT + 1):
        try:
            log(f"  Fetching {year} (attempt {attempt}/{RETRY_LIMIT})...")
            resp = requests.get(BASE_URL, params=params, timeout=60)
            if resp.status_code == 200:
                data = resp.json()
                hourly = data.get("hourly", {})
                if not hourly:
                    log(f"  x Empty response for {year}")
                    return None
                df = pd.DataFrame(hourly)
                df["time"] = pd.to_datetime(df["time"])
                df = df.set_index("time")
                return df
            if resp.status_code == 429:
                wait = 60 * attempt
                log(f"  ! Rate limit hit (429) - waiting {wait}s before retry...")
                time.sleep(wait)
            else:
                log(f"  x HTTP {resp.status_code} - {resp.text[:100]}")
                if attempt < RETRY_LIMIT:
                    time.sleep(RETRY_DELAY)
        except requests.RequestException as exc:
            log(f"  x Request error: {exc}")
            if attempt < RETRY_LIMIT:
                time.sleep(RETRY_DELAY)
    return None


def save_parquet(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(pa.Table.from_pandas(df), path, compression="snappy")
    size_kb = path.stat().st_size / 1024
    log(
        f"  + Saved -> {path} | {len(df):,} rows | {size_kb:.1f} KB | "
        f"{df.isnull().sum().sum()} missing values"
    )


def main(resume: bool = False, single_year: int | None = None) -> None:
    log_milestone("Open-Meteo Weather Historical Pull")
    log(f"Variables: {', '.join(VARIABLES)}")
    log("Range    : Jan 2022 -> March 2026")
    checkpoint = load_checkpoint() if resume else {"completed": [], "failed": []}

    if single_year:
        if single_year == PARTIAL_YEAR:
            years = [
                (
                    single_year,
                    f"{single_year}-01-01",
                    PARTIAL_END,
                    f"{single_year}_partial",
                )
            ]
        else:
            years = [
                (
                    single_year,
                    f"{single_year}-01-01",
                    f"{single_year}-12-31",
                    str(single_year),
                )
            ]
    else:
        years = [(y, f"{y}-01-01", f"{y}-12-31", str(y)) for y in FULL_YEARS]
        years.append(
            (
                PARTIAL_YEAR,
                f"{PARTIAL_YEAR}-01-01",
                PARTIAL_END,
                f"{PARTIAL_YEAR}_partial",
            )
        )

    total = len(years)
    for idx, (year, start, end, label) in enumerate(years, 1):
        key = f"weather_{year}"
        path = OUT_DIR / f"{label}.parquet"
        log(f"[{idx}/{total}] Weather {year} ({start} -> {end})")

        if resume and key in checkpoint["completed"]:
            log("  - Already pulled - skipping")
            continue

        df = fetch_year(year, start, end)
        if df is not None:
            save_parquet(df, path)
            checkpoint["completed"].append(key)
            checkpoint["failed"] = [f for f in checkpoint["failed"] if f != key]
            save_checkpoint(checkpoint)
            log_milestone(f"Progress: {idx}/{total} years complete ({(idx / total) * 100:.0f}%)")
        else:
            if key not in checkpoint["failed"]:
                checkpoint["failed"].append(key)
            save_checkpoint(checkpoint)
            log("  x Failed - run with --resume to retry")

        if idx < total:
            time.sleep(RATE_DELAY)

    log_milestone("Weather Pull Complete")
    log(f"Completed: {checkpoint['completed']}")
    if checkpoint["failed"]:
        log(f"Failed   : {checkpoint['failed']}")
        log("Run with --resume to retry failed years.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--year", type=int)
    args = parser.parse_args()
    main(resume=args.resume, single_year=args.year)
