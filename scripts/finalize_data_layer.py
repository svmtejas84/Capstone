"""
scripts/finalize_data_layer.py

Finalizes the data layer by:
1) Repairing 2022 city-level air quality gaps using station-based IDW interpolation.
2) Mapping station coordinates to nearest road-network nodes (UTM 43N) via KDTree.

Usage:
    python scripts/finalize_data_layer.py
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from pyproj import Transformer
from scipy.spatial import KDTree

CITY_CENTER_LAT = 12.9716
CITY_CENTER_LON = 77.5946

AIR_2022_PATH = Path("data/raw/airquality/2022.parquet")
STATION_2022_PATH = Path("data/raw/stations/2022.parquet")
STATION_2023_PATH = Path("data/raw/stations/2023.parquet")
STATION_META_PATH = Path("data/raw/stations/meta.parquet")
NODES_PATH = Path("data/graphs/bangalore_utm_nodes.parquet")
STATION_NODE_MAP_OUT = Path("data/processed/station_node_map.parquet")

CITY_TO_STATION_PARAM = {
    "nitrogen_dioxide": "no2",
    "sulphur_dioxide": "so2",
    "pm2_5": "pm25",
    "pm10": "pm10",
    "carbon_monoxide": "co",
}

RATIO_TARGET_PARAMS = ["pm25", "no2", "co"]


def haversine_meters(lat1: float, lon1: float, lat2: np.ndarray, lon2: np.ndarray) -> np.ndarray:
    """Compute great-circle distance in meters from one point to many points."""
    r = 6_371_000.0
    lat1_rad = np.radians(lat1)
    lon1_rad = np.radians(lon1)
    lat2_rad = np.radians(lat2)
    lon2_rad = np.radians(lon2)

    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = np.sin(dlat / 2.0) ** 2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon / 2.0) ** 2
    c = 2.0 * np.arctan2(np.sqrt(a), np.sqrt(1.0 - a))
    return r * c


def idw_estimate(values: np.ndarray, distances_m: np.ndarray, power: float = 2.0) -> float:
    """Estimate value with inverse-distance weighting."""
    if values.size == 0:
        return np.nan

    zero_mask = distances_m == 0.0
    if np.any(zero_mask):
        return float(np.mean(values[zero_mask]))

    weights = 1.0 / np.power(distances_m, power)
    return float(np.sum(weights * values) / np.sum(weights))


def normalize_time_index(df: pd.DataFrame) -> pd.DataFrame:
    """Convert index to naive local datetime for safe joining across files."""
    idx = df.index
    if not isinstance(idx, pd.DatetimeIndex):
        idx = pd.to_datetime(idx)

    if idx.tz is not None:
        idx = idx.tz_convert("Asia/Kolkata").tz_localize(None)

    out = df.copy()
    out.index = idx
    out.index.name = "time"
    return out


def _station_ratio_fingerprint_2023(station_2023_df: pd.DataFrame) -> tuple[dict[str, pd.Series], dict[str, float]]:
    """Build per-station and global pollutant/pm10 ratios from 2023 data."""
    station_2023_df = normalize_time_index(station_2023_df)
    y2023 = station_2023_df[station_2023_df.index.year == 2023]
    if y2023.empty:
        print("Warning: stations/2023.parquet has no calendar-year 2023 rows; using all rows in file for ratio fingerprint.")
        y2023 = station_2023_df.copy()

    cols = ["station_id", "parameter", "value"]
    y2023 = y2023[cols].dropna(subset=["station_id", "parameter", "value"])

    pivot = (
        y2023.assign(hour=y2023.index.floor("h"))
        .groupby(["hour", "station_id", "parameter"], observed=True)["value"]
        .mean()
        .unstack("parameter")
    )

    if pivot.empty or "pm10" not in pivot.columns:
        raise ValueError("2023 station data must contain pm10 to compute pollutant ratios.")

    pm10 = pivot["pm10"]
    per_station_ratios: dict[str, pd.Series] = {}
    global_ratios: dict[str, float] = {}

    means = y2023.groupby(["station_id", "parameter"], observed=True)["value"].mean().unstack("parameter")

    for pollutant in RATIO_TARGET_PARAMS:
        if pollutant not in pivot.columns:
            raise ValueError(f"2023 station data is missing required pollutant: {pollutant}")

        direct = (pivot[pollutant] / pm10).replace([np.inf, -np.inf], np.nan)
        direct = direct.where(pm10 > 0)
        ratio_by_station = direct.groupby("station_id").mean()

        if pollutant in means.columns and "pm10" in means.columns:
            ratio_of_means = (means[pollutant] / means["pm10"]).replace([np.inf, -np.inf], np.nan)
            ratio_by_station = ratio_by_station.fillna(ratio_of_means)

        ratio_by_station = ratio_by_station.where(ratio_by_station > 0)
        if ratio_by_station.dropna().empty:
            raise ValueError(f"Could not compute valid 2023 ratio for pollutant: {pollutant}")

        global_ratio = float(ratio_by_station.dropna().mean())
        per_station_ratios[pollutant] = ratio_by_station
        global_ratios[pollutant] = global_ratio

    return per_station_ratios, global_ratios


def impute_2022_station_pollutants_from_2023() -> pd.DataFrame:
    """Impute 2022 station PM2.5/NO2/CO from PM10 using 2023 station-specific ratios."""
    station_2022_df = normalize_time_index(pd.read_parquet(STATION_2022_PATH))
    station_2023_df = pd.read_parquet(STATION_2023_PATH)

    per_station_ratios, global_ratios = _station_ratio_fingerprint_2023(station_2023_df)

    # Keep only 2022 rows for enrichment.
    station_2022_df = station_2022_df[station_2022_df.index.year == 2022]

    units_by_param = (
        station_2023_df.reset_index()
        .groupby("parameter", observed=True)["unit"]
        .agg(lambda s: s.mode().iat[0] if not s.mode().empty else s.dropna().iat[0])
        .to_dict()
    )

    rows_2022 = station_2022_df.reset_index()
    pm10_rows = rows_2022[rows_2022["parameter"] == "pm10"].copy()
    if pm10_rows.empty:
        raise ValueError("2022 station data has no pm10 rows to anchor ratio-based imputation.")

    generated_parts: list[pd.DataFrame] = []
    for pollutant in RATIO_TARGET_PARAMS:
        ratios = per_station_ratios[pollutant]
        base = pm10_rows[["time", "station_id", "station_name", "value"]].copy()
        station_ratio = base["station_id"].map(ratios)
        base["ratio"] = station_ratio.fillna(global_ratios[pollutant])
        base["parameter"] = pollutant
        base["value"] = base["value"] * base["ratio"]
        base["unit"] = units_by_param.get(pollutant, pm10_rows["unit"].mode().iat[0])
        generated_parts.append(base[["time", "parameter", "value", "unit", "station_id", "station_name"]])

    generated = pd.concat(generated_parts, ignore_index=True)

    existing_targets = rows_2022[rows_2022["parameter"].isin(RATIO_TARGET_PARAMS)].copy()
    non_targets = rows_2022[~rows_2022["parameter"].isin(RATIO_TARGET_PARAMS)].copy()

    # Preserve any observed target pollutant rows; fill only missing triplets using generated values.
    all_targets = pd.concat([existing_targets, generated], ignore_index=True)
    all_targets = all_targets.sort_values(["time", "station_id", "parameter"]).drop_duplicates(
        subset=["time", "station_id", "parameter"], keep="first"
    )

    finalized = pd.concat([non_targets, all_targets], ignore_index=True)
    finalized = finalized.sort_values(["time", "station_id", "parameter"]).set_index("time")

    finalized.to_parquet(STATION_2022_PATH, index=True)

    print("2023 ratio fingerprint (pollutant / pm10):")
    for pollutant in RATIO_TARGET_PARAMS:
        print(f"  {pollutant}: global_mean_ratio={global_ratios[pollutant]:.4f}")
    print(f"Imputed/assembled 2022 station rows: {len(finalized):,}")

    return finalized


def repair_airquality_2022_with_idw() -> pd.DataFrame:
    city_df = pd.read_parquet(AIR_2022_PATH)
    station_df = pd.read_parquet(STATION_2022_PATH)
    station_meta = pd.read_parquet(STATION_META_PATH)

    city_df = normalize_time_index(city_df)
    station_df = normalize_time_index(station_df)

    # Keep only the 2022 window covered by the city file.
    t_min = city_df.index.min()
    t_max = city_df.index.max()
    station_df = station_df[(station_df.index >= t_min) & (station_df.index <= t_max)]

    coords = station_meta[["id", "lat", "lon"]].dropna().set_index("id")

    initial_missing = int(city_df.isna().sum().sum())
    station_params_2022 = sorted(station_df["parameter"].dropna().unique().tolist())
    print(f"Station parameters available in 2022 window: {station_params_2022}")

    for city_col, station_param in CITY_TO_STATION_PARAM.items():
        missing_times = city_df.index[city_df[city_col].isna()]
        if len(missing_times) == 0:
            continue

        subset = station_df[station_df["parameter"] == station_param][["station_id", "value"]].dropna()
        if subset.empty:
            continue

        # Aggregate 15-min sensor readings to hourly means per station.
        hourly = (
            subset.assign(hour=subset.index.floor("h"))
            .groupby(["hour", "station_id"], observed=True)["value"]
            .mean()
            .unstack("station_id")
        )

        for ts in missing_times:
            if ts not in hourly.index:
                continue

            row = hourly.loc[ts].dropna()
            if row.empty:
                continue

            common_ids = [sid for sid in row.index if sid in coords.index]
            if not common_ids:
                continue

            vals = row.loc[common_ids].to_numpy(dtype=float)
            lats = coords.loc[common_ids, "lat"].to_numpy(dtype=float)
            lons = coords.loc[common_ids, "lon"].to_numpy(dtype=float)
            dists = haversine_meters(CITY_CENTER_LAT, CITY_CENTER_LON, lats, lons)

            city_df.at[ts, city_col] = idw_estimate(vals, dists, power=2.0)

    city_df.to_parquet(AIR_2022_PATH, index=True)

    repaired_missing = int(city_df.isna().sum().sum())
    print(f"Initial 2022 missing count: {initial_missing}")
    print(f"Remaining 2022 missing count: {repaired_missing}")

    return city_df


def build_station_node_mapping() -> pd.DataFrame:
    station_meta = pd.read_parquet(STATION_META_PATH)
    nodes = pd.read_parquet(NODES_PATH)

    required_node_cols = {"osmid", "x", "y"}
    missing_cols = required_node_cols - set(nodes.columns)
    if missing_cols:
        raise ValueError(f"Missing required node columns in {NODES_PATH}: {sorted(missing_cols)}")

    transformer = Transformer.from_crs("EPSG:4326", "EPSG:32643", always_xy=True)
    station_x, station_y = transformer.transform(station_meta["lon"].to_numpy(), station_meta["lat"].to_numpy())

    node_xy = nodes[["x", "y"]].to_numpy(dtype=float)
    tree = KDTree(node_xy)

    distances, idx = tree.query(np.column_stack([station_x, station_y]), k=1)

    mapped = pd.DataFrame(
        {
            "location_id": station_meta["id"].to_numpy(),
            "station_name": station_meta["name"].to_numpy(),
            "node_id": nodes.iloc[idx]["osmid"].to_numpy(),
            "distance_meters": distances.astype(float),
        }
    )

    STATION_NODE_MAP_OUT.parent.mkdir(parents=True, exist_ok=True)
    mapped.to_parquet(STATION_NODE_MAP_OUT, index=False)

    print(f"Average Snap Distance (m): {mapped['distance_meters'].mean():.2f}")

    return mapped


def main() -> None:
    print("=== Finalize Data Layer ===")
    impute_2022_station_pollutants_from_2023()
    repair_airquality_2022_with_idw()
    build_station_node_mapping()
    print(f"Saved station-node mapping -> {STATION_NODE_MAP_OUT}")


if __name__ == "__main__":
    main()
