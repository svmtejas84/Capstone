"""Read-only structural measurements of the legacy Bengaluru road graph."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from pyproj import Transformer
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components


ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).with_name("graph_measurements_v2k.json")


class SpatialPartition:
    """Compatibility shell for the notebook's local partition pickle."""


def describe(values):
    x = np.asarray(values, dtype=float)
    finite = x[np.isfinite(x)]
    return {"count": int(len(x)), "finite": int(len(finite)),
            "min": float(finite.min()) if len(finite) else None,
            "median": float(np.median(finite)) if len(finite) else None,
            "max": float(finite.max()) if len(finite) else None}


def main():
    nodes = pd.read_parquet(ROOT / "data/graphs/bangalore_utm_nodes.parquet")
    edges = pd.read_parquet(ROOT / "data/graphs/bangalore_utm_edges.parquet")
    mapping = pd.read_parquet(ROOT / "data/processed/graph/topology_nodeid_to_index_map.parquet")
    station_map = pd.read_parquet(ROOT / "data/processed/graph/station_to_topology_node_map.parquet")
    elev = pd.read_parquet(ROOT / "data/processed/graph/nodes_elevation_true.parquet")
    graph = torch.load(ROOT / "data/processed/graph/topology_graph.pt", map_location="cpu", weights_only=False)
    pyg = torch.load(ROOT / "data/processed/graph/topology_graph_pyg_inference.pt", map_location="cpu", weights_only=False)
    parts = torch.load(ROOT / "data/processed/graph/partitioned_manifold_64_clusters.pt", map_location="cpu", weights_only=False)
    n = len(nodes)
    src, dst = graph["edge_index"].numpy()
    edge_pairs = pd.DataFrame({"src": src, "dst": dst})
    p = coo_matrix((np.ones(len(src), np.uint8), (src, dst)), shape=(n, n)).tocsr()
    weak_n, weak_labels = connected_components(p, directed=True, connection="weak")
    strong_n, strong_labels = connected_components(p, directed=True, connection="strong")
    labels = np.full(n, -1, dtype=np.int16)
    part_sizes = []
    part_edges = []
    repeated = 0
    for part in parts:
        ids = part.n_id.numpy()
        repeated += int(np.count_nonzero(labels[ids] != -1))
        labels[ids] = int(part.cid)
        part_sizes.append(len(ids))
        part_edges.append(int(part.edge_index.shape[1]))
    lon, lat = Transformer.from_crs("EPSG:32643", "EPSG:4326", always_xy=True).transform(
        nodes.x.to_numpy(float), nodes.y.to_numpy(float))
    mapped = station_map.merge(mapping, on="node_id", how="left", validate="many_to_one")
    model_input = pd.read_parquet(ROOT / "data/processed/model_input/model_input_node_hourly_features.parquet",
                                  columns=["node_id", "timestamp", "station_pm25", "weather_temperature_2m"])
    report = {
        "sources": ["data/graphs/bangalore_utm.graphml", "data/graphs/bangalore_utm_nodes.parquet",
                    "data/graphs/bangalore_utm_edges.parquet", "data/processed/graph/topology_graph.pt",
                    "data/processed/graph/topology_graph_pyg_inference.pt",
                    "data/processed/graph/partitioned_manifold_64_clusters.pt"],
        "raw_nodes": n, "raw_edges": len(edges), "raw_unique_node_ids": int(nodes.osmid.nunique()),
        "raw_missing_edge_endpoint_rows": int((~edges.u.isin(nodes.osmid) | ~edges.v.isin(nodes.osmid)).sum()),
        "raw_self_loops": int((edges.u == edges.v).sum()),
        "raw_duplicate_uv_key": int(edges.duplicated(["u", "v", "key"]).sum()),
        "raw_duplicate_uv": int(edges.duplicated(["u", "v"]).sum()),
        "raw_highway_missing": int(edges.highway.isna().sum()),
        "raw_oneway_counts": {str(k): int(v) for k, v in edges.oneway.value_counts(dropna=False).items()},
        "raw_highway_top": {str(k): int(v) for k, v in edges.highway.astype(str).value_counts().head(20).items()},
        "raw_length_m": describe(edges.length),
        "raw_length_invalid": int((~np.isfinite(pd.to_numeric(edges.length, errors="coerce")) |
                                  (pd.to_numeric(edges.length, errors="coerce") <= 0)).sum()),
        "raw_missing_attribute_rows": {c: int(edges[c].isna().sum()) for c in edges.columns},
        "coordinate_crs": "EPSG:32643 (UTM zone 43N), inferred from preprocessing and validated by lat/lon transform",
        "x_utm_m": describe(nodes.x), "y_utm_m": describe(nodes.y),
        "lat_deg": describe(lat), "lon_deg": describe(lon),
        "coordinate_invalid_rows": int((~np.isfinite(nodes.x) | ~np.isfinite(nodes.y) |
                                        ~np.isfinite(lat) | ~np.isfinite(lon)).sum()),
        "graph_nodes": int(graph["num_nodes"]), "graph_edges": len(src),
        "graph_x_shape": list(graph["x"].shape), "graph_edge_attr_shape": list(graph["edge_attr"].shape),
        "graph_node_schema": graph["node_feature_schema"], "graph_edge_schema": graph["edge_attr_schema"],
        "graph_highway_categories": graph["highway_categories"],
        "graph_index_out_of_range": int(((src < 0) | (dst < 0) | (src >= n) | (dst >= n)).sum()),
        "graph_self_loops": int((src == dst).sum()),
        "graph_duplicate_directed_pairs": int(edge_pairs.duplicated().sum()),
        "graph_length_m": describe(graph["edge_attr"][:, 0].numpy()),
        "graph_x_nonfinite": int((~torch.isfinite(graph["x"])).sum().item()),
        "graph_edge_attr_nonfinite": int((~torch.isfinite(graph["edge_attr"])).sum().item()),
        "weak_component_count": weak_n, "largest_weak_component": int(np.bincount(weak_labels).max()),
        "strong_component_count": strong_n, "largest_strong_component": int(np.bincount(strong_labels).max()),
        "pyg_same_edge_index": bool(torch.equal(pyg.edge_index, graph["edge_index"])),
        "pyg_same_x": bool(torch.equal(pyg.x, graph["x"])),
        "pyg_train_mask_nodes": int(pyg.train_mask.sum().item()),
        "node_index_unique": bool(mapping.node_index.is_unique),
        "node_id_map_unique": bool(mapping.node_id.is_unique),
        "station_map_rows": len(station_map),
        "station_map_unique_nodes": int(station_map.node_id.nunique()),
        "station_map_missing_node_indices": int(mapped.node_index.isna().sum()),
        "elevation_rows": len(elev), "elevation_missing": int(elev.elevation_true.isna().sum()),
        "partition_count": len(parts), "partition_sizes": part_sizes,
        "partition_edge_counts": part_edges,
        "partition_repeated_nodes": repeated,
        "partition_unassigned_nodes": int((labels < 0).sum()),
        "cross_partition_directed_edges": int((labels[src] != labels[dst]).sum()),
        "partition_total_internal_directed_edges": int(sum(part_edges)),
        "partition_feature_shapes": sorted({str(tuple(part.x.shape[1:])) for part in parts}),
        "model_input_rows": len(model_input),
        "model_input_nodes": int(model_input.node_id.nunique()),
        "model_input_hours": int(model_input.timestamp.nunique()),
        "model_input_pm25_nonnull": int(model_input.station_pm25.notna().sum()),
        "model_input_weather_temperature_nonnull": int(model_input.weather_temperature_2m.notna().sum()),
    }
    OUT.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in ("raw_nodes", "raw_edges", "graph_edges", "weak_component_count",
                                               "strong_component_count", "partition_count",
                                               "cross_partition_directed_edges", "model_input_nodes")}, indent=2))


if __name__ == "__main__":
    main()
