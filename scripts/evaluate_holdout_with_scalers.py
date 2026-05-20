from __future__ import annotations

import argparse
import json
from pathlib import Path
from collections import deque

import numpy as np
import pandas as pd
import torch

REPO_ROOT = Path(__file__).resolve().parents[1]
import sys
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from gnn.checkpoint import load_stpignn_checkpoint

FEATURE_COLS_16 = [
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
]
TARGET_SCALE = 342.9356
TARGET_PM25_MAX = 120.0


def _load_model_input(model_input_path: Path, node_map_path: Path) -> pd.DataFrame:
    df = pd.read_parquet(model_input_path)
    if "node_index" not in df.columns:
        node_map = pd.read_parquet(node_map_path)
        node_to_idx = dict(zip(node_map["node_id"].values, node_map["node_index"].values))
        df["node_index"] = df["node_id"].map(node_to_idx)

    ts_col = "timestamp" if "timestamp" in df.columns else "time"
    missing = [col for col in FEATURE_COLS_16 + ["station_pm25", "node_index", ts_col] if col not in df.columns]
    if missing:
        raise ValueError(f"Model input is missing required columns: {missing}")

    df = df.dropna(subset=["node_index", ts_col]).copy()
    df["node_index"] = df["node_index"].astype(int)
    df[ts_col] = pd.to_datetime(df[ts_col])
    df["station_pm25"] = pd.to_numeric(df["station_pm25"], errors="coerce").fillna(0.0).astype(float).clip(lower=0.0, upper=TARGET_PM25_MAX)
    df["target_scaled"] = df["station_pm25"] / TARGET_SCALE
    for col in FEATURE_COLS_16:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0).astype(float)
    return df.sort_values([ts_col, "node_index"]).rename(columns={ts_col: "timestamp"})


def evaluate_with_scalers(
    model_path: str,
    graph_path: str,
    model_input: str,
    node_map: str,
    scalers_path: str | None,
    holdout_hours: int = 336,
    window: int = 12,
    max_samples: int = 1000,
):
    model, info = load_stpignn_checkpoint(model_path, device=torch.device("cpu"))
    graph = torch.load(graph_path, map_location="cpu", weights_only=False)
    df = _load_model_input(Path(model_input), Path(node_map))

    times = pd.Index(sorted(df["timestamp"].unique()))
    holdout_times = times[-holdout_hours:]

    candidate_targets = df[
        df["timestamp"].isin(holdout_times) & df["target_scaled"].gt(0) & df["node_index"].notna()
    ][["timestamp", "node_index", "target_scaled"]]
    candidate_targets = candidate_targets.drop_duplicates(["timestamp", "node_index"]).head(max_samples)

    feature_lookup = {
        (row.timestamp, int(row.node_index)): np.asarray([getattr(row, col) for col in FEATURE_COLS_16], dtype=np.float32)
        for row in df[["timestamp", "node_index", *FEATURE_COLS_16]].itertuples(index=False)
    }

    node_map_df = pd.read_parquet(node_map)
    nodeidx_to_nodeid = {int(idx): int(nid) for nid, idx in zip(node_map_df["node_id"].values, node_map_df["node_index"].values)}

    preds = []
    targets = []
    node_ids = []

    src = graph.edge_index[0].cpu().numpy()
    dst = graph.edge_index[1].cpu().numpy()

    for row in candidate_targets.itertuples(index=False):
        ts = row.timestamp
        center = int(row.node_index)
        ts_idx = times.get_loc(ts)
        if ts_idx < window + 1:
            continue

        # local subgraph
        neighbors = {}
        for u, v in zip(src.tolist(), dst.tolist()):
            neighbors.setdefault(int(u), set()).add(int(v))
            neighbors.setdefault(int(v), set()).add(int(u))

        seen = {int(center)}
        queue = deque([(int(center), 0)])
        while queue and len(seen) < 256:
            node, depth = queue.popleft()
            if depth >= 1:
                continue
            for nb in sorted(neighbors.get(node, ())) :
                if nb not in seen:
                    seen.add(nb)
                    queue.append((nb, depth + 1))

        nodes = torch.tensor(sorted(seen), dtype=torch.long)
        node_pos = {int(n): i for i, n in enumerate(nodes.tolist())}
        keep = torch.isin(graph.edge_index[0].cpu(), nodes) & torch.isin(graph.edge_index[1].cpu(), nodes)
        sub_edge_global = graph.edge_index[:, keep]
        if sub_edge_global.numel() == 0:
            continue
        sub_edge_attr = graph.edge_attr[keep].float()
        sub_edge_index = torch.tensor(
            [[node_pos[int(value)] for value in row.tolist()] for row in sub_edge_global],
            dtype=torch.long,
        )

        input_end_idx = ts_idx - min(1, 1)  # predict next hour
        window_times = times[input_end_idx - window + 1 : input_end_idx + 1]
        if len(window_times) != window:
            continue

        x_seq = np.zeros((window, len(nodes), len(FEATURE_COLS_16)), dtype=np.float32)
        for t_i, w_ts in enumerate(window_times):
            for n_i, node in enumerate(nodes.tolist()):
                x_seq[t_i, n_i, :] = feature_lookup.get((w_ts, int(node)), 0.0)
        if not np.any(x_seq):
            continue

        with torch.no_grad():
            pred = model(x_seq=torch.from_numpy(x_seq).unsqueeze(0), edge_index=sub_edge_index, edge_attr=sub_edge_attr)[0, node_pos[int(center)]]

        pred_value = float(pred.detach().cpu().item())
        target_value = float(row.target_scaled)

        preds.append(pred_value)
        targets.append(target_value)
        node_ids.append(nodeidx_to_nodeid.get(center, center))

    preds = np.asarray(preds, dtype=np.float64)
    targets = np.asarray(targets, dtype=np.float64)
    node_ids = np.asarray(node_ids)

    result = {"samples": int(len(targets))}

    if len(targets) == 0:
        result.update({"raw": None, "scaled": None})
        return result

    def metrics(pred_arr, targ_arr):
        err = pred_arr - targ_arr
        mae = float(np.mean(np.abs(err)))
        rmse = float(np.sqrt(np.mean(err * err)))
        return {"mae_scaled": mae, "rmse_scaled": rmse, "mae_ug": mae * TARGET_SCALE, "rmse_ug": rmse * TARGET_SCALE}

    raw_metrics = metrics(preds, targets)

    # apply scalers if provided
    if scalers_path:
        with open(scalers_path) as fh:
            scalers = json.load(fh)
        preds_pm25 = preds * TARGET_SCALE
        preds_pm25_adj = []
        for p_pm, zid in zip(preds_pm25, node_ids):
            s = scalers.get(str(zid))
            if s and int(s.get("n", 0)) >= 3:
                a = float(s.get("a", 1.0))
                b = float(s.get("b", 0.0))
                adj = a * p_pm + b
            else:
                adj = p_pm
            preds_pm25_adj.append(adj)
        preds_scaled = (np.asarray(preds_pm25_adj, dtype=np.float64)) / TARGET_SCALE
        scaled_metrics = metrics(preds_scaled, targets)
    else:
        scaled_metrics = None

    result.update({"raw": raw_metrics, "scaled": scaled_metrics})
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="citywide_stpignn_best.pt")
    parser.add_argument("--graph", default="data/processed/graph/topology_graph_pyg_inference.pt")
    parser.add_argument("--model-input", default="data/processed/model_input/model_input_node_hourly_features.parquet")
    parser.add_argument("--node-map", default="data/processed/graph/topology_nodeid_to_index_map.parquet")
    parser.add_argument("--scalers", default="data/processed/per_zone_scalers.json")
    parser.add_argument("--holdout-hours", type=int, default=336)
    parser.add_argument("--window", type=int, default=12)
    parser.add_argument("--max-samples", type=int, default=1000)
    args = parser.parse_args()

    res = evaluate_with_scalers(
        args.model, args.graph, args.model_input, args.node_map, args.scalers, holdout_hours=args.holdout_hours, window=args.window, max_samples=args.max_samples
    )
    out = Path("docs/stpignn_holdout_with_scalers.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=2) + "\n")
    print(json.dumps(res, indent=2))
