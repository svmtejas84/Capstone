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
from scripts.generate_calibration_pairs import _load_model_input, FEATURE_COLS_16, TARGET_SCALE


def fit_and_eval(model, graph, df, node_map_path: Path, scalers: dict[str, dict], max_samples: int = 200):
    times = pd.Index(sorted(df["timestamp"].unique()))
    candidate_targets = df[df["target_scaled"].gt(0) & df["node_index"].notna()][["timestamp", "node_index", "target_scaled"]]
    candidate_targets = candidate_targets.drop_duplicates(["timestamp", "node_index"]).head(max_samples)

    feature_lookup = {
        (row.timestamp, int(row.node_index)): np.asarray([getattr(row, col) for col in FEATURE_COLS_16], dtype=np.float32)
        for row in df[["timestamp", "node_index", *FEATURE_COLS_16]].itertuples(index=False)
    }

    node_map_df = pd.read_parquet(node_map_path)
    nodeidx_to_nodeid = {int(idx): int(nid) for nid, idx in zip(node_map_df["node_id"].values, node_map_df["node_index"].values)}

    preds_raw = []
    preds_scaled = []
    targets = []

    src = graph.edge_index[0].cpu().numpy()
    dst = graph.edge_index[1].cpu().numpy()

    for row in candidate_targets.itertuples(index=False):
        ts = row.timestamp
        center_idx = int(row.node_index)
        ts_idx = times.get_loc(ts)
        if ts_idx < 12 + 1:
            continue
        nodes = {center_idx}
        queue = deque([(center_idx, 0)])
        neighbors = {}
        for u, v in zip(src.tolist(), dst.tolist()):
            neighbors.setdefault(int(u), set()).add(int(v))
            neighbors.setdefault(int(v), set()).add(int(u))
        while queue and len(nodes) < 256:
            node, depth = queue.popleft()
            if depth >= 1:
                continue
            for nb in sorted(neighbors.get(node, ())):
                if nb not in nodes:
                    nodes.add(nb)
                    queue.append((nb, depth + 1))
        nodes = list(sorted(nodes))
        node_pos = {n: i for i, n in enumerate(nodes)}
        keep = [i for i, (u, v) in enumerate(zip(src.tolist(), dst.tolist())) if u in nodes and v in nodes]
        if not keep:
            continue
        sub_edge_index = []
        for i in keep:
            u = src[i]; v = dst[i]
            sub_edge_index.append([node_pos[int(u)], node_pos[int(v)]])
        sub_edge_index = torch.tensor(sub_edge_index, dtype=torch.long).T if sub_edge_index else torch.empty((2, 0), dtype=torch.long)
        sub_edge_attr = graph.edge_attr[keep].float()
        if sub_edge_attr.shape[0] != sub_edge_index.shape[1]:
            continue
        input_end_idx = ts_idx - 1
        window_times = times[input_end_idx - 12 + 1 : input_end_idx + 1]
        x_seq = np.zeros((12, len(nodes), len(FEATURE_COLS_16)), dtype=np.float32)
        for t_i, w_ts in enumerate(window_times):
            for n_i, node in enumerate(nodes):
                x_seq[t_i, n_i, :] = feature_lookup.get((w_ts, int(node)), 0.0)
        if not np.any(x_seq):
            continue
        with torch.no_grad():
            pred = model(x_seq=torch.from_numpy(x_seq).unsqueeze(0), edge_index=sub_edge_index, edge_attr=sub_edge_attr)[0, node_pos[int(center_idx)]]
        pred_value = float(pred.detach().cpu().item())
        target_idx = input_end_idx + 1
        if target_idx >= len(times):
            continue
        target_ts = times[target_idx]
        target_row = df[(df['timestamp'] == target_ts) & (df['node_index'] == center_idx)]
        if target_row.empty:
            continue
        target_value = float(target_row['target_scaled'].iloc[0])

        # raw prediction (scaled units)
        preds_raw.append(pred_value)

        # apply per-node scaler if exists
        node_id = nodeidx_to_nodeid.get(center_idx, center_idx)
        s = scalers.get(str(node_id))
        if s and int(s.get('n', 0)) >= 3:
            a = float(s.get('a', 1.0))
            b = float(s.get('b', 0.0))
            adj = a * pred_value + (b / TARGET_SCALE)
        else:
            adj = pred_value
        preds_scaled.append(adj)
        targets.append(target_value)

    preds_raw = np.asarray(preds_raw, dtype=np.float64)
    preds_scaled = np.asarray(preds_scaled, dtype=np.float64)
    targets = np.asarray(targets, dtype=np.float64)

    def metrics(p, t):
        err = p - t
        mae = float(np.mean(np.abs(err)))
        rmse = float(np.sqrt(np.mean(err * err)))
        return {"mae_scaled": mae, "rmse_scaled": rmse, "mae_ug": mae * TARGET_SCALE, "rmse_ug": rmse * TARGET_SCALE}

    return {"samples": len(targets), "raw": metrics(preds_raw, targets), "scaled": metrics(preds_scaled, targets)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="citywide_stpignn_best.pt")
    parser.add_argument("--graph", default="data/processed/graph/topology_graph_pyg_inference.pt")
    parser.add_argument("--model-input", default="data/processed/model_input/model_input_node_hourly_features.parquet")
    parser.add_argument("--node-map", default="data/processed/graph/topology_nodeid_to_index_map.parquet")
    parser.add_argument("--scalers", default="data/processed/per_zone_scalers.json")
    parser.add_argument("--max-samples", type=int, default=500)
    args = parser.parse_args()

    model, info = load_stpignn_checkpoint(args.model, device=torch.device("cpu"))
    graph = torch.load(args.graph, map_location="cpu", weights_only=False)
    df = _load_model_input(Path(args.model_input), Path(args.node_map))

    with open(args.scalers) as fh:
        scalers = json.load(fh)

    res = fit_and_eval(model, graph, df, Path(args.node_map), scalers, max_samples=args.max_samples)
    outp = Path('docs/eval_scaler_comparison.json')
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(json.dumps(res, indent=2) + "\n")
    print(json.dumps(res, indent=2))
