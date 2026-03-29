"""
scripts/pull_stations.py

Pulls historical pollution readings from all OpenAQ CPCB stations
within Bangalore bounding box. Covers Jan 2022 -> March 2026.

Usage:
    python scripts/pull_stations.py
    python scripts/pull_stations.py --resume
    python scripts/pull_stations.py --year 2022
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
from rich.console import Console
from rich.live import Live
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn, MofNCompleteColumn

from shared.config import get_settings

console = Console()

settings = get_settings()
API_KEY = settings.openaq_api_key
BASE_URL = "https://api.openaq.org/v3"
BBOX = "77.461,12.834,77.781,13.144"

FULL_YEARS = [2022, 2023, 2024, 2025]
PARTIAL_YEAR = 2026
PARTIAL_END = "2026-03-28"
OUT_DIR = Path("data/raw/stations")
CHECKPOINT = Path("data/raw/.checkpoint_stations.json")
META_PATH = OUT_DIR / "meta.parquet"
RETRY_LIMIT = 5
RETRY_DELAY = 10
RATE_DELAY = 2
PAGE_LIMIT = 1000

HEADERS = {"X-API-Key": API_KEY}


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
    return {"completed": [], "failed": [], "stations": []}


def save_checkpoint(state: dict) -> None:
    CHECKPOINT.parent.mkdir(parents=True, exist_ok=True)
    CHECKPOINT.write_text(json.dumps(state, indent=2))


def fetch_with_retry(url: str, params: dict, label: str) -> dict | None:
    for attempt in range(1, RETRY_LIMIT + 1):
        try:
            resp = requests.get(url, headers=HEADERS, params=params, timeout=60)
            if resp.status_code == 200:
                return resp.json()
            elif resp.status_code == 429:
                wait = 60 * attempt
                log(f"  ⚠ Rate limit (429) — waiting {wait}s...")
                time.sleep(wait)
            else:
                log(f"  ✗ HTTP {resp.status_code} on {label} — moving on")
                return None
        except requests.RequestException as e:
            log(f"  ✗ Request error: {e} — moving on")
            return None
    return None


def discover_stations() -> list[dict]:
    log("Discovering Bangalore CPCB stations within bbox...")
    params = {"bbox": BBOX, "limit": 100}
    data = fetch_with_retry(f"{BASE_URL}/locations", params, "station discovery")
    if not data:
        raise RuntimeError("Failed to discover stations")

    results = data.get("results", [])
    seen_coords: set[tuple[float, float]] = set()
    stations: list[dict] = []

    for row in results:
        coords = row.get("coordinates", {})
        lat = coords.get("latitude")
        lon = coords.get("longitude")
        coord_key = (round(lat, 4), round(lon, 4)) if lat is not None and lon is not None else None

        if coord_key and coord_key in seen_coords:
            log(f"  - Deduplicating {row['name']} (same coords as existing station)")
            continue
        if coord_key:
            seen_coords.add(coord_key)

        sensor_map = {
            sensor["parameter"]["name"]: sensor["id"]
            for sensor in row.get("sensors", [])
            if sensor["parameter"]["name"] in ["no2", "so2", "pm25", "pm10", "co"]
        }
        if not sensor_map:
            log(f"  - Skipping {row['name']} - no relevant sensors")
            continue

        stations.append(
            {
                "id": row["id"],
                "name": row["name"],
                "lat": lat,
                "lon": lon,
                "sensors": sensor_map,
            }
        )
        log(f"  + {row['name']} - sensors: {sensor_map}")

    log(f"\n  Found {len(stations)} unique usable stations")
    return stations


def save_station_meta(stations: list[dict]) -> None:
    df = pd.DataFrame(stations)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pq.write_table(pa.Table.from_pandas(df), META_PATH, compression="snappy")
    log(f"  + Station metadata saved -> {META_PATH}")


def fetch_station_year(station: dict, year: int, start: str, end: str, progress, param_task, page_task) -> pd.DataFrame | None:
    all_rows      = []
    target_params = ["no2", "so2", "pm25", "pm10", "co"]
    sensors       = station.get("sensors", {})

    for param in target_params:
        progress.update(param_task, description=f"[yellow]{param}")
        sensor_id = sensors.get(param)
        if not sensor_id:
            progress.advance(param_task)
            progress.reset(page_task)
            continue

        page = 1
        while True:
            params = {
                "date_from": f"{start}T00:00:00Z",
                "date_to":   f"{end}T23:59:59Z",
                "limit":     PAGE_LIMIT,
                "page":      page,
            }
            url   = f"{BASE_URL}/sensors/{sensor_id}/measurements"
            label = f"{station['name']} {param} {year} page {page}"
            data  = fetch_with_retry(url, params, label)

            if not data:
                break

            results = data.get("results", [])
            if not results:
                break

            for r in results:
                all_rows.append({
                    "time":         r["period"]["datetimeFrom"]["local"],
                    "parameter":    param,
                    "value":        r.get("value"),
                    "unit":         r["parameter"]["units"],
                    "station_id":   station["id"],
                    "station_name": station["name"],
                })

            progress.update(page_task, description=f"[white]page {page} — {len(all_rows):,} rows")
            progress.advance(page_task)
            if len(results) < PAGE_LIMIT:
                break
            page += 1
            time.sleep(1)

        progress.advance(param_task)
        progress.reset(page_task)

    if not all_rows:
        return None

    df = pd.DataFrame(all_rows)
    df["time"] = pd.to_datetime(df["time"], utc=True).dt.tz_convert("Asia/Kolkata")
    df = df.set_index("time")
    return df


def save_parquet(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(pa.Table.from_pandas(df), path, compression="snappy")
    size_kb = path.stat().st_size / 1024
    log(f"  + Saved -> {path} | {len(df):,} rows | {size_kb:.1f} KB")


def main(resume: bool = False, single_year: int | None = None) -> None:
    if not API_KEY:
        raise ValueError("OPENAQ_API_KEY is required in .env")

    log_milestone("OpenAQ Station Historical Pull")
    log(f"Bbox : {BBOX}")
    log("Range: Jan 2022 -> March 2026")

    checkpoint = load_checkpoint() if resume else {"completed": [], "failed": [], "stations": []}

    if resume and checkpoint.get("stations"):
        stations = checkpoint["stations"]
        log(f"Using {len(stations)} stations from checkpoint")
    else:
        stations = discover_stations()
        checkpoint["stations"] = stations
        save_checkpoint(checkpoint)
        save_station_meta(stations)

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
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
        console=console,
        refresh_per_second=4,
    ) as progress:
        year_task = progress.add_task(f"[cyan]Years", total=total)
        station_task = progress.add_task(f"[green]Stations", total=len(stations))
        param_task = progress.add_task(f"[yellow]Parameters", total=5)
        page_task = progress.add_task(f"[white]Pages", total=None)

        for idx, (year, start, end, label) in enumerate(years, 1):
            year_key = f"stations_{year}"

            if resume and year_key in checkpoint["completed"]:
                progress.advance(year_task)
                continue

            progress.update(year_task, description=f"[cyan]Year {year}")
            progress.reset(station_task)

            year_frames = []
            for s_idx, station in enumerate(stations, 1):
                progress.update(station_task, description=f"[green]{station['name']}")
                progress.reset(param_task)

                df = fetch_station_year(station, year, start, end, progress, param_task, page_task)

                if df is not None:
                    year_frames.append(df)

                progress.advance(station_task)
                time.sleep(RATE_DELAY)

            if year_frames:
                combined = pd.concat(year_frames)
                path = OUT_DIR / f"{label}.parquet"
                save_parquet(combined, path)
                checkpoint["completed"].append(year_key)
                checkpoint["failed"] = [f for f in checkpoint["failed"] if f != year_key]
                save_checkpoint(checkpoint)
                log_milestone(f"Progress: {idx}/{total} years complete ({(idx / total) * 100:.0f}%)")
            else:
                if year_key not in checkpoint["failed"]:
                    checkpoint["failed"].append(year_key)
                save_checkpoint(checkpoint)
                log(f"  x No data for any station in {year} - run with --resume to retry")

            progress.advance(year_task)

            if idx < total:
                time.sleep(RATE_DELAY)

    log_milestone("Station Pull Complete")
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
