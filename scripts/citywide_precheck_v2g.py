"""W8 no-training audit of inputs available at every topology node."""
from __future__ import annotations

import datetime as dt
import subprocess

import numpy as np
import pandas as pd

from src.stpignn.paths import REPO_ROOT


def main():
    graph = REPO_ROOT / "data/processed/graph"
    nodes = pd.read_parquet(graph / "topology_nodeid_to_index_map.parquet")
    elevation = pd.read_parquet(graph / "nodes_elevation_true.parquet")
    stations = pd.read_parquet(graph / "station_to_topology_node_map.parquet")
    joined = nodes.merge(elevation[["osmid", "elevation_true"]], left_on="node_id", right_on="osmid",
                         how="left", validate="one_to_one")
    n = len(joined)
    if n != 154902:
        raise AssertionError(f"Expected 154902 nodes, got {n}")
    source = REPO_ROOT / "scripts/pull_weather.py"
    source_text = source.read_text()
    if "BANGALORE_LAT = 12.9716" not in source_text or "BANGALORE_LON = 77.5946" not in source_text:
        raise AssertionError("Weather source point needs reinspection")
    weather_files = sorted((REPO_ROOT / "data/raw/weather").glob("*.parquet"))
    weather = pd.concat([pd.read_parquet(path) for path in weather_files])
    weather_columns = ["wind_speed_10m", "wind_direction_10m", "wind_gusts_10m",
                       "temperature_2m", "relative_humidity_2m", "surface_pressure"]
    weather_finite_rows = int(np.isfinite(weather[weather_columns].to_numpy(dtype=float)).all(axis=1).sum())
    distinct_weather_points = 1
    temporal_path=REPO_ROOT/"data/processed/model_input/model_input_node_hourly_features.parquet"
    temporal_cols=["node_id","timestamp"]+["weather_"+name for name in weather_columns]
    temporal=pd.read_parquet(temporal_path,columns=temporal_cols)
    stored_nodes=int(temporal.node_id.nunique())
    signatures=[]
    groups=[]
    for node,part in temporal.groupby("node_id",sort=True):
        part=part.sort_values("timestamp")
        stamps=part.timestamp.to_numpy(dtype="datetime64[ns]")
        values=part[temporal_cols[2:]].to_numpy(dtype=float)
        groups.append((int(node),stamps,values))
    for node,stamps,values in groups:
        for signature in signatures:
            if (values.shape==signature[2].shape and np.array_equal(stamps,signature[1]) and
                    np.array_equal(values,signature[2],equal_nan=True)):
                signature[3].append(node)
                break
        else:
            signatures.append([node,stamps,values,[node]])
    duplicate_stored=sum(len(group[3]) for group in signatures if len(group[3])>1)
    duplicated_fraction=duplicate_stored/stored_nodes if stored_nodes else 0.0
    elevation_valid = int(np.isfinite(joined.elevation_true.to_numpy(dtype=float)).sum())
    station_nodes = int(stations.node_id.nunique())
    no_temporal_data=n-stored_nodes
    no_any_data = 0 if weather_finite_rows or elevation_valid == n else int((~np.isfinite(joined.elevation_true)).sum())
    verdict = "BLOCKED: citywide inputs are copies" if duplicated_fraction > 0.5 else "PRECHECK PASSED"
    lines = ["# Citywide precheck v2g", "",
             f"Source `scripts/citywide_precheck_v2g.py`, `scripts/pull_weather.py`, no training, no seed, commit `{subprocess.check_output(['git','rev-parse','HEAD'], cwd=REPO_ROOT, text=True).strip()}`, {dt.datetime.now(dt.timezone.utc).isoformat()}.", "",
             f"Nodes: {n}.", f"Distinct weather source points: {distinct_weather_points} (12.9716 N, 77.5946 E).",
             f"Nodes with stored hourly model-input rows: {stored_nodes}/{n}; nodes with no stored temporal model-input data: {no_temporal_data}.",
             f"Unique weather series among stored nodes: {len(signatures)}.",
             f"Stored nodes whose weather series exactly duplicates another stored node's: {duplicate_stored}/{stored_nodes} ({100*duplicated_fraction:.6f}%).",
             f"If the single raw weather series were broadcast to all topology nodes, duplicate fraction would be 100.000000%.",
             f"Weather hours with all six fields finite: {weather_finite_rows}/{len(weather)}.",
             f"Nodes with SRTM elevation: {elevation_valid}/{n}; missing: {n-elevation_valid}.",
             f"Nodes mapped to a station: {station_nodes}/{n}; without a station: {n-station_nodes}.",
             f"Nodes with no weather or SRTM data after broadcast: {no_any_data}.",
             f"{verdict}.", ""]
    (REPO_ROOT / "results/citywide_precheck_v2g.md").write_text("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
