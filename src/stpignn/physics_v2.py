"""Advection masks and auditable penalty variants in physical units."""
from __future__ import annotations

import numpy as np
import torch
import torch.nn.functional as F

from .legacy_canonical import compute_wind_advection_penalty


class MissingTrafficIndex(ValueError):
    pass


def compass_bearing_degrees(source_xy: torch.Tensor, destination_xy: torch.Tensor) -> torch.Tensor:
    """UTM source->destination bearing clockwise from true north."""
    delta = destination_xy - source_xy
    return torch.remainder(torch.rad2deg(torch.atan2(delta[..., 0], delta[..., 1])) + 360.0, 360.0)


def angular_distance_degrees(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    delta = torch.remainder(torch.abs(a - b), 360.0)
    return torch.minimum(delta, 360.0 - delta)


def corrected_wind_mask(coordinates_xy: torch.Tensor, edge_index: torch.Tensor,
                        wind_from_degrees: torch.Tensor | float, half_angle_degrees: float = 37.5) -> torch.Tensor:
    """Wind FROM west (270°) transports east and selects eastbound edges."""
    src, dst = edge_index
    bearings = compass_bearing_degrees(coordinates_xy[src], coordinates_xy[dst])
    wind = torch.as_tensor(wind_from_degrees, dtype=bearings.dtype, device=bearings.device)
    transport_to = torch.remainder(wind + 180.0, 360.0)
    return angular_distance_degrees(bearings, transport_to) <= half_angle_degrees


def legacy_wind_mask(coordinates_xy: torch.Tensor, edge_index: torch.Tensor,
                     scaled_wind_direction: torch.Tensor | float, cone_angle_degrees: float = 75.0) -> torch.Tensor:
    src, dst = edge_index
    delta = coordinates_xy[dst] - coordinates_xy[src]
    math_bearing = torch.remainder(torch.rad2deg(torch.atan2(delta[:, 1], delta[:, 0])) + 360.0, 360.0)
    reverse = torch.remainder(math_bearing + 180.0, 360.0)
    wind = torch.as_tensor(scaled_wind_direction, dtype=reverse.dtype, device=reverse.device)
    return angular_distance_degrees(reverse, wind) <= cone_angle_degrees / 2


def emission_margin_normalized(traffic_index: torch.Tensor | None, coefficient_ug_m3: torch.Tensor | float,
                               target_scale_ug_m3: float) -> torch.Tensor:
    """Q_norm = traffic index (unitless) * coefficient (µg/m³/index) / target scale."""
    if traffic_index is None:
        raise MissingTrafficIndex("Corrected Q requires measured traffic_index; source is absent")
    coefficient = torch.as_tensor(coefficient_ug_m3, dtype=traffic_index.dtype, device=traffic_index.device)
    return coefficient.clamp(min=0) * traffic_index.clamp(min=0) / float(target_scale_ug_m3)


def penalty(pred_norm: torch.Tensor, edge_index: torch.Tensor, mask: torch.Tensor,
            edge_attr: torch.Tensor, variant: str, traffic_index: torch.Tensor | None = None,
            q_coefficient_ug_m3: torch.Tensor | float = 0.0, target_scale_ug_m3: float = 1.0) -> torch.Tensor:
    """Mean squared rectified difference; corrected sigmoid uses edge length only."""
    if variant == "legacy":
        return compute_wind_advection_penalty(pred_norm, edge_index, mask, edge_attr)
    src, dst = edge_index
    if variant == "laplacian":
        return ((pred_norm[dst] - pred_norm[src]) ** 2).mean() if len(src) else pred_norm.new_tensor(0.0)
    if edge_index.shape[1] == 0 or not mask.any():
        return pred_norm.new_tensor(0.0)
    if variant not in {"corrected_mask", "corrected_q"}:
        raise ValueError(variant)
    diff = pred_norm[dst[mask]] - pred_norm[src[mask]]
    if variant == "corrected_q":
        q = emission_margin_normalized(traffic_index[mask] if traffic_index is not None else None,
                                       q_coefficient_ug_m3, target_scale_ug_m3)
        diff = diff - q
    length_km = edge_attr[mask, 0] / 1000.0
    resistance = torch.sigmoid(length_km)
    return torch.mean(F.relu(diff * resistance) ** 2)


def batched_penalty(pred_norm: torch.Tensor, edge_index: torch.Tensor, masks: torch.Tensor,
                    edge_attr: torch.Tensor, variant: str) -> torch.Tensor:
    """Differentiable batch penalty; pred_norm is physical PM2.5 / train target SD."""
    if pred_norm.ndim != 2 or masks.ndim != 2:
        raise ValueError("Expected predictions [B,N] and wind masks [B,E]")
    src, dst = edge_index
    if len(src) == 0:
        return pred_norm.new_tensor(0.0)
    diff = pred_norm[:, dst] - pred_norm[:, src]
    if variant == "laplacian":
        return torch.mean(diff ** 2)
    if variant == "legacy":
        resistance = torch.sigmoid(edge_attr.sum(dim=-1) / 1000.0)
    elif variant == "corrected_mask":
        resistance = torch.sigmoid(edge_attr[:, 0] / 1000.0)
    else:
        raise ValueError(variant)
    masked = F.relu(diff * resistance[None, :]) ** 2
    return (masked * masks.float()).sum() / masks.float().sum().clamp(min=1)


def pvr_statistics(pred_norm: torch.Tensor, edge_index: torch.Tensor, mask: torch.Tensor,
                   target_scale_ug_m3: float, thresholds=(0.0, 0.01, 0.05, 0.1),
                   q_norm: torch.Tensor | None = None) -> list[dict]:
    src, dst = edge_index
    diff = pred_norm[dst[mask]] - pred_norm[src[mask]]
    if q_norm is not None:
        diff = diff - q_norm[mask]
    count = int(mask.sum().item())
    out = []
    for threshold in thresholds:
        violations = int((diff > threshold).sum().item())
        out.append({"threshold_normalized": float(threshold),
                    "threshold_ug_m3": float(threshold * target_scale_ug_m3),
                    "active_edges": count, "violations": violations,
                    "pvr_percent": 100 * violations / count if count else None,
                    "with_q": q_norm is not None})
    return out
