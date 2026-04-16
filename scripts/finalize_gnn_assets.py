"""
scripts/finalize_gnn_assets.py

One-pass finalization for ST-PIGNN assets:
1) Temporal continuity repair on the training tensor.
2) Sensor train-mask creation from station-node mapping.
3) PyG Data serialization with built-in validation.

Outputs:
- data/processed/model_input/model_input_node_hourly_features.parquet
- data/processed/graph/topology_graph_pyg_inference.pt
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch_geometric.data import Data

from shared.physics_config import PHYSICS_LOSS_LAMBDA

MASTER_IN = Path("data/processed/model_input/model_input_node_hourly_features.parquet")
MASTER_OUT = MASTER_IN
STATION_NODE_MAP = Path("data/processed/graph/station_to_topology_node_map.parquet")
NODE_INDEX_MAP = Path("data/processed/graph/topology_nodeid_to_index_map.parquet")
STATIC_GRAPH_IN = Path("data/processed/graph/topology_graph.pt")
STATIC_GRAPH_OUT = Path("data/processed/graph/topology_graph_pyg_inference.pt")

AQ_PREFIXES = ("station_", "city_")
WEATHER_PREFIX = "weather_"


def _validate_inputs() -> None:
    required = [MASTER_IN, STATION_NODE_MAP, NODE_INDEX_MAP, STATIC_GRAPH_IN]
    missing = [str(p) for p in required if not p.exists()]
    if missing:
        raise FileNotFoundError(f"Missing required input files: {missing}")


def _node_hourly_spine(df: pd.DataFrame) -> pd.DataFrame:
    if "timestamp" not in df.columns:
        raise ValueError("Master dataframe must contain a 'timestamp' column.")
    if "node_id" not in df.columns:
        raise ValueError("Master dataframe must contain a 'node_id' column.")

    out = df.copy()
    out["timestamp"] = pd.to_datetime(out["timestamp"], errors="coerce")
    if isinstance(out["timestamp"].dtype, pd.DatetimeTZDtype):
        out["timestamp"] = out["timestamp"].dt.tz_convert("Asia/Kolkata").dt.tz_localize(None)
    out = out.dropna(subset=["timestamp", "node_id"]).copy()
    out["node_id"] = out["node_id"].astype("int64")

    if out.empty:
        raise ValueError("Master dataframe became empty after timestamp/node cleanup.")

    # Collapse accidental duplicates at (node_id, timestamp) before reindexing.
    numeric_cols = out.select_dtypes(include=["number", "bool"]).columns.tolist()
    agg: dict[str, str] = {}
    for col in out.columns:
        if col in {"timestamp", "node_id"}:
            continue
        agg[col] = "mean" if col in numeric_cols else "first"

    out = (
        out.sort_values(["node_id", "timestamp"])
        .groupby(["node_id", "timestamp"], as_index=False)
        .agg(agg)
    )

    min_t = out["timestamp"].min()
    max_t = out["timestamp"].max()
    tz = getattr(min_t, "tz", None)
    full_hours = pd.date_range(start=min_t, end=max_t, freq="h", tz=tz)

    nodes = np.sort(out["node_id"].unique())
    full_index = pd.MultiIndex.from_product([nodes, full_hours], names=["node_id", "timestamp"])

    out = out.set_index(["node_id", "timestamp"]).reindex(full_index)

    aq_cols = [c for c in out.columns if c.startswith(AQ_PREFIXES)]
    weather_cols = [c for c in out.columns if c.startswith(WEATHER_PREFIX)]

    if aq_cols:
        out[aq_cols] = out[aq_cols].apply(pd.to_numeric, errors="coerce")
        out[aq_cols] = (
            out.groupby(level=0)[aq_cols]
            .transform(lambda g: g.interpolate(method="linear", limit_direction="both"))
        )

    if weather_cols:
        out[weather_cols] = out[weather_cols].apply(pd.to_numeric, errors="coerce")
        out[weather_cols] = out.groupby(level=0)[weather_cols].transform(lambda g: g.ffill().bfill())

    # Fill remaining columns per node with nearest-known values.
    remaining_cols = [c for c in out.columns if c not in aq_cols and c not in weather_cols]
    if remaining_cols:
        out[remaining_cols] = out.groupby(level=0)[remaining_cols].transform(lambda g: g.ffill().bfill())

    out = out.reset_index().sort_values(["timestamp", "node_id"]).reset_index(drop=True)
    return out


def _build_sensor_train_mask(num_nodes: int) -> torch.Tensor:
    mapping = pd.read_parquet(STATION_NODE_MAP)
    idx_map = pd.read_parquet(NODE_INDEX_MAP)

    if "node_id" not in mapping.columns:
        raise ValueError("station_to_topology_node_map.parquet must contain column: node_id")
    if not {"node_id", "node_index"}.issubset(idx_map.columns):
        raise ValueError("topology_nodeid_to_index_map.parquet must contain columns: node_id, node_index")

    sensor_node_ids = pd.Series(mapping["node_id"]).dropna().astype("int64").drop_duplicates()
    merged = sensor_node_ids.to_frame("node_id").merge(
        idx_map[["node_id", "node_index"]].drop_duplicates(),
        on="node_id",
        how="left",
    )

    missing_map = merged["node_index"].isna().sum()
    if missing_map > 0:
        missing_ids = merged.loc[merged["node_index"].isna(), "node_id"].tolist()
        raise ValueError(f"{missing_map} sensor node_ids are missing from node_index_map: {missing_ids}")

    sensor_indices = merged["node_index"].astype("int64").to_numpy()
    if np.any(sensor_indices < 0) or np.any(sensor_indices >= num_nodes):
        raise ValueError("Mapped sensor node indices are out of graph index bounds.")

    train_mask = torch.zeros(num_nodes, dtype=torch.bool)
    train_mask[torch.tensor(sensor_indices, dtype=torch.long)] = True
    return train_mask


def finalize_assets() -> None:
    _validate_inputs()

    print("[1/3] Repairing Temporal Continuity...")
    master_df = pd.read_parquet(MASTER_IN)
    repaired_df = _node_hourly_spine(master_df)
    MASTER_OUT.parent.mkdir(parents=True, exist_ok=True)
    repaired_df.to_parquet(MASTER_OUT, index=False)

    unique_ts = pd.to_datetime(repaired_df["timestamp"], errors="coerce").dropna().drop_duplicates().sort_values()
    bad_steps = 0
    if len(unique_ts) > 1:
        bad_steps = int((unique_ts.diff().dropna().dt.total_seconds() != 3600).sum())
    print(f"✅ Continuity Fixed: {len(unique_ts):,} contiguous hourly steps (bad_steps={bad_steps}).")

    print("[2/3] Generating Sensor Mask...")
    graph_dict = torch.load(STATIC_GRAPH_IN, weights_only=False)
    if not isinstance(graph_dict, dict):
        raise TypeError("Expected topology_graph.pt to store a dict payload.")

    required_graph_keys = {"x", "edge_index", "edge_attr", "num_nodes"}
    missing_graph_keys = required_graph_keys - set(graph_dict.keys())
    if missing_graph_keys:
        raise KeyError(f"topology_graph.pt missing required keys: {sorted(missing_graph_keys)}")

    num_nodes = int(graph_dict["num_nodes"])
    train_mask = _build_sensor_train_mask(num_nodes)
    print(f"✅ Sensor Mask Ready: {int(train_mask.sum().item())} labeled nodes / {num_nodes:,} total.")

    print("[3/3] Serializing as PyG Data Object...")
    data = Data(
        x=graph_dict["x"],
        edge_index=graph_dict["edge_index"],
        edge_attr=graph_dict["edge_attr"],
        num_nodes=num_nodes,
        train_mask=train_mask,
        physics_lambda=torch.tensor([PHYSICS_LOSS_LAMBDA], dtype=torch.float32),
    )

    for key in ["node_feature_schema", "highway_categories", "edge_attr_schema"]:
        if key in graph_dict:
            setattr(data, key, graph_dict[key])

    data.validate(raise_on_error=True)
    STATIC_GRAPH_OUT.parent.mkdir(parents=True, exist_ok=True)
    torch.save(data, STATIC_GRAPH_OUT)

    print(f"Isolated Nodes: {data.has_isolated_nodes()}")
    print(f"Self Loops: {data.has_self_loops()}")
    print(f"✅ Success: '{STATIC_GRAPH_OUT}' is now V100-ready.")


if __name__ == "__main__":
    finalize_assets()
