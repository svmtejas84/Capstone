"""W2 residual station models with wind-conditioned edges and structured transport."""
from __future__ import annotations

import torch
from torch import nn
from torch.nn import functional as F
from torch_geometric.nn import GINEConv

from src.stpignn.models_v2 import expanded_edges


class GineGRUWind(nn.Module):
    def __init__(self, inputs: int, hidden: int):
        super().__init__()
        self.gru = nn.GRU(inputs, hidden, batch_first=True)
        self.gine = GINEConv(nn.Sequential(nn.Linear(hidden, hidden), nn.ReLU(),
                                           nn.Linear(hidden, hidden)), edge_dim=2)
        self.head = nn.Linear(hidden, 1)

    def encode(self, x, edge_index, edge_attr, wind_along):
        b, t, n, f = x.shape
        seq = x.permute(0, 2, 1, 3).reshape(b * n, t, f)
        hidden = self.gru(seq)[0][:, -1]
        edge = expanded_edges(edge_index, n, b)
        attrs = torch.stack((edge_attr[:, 0][None, :].expand(b, -1), wind_along), -1).reshape(-1, 2)
        return F.relu(self.gine(hidden, edge, attrs)).reshape(b, n, -1)

    def forward(self, x, edge_index, edge_attr, wind_along, anchor_z=None):
        return self.head(self.encode(x, edge_index, edge_attr, wind_along)).squeeze(-1)


class AdaptiveGraphST(nn.Module):
    def __init__(self, inputs: int, hidden: int, nodes: int, fixed_knn: bool = False):
        super().__init__()
        self.temporal = nn.Sequential(nn.Conv1d(inputs, hidden, 3, padding=2, dilation=2),
                                      nn.ReLU(), nn.Conv1d(hidden, hidden, 3, padding=4, dilation=4), nn.ReLU())
        self.node_emb = nn.Parameter(torch.randn(nodes, min(hidden, 16)) * 0.1)
        self.wind_gain = nn.Parameter(torch.tensor(0.1))
        self.head = nn.Sequential(nn.Linear(2 * hidden, hidden), nn.ReLU(), nn.Linear(hidden, 1))
        self.fixed_knn = fixed_knn

    def forward(self, x, edge_index, edge_attr, wind_along, anchor_z=None):
        b, t, n, f = x.shape
        seq = x.permute(0, 2, 3, 1).reshape(b * n, f, t)
        h = self.temporal(seq)[..., -1].reshape(b, n, -1)
        if self.fixed_knn:
            adjacency = h.new_zeros(n, n)
            adjacency[edge_index[1], edge_index[0]] = 1.0
            adjacency = adjacency / adjacency.sum(-1, keepdim=True).clamp_min(1.0)
            adjacency = adjacency[None].expand(b, -1, -1)
        else:
            logits = self.node_emb @ self.node_emb.T
            adjacency = logits[None].expand(b, -1, -1).clone()
        wind_gate = h.new_zeros(b, n, n)
        wind_gate[:, edge_index[1], edge_index[0]] = wind_along
        if self.fixed_knn:
            gated = adjacency * torch.sigmoid(self.wind_gain * wind_gate)
            adjacency = gated / gated.sum(-1, keepdim=True).clamp_min(1e-8)
        else:
            adjacency = torch.softmax(adjacency + self.wind_gain * wind_gate, dim=-1)
        spatial = torch.bmm(adjacency, h)
        return self.head(torch.cat((h, spatial), -1)).squeeze(-1)


class AdvDiffSource(nn.Module):
    def __init__(self, inputs: int, hidden: int, target_mean: float, target_sd: float,
                 source_removed: bool = False, transport_removed: bool = False):
        super().__init__()
        self.backbone = GineGRUWind(inputs, hidden)
        self.diffusion_raw = nn.Parameter(torch.tensor(-3.0))
        self.source_net = nn.Sequential(nn.Linear(inputs - 5, hidden), nn.ReLU(),
                                        nn.Linear(hidden, 1))
        self.source_removed = source_removed
        self.transport_removed = transport_removed
        self.target_mean = target_mean
        self.target_sd = target_sd
        self.last_diffusion = None
        self.last_source_mean = None

    def forward(self, x, edge_index, edge_attr, wind_along, anchor_z=None):
        residual = self.backbone(x, edge_index, edge_attr, wind_along)
        if self.transport_removed:
            return residual
        if anchor_z is None:
            raise ValueError("Transport requires a causal persistence anchor")
        source, dest = edge_index
        physical = torch.expm1(anchor_z * self.target_sd + self.target_mean).clamp_min(0)
        difference = physical[:, source] - physical[:, dest]
        upwind = F.relu(wind_along)
        diffusion = F.softplus(self.diffusion_raw)
        length = torch.expm1(edge_attr[:, 0]).clamp_min(1.0)
        edge_flux = (upwind + diffusion) * difference / (1.0 + length[None, :] / 1000.0)
        summed = physical.new_zeros(physical.shape).index_add(1, dest, edge_flux)
        counts = physical.new_zeros(physical.shape).index_add(1, dest,
                                                              torch.ones_like(edge_flux))
        transport = summed / counts.clamp_min(1.0)
        if self.source_removed:
            source_term = torch.zeros_like(transport)
        else:
            source_term = F.softplus(self.source_net(x[:, -1, :, 5:]).squeeze(-1))
        structured = torch.log1p((physical + transport + source_term).clamp_min(0))
        self.last_diffusion = diffusion.detach()
        self.last_source_mean = source_term.mean().detach()
        return residual + (structured - (anchor_z * self.target_sd + self.target_mean)) / self.target_sd


def make_model_v3(name: str, inputs: int, hidden: int, nodes: int,
                  target_mean: float, target_sd: float):
    if name == "gine_gru_wind":
        return GineGRUWind(inputs, hidden)
    if name == "adaptive_graph_st":
        return AdaptiveGraphST(inputs, hidden, nodes)
    if name == "adaptive_graph_st_fixed_knn":
        return AdaptiveGraphST(inputs, hidden, nodes, fixed_knn=True)
    if name in ("stpignn_v2", "stpignn_v2_source_removed", "stpignn_v2_transport_removed"):
        return AdvDiffSource(inputs, hidden, target_mean, target_sd,
                             source_removed=name.endswith("source_removed"),
                             transport_removed=name.endswith("transport_removed"))
    raise ValueError(name)
