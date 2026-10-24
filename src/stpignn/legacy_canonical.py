"""Pure ports of the audited notebook's dataset, mask, loss, and scoring rules.

The original functions are in evaluated_wind_advection.ipynb cells 7, 9, 13.
The explicit arguments here replace notebook global variables without changing
the calculations. This module preserves historical behavior for audit parity;
future corrected experiments need new, explicit policies.
"""
from __future__ import annotations

import numpy as np
import torch
import torch.nn.functional as F
from torch.utils.data import Dataset
from torch import nn
from torch_geometric.nn import GCNConv


class SpatialPartition:
    """Notebook cell 2 partition container, retained for checkpoint audit."""

    def __init__(self, cid, node_ids, edge_index, edge_attr, train_mask):
        self.cid = int(cid)
        self.n_id = torch.as_tensor(node_ids, dtype=torch.long)
        self.edge_index = edge_index.long()
        self.edge_attr = edge_attr.float()
        self.train_mask = train_mask.bool()
        self.val_mask = None
        self.upwind_edge_mask = torch.zeros(edge_index.shape[1], dtype=torch.bool)
        self.x = None


def compute_dynamic_upwind_mask_vectorized(edge_bearings, current_wind_dir_deg, cone_angle_deg=75.0):
    if edge_bearings.numel() == 0:
        return torch.zeros(0, dtype=torch.bool, device=edge_bearings.device)
    reverse_bearings = (edge_bearings + 180.0) % 360.0
    angular_diff = torch.abs(reverse_bearings - current_wind_dir_deg)
    angular_diff = torch.minimum(angular_diff, 360.0 - angular_diff)
    return angular_diff <= (cone_angle_deg / 2.0)


def compute_wind_advection_penalty(pred, edge_index, upwind_edge_mask, edge_attr):
    if edge_index.shape[1] == 0 or not upwind_edge_mask.any():
        return pred.new_tensor(0.0)
    row, col = edge_index
    spatial_diff = pred[col[upwind_edge_mask]] - pred[row[upwind_edge_mask]]
    if edge_attr is not None and edge_attr.shape[0] == edge_index.shape[1]:
        normalized_attr = edge_attr[upwind_edge_mask] / 1000.0
        resistance = torch.sigmoid(normalized_attr.sum(dim=-1))
        spatial_diff = spatial_diff * resistance
    return torch.mean(F.relu(spatial_diff) ** 2)


def scored_mask(target, graph_sensor_mask):
    return graph_sensor_mask.bool().view(-1) & (torch.abs(target.view(-1)) > 1e-8)


def masked_mae_rmse_vectorized(pred, target, mask):
    pred_1d = pred.view(-1)
    target_1d = target.view(-1)
    mask_1d = mask.view(-1)
    if not mask_1d.any():
        zero_tensor = pred.new_tensor(0.0)
        return zero_tensor, zero_tensor
    errors = pred_1d[mask_1d] - target_1d[mask_1d]
    return torch.mean(torch.abs(errors)), torch.sqrt(torch.mean(errors * errors))


def legacy_global_metrics(preds, targets, target_scale):
    """Notebook cell 24 pair-weighted statistics, without side effects."""
    p = torch.cat(preds).numpy() * target_scale
    t = torch.cat(targets).numpy() * target_scale
    error = p - t
    return p, t, float(np.mean(np.abs(error))), float(np.sqrt(np.mean(error ** 2))), float(np.median(np.abs(error)))


class VanillaGCN(nn.Module):
    """Notebook cell 22 baseline architecture; training is external."""

    def __init__(self, in_channels, hidden_dim, out_channels=1):
        super().__init__()
        self.conv1 = GCNConv(in_channels, hidden_dim)
        self.conv2 = GCNConv(hidden_dim, hidden_dim)
        self.regression_head = nn.Linear(hidden_dim, out_channels)

    def forward(self, x_seq, edge_index, edge_attr=None):
        x = x_seq.squeeze(0)[-1]
        x = torch.relu(self.conv1(x, edge_index))
        x = torch.relu(self.conv2(x, edge_index))
        return self.regression_head(x)


class ST_GRUGCN(nn.Module):
    """Notebook cell 22 baseline architecture; training is external."""

    def __init__(self, in_channels, hidden_dim, out_channels=1):
        super().__init__()
        self.spatial_conv = GCNConv(in_channels, hidden_dim)
        self.gru = nn.GRUCell(hidden_dim, hidden_dim)
        self.regression_head = nn.Linear(hidden_dim, out_channels)
        self.hidden_dim = hidden_dim

    def forward(self, x_seq, edge_index, edge_attr=None):
        x_seq = x_seq.squeeze(0)
        steps, nodes, _ = x_seq.shape
        h = torch.zeros(nodes, self.hidden_dim, device=x_seq.device)
        for t in range(steps):
            spatial_feats = torch.relu(self.spatial_conv(x_seq[t], edge_index))
            h = self.gru(spatial_feats, h)
        return self.regression_head(h)


class TierAwareClusterDatasetV3(Dataset):
    """Cell 9 dataset with source arrays passed explicitly instead of globals."""

    def __init__(self, clusters, t0, t1, time_count, time_breaks, raw_node_indices,
                 raw_targets, window=12, stride=128, phys_time_subsample=8):
        self.clusters = clusters
        self.window = int(window)
        self.starts = list(range(int(t0), min(int(t1), time_count) - self.window, int(stride)))
        self.cluster_global = [np.asarray(c.n_id.cpu().numpy(), dtype=np.int64) for c in clusters]
        self.cluster_has_sensor = [bool(c.train_mask.any()) for c in clusters]
        self.phys_time_subsample = max(1, int(phys_time_subsample))
        self.time_breaks = time_breaks
        self.raw_node_indices = raw_node_indices
        self.raw_targets = raw_targets
        self.samples = []
        for c_idx, n_ids in enumerate(self.cluster_global):
            has_sensor = self.cluster_has_sensor[c_idx]
            if has_sensor:
                for t_start in self.starts:
                    target_overlap = False
                    t_eval = t_start + self.window - 1
                    if t_eval < len(time_breaks) - 1:
                        s_ptr = time_breaks[t_eval]
                        e_ptr = time_breaks[t_eval + 1]
                        if e_ptr > s_ptr:
                            t_nodes = raw_node_indices[s_ptr:e_ptr]
                            if np.isin(t_nodes, n_ids, assume_unique=False).any():
                                target_overlap = True
                    if target_overlap:
                        self.samples.append((c_idx, t_start, "station"))
            else:
                for k, t_start in enumerate(self.starts):
                    if (k % self.phys_time_subsample) == 0:
                        self.samples.append((c_idx, t_start, "phys"))
        if len(self.samples) == 0:
            raise RuntimeError("Data compilation failed: Zero active tiered windows matched bounds.")

    def __len__(self):
        return len(self.samples)

    def __getitems__(self, indices):
        return [self.__getitem__(idx) for idx in indices]

    def __getitem__(self, idx):
        c_idx, t0, mode = self.samples[idx]
        part = self.clusters[c_idx]
        n_ids = self.cluster_global[c_idx]
        num_nodes = n_ids.shape[0]
        x_win = np.zeros((self.window, num_nodes, 16), dtype=np.float32)
        y_win = np.zeros((num_nodes,), dtype=np.float32)
        for w in range(self.window):
            t_curr = t0 + w
            for local_i, global_node_id in enumerate(n_ids.tolist()):
                node_registry = part.global_feature_registry[global_node_id]
                x_win[w, local_i, :] = node_registry[t_curr % node_registry.shape[0]].numpy()
            if mode == "station" and w == self.window - 1:
                t_target_safe = t_curr if t_curr < len(self.time_breaks) - 1 else (len(self.time_breaks) - 2)
                s_ptr = self.time_breaks[t_target_safe]
                e_ptr = self.time_breaks[t_target_safe + 1]
                if e_ptr > s_ptr:
                    t_nodes = self.raw_node_indices[s_ptr:e_ptr]
                    t_vals = self.raw_targets[s_ptr:e_ptr]
                    member = np.isin(t_nodes, n_ids, assume_unique=False)
                    if np.any(member):
                        g_sel = t_nodes[member]
                        loc = np.searchsorted(n_ids, g_sel)
                        ok = (loc >= 0) & (loc < num_nodes) & (n_ids[loc] == g_sel)
                        if np.any(ok):
                            y_win[loc[ok]] = t_vals[member][ok]
        return torch.from_numpy(x_win), torch.from_numpy(y_win), c_idx, int(t0)
