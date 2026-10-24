"""Batch-capable, trained baselines sharing the data_v2 information set."""
import torch
from torch import nn
from torch_geometric.nn import GCNConv

from gnn.model import STPIGNN


def expanded_edges(edge_index, nodes, batches):
    if batches == 1:
        return edge_index
    offsets = torch.arange(batches, device=edge_index.device) * nodes
    return (edge_index[:, None, :] + offsets[None, :, None]).reshape(2, -1)


class VanillaGCNV2(nn.Module):
    def __init__(self, inputs, hidden):
        super().__init__()
        self.conv1 = GCNConv(inputs, hidden)
        self.conv2 = GCNConv(hidden, hidden)
        self.head = nn.Linear(hidden, 1)

    def forward(self, x_seq, edge_index, edge_attr=None):
        batch, _, nodes, channels = x_seq.shape
        edge = expanded_edges(edge_index, nodes, batch)
        x = x_seq[:, -1].reshape(batch * nodes, channels)
        x = torch.relu(self.conv1(x, edge))
        x = torch.relu(self.conv2(x, edge))
        return self.head(x).reshape(batch, nodes)


class STGRUGCNV2(nn.Module):
    def __init__(self, inputs, hidden):
        super().__init__()
        self.spatial = GCNConv(inputs, hidden)
        self.gru = nn.GRUCell(hidden, hidden)
        self.head = nn.Linear(hidden, 1)
        self.hidden = hidden

    def forward(self, x_seq, edge_index, edge_attr=None):
        batch, steps, nodes, channels = x_seq.shape
        edge = expanded_edges(edge_index, nodes, batch)
        state = x_seq.new_zeros(batch * nodes, self.hidden)
        for t in range(steps):
            spatial = torch.relu(self.spatial(x_seq[:, t].reshape(batch * nodes, channels), edge))
            state = self.gru(spatial, state)
        return self.head(state).reshape(batch, nodes)


class GRUOnlyV2(nn.Module):
    def __init__(self, inputs, hidden):
        super().__init__()
        self.gru = nn.GRU(inputs, hidden, batch_first=True)
        self.head = nn.Linear(hidden, 1)

    def forward(self, x_seq, edge_index=None, edge_attr=None):
        batch, steps, nodes, channels = x_seq.shape
        seq = x_seq.permute(0, 2, 1, 3).reshape(batch * nodes, steps, channels)
        encoded, _ = self.gru(seq)
        return self.head(encoded[:, -1]).reshape(batch, nodes)


def make_model(name, inputs, hidden, edge_dim):
    if name == "vanilla_gcn":
        return VanillaGCNV2(inputs, hidden)
    if name == "st_gru_gcn":
        return STGRUGCNV2(inputs, hidden)
    if name == "gru_only":
        return GRUOnlyV2(inputs, hidden)
    if name.startswith("stpignn_"):
        return STPIGNN(inputs, edge_dim, hidden, hidden, gnn_layers=2)
    raise ValueError(name)
