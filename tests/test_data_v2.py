"""Causal split and fitting invariants on synthetic data."""
import numpy as np
import pandas as pd
import pytest

from src.stpignn.data_v2 import assert_input_cutoff, split_masks, train_only_mean_std


def test_input_must_end_at_forecast_cutoff():
    assert_input_cutoff(20, np.arange(8, 20), 1)
    with pytest.raises(AssertionError):
        assert_input_cutoff(20, np.arange(9, 21), 1)


def test_splits_disjoint_and_gap_enforced():
    times = pd.date_range("2025-06-27", "2025-09-25", freq="h", tz="UTC")
    cfg = {"train_start_utc": "2025-06-27T00:00Z", "train_end_utc": "2025-06-29T23:00Z",
           "validation_start_utc": "2025-07-01T00:00Z", "validation_end_utc": "2025-09-21T23:00Z",
           "test_start_utc": "2025-09-23T00:00Z", "test_end_utc": "2025-09-25T00:00Z",
           "minimum_gap_hours": 24}
    masks = split_masks(times, cfg)
    assert not np.any(masks["train"] & masks["validation"])
    assert not np.any(masks["validation"] & masks["test"])
    cfg["validation_start_utc"] = "2025-06-30T23:00Z"
    with pytest.raises(AssertionError):
        split_masks(times, cfg)


def test_fitted_statistic_ignores_validation_and_test():
    x = np.array([1.0, 2.0, 3.0, 100.0, 1000.0])
    train = np.array([True, True, True, False, False])
    before = train_only_mean_std(x, train)
    x[~train] = -999999.0
    assert before == train_only_mean_std(x, train)
