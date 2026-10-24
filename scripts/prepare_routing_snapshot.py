"""Create a 1.5 km central Bangalore OSMnx graph with ST-PIGNN edge PM2.5.

The latest available 12-hour feature window is used for one fixed exposure
snapshot; this is a simulation input, not contemporaneous trip measurements.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import networkx as nx
import numpy as np
import osmnx as ox
import pandas as pd
import torch
from torch_geometric.utils import subgraph

from src.stpignn.legacy_inference import load_stpignn_checkpoint, _build_temporal_x_seq, TARGET_SCALE, TARGET_PM25_MAX
from src.stpignn.paths import REPO_ROOT as ROOT


def main(radius_m: float) -> None:
    graph = ox.load_graphml(ROOT / "data/graphs/bangalore_utm.graphml")
    nodes = pd.read_parquet(ROOT / "data/graphs/bangalore_utm_nodes.parquet", columns=["osmid", "x", "y"])
    center = nodes[["x", "y"]].median().to_numpy()
    selected = set(nodes.loc[np.hypot(nodes.x - center[0], nodes.y - center[1]) <= radius_m, "osmid"].astype(int))
    urban = graph.subgraph(selected).copy()
    urban = graph.subgraph(max(nx.strongly_connected_components(urban), key=len)).copy()
    mapping = pd.read_parquet(ROOT / "data/processed/graph/topology_nodeid_to_index_map.parquet")
    indices = mapping.set_index("node_id").loc[sorted(urban.nodes), "node_index"].to_numpy(dtype=np.int64)
    topology = torch.load(ROOT / "data/processed/graph/topology_graph_pyg_inference.pt", map_location="cpu", weights_only=False)
    edge_index, edge_attr = subgraph(torch.as_tensor(indices), topology.edge_index,
                                     topology.edge_attr, relabel_nodes=True)
    x_seq = _build_temporal_x_seq(topology, torch.as_tensor(indices), None, 12)
    model, _ = load_stpignn_checkpoint(ROOT / "citywide_stpignn_best.pt", device="cpu", eval_mode=True)
    with torch.no_grad():
        values = model(x_seq=x_seq, edge_index=edge_index, edge_attr=edge_attr).view(-1).numpy()
    pm_by_id = {node: float(np.clip(value * TARGET_SCALE, 0, TARGET_PM25_MAX))
                for node, value in zip(sorted(urban.nodes), values)}
    for u, v, _key, data in urban.edges(keys=True, data=True):
        data["predicted_pm25"] = 0.5 * (pm_by_id[u] + pm_by_id[v])
    output = ROOT / "data/processed/evaluations/routing_snapshot.graphml"
    output.parent.mkdir(parents=True, exist_ok=True)
    ox.save_graphml(urban, output)
    print(f"Saved {len(urban)} nodes and {urban.number_of_edges()} directed edges to {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--radius-m", type=float, default=1500)
    main(parser.parse_args().radius_m)
