from __future__ import annotations

import pandas as pd
import numpy as np
import torch
from pathlib import Path
import sys
from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.generate_calibration_pairs import _load_model_input, FEATURE_COLS_16, TARGET_SCALE
from gnn.checkpoint import load_stpignn_checkpoint

model_input = Path('data/processed/model_input/model_input_node_hourly_features.parquet')
node_map_path = Path('data/processed/graph/topology_nodeid_to_index_map.parquet')
graph_path = Path('data/processed/graph/topology_graph_pyg_inference.pt')
checkpoint = 'citywide_stpignn_best.pt'

print('loading model and data...')
model, info = load_stpignn_checkpoint(checkpoint, device=torch.device('cpu'))
graph = torch.load(str(graph_path), map_location='cpu', weights_only=False)
df = _load_model_input(model_input, node_map_path)

times = pd.Index(sorted(df['timestamp'].unique()))
node_indices = sorted(df['node_index'].unique())
print('times', len(times), 'nodes', len(node_indices))

feature_lookup = {
    (row.timestamp, int(row.node_index)): np.asarray([getattr(row, col) for col in FEATURE_COLS_16], dtype=np.float32)
    for row in df[['timestamp','node_index', *FEATURE_COLS_16]].itertuples(index=False)
}

node_map_df = pd.read_parquet(node_map_path)
idx_to_node = {int(idx): int(nid) for nid, idx in zip(node_map_df['node_id'].values, node_map_df['node_index'].values)}

out_rows = []
window = 12

src = graph.edge_index[0].cpu().numpy()
dst = graph.edge_index[1].cpu().numpy()

for center in node_indices:
    node_times = sorted(df[df['node_index']==center]['timestamp'].unique())
    mids = node_times[window:]
    if not mids:
        continue
    sample_ts = mids[:3]
    for ts in sample_ts:
        ts_idx = times.get_loc(ts)
        input_end_idx = ts_idx - 1
        if input_end_idx - (window-1) < 0:
            continue
        window_times = times[input_end_idx - window + 1: input_end_idx + 1]
        if len(window_times) != window:
            continue
        neighbors = {}
        for u,v in zip(src.tolist(), dst.tolist()):
            neighbors.setdefault(int(u), set()).add(int(v))
            neighbors.setdefault(int(v), set()).add(int(u))
        seen = {int(center)}
        from collections import deque
        queue = deque([(int(center), 0)])
        while queue and len(seen) < 256:
            node, depth = queue.popleft()
            if depth >= 1:
                continue
            for nb in sorted(neighbors.get(node,())):
                if nb not in seen:
                    seen.add(nb)
                    queue.append((nb, depth+1))
        nodes = list(sorted(seen))
        node_pos = {n:i for i,n in enumerate(nodes)}
        keep = [i for i,(u,v) in enumerate(zip(src.tolist(), dst.tolist())) if u in nodes and v in nodes]
        if not keep:
            continue
        sub_edge_index = []
        for i in keep:
            u = src[i]; v = dst[i]
            sub_edge_index.append([node_pos[int(u)], node_pos[int(v)]])
        sub_edge_index = torch.tensor(sub_edge_index, dtype=torch.long).T if sub_edge_index else torch.empty((2,0), dtype=torch.long)
        sub_edge_attr = graph.edge_attr[keep].float()
        if sub_edge_attr.shape[0] != sub_edge_index.shape[1]:
            continue
        x_seq = np.zeros((window, len(nodes), len(FEATURE_COLS_16)), dtype=np.float32)
        for t_i, w_ts in enumerate(window_times):
            for n_i, node in enumerate(nodes):
                x_seq[t_i, n_i, :] = feature_lookup.get((w_ts, int(node)), 0.0)
        if not np.any(x_seq):
            continue
        with torch.no_grad():
            pred = model(x_seq=torch.from_numpy(x_seq).unsqueeze(0), edge_index=sub_edge_index, edge_attr=sub_edge_attr)[0, node_pos[int(center)]]
        pred_value = float(pred.detach().cpu().item())
        target_ts = times[input_end_idx + 1]
        target_row = df[(df['timestamp']==target_ts) & (df['node_index']==center)]
        if target_row.empty:
            continue
        target_value = float(target_row['target_scaled'].iloc[0])
        raw_pred_pm25 = pred_value * TARGET_SCALE
        obs_pm25 = target_value * TARGET_SCALE
        zone_node_id = idx_to_node.get(center, center)
        out_rows.append((str(zone_node_id), raw_pred_pm25, obs_pm25, target_ts.isoformat()))
    if len(out_rows) >= 200:
        break

import csv
with open('data/processed/calibration_pairs_direct.csv','w',newline='') as fh:
    writer = csv.writer(fh)
    writer.writerow(['zone_id','raw_pred','obs','timestamp'])
    for r in out_rows:
        writer.writerow([r[0], f"{r[1]:.6f}", f"{r[2]:.6f}", r[3]])

print('wrote', len(out_rows), 'rows to data/processed/calibration_pairs_direct.csv')
