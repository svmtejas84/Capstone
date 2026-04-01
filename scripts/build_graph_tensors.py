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

import ast
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
from scipy.spatial import KDTree

NODES_PATH = Path("data/graphs/bangalore_utm_nodes.parquet")
EDGES_PATH = Path("data/graphs/bangalore_utm_edges.parquet")
NODE_MAP_OUT = Path("data/processed/node_index_map.parquet")
STATIC_GRAPH_OUT = Path("data/processed/static_graph.pt")
ENV_GRID_PATH = Path("data/processed/environment_grid_utm.parquet")
MASTER_FEATURES_PATH = Path("data/processed/gnn_training_tensor_final.parquet")

NODE_FEATURE_COLUMNS = [
    "station_pm10",
    "station_pm25",
    "station_no2",
    "station_so2",
    "station_co",
    "weather_wind_speed_10m",
    "weather_wind_direction_10m",
    "weather_wind_gusts_10m",
    "weather_temperature_2m",
    "weather_relative_humidity_2m",
    "weather_surface_pressure",
    "city_nitrogen_dioxide",
    "city_sulphur_dioxide",
    "city_pm2_5",
    "city_pm10",
    "city_carbon_monoxide",
    "elevation",
]

X_CANDIDATES = ["x", "utm_x", "easting", "lon_utm"]
Y_CANDIDATES = ["y", "utm_y", "northing", "lat_utm"]


def _find_first_present(df: pd.DataFrame, candidates: list[str], label: str) -> str:
    for c in candidates:
        if c in df.columns:
            return c
    raise ValueError(f"Could not find {label} column. Tried: {candidates}")


def _normalize_highway(value: object) -> str:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return "unknown"

    normalized: str | None = None
    if isinstance(value, (list, tuple, set)):
        for item in value:
            item_str = str(item).strip().lower()
            if item_str:
                normalized = item_str
                break
    else:
        raw = str(value).strip()
        if not raw:
            return "unknown"
        if raw.startswith("[") and raw.endswith("]"):
            try:
                parsed = ast.literal_eval(raw)
                if isinstance(parsed, (list, tuple, set)):
                    for item in parsed:
                        item_str = str(item).strip().lower()
                        if item_str:
                            normalized = item_str
                            break
            except (SyntaxError, ValueError):
                normalized = None

        if normalized is None:
            token = raw.split(";")[0].split(",")[0].strip().lower()
            normalized = token or "unknown"

    if normalized in {"nan", "none", "null", ""}:
        return "unknown"
    return normalized


def _derive_elevation_from_utm_y(nodes_df: pd.DataFrame, y_col: str) -> pd.Series:
    y = pd.to_numeric(nodes_df[y_col], errors="coerce")
    y_min = float(y.min())
    y_max = float(y.max())
    if not np.isfinite(y_min) or not np.isfinite(y_max) or np.isclose(y_max, y_min):
        return pd.Series(np.full(len(nodes_df), 900.0), index=nodes_df.index, dtype="float64")
    scaled = 800.0 + 200.0 * ((y - y_min) / (y_max - y_min))
    return scaled.clip(800.0, 1000.0)


def _prepare_environment_grid(nodes_df: pd.DataFrame) -> pd.DataFrame:
    node_x_col = _find_first_present(nodes_df, X_CANDIDATES, "node x")
    node_y_col = _find_first_present(nodes_df, Y_CANDIDATES, "node y")

    if ENV_GRID_PATH.exists():
        env_df = pd.read_parquet(ENV_GRID_PATH)
        env_x_col = _find_first_present(env_df, X_CANDIDATES, "environment x")
        env_y_col = _find_first_present(env_df, Y_CANDIDATES, "environment y")

        if "timestamp" in env_df.columns:
            agg = {c: "median" for c in NODE_FEATURE_COLUMNS if c in env_df.columns}
            env_df = env_df.groupby([env_x_col, env_y_col], as_index=False).agg(agg)

        if "elevation" not in env_df.columns:
            env_df["elevation"] = np.nan

        env_df = env_df.rename(columns={env_x_col: "x", env_y_col: "y"})
        return env_df

    if not MASTER_FEATURES_PATH.exists():
        raise FileNotFoundError(
            "Missing feature source. Expected either data/processed/environment_grid_utm.parquet "
            "or data/processed/gnn_training_tensor_final.parquet"
        )

    master = pd.read_parquet(MASTER_FEATURES_PATH)
    if "node_id" not in master.columns:
        raise ValueError("gnn_training_tensor_final.parquet must contain node_id for fallback feature source")

    available_feature_cols = [c for c in NODE_FEATURE_COLUMNS if c in master.columns]
    if not available_feature_cols:
        raise ValueError("No expected node feature columns found in fallback master feature table")

    env_by_node = master.groupby("node_id", as_index=False)[available_feature_cols].median()
    node_coords = nodes_df[["osmid", node_x_col, node_y_col]].rename(
        columns={"osmid": "node_id", node_x_col: "x", node_y_col: "y"}
    )
    env_df = env_by_node.merge(node_coords, on="node_id", how="left")
    env_df = env_df.dropna(subset=["x", "y"]).copy()

    if "elevation" not in env_df.columns:
        env_df["elevation"] = np.nan

    return env_df


def _scale_and_sanitize_pm25(series: pd.Series) -> pd.Series:
    s = pd.to_numeric(series, errors="coerce")
    if s.dropna().empty:
        return s

    q99 = float(s.quantile(0.99))
    max_v = float(s.max())
    # CAMS PM2.5 can arrive in kg/m^3; convert to ug/m^3 when values are clearly sub-unit.
    if np.isfinite(max_v) and max_v < 0.005 and np.isfinite(q99) and q99 < 0.002:
        s = s * 1e9

    return s.clip(0.0, 500.0)


def _sanitize_node_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    for col in NODE_FEATURE_COLUMNS:
        if col not in out.columns:
            out[col] = np.nan

    for col in NODE_FEATURE_COLUMNS:
        out[col] = pd.to_numeric(out[col], errors="coerce")

    pm_cols = [c for c in NODE_FEATURE_COLUMNS if "pm25" in c or "pm2_5" in c]
    for col in pm_cols:
        out[col] = _scale_and_sanitize_pm25(out[col])

    if "weather_relative_humidity_2m" in out.columns:
        out["weather_relative_humidity_2m"] = out["weather_relative_humidity_2m"].clip(0.0, 100.0)
    if "weather_temperature_2m" in out.columns:
        out["weather_temperature_2m"] = out["weather_temperature_2m"].clip(10.0, 50.0)
    if "elevation" in out.columns:
        out["elevation"] = out["elevation"].clip(800.0, 1000.0)

    for col in NODE_FEATURE_COLUMNS:
        s = out[col]
        valid_for_median = s[np.isfinite(s) & (s != 0.0)]
        median = float(valid_for_median.median()) if not valid_for_median.empty else 1.0
        out[col] = s.where(np.isfinite(s) & (s != 0.0), median)

    return out[NODE_FEATURE_COLUMNS]


def _build_node_feature_matrix(nodes_df: pd.DataFrame, node_index_map: pd.DataFrame) -> torch.Tensor:
    node_x_col = _find_first_present(nodes_df, X_CANDIDATES, "node x")
    node_y_col = _find_first_present(nodes_df, Y_CANDIDATES, "node y")

    env_df = _prepare_environment_grid(nodes_df)
    if env_df.empty:
        raise ValueError("Environment feature table is empty after preprocessing")

    env_x = pd.to_numeric(env_df["x"], errors="coerce")
    env_y = pd.to_numeric(env_df["y"], errors="coerce")
    valid_env = np.isfinite(env_x) & np.isfinite(env_y)
    env_df = env_df.loc[valid_env].copy()
    if env_df.empty:
        raise ValueError("No valid UTM coordinates found in environment feature table")

    node_xy = nodes_df[[node_x_col, node_y_col]].apply(pd.to_numeric, errors="coerce")
    valid_nodes = np.isfinite(node_xy[node_x_col]) & np.isfinite(node_xy[node_y_col])
    if not bool(valid_nodes.all()):
        raise ValueError("Nodes table contains invalid UTM coordinates; cannot run KDTree join")

    if "elevation" not in env_df.columns:
        env_df["elevation"] = np.nan

    tree = KDTree(env_df[["x", "y"]].to_numpy(dtype="float64"))
    _, nearest_idx = tree.query(node_xy[[node_x_col, node_y_col]].to_numpy(dtype="float64"), k=1)

    joined = env_df.iloc[np.asarray(nearest_idx, dtype=int)].reset_index(drop=True)
    joined["node_id"] = nodes_df["osmid"].astype("int64").reset_index(drop=True)

    if joined["elevation"].isna().all():
        joined["elevation"] = _derive_elevation_from_utm_y(nodes_df.reset_index(drop=True), node_y_col)

    features = _sanitize_node_features(joined)
    features["node_id"] = joined["node_id"]

    ordered = node_index_map.merge(features, left_on="node_id", right_on="node_id", how="left")
    if ordered[NODE_FEATURE_COLUMNS].isna().any().any():
        ordered[NODE_FEATURE_COLUMNS] = _sanitize_node_features(ordered[NODE_FEATURE_COLUMNS])

    return torch.tensor(ordered[NODE_FEATURE_COLUMNS].to_numpy(dtype="float32"), dtype=torch.float)


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

    # 1b) Build node features with KDTree nearest-environment join in UTM meters.
    x_tensor = _build_node_feature_matrix(nodes, node_index_map)

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
    highway_normalized = e_bi["highway"].map(_normalize_highway)
    highway_codes, highway_categories = pd.factorize(highway_normalized, sort=True)
    highway_one_hot = F.one_hot(torch.tensor(highway_codes, dtype=torch.long), num_classes=len(highway_categories)).to(torch.float)
    length_tensor = torch.tensor(e_bi["length"].to_numpy(), dtype=torch.float).unsqueeze(1)
    edge_attr = torch.cat([length_tensor, highway_one_hot], dim=1)

    graph_obj = {
        "x": x_tensor,
        "edge_index": edge_index,
        "edge_attr": edge_attr,
        "num_nodes": int(len(node_index_map)),
        "node_feature_schema": list(NODE_FEATURE_COLUMNS),
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

    dead_zone_ratio = float((x_tensor.abs().sum(dim=1) == 0).float().mean().item()) if x_tensor.numel() else 0.0
    x_has_nan = bool(torch.isnan(x_tensor).any().item()) if x_tensor.numel() else False
    edge_has_nan = bool(torch.isnan(edge_attr).any().item()) if edge_attr.numel() else False
    edge_cat_nonzero_ratio = float((edge_attr[:, 1:].sum(dim=1) > 0).float().mean().item()) if edge_attr.shape[1] > 1 else 0.0
    elevation_idx = NODE_FEATURE_COLUMNS.index("elevation")
    elevation_std = float(x_tensor[:, elevation_idx].std(unbiased=False).item())

    print(f"[GRAPH] Saved node index map -> {NODE_MAP_OUT}")
    print(f"[GRAPH] Saved static graph tensor -> {STATIC_GRAPH_OUT}")
    print(f"[VALIDATION] Isolated nodes: {isolated_nodes}")
    print(f"[VALIDATION] Graph density (edges/nodes): {density:.6f}")
    print(f"[VALIDATION] Edge length range (m): min={min_len:.3f}, max={max_len:.3f}")
    print(f"[VALIDATION] graph.x shape: {tuple(x_tensor.shape)}")
    print(f"[VALIDATION] graph.x NaN present: {x_has_nan}")
    print(f"[VALIDATION] graph.x dead-zone ratio (all-zero rows): {dead_zone_ratio:.6f}")
    print(f"[VALIDATION] graph.x elevation std: {elevation_std:.6f}")
    print(f"[VALIDATION] graph.edge_attr NaN present: {edge_has_nan}")
    print(f"[VALIDATION] graph.edge_attr categorical non-zero row ratio: {edge_cat_nonzero_ratio:.6f}")


def main() -> None:
    build_graph_tensors()


if __name__ == "__main__":
    main()
