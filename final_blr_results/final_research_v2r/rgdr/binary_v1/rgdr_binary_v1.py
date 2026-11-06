"""Reliability-gated variant of the existing directed station penalty.

This component does not claim a conservative physical law. Inputs must be
cutoff-eligible; the caller remains responsible for data/target separation.
"""
from __future__ import annotations

import torch
import torch.nn.functional as F


def observation_reliability(lag_is_imputed: torch.Tensor) -> torch.Tensor:
    """Binary cutoff observation indicator: 1 only for an observed immediate lag."""
    if lag_is_imputed.ndim != 2:
        raise ValueError("lag_is_imputed must be [batch,nodes]")
    if not torch.isfinite(lag_is_imputed).all():
        raise ValueError("nonfinite missingness flag")
    if not torch.all((lag_is_imputed == 0) | (lag_is_imputed == 1)):
        raise ValueError("missingness flag must be binary")
    return 1.0 - lag_is_imputed.to(torch.float32)


def edge_reliability(node_reliability: torch.Tensor, edge_index: torch.Tensor) -> torch.Tensor:
    """Endpoint product; the directional mask is a separate input."""
    if node_reliability.ndim != 2 or edge_index.shape[0] != 2:
        raise ValueError("expected reliability [B,N] and edge_index [2,E]")
    if not torch.isfinite(node_reliability).all() or torch.any((node_reliability < 0) | (node_reliability > 1)):
        raise ValueError("reliability must be finite in [0,1]")
    src, dst = edge_index
    return node_reliability[:, src] * node_reliability[:, dst]


def rgdr_penalty(pred_norm: torch.Tensor, edge_index: torch.Tensor, wind_mask: torch.Tensor,
                 edge_attr: torch.Tensor, node_reliability: torch.Tensor) -> torch.Tensor:
    """Masked, reliability-weighted original hinge with identical geometry."""
    if pred_norm.ndim != 2 or wind_mask.ndim != 2 or node_reliability.shape != pred_norm.shape:
        raise ValueError("expected prediction/reliability [B,N] and mask [B,E]")
    if edge_index.shape != (2, wind_mask.shape[1]) or wind_mask.shape[0] != pred_norm.shape[0]:
        raise ValueError("edge/mask shape mismatch")
    if edge_attr.ndim != 2 or edge_attr.shape[0] != edge_index.shape[1] or edge_attr.shape[1] < 1:
        raise ValueError("edge_attr requires edge length in first channel")
    if not torch.isfinite(pred_norm).all() or not torch.isfinite(edge_attr[:, 0]).all():
        raise ValueError("nonfinite prediction or length")
    if torch.any(edge_attr[:, 0] < 0):
        raise ValueError("negative edge length")
    src, dst = edge_index
    if len(src) == 0:
        return pred_norm.sum() * 0.0
    r = edge_reliability(node_reliability, edge_index)
    weights = wind_mask.to(pred_norm.dtype) * r.to(pred_norm.dtype)
    geometry = torch.sigmoid(edge_attr[:, 0] / 1000.0)
    diff = pred_norm[:, dst] - pred_norm[:, src]
    hinge = F.relu(diff * geometry[None, :]).square()
    return (weights * hinge).sum() / weights.sum().clamp_min(1.0)


def reliability_weighted_smoothing(pred_norm: torch.Tensor, edge_index: torch.Tensor,
                                   edge_attr: torch.Tensor, node_reliability: torch.Tensor) -> torch.Tensor:
    """Symmetric, non-directional comparator using the same reliability/geometry."""
    if pred_norm.ndim != 2 or node_reliability.shape != pred_norm.shape:
        raise ValueError("expected [B,N] prediction and reliability")
    src, dst = edge_index
    if len(src) == 0:
        return pred_norm.sum() * 0.0
    if edge_attr.ndim != 2 or edge_attr.shape[0] != len(src) or edge_attr.shape[1] < 1:
        raise ValueError("bad edge attributes")
    r = edge_reliability(node_reliability, edge_index).to(pred_norm.dtype)
    geometry = torch.sigmoid(edge_attr[:, 0] / 1000.0)
    diff = (pred_norm[:, dst] - pred_norm[:, src]) * geometry[None, :]
    return (r * diff.square()).sum() / r.sum().clamp_min(1.0)
