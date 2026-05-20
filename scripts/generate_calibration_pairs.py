from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from collections import deque

import numpy as np
import pandas as pd
import torch

REPO_ROOT = Path(__file__).resolve().parents[1]
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


def main(
    model_input: str,
    node_map: str,
    graph: str,
    checkpoint: str,
    out_csv: str,
    window: int = 12,
    max_samples: int = 10000,
    hops: int = 1,
    max_nodes: int = 256,
):
    model, info = load_stpignn_checkpoint(checkpoint, device=torch.device("cpu"))
    graph_obj = torch.load(graph, map_location="cpu", weights_only=False)
    df = _load_model_input(Path(model_input), Path(node_map))

    times = pd.Index(sorted(df["timestamp"].unique()))
    candidate_targets = df[df["target_scaled"].gt(0) & df["node_index"].notna()][["timestamp", "node_index", "target_scaled"]]
    candidate_targets = candidate_targets.drop_duplicates(["timestamp", "node_index"]).head(max_samples)

    feature_lookup = {
        (row.timestamp, int(row.node_index)): np.asarray([getattr(row, col) for col in FEATURE_COLS_16], dtype=np.float32)
        for row in df[["timestamp", "node_index", *FEATURE_COLS_16]].itertuples(index=False)
    }

    node_map_df = pd.read_parquet(node_map)
    idx_to_node = {int(idx): int(nid) for nid, idx in zip(node_map_df["node_id"].values, node_map_df["node_index"].values)}

    with open(out_csv, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["zone_id", "raw_pred", "obs", "timestamp"]) 
        writer.writeheader()

        for row in candidate_targets.itertuples(index=False):
            ts = row.timestamp
            center_idx = int(row.node_index)
            ts_idx = times.get_loc(ts)
            if ts_idx < window + 1:
                continue

            # build local subgraph like evaluate
            neighbors = {}
            src = graph_obj.edge_index[0].cpu().numpy()
            dst = graph_obj.edge_index[1].cpu().numpy()
            for u, v in zip(src.tolist(), dst.tolist()):
                neighbors.setdefault(int(u), set()).add(int(v))
                neighbors.setdefault(int(v), set()).add(int(u))

            seen = {int(center_idx)}
            from collections import deque
            queue = deque([(int(center_idx), 0)])
            while queue and len(seen) < max_nodes:
                node, depth = queue.popleft()
                if depth >= hops:
                    continue
                for nb in sorted(neighbors.get(node, ())):
                    if nb not in seen:
                        seen.add(nb)
                        queue.append((nb, depth + 1))
                        if len(seen) >= max_nodes:
                            break

            nodes = list(sorted(seen))
            node_pos = {int(n): i for i, n in enumerate(nodes)}
            keep = [i for i, (u, v) in enumerate(zip(src.tolist(), dst.tolist())) if u in nodes and v in nodes]
            if not keep:
                continue

            sub_edge_index = []
            for i in keep:
                u = src[i]; v = dst[i]
                sub_edge_index.append([node_pos[int(u)], node_pos[int(v)]])
            sub_edge_index = torch.tensor(sub_edge_index, dtype=torch.long).T if sub_edge_index else torch.empty((2, 0), dtype=torch.long)
            sub_edge_attr = graph_obj.edge_attr[keep].float()
            if sub_edge_attr.shape[0] != sub_edge_index.shape[1]:
                continue

            # build x_seq
            input_end_idx = ts_idx - 1  # predict next hour
            window_times = times[input_end_idx - window + 1 : input_end_idx + 1]
            if len(window_times) != window:
                continue
            x_seq = np.zeros((window, len(nodes), len(FEATURE_COLS_16)), dtype=np.float32)
            for t_i, w_ts in enumerate(window_times):
                for n_i, node in enumerate(nodes):
                    x_seq[t_i, n_i, :] = feature_lookup.get((w_ts, int(node)), 0.0)

            if not np.any(x_seq):
                continue

            with torch.no_grad():
                pred = model(x_seq=torch.from_numpy(x_seq).unsqueeze(0), edge_index=sub_edge_index, edge_attr=sub_edge_attr)[0, node_pos[int(center_idx)]]

            pred_value = float(pred.detach().cpu().item())

            # target at next step
            target_idx = input_end_idx + 1
            if target_idx >= len(times):
                continue
            target_ts = times[target_idx]
            target_row = df[(df['timestamp'] == target_ts) & (df['node_index'] == center_idx)]
            if target_row.empty:
                continue
            target_value = float(target_row['target_scaled'].iloc[0])

            # write scaled back to pm25 units
            raw_pred_pm25 = pred_value * TARGET_SCALE
            obs_pm25 = target_value * TARGET_SCALE
            zone_node_id = idx_to_node.get(center_idx, center_idx)
            writer.writerow({
                "zone_id": str(zone_node_id),
                "raw_pred": f"{raw_pred_pm25:.6f}",
                "obs": f"{obs_pm25:.6f}",
                "timestamp": target_ts.isoformat(),
            })


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-input", default="data/processed/model_input/model_input_node_hourly_features.parquet")
    parser.add_argument("--node-map", default="data/processed/graph/topology_nodeid_to_index_map.parquet")
    parser.add_argument("--graph", default="data/processed/graph/topology_graph_pyg_inference.pt")
    parser.add_argument("--checkpoint", default="citywide_stpignn_best.pt")
    parser.add_argument("--out", default="data/processed/calibration_pairs.csv")
    parser.add_argument("--window", type=int, default=12)
    parser.add_argument("--max-samples", type=int, default=5000)
    args = parser.parse_args()
    main(args.model_input, args.node_map, args.graph, args.checkpoint, args.out, window=args.window, max_samples=args.max_samples)
