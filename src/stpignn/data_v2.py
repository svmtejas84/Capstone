"""Observed-only, UTC-aligned station data with train-only fitting.

No statistic in this module is fit after the configured training end. Inputs
for a target at hour t+h are sliced only through t. Missing environmental
channels are recorded and omitted, never duplicated or fabricated.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import warnings

import numpy as np
import pandas as pd
import yaml

from .paths import REPO_ROOT

POLLUTANTS = {
    "pm25": ("pm25_lagged", "µg/m³"),
    "pm10": ("pm10", "µg/m³"),
    "no2": ("no2", "µg/m³"),
    "so2": ("so2", "µg/m³"),
    "co": ("co", "µg/m³"),
}
WEATHER = {
    "wind_speed_10m": ("wind_speed", "m/s"),
    "wind_gusts_10m": ("wind_gusts", "m/s"),
    "temperature_2m": ("temperature", "°C"),
    "relative_humidity_2m": ("humidity", "%"),
    "surface_pressure": ("surface_pressure", "hPa"),
}
REQUESTED_MISSING = {
    "pblh": "No boundary-layer-height column or file in raw weather sources",
    "population_density": "No population raster or node-level population source",
    "road_proximity": "No precomputed distance-to-road source; OSM graph nodes lie on roads",
    "traffic_index": "No time-indexed traffic or emissions source",
}


def utc_hour(values, assume_naive_utc=False):
    idx = pd.DatetimeIndex(pd.to_datetime(values))
    if idx.tz is None:
        if not assume_naive_utc:
            raise ValueError("Station observations must carry timezone information")
        idx = idx.tz_localize("UTC")
    return idx.tz_convert("UTC").floor("h")


def split_masks(times: pd.DatetimeIndex, cfg: dict) -> dict[str, np.ndarray]:
    out = {}
    for name, prefix in (("train", "train"), ("validation", "validation"), ("test", "test")):
        a = pd.Timestamp(cfg[f"{prefix}_start_utc"])
        b = pd.Timestamp(cfg[f"{prefix}_end_utc"])
        out[name] = np.asarray((times >= a) & (times <= b), dtype=bool)
    if np.any(out["train"] & out["validation"]) or np.any(out["train"] & out["test"]) or np.any(out["validation"] & out["test"]):
        raise AssertionError("Split timestamps overlap")
    gap = int(cfg["minimum_gap_hours"])
    if (pd.Timestamp(cfg["validation_start_utc"]) - pd.Timestamp(cfg["train_end_utc"])).total_seconds() / 3600 <= gap:
        raise AssertionError("Train/validation gap is too short")
    if (pd.Timestamp(cfg["test_start_utc"]) - pd.Timestamp(cfg["validation_end_utc"])).total_seconds() / 3600 <= gap:
        raise AssertionError("Validation/test gap is too short")
    return out


def assert_input_cutoff(target_index: int, input_indices: np.ndarray, horizon: int) -> None:
    cutoff = target_index - horizon
    if len(input_indices) == 0 or np.max(input_indices) > cutoff:
        raise AssertionError("Input includes a timestamp later than forecast cutoff")


def train_only_mean_std(values: np.ndarray, time_mask: np.ndarray):
    train = np.asarray(values)[time_mask]
    finite = train[np.isfinite(train)]
    if len(finite) == 0:
        raise ValueError("No finite training values for fitted statistic")
    return float(np.mean(finite)), float(np.std(finite) or 1.0)


@dataclass
class DataV2:
    times: pd.DatetimeIndex
    station_ids: np.ndarray
    node_indices: np.ndarray
    coordinates: np.ndarray
    elevation_m: np.ndarray
    raw_values: np.ndarray  # [T,N,F], before train-fitted normalization
    features: np.ndarray  # [T,N,F], finite normalized network inputs
    raw_wind_degrees: np.ndarray  # [T], unscaled meteorological FROM direction
    observed_target: np.ndarray  # [T,N], NaN for missing raw observation
    observed_mask: np.ndarray  # [T,N]
    imputed_target: np.ndarray  # [T,N], train-only-fitted, never evaluation truth
    imputation_tier: np.ndarray  # [T,N], O/R/C/D/M
    split_masks: dict[str, np.ndarray]
    feature_registry: list[dict]
    fit: dict
    config: dict

    def target_indices(self, split: str, horizon: int, observed_only=True) -> np.ndarray:
        mask = self.split_masks[split].copy()
        mask[:int(self.config["history_hours"]) - 1 + horizon] = False
        eligible = self.observed_mask.any(axis=1) if observed_only else np.isfinite(self.imputed_target).any(axis=1)
        return np.flatnonzero(mask & eligible)

    def window(self, target_index: int, horizon: int, mask_own_history=False):
        cutoff = target_index - horizon
        history = int(self.config["history_hours"])
        indices = np.arange(cutoff - history + 1, cutoff + 1)
        assert_input_cutoff(target_index, indices, horizon)
        if indices.min() < 0:
            raise IndexError("Insufficient history")
        x = self.features[indices].copy()
        if mask_own_history:
            x[:, :, 0] = 0.0
        return x, self.observed_target[target_index].copy(), self.observed_mask[target_index].copy()


def _load_raw_table(pattern: str, skip_meta=False):
    paths = sorted(REPO_ROOT.glob(pattern))
    if skip_meta:
        paths = [p for p in paths if p.name != "meta.parquet"]
    frames = [pd.read_parquet(path).reset_index() for path in paths]
    if not frames:
        raise FileNotFoundError(pattern)
    return pd.concat(frames, ignore_index=True), [str(p.relative_to(REPO_ROOT)) for p in paths]


def _station_values(raw: pd.DataFrame, times: pd.DatetimeIndex, station_ids: np.ndarray, parameter: str) -> np.ndarray:
    subset = raw.loc[raw.parameter.eq(parameter), ["station_id", "time_utc", "value"]]
    subset = subset[np.isfinite(pd.to_numeric(subset.value, errors="coerce"))]
    subset = subset[pd.to_numeric(subset.value, errors="coerce") >= 0]
    grouped = subset.groupby(["time_utc", "station_id"], observed=True).value.mean().reset_index()
    pivot = grouped.pivot(index="time_utc", columns="station_id", values="value")
    return pivot.reindex(index=times, columns=station_ids).to_numpy(dtype=np.float32)


def _train_climatology(values: np.ndarray, times: pd.DatetimeIndex, train_mask: np.ndarray):
    """Fit per-station hour/day medians using only training observations."""
    group = (times.hour * 7 + times.dayofweek).to_numpy()
    table = np.full((168, values.shape[1]), np.nan, dtype=np.float32)
    for key in range(168):
        selected = values[train_mask & (group == key)]
        if selected.size:
            with np.errstate(all="ignore"), warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)
                table[key] = np.nanmedian(selected, axis=0)
    with np.errstate(all="ignore"), warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        station_median = np.nanmedian(values[train_mask], axis=0)
        global_median = float(np.nanmedian(values[train_mask]))
    if not np.isfinite(global_median):
        raise ValueError("No observed PM2.5 training data")
    return table, station_median, global_median


def _fit_imputed_pm25(pm25, pm10, times, train_mask, station_ids):
    table, station_median, global_median = _train_climatology(pm25, times, train_mask)
    ratio = np.full(pm25.shape[1], np.nan, dtype=np.float32)
    for station in range(pm25.shape[1]):
        matched = train_mask & np.isfinite(pm25[:, station]) & np.isfinite(pm10[:, station]) & (pm10[:, station] > 0)
        if matched.any():
            ratio[station] = np.median(pm25[matched, station] / pm10[matched, station])
    out = pm25.copy()
    tier = np.full(pm25.shape, "M", dtype="U1")
    tier[np.isfinite(pm25)] = "O"
    for station in range(pm25.shape[1]):
        missing = ~np.isfinite(out[:, station])
        if np.isfinite(ratio[station]):
            rmask = missing & np.isfinite(pm10[:, station])
            out[rmask, station] = pm10[rmask, station] * ratio[station]
            tier[rmask, station] = "R"
        missing = ~np.isfinite(out[:, station])
        keys = (times.hour * 7 + times.dayofweek).to_numpy()
        climat = table[keys, station]
        cmask = missing & np.isfinite(climat)
        out[cmask, station] = climat[cmask]
        tier[cmask, station] = "C"
        missing = ~np.isfinite(out[:, station])
        fill = station_median[station] if np.isfinite(station_median[station]) else global_median
        out[missing, station] = fill
        tier[missing, station] = "D"
    return out, tier, {"ratio_by_station": dict(zip(station_ids.astype(str), ratio.tolist())),
                       "climatology": table.tolist(), "station_median": station_median.tolist(),
                       "global_median": global_median}


def _causal_fill(values: np.ndarray, train_mask: np.ndarray, max_forward: int):
    shape = values.shape
    out = values.copy()
    train_medians = np.empty(shape[2], dtype=np.float32)
    for feature in range(shape[2]):
        train = values[train_mask, :, feature]
        finite = train[np.isfinite(train)]
        if len(finite) == 0:
            raise ValueError(f"Feature {feature} has no training values")
        train_medians[feature] = np.median(finite)
        for station in range(shape[1]):
            series = pd.Series(out[:, station, feature])
            out[:, station, feature] = series.ffill(limit=max_forward).fillna(train_medians[feature]).to_numpy(dtype=np.float32)
    return out, train_medians


def build(config_path: Path) -> tuple[DataV2, dict]:
    cfg = yaml.safe_load(Path(config_path).read_text())
    times = pd.date_range(cfg["train_start_utc"], cfg["test_end_utc"], freq="h", tz="UTC")
    if not times.is_monotonic_increasing or not times.is_unique or np.any(np.diff(times.asi8) != 3_600_000_000_000):
        raise AssertionError("Global UTC timeline must be unique and gapless")
    splits = split_masks(times, cfg)
    raw, source_paths = _load_raw_table(cfg["raw_stations_glob"], skip_meta=True)
    raw["time_utc"] = utc_hour(raw["time"])
    raw["value"] = pd.to_numeric(raw.value, errors="coerce")
    raw = raw.loc[raw.station_id.notna() & raw.parameter.isin(POLLUTANTS)]
    raw = raw.loc[np.isfinite(raw.value) & (raw.value >= 0)]
    station_ids = np.sort(raw.loc[raw.parameter.eq("pm25"), "station_id"].unique()).astype(np.int64)
    station_map = pd.read_parquet(REPO_ROOT / cfg["station_to_node"])
    node_map = pd.read_parquet(REPO_ROOT / cfg["node_index_map"])
    metadata = pd.read_parquet(REPO_ROOT / cfg["station_metadata"])
    elevation = pd.read_parquet(REPO_ROOT / cfg["true_elevation"])
    station = pd.DataFrame({"station_id": station_ids})
    station = station.merge(station_map, left_on="station_id", right_on="location_id", validate="one_to_one")
    station = station.merge(node_map, left_on="node_id", right_on="node_id", validate="one_to_one")
    station = station.merge(metadata[["id", "lat", "lon"]], left_on="station_id", right_on="id", validate="one_to_one")
    station = station.merge(elevation[["osmid", "elevation_true", "utm_x", "utm_y"]], left_on="node_id", right_on="osmid", validate="one_to_one")
    if station.node_index.isna().any() or station.elevation_true.isna().any():
        raise ValueError("Observed station mapping or SRTM elevation missing")
    n = len(station)
    observed = {p: _station_values(raw, times, station_ids, p) for p in POLLUTANTS}
    target = observed["pm25"]
    observed_mask = np.isfinite(target)
    imputed, tier, impute_fit = _fit_imputed_pm25(target, observed["pm10"], times, splits["train"], station_ids)

    weather_raw, weather_paths = _load_raw_table(cfg["raw_weather_glob"])
    weather_raw["time_utc"] = utc_hour(weather_raw.time, assume_naive_utc=True)
    weather = weather_raw.groupby("time_utc", observed=True).mean(numeric_only=True).reindex(times)
    wind_raw = weather["wind_direction_10m"].to_numpy(dtype=np.float32)
    # Direction is a circular measurement; retain raw degrees for physics.
    wind_sin = np.sin(np.deg2rad(wind_raw)).astype(np.float32)
    wind_cos = np.cos(np.deg2rad(wind_raw)).astype(np.float32)
    channels, registry = [], []

    def add(name, source, units, array):
        channels.append(np.asarray(array, dtype=np.float32))
        registry.append({"order": len(registry), "name": name, "source": source, "units": units,
                         "status": "available"})

    for pollutant, (name, units) in POLLUTANTS.items():
        values = imputed if pollutant == "pm25" else observed[pollutant]
        add(name, f"raw station {pollutant}; train-only fill", units, values)
    for raw_name, (name, units) in WEATHER.items():
        values = weather[raw_name].to_numpy(dtype=np.float32)[:, None].repeat(n, axis=1)
        add(name, f"raw weather {raw_name}", units, values)
    add("wind_direction_sin", "sin(raw weather wind_direction_10m degrees)", "unitless", wind_sin[:, None].repeat(n, axis=1))
    add("wind_direction_cos", "cos(raw weather wind_direction_10m degrees)", "unitless", wind_cos[:, None].repeat(n, axis=1))
    add("srtm_elevation", cfg["true_elevation"] + ":elevation_true", "m",
        station.elevation_true.to_numpy(dtype=np.float32)[None, :].repeat(len(times), axis=0))
    for name, reason in REQUESTED_MISSING.items():
        registry.append({"order": None, "name": name, "source": None, "units": None,
                         "status": "missing", "reason": reason})
    raw_values = np.stack(channels, axis=2)
    filled, fill_medians = _causal_fill(raw_values, splits["train"], int(cfg["feature_forward_fill_limit_hours"]))
    train_values = filled[splits["train"]]
    means = train_values.mean(axis=(0, 1))
    stds = train_values.std(axis=(0, 1))
    stds[stds == 0] = 1.0
    features = ((filled - means) / stds).astype(np.float32)
    pm_train = target[splits["train"]]
    pm_train = pm_train[np.isfinite(pm_train)]
    target_mean = float(pm_train.mean())
    target_std = float(pm_train.std())
    log_train = np.log1p(pm_train)
    fit = {"fit_end_utc": cfg["train_end_utc"], "feature_means": means.tolist(),
           "feature_stds": stds.tolist(), "feature_train_medians": fill_medians.tolist(),
           "target_standard_mean": target_mean, "target_standard_std": target_std,
           "target_log1p_mean": float(log_train.mean()), "target_log1p_std": float(log_train.std()),
           "legacy_342_9356_ratio_to_train_std": 342.9356 / target_std,
           "imputation": impute_fit}
    data = DataV2(times, station_ids, station.node_index.to_numpy(dtype=np.int64),
                  station[["utm_x", "utm_y"]].to_numpy(dtype=np.float32),
                  station.elevation_true.to_numpy(dtype=np.float32), raw_values, features,
                  wind_raw, target, observed_mask, imputed, tier, splits, registry, fit, cfg)
    provenance = {"station_sources": source_paths, "weather_sources": weather_paths,
                  "raw_rows": len(raw), "observed_pm25_pairs": int(observed_mask.sum()),
                  "timeline_hours": len(times), "missing_weather_direction_hours": int(np.isnan(wind_raw).sum()),
                  "missing_requested_channels": REQUESTED_MISSING}
    return data, {"station_table": station, "provenance": provenance}
