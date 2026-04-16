"""
2023 station remap + retry recovery pass.

Purpose:
- Start from previously confirmed-missing 2023 tasks.
- For each station+parameter window, discover all candidate sensor IDs for that location.
- Retry pulls across candidate sensors to recover rows missed by original sensor mapping.

Outputs:
- data/raw/remap_2023_retry.log
- data/raw/remap_2023_retry_log.md
- data/raw/remap_2023_retry_events.parquet
- data/raw/.checkpoint_2023_remap_retry.json

Usage:
    python scripts/pull_stations_2023_remap_retry.py
    python scripts/pull_stations_2023_remap_retry.py --resume
    python scripts/pull_stations_2023_remap_retry.py --max-tasks 10
"""

from __future__ import annotations

import argparse
import json
import os
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import requests
from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

console = Console()

BASE_URL = "https://api.openaq.org/v3"
TARGET_YEAR = 2023
TARGET_PARAMS = {"no2", "so2", "pm25", "pm10", "co"}
PAGE_LIMIT = 1000
RETRY_LIMIT = 5
REQUEST_TIMEOUT = 60

EVENTS_IN = Path("data/raw/targeted_missing_pull_events.parquet")
YEAR_FILE = Path("data/raw/stations/2023.parquet")
CHECKPOINT = Path("data/raw/.checkpoint_2023_remap_retry.json")

LOG_TXT = Path("data/raw/remap_2023_retry.log")
LOG_MD = Path("data/raw/remap_2023_retry_log.md")
EVENTS_OUT = Path("data/raw/remap_2023_retry_events.parquet")


@dataclass(frozen=True)
class Task:
    task_id: str
    station_id: int
    station_name: str
    parameter: str
    date_from: str
    date_to: str
    original_sensor_id: int


@dataclass
class Event:
    task_id: str
    station_id: int
    station_name: str
    parameter: str
    date_from: str
    date_to: str
    original_sensor_id: int
    tried_sensor_ids: str
    selected_sensor_id: int
    status: str
    http_status: int
    raw_api_rows: int
    api_rows: int
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


def append_log(message: str) -> None:
    LOG_TXT.parent.mkdir(parents=True, exist_ok=True)
    with LOG_TXT.open("a", encoding="utf-8") as f:
        f.write(message + "\n")


def save_parquet(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    pq.write_table(pa.Table.from_pandas(df), tmp, compression="snappy")
    tmp.replace(path)


def load_checkpoint() -> dict:
    if CHECKPOINT.exists():
        state = json.loads(CHECKPOINT.read_text())
    else:
        state = {}
    state.setdefault("completed_task_ids", [])
    return state


def save_checkpoint(state: dict) -> None:
    CHECKPOINT.parent.mkdir(parents=True, exist_ok=True)
    CHECKPOINT.write_text(json.dumps(state, indent=2))


def load_tasks() -> list[Task]:
    if not EVENTS_IN.exists():
        raise FileNotFoundError(f"Missing input events file: {EVENTS_IN}")

    src = pd.read_parquet(EVENTS_IN)
    src = src[(src["year"] == TARGET_YEAR) & (src["status"] == "confirmed_missing")]

    keep = [
        "station_id",
        "station_name",
        "parameter",
        "date_from",
        "date_to",
        "sensor_id",
    ]
    src = src[keep].drop_duplicates().copy()
    src["station_id"] = src["station_id"].astype(int)
    src["sensor_id"] = src["sensor_id"].astype(int)

    tasks: list[Task] = []
    for r in src.sort_values(["station_id", "parameter", "date_from"]).itertuples(index=False):
        if r.parameter not in TARGET_PARAMS:
            continue
        task_id = f"2023|{r.station_id}|{r.parameter}|{r.date_from}|{r.date_to}"
        tasks.append(
            Task(
                task_id=task_id,
                station_id=int(r.station_id),
                station_name=str(r.station_name),
                parameter=str(r.parameter),
                date_from=str(r.date_from),
                date_to=str(r.date_to),
                original_sensor_id=int(r.sensor_id),
            )
        )
    return tasks


def discover_candidate_sensors(headers: dict, station_id: int, parameter: str, original_sensor_id: int) -> list[int]:
    out: list[int] = [original_sensor_id]

    try:
        r = requests.get(f"{BASE_URL}/locations/{station_id}/sensors", headers=headers, timeout=REQUEST_TIMEOUT)
        if r.status_code == 200:
            for s in r.json().get("results", []):
                pid = s.get("parameter", {}).get("name")
                sid = s.get("id")
                if pid == parameter and sid is not None:
                    out.append(int(sid))
    except requests.RequestException:
        pass

    uniq = []
    seen = set()
    for sid in out:
        if sid not in seen:
            seen.add(sid)
            uniq.append(sid)
    return uniq


def fetch_measurements(headers: dict, sensor_id: int, date_from: str, date_to: str) -> tuple[list[dict], int]:
    rows: list[dict] = []
    page = 1
    last_status = 200

    while True:
        payload = None
        code = -1
        for attempt in range(1, RETRY_LIMIT + 1):
            try:
                r = requests.get(
                    f"{BASE_URL}/sensors/{sensor_id}/measurements",
                    headers=headers,
                    params={
                        "datetime_from": date_from,
                        "datetime_to": date_to,
                        "limit": PAGE_LIMIT,
                        "page": page,
                    },
                    timeout=REQUEST_TIMEOUT,
                )
                code = r.status_code
                if code == 200:
                    payload = r.json()
                    break
                if code in (408, 429, 502, 503, 504):
                    time.sleep(min(30, attempt * 3))
                    continue
                break
            except requests.RequestException:
                time.sleep(min(20, attempt * 2))

        last_status = code
        if payload is None:
            return rows, last_status

        batch = payload.get("results", [])
        if not batch:
            break

        rows.extend(batch)
        if len(batch) < PAGE_LIMIT:
            break

        page += 1
        time.sleep(0.2)

    return rows, last_status


def to_year_df(raw_rows: list[dict], station_id: int, station_name: str, parameter: str, sensor_id: int) -> pd.DataFrame:
    if not raw_rows:
        out = pd.DataFrame(columns=["parameter", "value", "unit", "station_id", "station_name", "sensor_id"])
        out.index = pd.DatetimeIndex([], name="time")
        return out

    rows = []
    for r in raw_rows:
        rows.append(
            {
                "time": r.get("period", {}).get("datetimeFrom", {}).get("local"),
                "parameter": parameter,
                "value": r.get("value"),
                "unit": r.get("parameter", {}).get("units"),
                "station_id": station_id,
                "station_name": station_name,
                "sensor_id": sensor_id,
            }
        )

    df = pd.DataFrame(rows)
    df["time"] = pd.to_datetime(df["time"], errors="coerce", utc=True).dt.tz_convert("Asia/Kolkata")
    df = df.dropna(subset=["time"])
    df = df[df["time"].dt.year == TARGET_YEAR]
    if not len(df):
        out = pd.DataFrame(columns=["parameter", "value", "unit", "station_id", "station_name", "sensor_id"])
        out.index = pd.DatetimeIndex([], name="time")
        return out

    df = df.sort_values("time").drop_duplicates(subset=["time", "station_id", "parameter", "sensor_id"], keep="last")
    return df.set_index("time")


def merge_insert(year_df: pd.DataFrame, incoming: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    before = len(year_df)
    merged = pd.concat([year_df, incoming], axis=0)
    merged = merged.reset_index().rename(columns={"index": "time"})
    merged = merged.drop_duplicates(subset=["time", "station_id", "parameter"], keep="last")
    merged = merged.sort_values("time").set_index("time")
    inserted = max(0, len(merged) - before)
    return merged, inserted


def write_markdown_log(events: list[Event], total_tasks: int) -> None:
    LOG_MD.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    lines.append("# 2023 Remap Retry Log")
    lines.append("")
    lines.append(f"Generated at: {datetime.now().isoformat()}")
    lines.append("")
    lines.append("## Summary")
    lines.append("")

    if not events:
        lines.append(f"- Tasks discovered: {total_tasks}")
        lines.append("- Tasks executed this run: 0")
        lines.append("- No events produced.")
        LOG_MD.write_text("\n".join(lines), encoding="utf-8")
        return

    df = pd.DataFrame([e.__dict__ for e in events])
    lines.append(f"- Tasks discovered: {total_tasks}")
    lines.append(f"- Tasks executed this run: {len(df)}")
    lines.append(f"- Tasks with inserts: {int((df['inserted_rows'] > 0).sum())}")
    lines.append(f"- Confirmed missing: {int((df['status'] == 'confirmed_missing').sum())}")
    lines.append(f"- Failed tasks: {int((df['status'] == 'failed').sum())}")
    lines.append(f"- Inserted rows total: {int(df['inserted_rows'].sum())}")
    lines.append("")

    lines.append("## Task Outcomes")
    lines.append("")
    lines.append("| Station | Param | Date From | Date To | Status | Inserted | Tried Sensors | Message |")
    lines.append("|---|---|---|---|---|---:|---|---|")

    for r in df.sort_values(["station_id", "parameter", "date_from"]).itertuples(index=False):
        lines.append(
            f"| {r.station_name} | {r.parameter} | {r.date_from} | {r.date_to} | {r.status} | "
            f"{int(r.inserted_rows)} | {r.tried_sensor_ids} | {r.message} |"
        )

    LOG_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--max-tasks", type=int, default=0, help="Run only first N pending tasks")
    args = parser.parse_args()

    api_key = get_api_key()
    headers = {"X-API-Key": api_key}

    tasks = load_tasks()

    if YEAR_FILE.exists():
        year_df = pd.read_parquet(YEAR_FILE)
        if len(year_df):
            year_df = year_df[year_df.index.year == TARGET_YEAR].sort_index()
    else:
        year_df = pd.DataFrame(columns=["parameter", "value", "unit", "station_id", "station_name", "sensor_id"])
        year_df.index = pd.DatetimeIndex([], name="time")

    state = load_checkpoint() if args.resume else {"completed_task_ids": []}
    completed = set(state.get("completed_task_ids", []))

    events: list[Event] = []
    processed = 0

    append_log("=" * 100)
    append_log(f"[{datetime.now().isoformat()}] Start 2023 remap retry | tasks={len(tasks)} | resume={args.resume}")

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold cyan]{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total}"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        bar = progress.add_task("2023 remap tasks", total=len(tasks))

        for t in tasks:
            if t.task_id in completed:
                progress.advance(bar)
                continue

            if args.max_tasks > 0 and processed >= args.max_tasks:
                break

            progress.update(bar, description=f"[bold cyan]{t.station_name} {t.parameter} {t.date_from[:10]}->{t.date_to[:10]}")

            candidates = discover_candidate_sensors(headers, t.station_id, t.parameter, t.original_sensor_id)
            append_log(
                f"[{datetime.now().isoformat()}] START task={t.task_id} station={t.station_name} "
                f"param={t.parameter} candidates={candidates}"
            )

            best_status = "confirmed_missing"
            best_http = 200
            best_raw = 0
            best_api = 0
            best_inserted = 0
            best_message = "all_candidate_sensors_returned_no_rows"
            selected_sensor_id = -1

            for sid in candidates:
                raw_rows, http_status = fetch_measurements(headers, sid, t.date_from, t.date_to)
                year_rows = to_year_df(raw_rows, t.station_id, t.station_name, t.parameter, sid)

                raw_count = len(raw_rows)
                api_count = len(year_rows)

                append_log(
                    f"[{datetime.now().isoformat()}] TRY task={t.task_id} sensor={sid} http={http_status} "
                    f"raw_api_rows={raw_count} api_rows={api_count}"
                )

                if api_count > 0:
                    year_df, inserted = merge_insert(year_df, year_rows)
                    selected_sensor_id = sid
                    best_http = http_status
                    best_raw = raw_count
                    best_api = api_count
                    best_inserted = inserted
                    if inserted > 0:
                        best_status = "success"
                        best_message = "inserted_new_rows_from_remapped_sensor"
                    else:
                        best_status = "confirmed_missing"
                        best_message = "rows_returned_but_already_present_after_dedupe"
                    break

                if http_status != 200:
                    best_status = "failed"
                    best_http = http_status
                    best_message = f"http_status_{http_status}"

            event = Event(
                task_id=t.task_id,
                station_id=t.station_id,
                station_name=t.station_name,
                parameter=t.parameter,
                date_from=t.date_from,
                date_to=t.date_to,
                original_sensor_id=t.original_sensor_id,
                tried_sensor_ids=",".join(str(x) for x in candidates),
                selected_sensor_id=selected_sensor_id,
                status=best_status,
                http_status=best_http,
                raw_api_rows=best_raw,
                api_rows=best_api,
                inserted_rows=best_inserted,
                message=best_message,
                finished_at=datetime.now().isoformat(),
            )
            events.append(event)

            append_log(
                f"[{event.finished_at}] END task={event.task_id} status={event.status} http={event.http_status} "
                f"raw_api_rows={event.raw_api_rows} api_rows={event.api_rows} inserted={event.inserted_rows} "
                f"selected_sensor={event.selected_sensor_id} msg={event.message}"
            )

            completed.add(t.task_id)
            state["completed_task_ids"] = sorted(completed)
            save_checkpoint(state)
            progress.advance(bar)
            processed += 1

    save_parquet(year_df, YEAR_FILE)

    event_df = pd.DataFrame([e.__dict__ for e in events]) if events else pd.DataFrame(columns=list(Event.__annotations__.keys()))
    save_parquet(event_df, EVENTS_OUT)
    write_markdown_log(events, total_tasks=len(tasks))

    append_log(f"[{datetime.now().isoformat()}] Finished 2023 remap retry | processed={len(events)}")

    console.print("\n[bold green]2023 remap retry finished[/bold green]")
    console.print(f"Text log   : {LOG_TXT}")
    console.print(f"Markdown   : {LOG_MD}")
    console.print(f"Events data: {EVENTS_OUT}")


if __name__ == "__main__":
    main()
