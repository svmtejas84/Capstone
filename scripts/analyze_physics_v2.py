"""Measure mask coverage difference on the observed-station graph."""
import datetime as dt
import json
import subprocess

import numpy as np
import pandas as pd
import torch

from src.stpignn.paths import REPO_ROOT
from src.stpignn.physics_v2 import corrected_wind_mask, legacy_wind_mask
from src.stpignn.station_graph import directed_knn_graph


def main():
    cfg = __import__("yaml").safe_load((REPO_ROOT / "configs/data_v2.yaml").read_text())
    z = np.load(REPO_ROOT / "results/data_v2_arrays.npz")
    split = json.loads((REPO_ROOT / "results/splits_v2.json").read_text())
    times = pd.DatetimeIndex(pd.to_datetime(z["times_ns"], utc=True))
    xy = torch.as_tensor(z["coordinates"], dtype=torch.float32)
    edge_index, edge_attr = directed_knn_graph(z["coordinates"], int(cfg["station_graph_neighbours"]))
    # Reconstruct the exact legacy feature scaling from the master artifact.
    master = pd.read_parquet(REPO_ROOT / "data/processed/graph/master_scaled_checkpoint.parquet",
                             columns=["wind_direction_10m", "wind_direction_10m_scaled"])
    pair = master.dropna().drop_duplicates()
    slope, intercept = np.polyfit(pair.wind_direction_10m.to_numpy(float),
                                  pair.wind_direction_10m_scaled.to_numpy(float), 1)
    a = pd.Timestamp(split["requested_boundaries"]["validation_start_utc"])
    b = pd.Timestamp(split["requested_boundaries"]["validation_end_utc"])
    target_hours = np.flatnonzero(np.asarray((times >= a) & (times <= b)) & z["observed_mask"].any(axis=1))
    rows = []
    for target in target_hours:
        input_hour = target - int(cfg["primary_horizon_hours"])
        wind_raw = float(z["raw_wind_degrees"][input_hour])
        if not np.isfinite(wind_raw):
            continue
        corrected = corrected_wind_mask(xy, edge_index, wind_raw)
        legacy_scaled = slope * wind_raw + intercept
        legacy = legacy_wind_mask(xy, edge_index, legacy_scaled)
        union = int((corrected | legacy).sum())
        rows.append({"target_time_utc": times[target].isoformat(), "wind_from_degrees": wind_raw,
                     "legacy_scaled_direction": float(legacy_scaled),
                     "all_edges": edge_index.shape[1], "corrected_edges": int(corrected.sum()),
                     "legacy_edges": int(legacy.sum()),
                     "corrected_fraction": float(corrected.float().mean()),
                     "legacy_fraction": float(legacy.float().mean()),
                     "mask_disagreement_fraction": float((corrected != legacy).float().mean()),
                     "jaccard": int((corrected & legacy).sum()) / union if union else 1.0})
    frame = pd.DataFrame(rows)
    frame.to_csv(REPO_ROOT / "results/wind_mask_coverage_v2.csv", index=False)
    result = {"timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
              "script": "scripts/analyze_physics_v2.py", "config": "configs/data_v2.yaml", "seed": cfg["seed"],
              "source_git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True).strip(),
              "station_nodes": len(z["station_ids"]), "directed_edges": edge_index.shape[1],
              "hours": len(frame), "legacy_direction_slope": float(slope),
              "legacy_direction_intercept": float(intercept),
              "corrected_fraction_mean": float(frame.corrected_fraction.mean()),
              "legacy_fraction_mean": float(frame.legacy_fraction.mean()),
              "disagreement_fraction_mean": float(frame.mask_disagreement_fraction.mean()),
              "jaccard_mean": float(frame.jaccard.mean()),
              "traffic_index_available": False,
              "q_variant_status": "BLOCKED: no traffic index source"}
    (REPO_ROOT / "results/physics_v2_mask_summary.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
