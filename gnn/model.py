from __future__ import annotations

from dataclasses import dataclass

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.amp import GradScaler, autocast
from torch_geometric.nn import GINEConv

from gnn.plume_physics import dispersion_sigmas, gaussian_plume
from shared.physics_config import PHYSICS_LOSS_LAMBDA


@dataclass
class LossBreakdown:
    total: torch.Tensor
    data: torch.Tensor
    physics: torch.Tensor


class STPIGNN(nn.Module):
    """Spatio-Temporal Physics-Informed GNN with GINE + GRU backbone."""

    def __init__(
        self,
        node_in_dim: int,
        edge_dim: int,
        spatial_hidden_dim: int = 128,
        temporal_hidden_dim: int = 128,
        gnn_layers: int = 2,
        gru_layers: int = 1,
        dropout: float = 0.1,
    ) -> None:
        super().__init__()
        if node_in_dim <= 0 or edge_dim <= 0:
            raise ValueError("node_in_dim and edge_dim must be positive")

        self.node_encoder = nn.Linear(node_in_dim, spatial_hidden_dim)

        self.gnn_layers = nn.ModuleList()
        self.norms = nn.ModuleList()
        for _ in range(gnn_layers):
            mlp = nn.Sequential(
                nn.Linear(spatial_hidden_dim, spatial_hidden_dim),
                nn.ReLU(),
                nn.Linear(spatial_hidden_dim, spatial_hidden_dim),
            )
            self.gnn_layers.append(GINEConv(nn=mlp, edge_dim=edge_dim))
            self.norms.append(nn.LayerNorm(spatial_hidden_dim))

        self.gru = nn.GRU(
            input_size=spatial_hidden_dim,
            hidden_size=temporal_hidden_dim,
            num_layers=gru_layers,
            dropout=dropout if gru_layers > 1 else 0.0,
            batch_first=True,
        )

        self.dropout = nn.Dropout(dropout)
        self.head = nn.Linear(temporal_hidden_dim, 1)

    @staticmethod
    def _expand_edge_index_for_batch(edge_index: torch.Tensor, num_nodes: int, batch_size: int) -> torch.Tensor:
        if batch_size == 1:
            return edge_index
        offsets = torch.arange(batch_size, device=edge_index.device, dtype=edge_index.dtype) * num_nodes
        expanded = edge_index.unsqueeze(0) + offsets.view(-1, 1, 1)
        return expanded.permute(1, 0, 2).reshape(2, -1)

    def _spatial_encode(
        self,
        x_t: torch.Tensor,
        edge_index: torch.Tensor,
        edge_attr: torch.Tensor,
    ) -> torch.Tensor:
        """
        Args:
            x_t: [B, N, F]
            edge_index: [2, E]
            edge_attr: [E, D]

        Returns:
            Tensor [B, N, H]
        """
        bsz, num_nodes, _ = x_t.shape
        x = self.node_encoder(x_t).reshape(bsz * num_nodes, -1)

        batch_edge_index = self._expand_edge_index_for_batch(edge_index, num_nodes, bsz)
        if bsz == 1:
            batch_edge_attr = edge_attr
        else:
            batch_edge_attr = edge_attr.repeat(bsz, 1)

        for conv, norm in zip(self.gnn_layers, self.norms):
            residual = x
            x = conv(x, batch_edge_index, batch_edge_attr)
            x = norm(x)
            x = F.relu(x)
            x = self.dropout(x)
            x = x + residual

        return x.reshape(bsz, num_nodes, -1)

    def forward(
        self,
        x_seq: torch.Tensor,
        edge_index: torch.Tensor,
        edge_attr: torch.Tensor,
    ) -> torch.Tensor:
        """
        Args:
            x_seq: [B, T, N, F] or [T, N, F]
            edge_index: [2, E]
            edge_attr: [E, D]

        Returns:
            PM2.5 prediction at next step: [B, N]
        """
        if x_seq.dim() == 3:
            x_seq = x_seq.unsqueeze(0)
        if x_seq.dim() != 4:
            raise ValueError("x_seq must have shape [B, T, N, F] or [T, N, F]")

        bsz, seq_len, num_nodes, _ = x_seq.shape
        spatial_steps: list[torch.Tensor] = []
        for t in range(seq_len):
            step_emb = self._spatial_encode(x_seq[:, t, :, :], edge_index=edge_index, edge_attr=edge_attr)
            spatial_steps.append(step_emb)

        spatial_seq = torch.stack(spatial_steps, dim=1)  # [B, T, N, H]
        spatial_seq = spatial_seq.permute(0, 2, 1, 3).reshape(bsz * num_nodes, seq_len, -1)  # [B*N, T, H]

        gru_out, _ = self.gru(spatial_seq)
        last_h = gru_out[:, -1, :]
        pred = self.head(self.dropout(last_h)).reshape(bsz, num_nodes)
        return pred


def masked_data_loss(pred: torch.Tensor, target: torch.Tensor, train_mask: torch.Tensor) -> torch.Tensor:
    """MSE computed only on masked (sensor) nodes."""
    if pred.shape != target.shape:
        raise ValueError(f"pred and target shapes must match. Got {pred.shape} vs {target.shape}")

    if train_mask.dtype != torch.bool:
        train_mask = train_mask.bool()

    if train_mask.dim() == 1:
        train_mask = train_mask.unsqueeze(0).expand_as(pred)
    elif train_mask.shape != pred.shape:
        raise ValueError(f"train_mask shape {train_mask.shape} is incompatible with prediction shape {pred.shape}")

    if int(train_mask.sum().item()) == 0:
        raise ValueError("train_mask selects no nodes; cannot compute data loss")

    return F.mse_loss(pred[train_mask], target[train_mask])


def physics_upwind_penalty(
    pred: torch.Tensor,
    edge_index: torch.Tensor,
    upwind_edge_mask: torch.Tensor,
    edge_attr: torch.Tensor | None = None,
    wind_speed: float = 2.0,
    margin: float = 0.0,
) -> torch.Tensor:
    """
    Penalize cases where upwind node concentration exceeds its paired node.

    Convention:
    - upwind_edge_mask marks edges (u -> v) where v is upwind relative to u.
    - Penalized term: relu(pred[v] - pred[u] - margin).
    """
    if pred.dim() == 1:
        pred = pred.unsqueeze(0)
    if pred.dim() != 2:
        raise ValueError("pred must have shape [N] or [B, N]")

    if upwind_edge_mask.dtype != torch.bool:
        upwind_edge_mask = upwind_edge_mask.bool()

    if upwind_edge_mask.numel() != edge_index.shape[1]:
        raise ValueError("upwind_edge_mask length must match number of edges")

    if int(upwind_edge_mask.sum().item()) == 0:
        return pred.new_tensor(0.0)

    src = edge_index[0, upwind_edge_mask]
    dst = edge_index[1, upwind_edge_mask]

    src_pred = pred[:, src]
    dst_pred = pred[:, dst]
    violation = F.relu(dst_pred - src_pred - margin)

    edge_weights = pred.new_ones(src.shape[0])
    if edge_attr is not None and edge_attr.numel() > 0:
        selected_attr = edge_attr[upwind_edge_mask]
        if selected_attr.dim() == 2 and selected_attr.shape[1] >= 1:
            lengths = selected_attr[:, 0].detach().to("cpu").float().numpy()
            plume_vals: list[float] = []
            for length_m in lengths:
                sigma_y, sigma_z = dispersion_sigmas(float(max(1.0, length_m)))
                plume_vals.append(
                    gaussian_plume(
                        q=1.0,
                        x_downwind_m=float(max(1.0, length_m)),
                        y_crosswind_m=0.0,
                        wind_speed=max(0.2, float(wind_speed)),
                        sigma_y=sigma_y,
                        sigma_z=sigma_z,
                    )
                )
            plume_tensor = torch.tensor(plume_vals, dtype=pred.dtype, device=pred.device)
            max_val = plume_tensor.max().clamp(min=1e-8)
            edge_weights = 1.0 + plume_tensor / max_val

    return ((violation ** 2) * edge_weights.unsqueeze(0)).mean()


def compute_total_loss(
    pred: torch.Tensor,
    target: torch.Tensor,
    train_mask: torch.Tensor,
    edge_index: torch.Tensor,
    edge_attr: torch.Tensor | None = None,
    upwind_edge_mask: torch.Tensor | None = None,
    physics_lambda: float = PHYSICS_LOSS_LAMBDA,
) -> LossBreakdown:
    data_loss = masked_data_loss(pred=pred, target=target, train_mask=train_mask)

    if upwind_edge_mask is None:
        physics_loss = pred.new_tensor(0.0)
    else:
        physics_loss = physics_upwind_penalty(
            pred=pred,
            edge_index=edge_index,
            upwind_edge_mask=upwind_edge_mask,
            edge_attr=edge_attr,
        )

    total = data_loss + physics_lambda * physics_loss
    return LossBreakdown(total=total, data=data_loss, physics=physics_loss)


def train_step_amp(
    model: STPIGNN,
    optimizer: torch.optim.Optimizer,
    x_seq: torch.Tensor,
    target: torch.Tensor,
    edge_index: torch.Tensor,
    edge_attr: torch.Tensor,
    train_mask: torch.Tensor,
    upwind_edge_mask: torch.Tensor | None,
    device: torch.device,
    scaler: GradScaler,
    physics_lambda: float = PHYSICS_LOSS_LAMBDA,
) -> dict[str, float]:
    """Single AMP-enabled optimization step for V100/Tensor Core training."""
    model.train()
    optimizer.zero_grad(set_to_none=True)

    x_seq = x_seq.to(device)
    target = target.to(device)
    edge_index = edge_index.to(device)
    edge_attr = edge_attr.to(device)
    train_mask = train_mask.to(device)
    if upwind_edge_mask is not None:
        upwind_edge_mask = upwind_edge_mask.to(device)

    amp_enabled = device.type == "cuda"
    with autocast(device_type=device.type, enabled=amp_enabled):
        pred = model(x_seq=x_seq, edge_index=edge_index, edge_attr=edge_attr)
        losses = compute_total_loss(
            pred=pred,
            target=target,
            train_mask=train_mask,
            edge_index=edge_index,
            edge_attr=edge_attr,
            upwind_edge_mask=upwind_edge_mask,
            physics_lambda=physics_lambda,
        )

    scaler.scale(losses.total).backward()
    scaler.step(optimizer)
    scaler.update()

    return {
        "loss_total": float(losses.total.detach().item()),
        "loss_data": float(losses.data.detach().item()),
        "loss_physics": float(losses.physics.detach().item()),
    }
