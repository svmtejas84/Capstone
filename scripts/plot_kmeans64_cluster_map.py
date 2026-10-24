"""Plot the paper's 64 geographic K-Means partitions from existing nodes.

Run from any directory: python /path/to/Capstone/scripts/plot_kmeans64_cluster_map.py
Writes /path/to/Capstone/cluster_map.png (300 DPI).
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm, ListedColormap
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans


ROOT = Path(__file__).resolve().parents[1]
PREFERRED_NODES = ROOT / "data/processed/graph/nodes_elevation_true.parquet"
FALLBACK_NODES = ROOT / "data/graphs/bangalore_utm_nodes.parquet"
NODE_INDEX = ROOT / "data/processed/graph/topology_nodeid_to_index_map.parquet"
OUTPUT = ROOT / "cluster_map.png"
EXPECTED_NODES = 154_902
N_CLUSTERS = 64


def load_aligned_nodes() -> tuple[pd.DataFrame, Path]:
    """Match the production notebook's graph-index order before clustering."""
    source = PREFERRED_NODES if PREFERRED_NODES.exists() else FALLBACK_NODES
    if not source.exists():
        raise FileNotFoundError(f"Neither node file exists: {PREFERRED_NODES}, {FALLBACK_NODES}")
    nodes = pd.read_parquet(source)
    x_col, y_col = ("utm_x", "utm_y") if {"utm_x", "utm_y"} <= set(nodes) else ("x", "y")
    required = {"osmid", x_col, y_col}
    if not required <= set(nodes):
        raise ValueError(f"{source} must contain {sorted(required)}")
    if len(nodes) != EXPECTED_NODES or nodes.osmid.duplicated().any():
        raise ValueError(f"Expected {EXPECTED_NODES:,} unique physical road nodes in {source}")
    mapping = pd.read_parquet(NODE_INDEX, columns=["node_id", "node_index"])
    if len(mapping) != EXPECTED_NODES or mapping.node_index.duplicated().any():
        raise ValueError("Graph node-index mapping is incomplete or duplicated")
    aligned = mapping.merge(nodes, left_on="node_id", right_on="osmid", how="left",
                            validate="one_to_one").sort_values("node_index").reset_index(drop=True)
    if not np.array_equal(aligned.node_index.to_numpy(), np.arange(EXPECTED_NODES)):
        raise ValueError("Node indices must be contiguous from 0 to 154901")
    if not np.isfinite(aligned[[x_col, y_col]].to_numpy(dtype=float)).all():
        raise ValueError("Missing or non-finite UTM coordinates after graph-index alignment")
    return aligned.rename(columns={x_col: "plot_x", y_col: "plot_y"}), source


def partition_labels(nodes: pd.DataFrame) -> tuple[np.ndarray, str]:
    for candidate in ("cluster_id", "cluster", "kmeans_cluster", "partition_id"):
        if candidate in nodes:
            labels = nodes[candidate].to_numpy()
            if pd.isna(labels).any() or len(np.unique(labels)) != N_CLUSTERS:
                raise ValueError(f"Saved {candidate} must contain exactly 64 non-null clusters")
            return pd.Categorical(labels).codes.astype(np.int16), f"saved column '{candidate}'"
    # Match notebooks/production/evaluated_wind_advection.ipynb: UTM x/y in
    # node_index order, float32, random_state=42 and n_init=10.
    coordinates = nodes[["plot_x", "plot_y"]].to_numpy(dtype=np.float32)
    labels = KMeans(n_clusters=N_CLUSTERS, random_state=42, n_init=10).fit_predict(coordinates)
    return labels.astype(np.int16), "KMeans(n_clusters=64, random_state=42, n_init=10)"


def categorical_palette() -> ListedColormap:
    # Four established categorical palettes provide 64 distinct colors.
    colors = np.vstack([
        plt.get_cmap("tab20").colors,
        plt.get_cmap("tab20b").colors,
        plt.get_cmap("tab20c").colors,
        plt.get_cmap("Set1").colors[:4],
    ])
    return ListedColormap(colors, name="distinct_64_clusters")


def main() -> None:
    nodes, source = load_aligned_nodes()
    labels, provenance = partition_labels(nodes)
    counts = np.bincount(labels, minlength=N_CLUSTERS)
    if len(labels) != EXPECTED_NODES or len(counts) != N_CLUSTERS or np.any(counts == 0):
        raise ValueError("Every one of the 64 clusters must contain at least one of the 154,902 nodes")

    cmap = categorical_palette()
    norm = BoundaryNorm(np.arange(-0.5, N_CLUSTERS + 0.5, 1), cmap.N)
    fig, ax = plt.subplots(figsize=(12, 10), facecolor="white")
    points = ax.scatter(nodes.plot_x, nodes.plot_y, c=labels, cmap=cmap, norm=norm,
                        s=0.5, alpha=0.8, linewidths=0, rasterized=True)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_title("Geographic Distribution of 64 K-Means Sub-Graph Partitions",
                 fontsize=16, pad=18)
    colorbar = fig.colorbar(points, ax=ax, fraction=0.028, pad=0.015,
                            ticks=[0, 15, 31, 47, 63])
    colorbar.set_label("Partition ID", fontsize=10)
    colorbar.ax.tick_params(labelsize=9, length=0)
    colorbar.outline.set_visible(False)
    fig.savefig(OUTPUT, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved {OUTPUT} using {len(nodes):,} nodes from {source}")
    print(f"Assignments: {provenance}; 64 clusters; sizes {counts.min():,}–{counts.max():,}")


if __name__ == "__main__":
    main()
