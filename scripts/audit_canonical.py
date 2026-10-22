"""Read-only provenance audit for evaluated_wind_advection.ipynb.

Writes measurements to results/; never executes notebook training cells.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import subprocess
import time
from pathlib import Path

import numpy as np
import pandas as pd
import scipy
import sklearn
import torch
import torch_geometric
import networkx as nx
from pyproj import Transformer

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results"
OUT.mkdir(exist_ok=True)


class SpatialPartition:
    """Compatibility shell for reading the notebook's pickled partition artifact."""
    pass


def describe(a):
    a = np.asarray(a, dtype=float)
    a = a[np.isfinite(a)]
    return {"n": len(a), "mean": float(a.mean()) if len(a) else None,
            "std": float(a.std()) if len(a) else None,
            "min": float(a.min()) if len(a) else None,
            "max": float(a.max()) if len(a) else None}


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main():
    began = time.perf_counter()
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    path = ROOT / "citywide_stpignn_best.pt"
    ck = torch.load(path, map_location="cpu", weights_only=False)
    model_input = pd.read_parquet(ROOT / "data/processed/model_input/model_input_node_hourly_features.parquet")
    master = pd.read_parquet(ROOT / "data/processed/graph/master_scaled_checkpoint.parquet")
    node_map = pd.read_parquet(ROOT / "data/processed/graph/topology_nodeid_to_index_map.parquet")
    nodes = pd.read_parquet(ROOT / "data/graphs/bangalore_utm_nodes.parquet", columns=["osmid", "x", "y"])
    elev = pd.read_parquet(ROOT / "data/processed/graph/nodes_elevation_true.parquet", columns=["osmid", "utm_y", "elevation_true"])
    graph = torch.load(ROOT / "data/processed/graph/topology_graph_pyg_inference.pt", map_location="cpu", weights_only=False)
    parts = torch.load(ROOT / "data/processed/graph/partitioned_manifold_64_clusters.pt", map_location="cpu", weights_only=False)
    labels = np.full(len(nodes), -1, dtype=np.int16)
    for part in parts:
        labels[part.n_id.numpy()] = part.cid
    report = {"timestamp_utc": now, "seed": 42,
              "source_git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
              "artifact_sha256": {"canonical_notebook": sha256(ROOT / "notebooks/production/evaluated_wind_advection.ipynb"),
                                  "checkpoint": sha256(path)},
              "hardware": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU",
              "versions": {"torch": torch.__version__, "torch_geometric": torch_geometric.__version__,
                           "pandas": pd.__version__, "numpy": np.__version__,
                           "scipy": scipy.__version__, "sklearn": sklearn.__version__},
              "checkpoint": {"path": str(path.relative_to(ROOT)),
                             "mtime_utc": dt.datetime.fromtimestamp(path.stat().st_mtime, dt.timezone.utc).isoformat(),
                             "embedded_timestamp": ck.get("timestamp"), "epoch": ck.get("epoch"),
                             "global_config": ck.get("global_config"),
                             "metadata": ck.get("metadata"), "best_val_mse": ck.get("best_val_mse")},
              "rows": {"model_input": len(model_input), "master": len(master), "nodes": len(nodes)},
              "graph": {"sensor_mask_nodes": int(graph.train_mask.sum()), "edges": int(graph.edge_index.shape[1]),
                        "edge_feature_names": list(graph.edge_attr_schema), "node_feature_names": list(graph.node_feature_schema)}}
    times = pd.DatetimeIndex(pd.to_datetime(model_input.timestamp.unique(), utc=True)).sort_values()
    report["time"] = {"distinct_hours": len(times), "first": times.min().isoformat(),
                      "last": times.max().isoformat(),
                      "train_start_0": times[0].isoformat(),
                      "train_last_target_87178": times[min(87178, len(times)-1)].isoformat(),
                      "val_first_target_87189": times[min(87189, len(times)-1)].isoformat(),
                      "val_last_start_87514": times[min(87514, len(times)-1)].isoformat()}
    report["station_counts"] = {"model_input_ids": int(model_input.station_id.nunique(dropna=True)),
                                "model_input_nodes": int(model_input.node_id.nunique(dropna=True)),
                                "master_ids": int(master.station_id.nunique(dropna=True)),
                                "master_nodes": int(master.node_index.nunique(dropna=True))}
    report["model_input_target"] = describe(model_input.station_pm25)
    report["master_pm25_scaled"] = describe(master.pm2_5_scaled)
    report["elevation"] = {"model_input_has_elevation": "elevation" in model_input.columns,
                           "master_has_elevation": any("elevation" in c for c in master.columns),
                           "true": describe(elev.elevation_true),
                           "true_pearson_northing": float(elev.elevation_true.corr(elev.utm_y)),
                           "true_spearman_northing": float(elev.elevation_true.corr(elev.utm_y, method="spearman"))}
    aligned_elev = node_map.merge(elev, left_on="node_id", right_on="osmid").sort_values("node_index")
    graph_elevation = graph.x[:, 16].numpy()
    report["elevation"].update({"graph": describe(graph_elevation),
                                "graph_pearson_northing": float(np.corrcoef(graph_elevation, aligned_elev.utm_y)[0, 1]),
                                "graph_pearson_srtm": float(np.corrcoef(graph_elevation, aligned_elev.elevation_true)[0, 1]),
                                "graph_mean_absolute_difference_srtm_m": float(np.mean(np.abs(graph_elevation - aligned_elev.elevation_true)))})
    model_input = model_input.merge(node_map, on="node_id", how="left")
    model_input["target_nonzero"] = pd.to_numeric(model_input.station_pm25, errors="coerce").fillna(0).abs() > 1e-8
    model_input["graph_sensor"] = graph.train_mask[torch.as_tensor(model_input.node_index.fillna(-1).clip(lower=0).to_numpy(), dtype=torch.long)].numpy()
    # The notebook's training and validation datasets use index positions, not dates.
    idx = pd.Index(times)
    tcode = idx.get_indexer(pd.to_datetime(model_input.timestamp, utc=True))
    train_starts = set(range(0, min(87178, len(times)) - 12, 128))
    val_starts = set(range(87178, min(87514, len(times)) - 12, 24))
    train_targets = {s + 11 for s in train_starts}
    val_targets = {s + 11 for s in val_starts}
    report["split"] = {"train_starts": len(train_starts), "val_starts": len(val_starts),
                       "distinct_train_scored_hours": len(train_targets),
                       "distinct_val_scored_hours": len(val_targets),
                       "train_first_target": times[min(train_targets)].isoformat() if train_targets else None,
                       "train_last_target": times[max(train_targets)].isoformat() if train_targets else None,
                       "val_first_target": times[min(val_targets)].isoformat() if val_targets else None,
                       "val_last_target": times[max(val_targets)].isoformat() if val_targets else None,
                       "scored_train_rows_nonzero": int((np.isin(tcode, list(train_targets)) & model_input.target_nonzero & model_input.graph_sensor).sum()),
                       "scored_val_rows_nonzero": int((np.isin(tcode, list(val_targets)) & model_input.target_nonzero & model_input.graph_sensor).sum())}
    station = model_input.groupby(["station_id", "node_id", "node_index"], dropna=False).agg(
        nonzero_train_scored_hours=("target_nonzero", lambda x: int(x[np.isin(tcode[x.index], list(train_targets))].sum())),
        nonzero_val_scored_hours=("target_nonzero", lambda x: int(x[np.isin(tcode[x.index], list(val_targets))].sum())),
        total_rows=("target_nonzero", "size")).reset_index()
    observed = master.loc[(master.parameter == "pm25") & (~master.is_imputed) & master.observed_value.notna(),
                          ["station_id", "timestamp"]].copy()
    observed["timestamp"] = pd.to_datetime(observed.timestamp, utc=True)
    observed["time_code"] = idx.get_indexer(observed.timestamp)
    observed["train"] = observed.time_code.isin(train_targets)
    observed["val"] = observed.time_code.isin(val_targets)
    observed_counts = observed.groupby("station_id").agg(
        observed_train_hours=("train", "sum"), observed_val_hours=("val", "sum")).reset_index()
    station = station.merge(observed_counts, on="station_id", how="left")
    station[["observed_train_hours", "observed_val_hours"]] = station[["observed_train_hours", "observed_val_hours"]].fillna(0).astype(int)
    station = station.merge(nodes, left_on="node_id", right_on="osmid", how="left")
    station = station.rename(columns={"x": "utm_x", "y": "utm_y"})
    station["cluster"] = [int(labels[int(i)]) if pd.notna(i) else -1 for i in station.node_index]
    lon, lat = Transformer.from_crs("EPSG:32643", "EPSG:4326", always_xy=True).transform(station.utm_x.to_numpy(), station.utm_y.to_numpy())
    station["latitude"] = lat
    station["longitude"] = lon
    station.to_csv(OUT / "stations.csv", index=False)
    # Count actual imputation tiers recorded in master; label these as source rows, not train-only fitted.
    master["year"] = pd.to_datetime(master.time, utc=True).dt.year
    breakdown = master.groupby(["year", "station_id", "impute_tier"], dropna=False).size().rename("rows").reset_index()
    breakdown.to_csv(OUT / "audit_imputation_tiers.csv", index=False)
    pm25 = master[master.parameter == "pm25"]
    report["master_pm25_tiers"] = {str(key): int(value) for key, value in pm25.impute_tier.value_counts().items()}
    report["master_pm25_imputed_fraction"] = float(pm25.is_imputed.mean())
    report["confirmed_observed_scored_hours"] = {
        "train": int(station.observed_train_hours.sum()), "validation": int(station.observed_val_hours.sum())}
    routing_path = ROOT / "data/processed/evaluations/routing_snapshot.graphml"
    if routing_path.exists():
        route_graph = nx.read_graphml(routing_path)
        route_pm = [float(data["predicted_pm25"]) for _, _, data in route_graph.edges(data=True)
                    if "predicted_pm25" in data]
        report["routing_snapshot"] = {"path": str(routing_path.relative_to(ROOT)),
                                      "concentrations_ug_m3": describe(route_pm)}
    report["runtime_seconds"] = time.perf_counter() - began
    (OUT / "audit_canonical.json").write_text(json.dumps(report, indent=2, default=str) + "\n")
    print(json.dumps(report, indent=2, default=str))


if __name__ == "__main__":
    main()
