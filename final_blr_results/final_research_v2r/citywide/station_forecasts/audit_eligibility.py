"""Read-only station eligibility and one fold-safe feature-builder audit."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd

from src.stpignn.data_v2 import build

OUT = Path(__file__).resolve().parent


def main() -> None:
    z = np.load(ROOT / "results/data_v2j_arrays.npz")
    cfg = ROOT / "configs/data_v2.yaml"
    import yaml
    c = yaml.safe_load(cfg.read_text())
    times = pd.DatetimeIndex(pd.to_datetime(z["times_ns"], utc=True))
    rows = []
    for j, sid in enumerate(z["station_ids"]):
        row = {"station_id": int(sid), "station_index": j}
        for split in ("train", "validation", "test"):
            period = (times >= pd.Timestamp(c[f"{split}_start_utc"])) & (times <= pd.Timestamp(c[f"{split}_end_utc"]))
            row[f"observed_{split}_hours"] = int((z["observed_mask"][:, j] & period).sum())
        row["test_scored"] = bool(row["observed_test_hours"] > 0)
        rows.append(row)
    pd.DataFrame(rows).to_csv(OUT / "station_eligibility.csv", index=False)
    sid = next(row["station_id"] for row in rows if row["test_scored"])
    started = time.perf_counter()
    data, _ = build(cfg, excluded_station_id=sid, weather_half_hour_rule=True, weather_cutoff_safe=True)
    fit_ids = set(map(int, data.fit["fitted_station_ids"]))
    assert sid not in fit_ids and len(fit_ids) == len(rows)-1
    assert len(data.station_ids) == 15 and data.features.shape[-1] == 13
    idx = int(np.flatnonzero(data.station_ids == sid)[0])
    # Target remains available solely for future scoring, never as a fit source.
    assert np.isfinite(data.observed_target[:, idx]).any()
    result = {"audit_station_id": sid, "builder_seconds": time.perf_counter()-started,
              "station_count": len(rows), "feature_channels_base": data.features.shape[-1],
              "fit_station_count": len(fit_ids), "heldout_excluded_from_fit": True,
              "weather_half_hour_rule": True, "weather_cutoff_safe": True,
              "scored_test_stations": sum(row["test_scored"] for row in rows),
              "unscored_test_station_ids": [row["station_id"] for row in rows if not row["test_scored"]],
              "source_forecasts_generated": False}
    (OUT / "fold_builder_audit.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
