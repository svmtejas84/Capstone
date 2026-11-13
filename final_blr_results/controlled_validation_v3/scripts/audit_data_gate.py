"""Read-only timestamp and future-perturbation audit for the v3 candidate array."""
from pathlib import Path
import csv
import hashlib
import json
import numpy as np
import pandas as pd

from src.stpignn.data_v2 import _causal_fill, _fit_imputed_pm25

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parents[1]
ARRAY = ROOT / "final_blr_results/baselines/v2m/data/data_v2m_arrays.npz"


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(4 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main():
    z = np.load(ARRAY)
    times = pd.to_datetime(z["times_ns"], utc=True)
    assert z["features"].shape == (37152, 15, 13)
    assert len(z["station_ids"]) == 15
    assert times.max() == pd.Timestamp("2026-03-28T23:00:00Z")
    assert np.isfinite(z["features"]).all()
    test = (times >= pd.Timestamp("2025-09-23T00:00:00Z")) & (times <= times.max())
    assert int(np.isfinite(z["observed_target"][test]).sum()) == 14583

    # A future mutation cannot change causal forward filling at an earlier issue.
    a = np.array([[[1.0]], [[np.nan]], [[np.nan]], [[4.0]], [[np.nan]]], np.float32)
    train = np.array([True, True, False, False, False])
    early = _causal_fill(a, train, 24)[0][:3].copy()
    b = a.copy(); b[3:] = 1e6
    assert np.array_equal(early, _causal_fill(b, train, 24)[0][:3])

    # Same-hour IDW and train-only ratios must not draw future PM2.5 into early inputs.
    t = pd.date_range("2024-01-01", periods=5, freq="h", tz="UTC")
    pm = np.array([[10., 20.], [np.nan, 21.], [12., np.nan], [13., 23.], [14., 24.]], np.float32)
    pm10 = np.full_like(pm, 30.)
    fit = np.array([True, True, False, False, False])
    xy = np.array([[0., 0.], [1., 0.]])
    early = _fit_imputed_pm25(pm, pm10, t, fit, np.array([1, 2]), xy)[0][:3].copy()
    changed = pm.copy(); changed[3:] = 1e6
    assert np.array_equal(early, _fit_imputed_pm25(changed, pm10, t, fit, np.array([1, 2]), xy)[0][:3])

    sources = ["configs/data_v2.yaml", "configs/benchmark_v2g.yaml", "src/stpignn/data_v2.py",
               "src/stpignn/physics_v2.py", "scripts/benchmark_v2j.py",
               "final_blr_results/baselines/v2m/data/data_v2m_arrays.npz",
               "final_blr_results/baselines/v2m/data/data_v2m_fit.json"]
    (OUT / "data_manifests").mkdir(exist_ok=True)
    with (OUT / "data_manifests/source_checksums.csv").open("w", newline="") as f:
        w = csv.writer(f); w.writerow(["path", "sha256", "bytes"])
        for p in sources:
            q = ROOT / p
            w.writerow([p, sha(q), q.stat().st_size])
    summary = {
        "array_sha256": sha(ARRAY), "first_utc": times.min().isoformat(), "last_utc": times.max().isoformat(),
        "station_count": 15, "base_feature_count": 13, "model_feature_count": 18,
        "test_observed_pairs": 14583,
        "causal_fill_synthetic_future_mutation": "PASS",
        "pm25_imputation_synthetic_future_mutation": "PASS",
        "weather_timestamp_rule": "source-inspected: latest archive record timestamp <= feature hour; actual release latency unknown",
        "new_untouched_temporal_holdout": False,
        "operational_issue_time_verification": False,
    }
    (OUT / "data_manifests/eligibility.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
