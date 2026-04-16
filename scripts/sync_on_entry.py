"""
scripts/sync_on_entry.py

Welcome Gate sync script:
- Checks whether raw data horizon is newer than processed master horizon.
- Runs full merge only when new raw data is detected.
- Applies 2023 pollutant ratio logic for station pm25/no2/co completion from pm10.
- Updates data README with automated sync horizon notes.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import re

import numpy as np
import pandas as pd

# Project root: parent of this script directory.
BASE_DIR = Path(__file__).resolve().parent.parent

MASTER_PATH = BASE_DIR / "data" / "processed" / "model_input" / "model_input_node_hourly_features.parquet"
MAP_PATH = BASE_DIR / "data" / "processed" / "graph" / "station_to_topology_node_map.parquet"
RATIO_CACHE_PATH = BASE_DIR / "data" / "processed" / "2023_ratios.parquet"
README_PATH = BASE_DIR / "data" / "README.md"

RAW_DIRS = [
    BASE_DIR / "data" / "raw" / "weather",
    BASE_DIR / "data" / "raw" / "airquality",
    BASE_DIR / "data" / "raw" / "stations",
]

WEATHER_DIR = BASE_DIR / "data" / "raw" / "weather"
AIR_DIR = BASE_DIR / "data" / "raw" / "airquality"
STATION_DIR = BASE_DIR / "data" / "raw" / "stations"

RATIO_SOURCE_PATH = STATION_DIR / "2023.parquet"
RATIO_TARGET_PARAMS = ["pm25", "no2", "co"]

STATION_FEATURE_COLS = ["station_pm10", "station_pm25", "station_no2", "station_so2", "station_co"]
WEATHER_FEATURE_COLS = [
    "weather_wind_speed_10m",
    "weather_wind_direction_10m",
    "weather_wind_gusts_10m",
    "weather_temperature_2m",
    "weather_relative_humidity_2m",
    "weather_surface_pressure",
]
CITY_FEATURE_COLS = [
    "city_nitrogen_dioxide",
    "city_sulphur_dioxide",
    "city_pm2_5",
    "city_pm10",
    "city_carbon_monoxide",
]
MASTER_FEATURE_COLS = STATION_FEATURE_COLS + WEATHER_FEATURE_COLS + CITY_FEATURE_COLS


def normalize_ts_index(df: pd.DataFrame) -> pd.DataFrame:
    idx = df.index
    if not isinstance(idx, pd.DatetimeIndex):
        idx = pd.to_datetime(idx, errors="coerce")

    if idx.tz is not None:
        idx = idx.tz_convert("UTC").tz_localize(None)

    out = df.copy()
    out.index = idx
    out.index.name = "timestamp"
    return out


def as_utc(ts: pd.Timestamp | None) -> pd.Timestamp | None:
    if ts is None or pd.isna(ts):
        return None
    ts = pd.Timestamp(ts)
    if ts.tzinfo is None:
        return ts.tz_localize("UTC")
    return ts.tz_convert("UTC")


def to_hour_local(ts: pd.Timestamp | None) -> pd.Timestamp | None:
    ts_utc = as_utc(ts)
    if ts_utc is None:
        return None
    return ts_utc.tz_localize(None).floor("h")


def file_max_timestamp(path: Path) -> pd.Timestamp | None:
    try:
        df = pd.read_parquet(path)
    except Exception:
        return None

    if isinstance(df.index, pd.DatetimeIndex):
        idx = pd.to_datetime(df.index, errors="coerce")
        if idx.empty:
            return None
        return as_utc(pd.Series(idx).dropna().max())

    for col in ["timestamp", "time"]:
        if col in df.columns:
            vals = pd.to_datetime(df[col], errors="coerce")
            if vals.notna().any():
                return as_utc(vals.max())

    return None


def raw_data_horizon() -> pd.Timestamp | None:
    max_ts: pd.Timestamp | None = None
    for raw_dir in RAW_DIRS:
        for p in sorted(raw_dir.glob("*.parquet")):
            ts = to_hour_local(file_max_timestamp(p))
            if ts is None:
                continue
            if max_ts is None or ts > max_ts:
                max_ts = ts
    return max_ts


def processed_horizon() -> pd.Timestamp | None:
    if not MASTER_PATH.exists():
        return None
    return to_hour_local(file_max_timestamp(MASTER_PATH))


def _station_ratio_fingerprint(source_df: pd.DataFrame) -> tuple[dict[str, pd.Series], dict[str, float]]:
    source_df = normalize_ts_index(source_df)
    y2023 = source_df[source_df.index.year == 2023]
    if y2023.empty:
        y2023 = source_df.copy()
        print("[WARN] 2023 ratio source file has no calendar-year 2023 rows; using all rows.")

    y2023 = y2023[["station_id", "parameter", "value"]].dropna(subset=["station_id", "parameter", "value"])

    hourly = (
        y2023.groupby([y2023.index.floor("h"), "station_id", "parameter"], observed=True)["value"]
        .mean()
        .unstack("parameter")
    )
    hourly.index = hourly.index.set_names(["timestamp", "station_id"])

    if hourly.empty or "pm10" not in hourly.columns:
        raise ValueError("Cannot compute ratios: pm10 missing in ratio source data.")

    means = y2023.groupby(["station_id", "parameter"], observed=True)["value"].mean().unstack("parameter")

    per_station: dict[str, pd.Series] = {}
    global_ratio: dict[str, float] = {}
    pm10 = hourly["pm10"]

    for pollutant in RATIO_TARGET_PARAMS:
        if pollutant not in hourly.columns:
            raise ValueError(f"Cannot compute ratios: {pollutant} missing in ratio source data.")

        direct = (hourly[pollutant] / pm10).replace([np.inf, -np.inf], np.nan)
        direct = direct.where(pm10 > 0)
        ratio_by_station = direct.groupby("station_id").mean()

        if pollutant in means.columns and "pm10" in means.columns:
            ratio_by_station = ratio_by_station.fillna((means[pollutant] / means["pm10"]).replace([np.inf, -np.inf], np.nan))

        ratio_by_station = ratio_by_station.where(ratio_by_station > 0)
        if ratio_by_station.dropna().empty:
            raise ValueError(f"No valid ratio values for pollutant: {pollutant}")

        per_station[pollutant] = ratio_by_station
        global_ratio[pollutant] = float(ratio_by_station.dropna().mean())

    return per_station, global_ratio


def _fallback_ratio_source() -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for p in sorted(STATION_DIR.glob("*.parquet")):
        if p.name == "meta.parquet" or p.name == "2023.parquet":
            continue
        try:
            df = pd.read_parquet(p)
        except Exception:
            continue
        if {"station_id", "parameter", "value"}.issubset(df.columns):
            frames.append(df)

    if not frames:
        raise ValueError("No fallback station files were available to compute ratio maps.")

    return pd.concat(frames, axis=0, ignore_index=False)


def _persist_ratio_cache(per_station: dict[str, pd.Series], global_ratio: dict[str, float]) -> None:
    rows: list[dict[str, object]] = []
    for pollutant in RATIO_TARGET_PARAMS:
        ratio_by_station = per_station[pollutant].dropna()
        for station_id, ratio_value in ratio_by_station.items():
            rows.append(
                {
                    "station_id": station_id,
                    "pollutant": pollutant,
                    "ratio": float(ratio_value),
                    "global_ratio": float(global_ratio[pollutant]),
                }
            )

    cache_df = pd.DataFrame(rows)
    if cache_df.empty:
        raise ValueError("Ratio cache dataframe is empty; aborting ratio cache write.")

    RATIO_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    cache_df.to_parquet(RATIO_CACHE_PATH, index=False)


def _load_or_build_ratio_maps(force_refresh: bool = False) -> tuple[dict[str, pd.Series], dict[str, float]]:
    if RATIO_CACHE_PATH.exists() and not force_refresh:
        try:
            cached = pd.read_parquet(RATIO_CACHE_PATH)
            required_cols = {"station_id", "pollutant", "ratio", "global_ratio"}
            if required_cols.issubset(cached.columns):
                per_station: dict[str, pd.Series] = {}
                global_ratio: dict[str, float] = {}
                for pollutant in RATIO_TARGET_PARAMS:
                    pollutant_df = cached[cached["pollutant"] == pollutant]
                    if pollutant_df.empty:
                        raise ValueError(f"Cached ratio file missing pollutant rows: {pollutant}")

                    per_station[pollutant] = pollutant_df.set_index("station_id")["ratio"]
                    global_ratio[pollutant] = float(pollutant_df["global_ratio"].dropna().iloc[0])

                return per_station, global_ratio
        except Exception as exc:
            print(f"[WARN] Unable to load cached 2023 ratios; rebuilding from source ({exc}).")

    ratio_source = pd.read_parquet(RATIO_SOURCE_PATH)
    try:
        per_station, global_ratio = _station_ratio_fingerprint(ratio_source)
    except Exception as exc:
        print(f"[WARN] 2023 ratio source unavailable; falling back to other raw station files ({exc}).")
        ratio_source = _fallback_ratio_source()
        per_station, global_ratio = _station_ratio_fingerprint(ratio_source)
    _persist_ratio_cache(per_station, global_ratio)
    return per_station, global_ratio


def _load_concat_parquets(folder: Path) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for p in sorted(folder.glob("*.parquet")):
        if p.name == "meta.parquet":
            continue
        df = pd.read_parquet(p)
        df = normalize_ts_index(df)
        frames.append(df)

    if not frames:
        raise FileNotFoundError(f"No parquet files found in {folder}")

    merged = pd.concat(frames, axis=0)
    return merged.sort_index()


def build_master_dataframe(force_refresh_ratios: bool = False) -> pd.DataFrame:
    weather = _load_concat_parquets(WEATHER_DIR)
    air = _load_concat_parquets(AIR_DIR)
    stations = _load_concat_parquets(STATION_DIR)

    per_station_ratios, global_ratios = _load_or_build_ratio_maps(force_refresh=force_refresh_ratios)

    station_slice = stations[["station_id", "station_name", "parameter", "value"]].dropna(
        subset=["station_id", "parameter", "value"]
    )
    station_hourly = (
        station_slice.groupby(
            [station_slice.index.floor("h"), "station_id", "station_name", "parameter"],
            observed=True,
        )["value"]
        .mean()
        .unstack("parameter")
    )
    station_hourly.index = station_hourly.index.set_names(["timestamp", "station_id", "station_name"])

    if "pm10" not in station_hourly.columns:
        raise ValueError("Station data does not contain pm10; cannot apply ratio imputation.")

    station_ids = station_hourly.index.get_level_values("station_id")
    for pollutant in RATIO_TARGET_PARAMS:
        if pollutant not in station_hourly.columns:
            station_hourly[pollutant] = np.nan
        ratio_map = pd.Series(station_ids, index=station_hourly.index).map(per_station_ratios[pollutant])
        ratio_map = ratio_map.fillna(global_ratios[pollutant])
        imputed = station_hourly["pm10"] * ratio_map
        station_hourly[pollutant] = station_hourly[pollutant].fillna(imputed)

    station_hourly = station_hourly.reset_index()

    mapping = pd.read_parquet(MAP_PATH)
    mapping = mapping.rename(columns={"location_id": "station_id"})

    station_join = station_hourly.merge(
        mapping[["station_id", "node_id", "distance_meters"]],
        on="station_id",
        how="left",
    )

    weather_h = weather.copy()
    weather_h.index = weather_h.index.floor("h")
    weather_h = weather_h.groupby(level=0).mean().add_prefix("weather_")

    air_h = air.copy()
    air_h.index = air_h.index.floor("h")
    air_h = air_h.groupby(level=0).mean().add_prefix("city_")

    station_join = station_join.rename(columns={
        "pm10": "station_pm10",
        "pm25": "station_pm25",
        "no2": "station_no2",
        "so2": "station_so2",
        "co": "station_co",
    })

    master = station_join.merge(weather_h, left_on="timestamp", right_index=True, how="left")
    master = master.merge(air_h, left_on="timestamp", right_index=True, how="left")

    # Persist processed master timestamps as timezone-naive UTC to align with
    # other processed parquet time columns used for joins.
    ts = pd.to_datetime(master["timestamp"], errors="coerce")
    if isinstance(ts.dtype, pd.DatetimeTZDtype):
        ts = ts.dt.tz_convert("UTC").dt.tz_localize(None)
    master["timestamp"] = ts

    # Fill feature gaps so downstream V100 training windows are finite.
    master = master.sort_values(["station_id", "timestamp", "node_id"]).reset_index(drop=True)
    master[MASTER_FEATURE_COLS] = master[MASTER_FEATURE_COLS].apply(pd.to_numeric, errors="coerce")

    if STATION_FEATURE_COLS:
        master[STATION_FEATURE_COLS] = (
            master.groupby("station_id", observed=True)[STATION_FEATURE_COLS]
            .transform(lambda g: g.interpolate(method="linear", limit_direction="both"))
        )
        master[STATION_FEATURE_COLS] = master.groupby("station_id", observed=True)[STATION_FEATURE_COLS].transform(
            lambda g: g.ffill().bfill()
        )

    if WEATHER_FEATURE_COLS or CITY_FEATURE_COLS:
        temporal_cols = WEATHER_FEATURE_COLS + CITY_FEATURE_COLS
        master[temporal_cols] = (
            master.sort_values(["timestamp", "node_id", "station_id"])
            .groupby("timestamp", observed=True)[temporal_cols]
            .transform(lambda g: g.ffill().bfill())
        )
        master[temporal_cols] = master.groupby("timestamp", observed=True)[temporal_cols].transform(
            lambda g: g.ffill().bfill()
        )

    for col in MASTER_FEATURE_COLS:
        if master[col].isna().any():
            col_median = master[col].median(skipna=True)
            if pd.isna(col_median):
                col_median = 0.0
            master[col] = master[col].fillna(float(col_median))

    master = master.sort_values(["timestamp", "node_id", "station_id"]).reset_index(drop=True)
    return master


def append_readme_sync_note(horizon: pd.Timestamp) -> None:
    note_header = "### Automated Sync Gate"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    horizon_str = horizon.strftime("%Y-%m-%d %H:%M:%S") + " UTC"
    note_line = (
        f"- Sync gate active: full merge runs only when raw-data horizon exceeds master horizon. "
        f"Latest Data Horizon: {horizon_str} (updated {now})."
    )

    text = README_PATH.read_text(encoding="utf-8") if README_PATH.exists() else ""
    if note_header not in text:
        if text and not text.endswith("\n"):
            text += "\n"
        text += f"\n{note_header}\n\n"

    text = re.sub(r"^- Sync gate active: .*\n", "", text, flags=re.MULTILINE)
    text += f"{note_line}\n"
    README_PATH.write_text(text, encoding="utf-8")


def print_activate_hook_instructions() -> None:
    print("\n[AUTOMATION] Add this block to .venv/bin/activate to run sync on environment entry:")
    print("--------------------")
    print('if [ -f "$VIRTUAL_ENV/../scripts/sync_on_entry.py" ]; then')
    print('  "$VIRTUAL_ENV/bin/python" "$VIRTUAL_ENV/../scripts/sync_on_entry.py"')
    print("fi")
    print("--------------------")


def main() -> None:
    processed_max = processed_horizon()
    raw_max = raw_data_horizon()

    if raw_max is None:
        raise RuntimeError("Unable to determine raw data horizon from parquet inputs.")

    if not MAP_PATH.exists():
        raise FileNotFoundError(f"Required helper file not found: {MAP_PATH}")

    # Keep helper ratios persisted even when main sync is skipped.
    _load_or_build_ratio_maps(force_refresh=False)

    if processed_max is not None and raw_max <= processed_max:
        horizon_str = processed_max.strftime("%Y-%m-%d %H:%M:%S") + " UTC"
        print(f"[CHECKPOINT] Data is up to date (Horizon: {horizon_str}). Skipping sync.")
        print_activate_hook_instructions()
        return

    print("[SYNC] Applying pollutant ratio logic...")
    master = build_master_dataframe(force_refresh_ratios=True)

    if master.empty:
        raise RuntimeError("Master dataframe is empty after merge; aborting write.")

    new_horizon = to_hour_local(pd.to_datetime(master["timestamp"]).max())
    if new_horizon is None:
        raise RuntimeError("Could not determine new master horizon.")

    if processed_max is None:
        new_hours = int(master["timestamp"].nunique())
    else:
        new_hours = int((pd.to_datetime(master["timestamp"]) > processed_max).sum())
        # Convert row count to hourly count.
        new_hours = int(pd.to_datetime(master.loc[pd.to_datetime(master["timestamp"]) > processed_max, "timestamp"]).nunique())

    MASTER_PATH.parent.mkdir(parents=True, exist_ok=True)
    master.to_parquet(MASTER_PATH, index=False)

    append_readme_sync_note(new_horizon)

    horizon_str = new_horizon.strftime("%Y-%m-%d %H:%M:%S") + " UTC"
    print(f"[SYNC] Detected {new_hours} new hours of data. Master tensor updated.")
    print(f"[STATUS] New Data Horizon: {horizon_str}.")
    print_activate_hook_instructions()


if __name__ == "__main__":
    main()
