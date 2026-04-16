"""
Targeted station gap recovery for known missing data only.

This script:
- Computes missing stations and missing date ranges from current station yearly files.
- Builds targeted pull tasks only for those gaps (not full historical reruns).
- Processes years in increasing order with 2023 intentionally last.
- Uses progress bars.
- Logs task outcomes to both plain text and markdown logs.

Outputs:
- data/raw/targeted_missing_pull.log
- data/raw/targeted_missing_pull_log.md
- data/raw/targeted_missing_pull_events.parquet
- data/raw/.checkpoint_stations_targeted_missing.json

Usage:
    python scripts/pull_stations_missing_targeted.py
    python scripts/pull_stations_missing_targeted.py --resume
"""

from __future__ import annotations

import argparse
import calendar
import json
import os
import time
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Callable

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import requests
from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

console = Console()

BASE_URL = "https://api.openaq.org/v3"
TARGET_PARAMS = ["no2", "so2", "pm25", "pm10", "co"]
RETRY_LIMIT = 5
PAGE_LIMIT = 1000
REQUEST_TIMEOUT = 60

STATIONS_DIR = Path("data/raw/stations")
META_PATH = STATIONS_DIR / "meta.parquet"
CHECKPOINT_PATH = Path("data/raw/.checkpoint_stations_targeted_missing.json")

LOG_TXT = Path("data/raw/targeted_missing_pull.log")
LOG_MD = Path("data/raw/targeted_missing_pull_log.md")
EVENTS_PARQUET = Path("data/raw/targeted_missing_pull_events.parquet")

# Requested execution order: increasing order, but keep 2023 for the end.
YEAR_FILE_ORDER = [
    (2022, "2022.parquet"),
    (2024, "2024.parquet"),
    (2025, "2025.parquet"),
    (2026, "2026_partial.parquet"),
    (2023, "2023.parquet"),
]


@dataclass(frozen=True)
class Task:
    task_id: str
    year: int
    file_name: str
    station_id: int
    station_name: str
    parameter: str
    sensor_id: int
    date_from: str
    date_to: str
    task_type: str  # missing_station_full_year | missing_date_range


@dataclass
class Result:
    task_id: str
    year: int
    file_name: str
    station_id: int
    station_name: str
    parameter: str
    sensor_id: int
    date_from: str
    date_to: str
    task_type: str
    status: str
    http_status: int
    raw_api_rows: int
    api_rows: int
    year_filtered_out_rows: int
    dedupe_overlap_rows: int
    inserted_rows: int
    message: str
    finished_at: str


def get_api_key() -> str:
    key = os.getenv("OPENAQ_API_KEY")
    if key:
        return key
    env_path = Path(".env")
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if line.startswith("OPENAQ_API_KEY="):
                return line.split("=", 1)[1].strip()
    raise ValueError("OPENAQ_API_KEY is missing. Set env var or .env value.")


def save_parquet(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    pq.write_table(pa.Table.from_pandas(df), tmp, compression="snappy")
    tmp.replace(path)


def load_checkpoint() -> dict:
    if CHECKPOINT_PATH.exists():
        state = json.loads(CHECKPOINT_PATH.read_text())
    else:
        state = {}
    state.setdefault("completed_task_ids", [])
    return state


def save_checkpoint(state: dict) -> None:
    CHECKPOINT_PATH.parent.mkdir(parents=True, exist_ok=True)
    CHECKPOINT_PATH.write_text(json.dumps(state, indent=2))


def discover_station_sensors(api_key: str) -> dict[int, dict]:
    # Prefer existing checkpoint station metadata if available.
    ckp = Path("data/raw/.checkpoint_stations.json")
    if ckp.exists():
        data = json.loads(ckp.read_text())
        stations = data.get("stations", [])
        out: dict[int, dict] = {}
        for s in stations:
            sid = int(s["id"])
            sensors = {k: int(v) for k, v in s.get("sensors", {}).items() if k in TARGET_PARAMS}
            if sensors:
                out[sid] = {"name": s.get("name", str(sid)), "sensors": sensors}
        if out:
            return out

    headers = {"X-API-Key": api_key}
    resp = requests.get(
        f"{BASE_URL}/locations",
        headers=headers,
        params={"bbox": "77.461,12.834,77.781,13.144", "limit": 100},
        timeout=REQUEST_TIMEOUT,
    )
    resp.raise_for_status()
    results = resp.json().get("results", [])

    out: dict[int, dict] = {}
    for row in results:
        sid = int(row["id"])
        sensors = {
            s["parameter"]["name"]: int(s["id"])
            for s in row.get("sensors", [])
            if s.get("parameter", {}).get("name") in TARGET_PARAMS
        }
        if sensors:
            out[sid] = {"name": row.get("name", str(sid)), "sensors": sensors}
    return out


def compress_ranges(missing_days: list[date]) -> list[tuple[date, date]]:
    if not missing_days:
        return []
    missing_days = sorted(missing_days)
    out: list[tuple[date, date]] = []
    start = prev = missing_days[0]
    for d in missing_days[1:]:
        if (d - prev).days == 1:
            prev = d
            continue
        out.append((start, prev))
        start = prev = d
    out.append((start, prev))
    return out


def date_bounds_for_file(year: int, file_name: str, df: pd.DataFrame) -> tuple[pd.Timestamp, pd.Timestamp]:
    start = pd.Timestamp(f"{year}-01-01T00:00:00", tz="UTC")
    end = pd.Timestamp(f"{year}-12-31T23:59:59", tz="UTC")
    if file_name == "2026_partial.parquet":
        if len(df):
            end = pd.to_datetime(df.index.max(), utc=True)
        else:
            end = pd.Timestamp(datetime.now(timezone.utc).date(), tz="UTC") + pd.Timedelta(hours=23, minutes=59, seconds=59)
    return start, end


def build_tasks(api_key: str) -> tuple[list[Task], dict[int, pd.DataFrame]]:
    station_meta = pd.read_parquet(META_PATH)
    expected_ids = sorted(station_meta["id"].astype(int).unique().tolist())

    station_sensors = discover_station_sensors(api_key)

    tasks: list[Task] = []
    frame_cache: dict[int, pd.DataFrame] = {}

    for year, file_name in YEAR_FILE_ORDER:
        path = STATIONS_DIR / file_name
        df = pd.read_parquet(path) if path.exists() else pd.DataFrame()
        if len(df):
            df = df[df.index.year == year].sort_index()
        frame_cache[year] = df

        start, end = date_bounds_for_file(year, file_name, df)
        all_days = pd.date_range(start.date(), end.date(), freq="D").date.tolist()

        present_station_ids = sorted(df["station_id"].astype(int).unique().tolist()) if len(df) and "station_id" in df.columns else []
        missing_station_ids = [sid for sid in expected_ids if sid not in set(present_station_ids)]

        present_days = sorted(set(pd.to_datetime(df.index).date)) if len(df) else []
        missing_days = [d for d in all_days if d not in set(present_days)]
        missing_ranges = compress_ranges(missing_days)

        # Tasks for stations missing entire coverage in this year file.
        for sid in missing_station_ids:
            station_info = station_sensors.get(sid)
            if not station_info:
                continue
            for param, sensor_id in sorted(station_info["sensors"].items()):
                task_id = f"{year}|{file_name}|station_full|{sid}|{param}|{start.date()}|{end.date()}"
                tasks.append(
                    Task(
                        task_id=task_id,
                        year=year,
                        file_name=file_name,
                        station_id=sid,
                        station_name=station_info["name"],
                        parameter=param,
                        sensor_id=int(sensor_id),
                        date_from=f"{start.date().isoformat()}T00:00:00Z",
                        date_to=f"{end.date().isoformat()}T23:59:59Z",
                        task_type="missing_station_full_year",
                    )
                )

        # Tasks for known missing date ranges (for stations already present in year file).
        for sid in present_station_ids:
            station_info = station_sensors.get(sid)
            if not station_info:
                continue
            for r_start, r_end in missing_ranges:
                for param, sensor_id in sorted(station_info["sensors"].items()):
                    task_id = f"{year}|{file_name}|date_gap|{sid}|{param}|{r_start}|{r_end}"
                    tasks.append(
                        Task(
                            task_id=task_id,
                            year=year,
                            file_name=file_name,
                            station_id=sid,
                            station_name=station_info["name"],
                            parameter=param,
                            sensor_id=int(sensor_id),
                            date_from=f"{r_start.isoformat()}T00:00:00Z",
                            date_to=f"{r_end.isoformat()}T23:59:59Z",
                            task_type="missing_date_range",
                        )
                    )

    # Deduplicate deterministicly.
    uniq: dict[str, Task] = {}
    for t in tasks:
        uniq[t.task_id] = t
    ordered = sorted(
        uniq.values(),
        key=lambda t: (
            YEAR_FILE_ORDER.index((t.year, t.file_name)),
            t.date_from,
            t.station_id,
            t.parameter,
            t.task_type,
        ),
    )
    return ordered, frame_cache


def fetch_measurements(
    headers: dict,
    task: Task,
    on_tick: Callable[[str], None] | None = None,
) -> tuple[list[dict], int]:
    rows: list[dict] = []
    page = 1
    last_status = 200

    while True:
        if on_tick:
            on_tick(f"page={page} request")
        payload = None
        code = -1
        for attempt in range(1, RETRY_LIMIT + 1):
            try:
                r = requests.get(
                    f"{BASE_URL}/sensors/{task.sensor_id}/measurements",
                    headers=headers,
                    params={
                        "datetime_from": task.date_from,
                        "datetime_to": task.date_to,
                        "limit": PAGE_LIMIT,
                        "page": page,
                    },
                    timeout=REQUEST_TIMEOUT,
                )
                code = r.status_code
                if code == 200:
                    if on_tick:
                        on_tick(f"page={page} ok")
                    payload = r.json()
                    break
                if code in (408, 429, 502, 503, 504):
                    if on_tick:
                        on_tick(f"page={page} retry attempt={attempt} code={code}")
                    append_text_log(
                        f"[{datetime.now().isoformat()}] RETRY station={task.station_name} param={task.parameter} "
                        f"range={task.date_from}->{task.date_to} page={page} attempt={attempt} code={code}"
                    )
                    time.sleep(min(30, attempt * 3))
                    continue
                break
            except requests.RequestException:
                if on_tick:
                    on_tick(f"page={page} retry attempt={attempt} request_exception")
                append_text_log(
                    f"[{datetime.now().isoformat()}] RETRY station={task.station_name} param={task.parameter} "
                    f"range={task.date_from}->{task.date_to} page={page} attempt={attempt} code=request_exception"
                )
                time.sleep(min(20, attempt * 2))

        last_status = code
        if payload is None:
            return rows, last_status

        batch = payload.get("results", [])
        if not batch:
            break

        for r in batch:
            rows.append(
                {
                    "time": r["period"]["datetimeFrom"]["local"],
                    "parameter": task.parameter,
                    "value": r.get("value"),
                    "unit": r.get("parameter", {}).get("units"),
                    "station_id": task.station_id,
                    "station_name": task.station_name,
                    "sensor_id": task.sensor_id,
                }
            )

        if len(batch) < PAGE_LIMIT:
            break
        page += 1
        time.sleep(0.2)

    return rows, last_status


def to_year_filtered_df(rows: list[dict], year: int) -> pd.DataFrame:
    if not rows:
        out = pd.DataFrame(columns=["parameter", "value", "unit", "station_id", "station_name", "sensor_id"])
        out.index = pd.DatetimeIndex([], name="time")
        return out

    df = pd.DataFrame(rows)
    df["time"] = pd.to_datetime(df["time"], errors="coerce", utc=True).dt.tz_localize(None)
    df = df.dropna(subset=["time"])
    df = df[df["time"].dt.year == year]
    if not len(df):
        out = pd.DataFrame(columns=["parameter", "value", "unit", "station_id", "station_name", "sensor_id"])
        out.index = pd.DatetimeIndex([], name="time")
        return out

    df = df.sort_values("time").drop_duplicates(subset=["time", "station_id", "parameter", "sensor_id"], keep="last")
    return df.set_index("time")


def append_text_log(msg: str) -> None:
    LOG_TXT.parent.mkdir(parents=True, exist_ok=True)
    with LOG_TXT.open("a", encoding="utf-8") as f:
        f.write(msg + "\n")


def write_markdown_log(events: list[Result]) -> None:
    LOG_MD.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    lines.append("# Targeted Missing Pull Log")
    lines.append("")
    lines.append(f"Generated at: {datetime.now().isoformat()}")
    lines.append("")

    if not events:
        lines.append("No tasks were executed.")
        LOG_MD.write_text("\n".join(lines))
        return

    df = pd.DataFrame([e.__dict__ for e in events])

    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Total tasks processed: {len(df)}")
    lines.append(f"- Success with inserts: {int((df['inserted_rows'] > 0).sum())}")
    lines.append(f"- Confirmed missing (no rows): {int((df['status'] == 'confirmed_missing').sum())}")
    lines.append(f"- Failed tasks: {int((df['status'] == 'failed').sum())}")
    lines.append("")

    lines.append("## Failures / Confirmed Missing")
    lines.append("")
    lines.append("| Year | File | Station | Param | Date From | Date To | Status | HTTP | Message |")
    lines.append("|---:|---|---|---|---|---|---|---:|---|")

    bad = df[(df["status"] != "success") | (df["inserted_rows"] == 0)]
    if len(bad):
        for r in bad.itertuples(index=False):
            lines.append(
                f"| {r.year} | {r.file_name} | {r.station_name} | {r.parameter} | {r.date_from} | {r.date_to} | "
                f"{r.status} | {r.http_status} | {r.message} |"
            )
    else:
        lines.append("| - | - | - | - | - | - | - | - | No failures or confirmed-missing tasks. |")

    LOG_MD.write_text("\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--resume", action="store_true")
    parser.add_argument(
        "--max-tasks",
        type=int,
        default=0,
        help="Run only the first N pending tasks (0 means no limit)",
    )
    args = parser.parse_args()

    api_key = get_api_key()
    headers = {"X-API-Key": api_key}

    tasks, frame_cache = build_tasks(api_key)

    state = load_checkpoint() if args.resume else {"completed_task_ids": []}
    completed = set(state.get("completed_task_ids", []))

    events: list[Result] = []
    processed_this_run = 0

    append_text_log("=" * 100)
    append_text_log(f"[{datetime.now().isoformat()}] Starting targeted missing pull | tasks={len(tasks)} | resume={args.resume}")

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold cyan]{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total}"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task_bar = progress.add_task("Targeted gap tasks", total=len(tasks))

        for t in tasks:
            if t.task_id in completed:
                progress.advance(task_bar)
                continue

            if args.max_tasks > 0 and processed_this_run >= args.max_tasks:
                break

            progress.update(
                task_bar,
                description=(
                    f"[bold cyan]{t.year} {t.station_name} {t.parameter} "
                    f"{t.date_from[:10]}->{t.date_to[:10]}"
                ),
            )
            append_text_log(
                f"[{datetime.now().isoformat()}] START year={t.year} file={t.file_name} station={t.station_name} "
                f"param={t.parameter} range={t.date_from}->{t.date_to} task_type={t.task_type}"
            )

            def on_tick(msg: str) -> None:
                progress.update(
                    task_bar,
                    description=(
                        f"[bold cyan]{t.year} {t.station_name} {t.parameter} "
                        f"{t.date_from[:10]}->{t.date_to[:10]} | {msg}"
                    ),
                )

            api_rows_raw, http_status = fetch_measurements(headers, t, on_tick=on_tick)
            raw_api_rows = len(api_rows_raw)
            pulled = to_year_filtered_df(api_rows_raw, t.year)
            api_rows = len(pulled)
            year_filtered_out_rows = max(0, raw_api_rows - api_rows)

            year_df = frame_cache[t.year]
            before = len(year_df)
            dedupe_overlap_rows = 0

            if api_rows > 0:
                overlap = pd.concat([year_df, pulled], axis=0)
                overlap = overlap.reset_index().rename(columns={"index": "time"})
                overlap = overlap.duplicated(subset=["time", "station_id", "parameter"], keep="last")
                dedupe_overlap_rows = int(overlap.sum())

                merged = pd.concat([year_df, pulled], axis=0)
                merged = merged.reset_index().rename(columns={"index": "time"})
                merged = merged.drop_duplicates(subset=["time", "station_id", "parameter"], keep="last")
                merged = merged.sort_values("time").set_index("time")
                frame_cache[t.year] = merged
                inserted = len(merged) - before
                status = "success" if inserted > 0 else "confirmed_missing"
                if inserted > 0:
                    message = "inserted_new_rows"
                else:
                    message = "not_inserted_all_rows_already_present_after_dedupe"
            else:
                inserted = 0
                if http_status == 200:
                    status = "confirmed_missing"
                    if raw_api_rows > 0 and year_filtered_out_rows > 0:
                        message = "not_inserted_rows_outside_target_year"
                    else:
                        message = "api_returned_no_rows_for_requested_window"
                else:
                    status = "failed"
                    message = f"http_status_{http_status}"

            result = Result(
                task_id=t.task_id,
                year=t.year,
                file_name=t.file_name,
                station_id=t.station_id,
                station_name=t.station_name,
                parameter=t.parameter,
                sensor_id=t.sensor_id,
                date_from=t.date_from,
                date_to=t.date_to,
                task_type=t.task_type,
                status=status,
                http_status=http_status,
                raw_api_rows=raw_api_rows,
                api_rows=api_rows,
                year_filtered_out_rows=year_filtered_out_rows,
                dedupe_overlap_rows=dedupe_overlap_rows,
                inserted_rows=inserted,
                message=message,
                finished_at=datetime.now().isoformat(),
            )
            events.append(result)
            append_text_log(
                f"[{result.finished_at}] year={result.year} file={result.file_name} station={result.station_name} "
                f"param={result.parameter} range={result.date_from}->{result.date_to} status={result.status} "
                f"http={result.http_status} raw_api_rows={result.raw_api_rows} api_rows={result.api_rows} "
                f"year_filtered_out={result.year_filtered_out_rows} dedupe_overlap={result.dedupe_overlap_rows} "
                f"inserted={result.inserted_rows} msg={result.message}"
            )

            completed.add(t.task_id)
            state["completed_task_ids"] = sorted(completed)
            save_checkpoint(state)
            progress.advance(task_bar)
            processed_this_run += 1

    # Persist yearly files after all targeted tasks.
    for year, file_name in YEAR_FILE_ORDER:
        out_path = STATIONS_DIR / file_name
        ydf = frame_cache[year]
        if len(ydf):
            ydf = ydf[ydf.index.year == year]
        save_parquet(ydf, out_path)

    # Persist event logs.
    event_df = pd.DataFrame([e.__dict__ for e in events]) if events else pd.DataFrame(
        columns=list(Result.__annotations__.keys())
    )
    save_parquet(event_df, EVENTS_PARQUET)
    write_markdown_log(events)

    append_text_log(f"[{datetime.now().isoformat()}] Finished targeted missing pull | processed={len(events)}")

    console.print("\n[bold green]Targeted pull finished[/bold green]")
    console.print(f"Text log   : {LOG_TXT}")
    console.print(f"Markdown   : {LOG_MD}")
    console.print(f"Events data: {EVENTS_PARQUET}")


if __name__ == "__main__":
    main()
