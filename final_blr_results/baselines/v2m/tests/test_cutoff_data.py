"""Essential v2m data invariants; no model training."""
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
OLD = np.load(ROOT / "results/data_v2j_arrays.npz")
NEW = np.load(ROOT / "final_blr_results/baselines/v2m/data/data_v2m_arrays.npz")
FIT = json.loads((ROOT / "final_blr_results/baselines/v2m/data/data_v2m_fit.json").read_text())

def test_targets_masks_and_timeline():
    for key in ("times_ns", "station_ids", "observed_mask", "observed_target"):
        assert np.array_equal(OLD[key], NEW[key], equal_nan=True)

def test_shapes_and_finiteness():
    assert NEW["features"].shape == (37152, 15, 13)
    assert NEW["features"].shape[-1] + 1 + 4 == 18
    assert np.isfinite(NEW["features"]).all()

def test_weather_timestamp_and_cutoff():
    from src.stpignn.data_v2 import weather_utc_half_hours
    raw = pd.DatetimeIndex(["2025-09-23T07:00:00"])
    assert weather_utc_half_hours(raw)[0] == pd.Timestamp("2025-09-23T01:30:00Z")
    cutoff = pd.Timestamp("2025-09-23T02:00:00Z")
    assert pd.Timestamp("2025-09-23T01:30:00Z") <= cutoff
    assert FIT["sample_cutoff_utc"] == cutoff.isoformat().replace("+00:00", "Z")
    assert FIT["sample_temperature_c"] == 20.7

if __name__ == "__main__":
    test_targets_masks_and_timeline()
    test_shapes_and_finiteness()
    test_weather_timestamp_and_cutoff()
    print("3 essential v2m data checks passed")
