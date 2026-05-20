from __future__ import annotations

import argparse
import csv
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
    df = df.dropna(subset=["node_index", ts_col]).copy()
    df["node_index"] = df["node_index"].astype(int)
    df[ts_col] = pd.to_datetime(df[ts_col])
    df["station_pm25"] = pd.to_numeric(df["station_pm25"], errors="coerce").fillna(0.0).astype(float).clip(lower=0.0, upper=TARGET_PM25_MAX)
    df["target_scaled"] = df["station_pm25"] / TARGET_SCALE
    for col in FEATURE_COLS_16:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0).astype(float)
    return df.sort_values([ts_col, "node_index"]).rename(columns={ts_col: "timestamp"})


def main(
    model_path: str,
    graph_path: str,
    model_input: str,
    node_map: str,
    out_csv: str,
    holdout_hours: int = 336,
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

    src = graph.edge_index[0].cpu().numpy()
    dst = graph.edge_index[1].cpu().numpy()

    outp = Path(out_csv)
    outp.parent.mkdir(parents=True, exist_ok=True)
    with open(outp, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["zone_id", "raw_pred", "obs", "timestamp"])
        writer.writeheader()

        for row in candidate_targets.itertuples(index=False):
            ts = row.timestamp
            center = int(row.node_index)
            ts_idx = times.get_loc(ts)
            if ts_idx < 12 + 1:
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

            input_end_idx = ts_idx - 1
            window_times = times[input_end_idx - 12 + 1 : input_end_idx + 1]
            if len(window_times) != 12:
                continue

            x_seq = np.zeros((12, len(nodes), len(FEATURE_COLS_16)), dtype=np.float32)
            for t_i, w_ts in enumerate(window_times):
                for n_i, node in enumerate(nodes.tolist()):
                    x_seq[t_i, n_i, :] = feature_lookup.get((w_ts, int(node)), 0.0)
            if not np.any(x_seq):
                continue

            with torch.no_grad():
                pred = model(x_seq=torch.from_numpy(x_seq).unsqueeze(0), edge_index=sub_edge_index, edge_attr=sub_edge_attr)[0, node_pos[int(center)]]

            pred_value = float(pred.detach().cpu().item())
            target_idx = input_end_idx + 1
            if target_idx >= len(times):
                continue
            target_ts = times[target_idx]
            target_row = df[(df['timestamp'] == target_ts) & (df['node_index'] == center)]
            if target_row.empty:
                continue
            target_value = float(target_row['target_scaled'].iloc[0])

            raw_pred_pm25 = pred_value * TARGET_SCALE
            obs_pm25 = target_value * TARGET_SCALE
            zone_node_id = nodeidx_to_nodeid.get(center, center)
            writer.writerow({
                "zone_id": str(zone_node_id),
                "raw_pred": f"{raw_pred_pm25:.6f}",
                "obs": f"{obs_pm25:.6f}",
                "timestamp": target_ts.isoformat(),
            })


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="citywide_stpignn_best.pt")
    parser.add_argument("--graph", default="data/processed/graph/topology_graph_pyg_inference.pt")
    parser.add_argument("--model-input", default="data/processed/model_input/model_input_node_hourly_features.parquet")
    parser.add_argument("--node-map", default="data/processed/graph/topology_nodeid_to_index_map.parquet")
    parser.add_argument("--out", default="data/processed/holdout_pairs.csv")
    parser.add_argument("--holdout-hours", type=int, default=336)
    parser.add_argument("--max-samples", type=int, default=1000)
    args = parser.parse_args()
    main(args.model, args.graph, args.model_input, args.node_map, args.out, holdout_hours=args.holdout_hours, max_samples=args.max_samples)
