from __future__ import annotations

import argparse
import json
import sys
from collections import deque
from pathlib import Path

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


def _metrics(pred: np.ndarray, target: np.ndarray) -> dict[str, float]:
    err = pred - target
    return {
        "mae_scaled": float(np.mean(np.abs(err))),
        "rmse_scaled": float(np.sqrt(np.mean(err * err))),
        "mse_scaled": float(np.mean(err * err)),
        "mae_unscaled_pm25": float(np.mean(np.abs(err)) * TARGET_SCALE),
        "rmse_unscaled_pm25": float(np.sqrt(np.mean(err * err)) * TARGET_SCALE),
    }


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
    df["node_index"] = df["node_index"].astype(np.int64)
    df[ts_col] = pd.to_datetime(df[ts_col])
    df["target_scaled"] = pd.to_numeric(df["station_pm25"], errors="coerce").fillna(0.0).astype(np.float32) / TARGET_SCALE
    for col in FEATURE_COLS_16:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0).astype(np.float32)
    return df.sort_values([ts_col, "node_index"]).rename(columns={ts_col: "timestamp"})


def _local_subgraph(
    edge_index: torch.Tensor,
    center_node: int,
    hops: int,
    max_nodes: int,
) -> tuple[torch.Tensor, torch.Tensor, int]:
    neighbors: dict[int, set[int]] = {}
    src = edge_index[0].cpu().numpy()
    dst = edge_index[1].cpu().numpy()
    for u, v in zip(src.tolist(), dst.tolist(), strict=False):
        neighbors.setdefault(int(u), set()).add(int(v))
        neighbors.setdefault(int(v), set()).add(int(u))

    seen = {int(center_node)}
    queue: deque[tuple[int, int]] = deque([(int(center_node), 0)])
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

    nodes = torch.tensor(sorted(seen), dtype=torch.long)
    node_pos = {int(n): i for i, n in enumerate(nodes.tolist())}
    keep = torch.isin(edge_index[0].cpu(), nodes) & torch.isin(edge_index[1].cpu(), nodes)
    sub_edges_global = edge_index[:, keep].cpu()
    if sub_edges_global.numel() == 0:
        sub_edge_index = torch.empty((2, 0), dtype=torch.long)
    else:
        remapped = [[node_pos[int(v)] for v in row.tolist()] for row in sub_edges_global]
        sub_edge_index = torch.tensor(remapped, dtype=torch.long)
    return nodes, sub_edge_index, node_pos[int(center_node)]


def evaluate(args: argparse.Namespace) -> dict[str, object]:
    device = torch.device(args.device)
    model, info = load_stpignn_checkpoint(args.checkpoint, device=device)
    graph = torch.load(args.graph, map_location="cpu", weights_only=False)
    df = _load_model_input(Path(args.model_input), Path(args.node_map))

    times = pd.Index(sorted(df["timestamp"].unique()))
    holdout_times = times[-args.holdout_hours :]
    horizons = [int(h.strip()) for h in str(args.horizons).split(",") if h.strip()]
    if not horizons:
        raise ValueError("--horizons must contain at least one integer horizon")

    candidate_targets = df[
        df["timestamp"].isin(holdout_times)
        & df["target_scaled"].gt(0)
        & df["node_index"].notna()
    ][["timestamp", "node_index", "target_scaled"]]
    candidate_targets = candidate_targets.drop_duplicates(["timestamp", "node_index"]).head(args.max_samples)

    feature_lookup = {
        (row.timestamp, int(row.node_index)): np.asarray([getattr(row, col) for col in FEATURE_COLS_16], dtype=np.float32)
        for row in df[["timestamp", "node_index", *FEATURE_COLS_16]].itertuples(index=False)
    }
    target_lookup = {
        (row.timestamp, int(row.node_index)): float(row.target_scaled)
        for row in df[["timestamp", "node_index", "target_scaled"]].itertuples(index=False)
    }
    station_mean = float(df.loc[df["target_scaled"].gt(0), "target_scaled"].mean())

    horizon_rows: dict[int, dict[str, list[float] | int]] = {
        horizon: {"preds": [], "targets": [], "persistence": [], "means": [], "skipped": 0}
        for horizon in horizons
    }

    for row in candidate_targets.itertuples(index=False):
        ts = row.timestamp
        center = int(row.node_index)
        ts_idx = times.get_loc(ts)
        if ts_idx < args.window + max(horizons):
            for horizon in horizons:
                horizon_rows[horizon]["skipped"] = int(horizon_rows[horizon]["skipped"]) + 1
            continue

        nodes, sub_edge_index, center_local = _local_subgraph(
            graph.edge_index,
            center_node=center,
            hops=args.hops,
            max_nodes=args.max_nodes,
        )
        if sub_edge_index.shape[1] == 0:
            for horizon in horizons:
                horizon_rows[horizon]["skipped"] = int(horizon_rows[horizon]["skipped"]) + 1
            continue

        keep = torch.isin(graph.edge_index[0].cpu(), nodes) & torch.isin(graph.edge_index[1].cpu(), nodes)
        sub_edge_attr = graph.edge_attr[keep].float()
        if sub_edge_attr.shape[0] != sub_edge_index.shape[1]:
            for horizon in horizons:
                horizon_rows[horizon]["skipped"] = int(horizon_rows[horizon]["skipped"]) + 1
            continue

        x_seq = np.zeros((args.window, len(nodes), len(FEATURE_COLS_16)), dtype=np.float32)
        input_end_idx = ts_idx - min(horizons) + 1
        window_times = times[input_end_idx - args.window : input_end_idx]
        for t_i, w_ts in enumerate(window_times):
            for n_i, node in enumerate(nodes.tolist()):
                x_seq[t_i, n_i, :] = feature_lookup.get((w_ts, int(node)), 0.0)

        if not np.any(x_seq):
            for horizon in horizons:
                horizon_rows[horizon]["skipped"] = int(horizon_rows[horizon]["skipped"]) + 1
            continue

        with torch.no_grad():
            pred = model(
                x_seq=torch.from_numpy(x_seq).unsqueeze(0).to(device),
                edge_index=sub_edge_index.to(device),
                edge_attr=sub_edge_attr.to(device),
            )[0, center_local]

        pred_value = float(pred.detach().cpu().item())
        for horizon in horizons:
            target_idx = input_end_idx + horizon - 1
            if target_idx >= len(times):
                horizon_rows[horizon]["skipped"] = int(horizon_rows[horizon]["skipped"]) + 1
                continue
            target_ts = times[target_idx]
            target = target_lookup.get((target_ts, center))
            if target is None or target <= 0.0:
                horizon_rows[horizon]["skipped"] = int(horizon_rows[horizon]["skipped"]) + 1
                continue
            prev_target = target_lookup.get((window_times[-1], center), station_mean)
            horizon_rows[horizon]["preds"].append(pred_value)  # type: ignore[union-attr]
            horizon_rows[horizon]["targets"].append(float(target))  # type: ignore[union-attr]
            horizon_rows[horizon]["persistence"].append(float(prev_target))  # type: ignore[union-attr]
            horizon_rows[horizon]["means"].append(station_mean)  # type: ignore[union-attr]

    reports: dict[str, object] = {}
    for horizon, rows in horizon_rows.items():
        preds = rows["preds"]
        targets = rows["targets"]
        persistence = rows["persistence"]
        means = rows["means"]
        if not isinstance(preds, list) or not preds:
            reports[str(horizon)] = {
                "samples_evaluated": 0,
                "samples_skipped": int(rows["skipped"]),
                "error": "No holdout samples were evaluated for this horizon",
            }
            continue
        pred_np = np.asarray(preds, dtype=np.float64)
        target_np = np.asarray(targets, dtype=np.float64)
        reports[str(horizon)] = {
            "samples_evaluated": len(preds),
            "samples_skipped": int(rows["skipped"]),
            "stpignn": _metrics(pred_np, target_np),
            "baseline_persistence": _metrics(np.asarray(persistence, dtype=np.float64), target_np),
            "baseline_station_mean": _metrics(np.asarray(means, dtype=np.float64), target_np),
        }

    result = {
        "checkpoint": {
            "path": str(info.path),
            "epoch": info.epoch,
            "best_val_mse": info.best_val_mse,
            "tensor_count": info.tensor_count,
            "architecture": {
                "node_in_dim": info.node_in_dim,
                "edge_dim": info.edge_dim,
                "spatial_hidden_dim": info.spatial_hidden_dim,
                "temporal_hidden_dim": info.temporal_hidden_dim,
                "gnn_layers": info.gnn_layers,
            },
        },
        "holdout": {
            "window": args.window,
            "holdout_hours": args.holdout_hours,
            "max_samples": args.max_samples,
            "max_nodes_per_subgraph": args.max_nodes,
            "hops": args.hops,
            "horizons": horizons,
        },
        "by_horizon_hours": reports,
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate the archived ST-PIGNN checkpoint on a late-time holdout slice.")
    parser.add_argument("--checkpoint", default="citywide_stpignn_best.pt")
    parser.add_argument("--graph", default="data/processed/graph/topology_graph_pyg_inference.pt")
    parser.add_argument("--model-input", default="data/processed/model_input/model_input_node_hourly_features.parquet")
    parser.add_argument("--node-map", default="data/processed/graph/topology_nodeid_to_index_map.parquet")
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--window", type=int, default=12)
    parser.add_argument("--holdout-hours", type=int, default=336)
    parser.add_argument("--horizons", default="1,3,6,12")
    parser.add_argument("--max-samples", type=int, default=64)
    parser.add_argument("--hops", type=int, default=1)
    parser.add_argument("--max-nodes", type=int, default=256)
    parser.add_argument("--out", default="docs/stpignn_holdout_report.json")
    args = parser.parse_args()

    result = evaluate(args)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
