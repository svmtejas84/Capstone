"""Rejected raw values cannot reach observed targets or fitted statistics."""
import numpy as np
import pandas as pd
import yaml

from src.stpignn.data_v2 import _causal_fill, _clean_rows, _fit_imputed_pm25, _station_values, train_only_mean_std
from src.stpignn.paths import REPO_ROOT


def test_rejected_pm25_is_missing_before_target_and_fit():
    cfg = yaml.safe_load((REPO_ROOT / "configs/data_v2.yaml").read_text())
    times = pd.date_range("2025-01-01", periods=3, freq="h", tz="UTC")
    raw = pd.DataFrame({"time_utc": times, "station_id": [1, 1, 1],
                        "parameter": ["pm25"] * 3, "value": [20.0, 647953.0, 40.0]})
    cleaned, counts = _clean_rows(raw, cfg, "station", "time_utc")
    target = _station_values(cleaned, times, np.array([1]), "pm25")
    assert np.isnan(target[1, 0])
    assert target[0, 0] == 20.0 and target[2, 0] == 40.0
    assert train_only_mean_std(target, np.ones(3, dtype=bool)) == (30.0, 10.0)
    imputed, _, fit = _fit_imputed_pm25(target, np.full_like(target, np.nan), times,
                                       np.ones(3, dtype=bool), np.array([1]))
    features, medians = _causal_fill(imputed[:, :, None], np.ones(3, dtype=bool), max_forward=1)
    assert np.nanmax(imputed) <= 40.0
    assert np.nanmax(features) <= 40.0
    assert fit["global_median"] == 30.0 and medians[0] == 30.0
    assert int(counts.loc[counts.reason.eq("pm25_above_old_graph_cap"), "rows"].sum()) == 1


def test_weather_out_of_range_becomes_missing():
    cfg = yaml.safe_load((REPO_ROOT / "configs/data_v2.yaml").read_text())
    raw = pd.DataFrame({"time_utc": pd.date_range("2025-01-01", periods=2, freq="h", tz="UTC"),
                        "relative_humidity_2m": [50.0, 120.0], "temperature_2m": [30.0, 60.0]})
    cleaned, counts = _clean_rows(raw, cfg, "weather", "time_utc")
    assert pd.isna(cleaned.loc[1, "relative_humidity_2m"])
    assert pd.isna(cleaned.loc[1, "temperature_2m"])
    assert int(counts.loc[counts.reason.ne("kept"), "rows"].sum()) == 2
