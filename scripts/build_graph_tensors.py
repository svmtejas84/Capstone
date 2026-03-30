"""
Build static graph tensors for PyTorch Geometric from read-only graph parquet inputs.

Inputs (read-only):
- data/graphs/bangalore_utm_nodes.parquet
- data/graphs/bangalore_utm_edges.parquet

Outputs:
- data/processed/node_index_map.parquet
- data/processed/static_graph.pt
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import torch
import torch.nn.functional as F

NODES_PATH = Path("data/graphs/bangalore_utm_nodes.parquet")
EDGES_PATH = Path("data/graphs/bangalore_utm_edges.parquet")
NODE_MAP_OUT = Path("data/processed/node_index_map.parquet")
STATIC_GRAPH_OUT = Path("data/processed/static_graph.pt")


def build_graph_tensors() -> None:
    nodes = pd.read_parquet(NODES_PATH)
    edges = pd.read_parquet(EDGES_PATH)

    required_node_cols = {"osmid"}
    required_edge_cols = {"u", "v", "length", "highway"}
    missing_node = required_node_cols - set(nodes.columns)
    missing_edge = required_edge_cols - set(edges.columns)
    if missing_node:
        raise ValueError(f"Missing required node columns: {sorted(missing_node)}")
    if missing_edge:
        raise ValueError(f"Missing required edge columns: {sorted(missing_edge)}")

    # 1) Continuous node indexing.
    node_ids = nodes["osmid"].astype("int64").drop_duplicates().reset_index(drop=True)
    node_index_map = pd.DataFrame({
        "node_id": node_ids,
        "node_index": node_ids.index.astype("int64"),
    })

    node_to_idx = dict(zip(node_index_map["node_id"], node_index_map["node_index"], strict=False))
    NODE_MAP_OUT.parent.mkdir(parents=True, exist_ok=True)
    node_index_map.to_parquet(NODE_MAP_OUT, index=False)

    # 2) Map u/v to indices and retain only edges whose endpoints exist in node map.
    e = edges[["u", "v", "length", "highway"]].copy()
    e["u"] = e["u"].astype("int64")
    e["v"] = e["v"].astype("int64")
    e["u_idx"] = e["u"].map(node_to_idx)
    e["v_idx"] = e["v"].map(node_to_idx)
    e = e.dropna(subset=["u_idx", "v_idx", "length", "highway"]).copy()
    e["u_idx"] = e["u_idx"].astype("int64")
    e["v_idx"] = e["v_idx"].astype("int64")

    # Remove self-loops before and after bidirectional expansion.
    e = e[e["u_idx"] != e["v_idx"]].copy()

    # 3) Ensure bidirectionality by adding reverse edges.
    e_rev = e.rename(columns={"u_idx": "v_idx", "v_idx": "u_idx"})
    e_bi = pd.concat([e, e_rev], ignore_index=True)
    e_bi = e_bi[e_bi["u_idx"] != e_bi["v_idx"]].copy()

    # Deduplicate by directed pair + attributes.
    e_bi = e_bi.drop_duplicates(subset=["u_idx", "v_idx", "length", "highway"]).reset_index(drop=True)

    # 4) Build edge_index tensor [2, E].
    edge_index = torch.tensor(e_bi[["u_idx", "v_idx"]].to_numpy().T, dtype=torch.long)

    # 5) Build edge_attr tensor: [length, one-hot highway_type...]
    highway_codes, highway_categories = pd.factorize(e_bi["highway"].astype(str), sort=True)
    highway_one_hot = F.one_hot(torch.tensor(highway_codes, dtype=torch.long), num_classes=len(highway_categories)).to(torch.float)
    length_tensor = torch.tensor(e_bi["length"].to_numpy(), dtype=torch.float).unsqueeze(1)
    edge_attr = torch.cat([length_tensor, highway_one_hot], dim=1)

    graph_obj = {
        "edge_index": edge_index,
        "edge_attr": edge_attr,
        "num_nodes": int(len(node_index_map)),
        "highway_categories": [str(x) for x in highway_categories.tolist()],
        "edge_attr_schema": ["length"] + [f"highway_{str(x)}" for x in highway_categories.tolist()],
    }

    STATIC_GRAPH_OUT.parent.mkdir(parents=True, exist_ok=True)
    torch.save(graph_obj, STATIC_GRAPH_OUT)

    # 6) Physics/connectivity validation prints.
    num_nodes = int(len(node_index_map))
    num_edges = int(edge_index.shape[1])

    degree = torch.bincount(edge_index[0], minlength=num_nodes) + torch.bincount(edge_index[1], minlength=num_nodes)
    isolated_nodes = int((degree == 0).sum().item())

    density = num_edges / num_nodes if num_nodes > 0 else 0.0
    min_len = float(length_tensor.min().item()) if num_edges > 0 else float("nan")
    max_len = float(length_tensor.max().item()) if num_edges > 0 else float("nan")

    print(f"[GRAPH] Saved node index map -> {NODE_MAP_OUT}")
    print(f"[GRAPH] Saved static graph tensor -> {STATIC_GRAPH_OUT}")
    print(f"[VALIDATION] Isolated nodes: {isolated_nodes}")
    print(f"[VALIDATION] Graph density (edges/nodes): {density:.6f}")
    print(f"[VALIDATION] Edge length range (m): min={min_len:.3f}, max={max_len:.3f}")


def main() -> None:
    build_graph_tensors()


if __name__ == "__main__":
    main()
