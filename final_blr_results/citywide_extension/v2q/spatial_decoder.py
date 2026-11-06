"""Forecast-origin station-to-location bridge; no observed target enters forward().

This is an untrained feasibility component. Caller must provide station forecasts
made at a verified common cutoff, with any held-out site removed from support.
"""
from __future__ import annotations

import torch
from torch import nn


def forecast_idw(
    support_xy_m: torch.Tensor,
    support_forecast_ugm3: torch.Tensor,
    query_xy_m: torch.Tensor,
    power: float = 2.0,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Return IDW forecast and nearest-support distance; coordinates must be metres."""
    if support_xy_m.ndim != 2 or query_xy_m.ndim != 2 or support_xy_m.shape[1] != 2 or query_xy_m.shape[1] != 2:
        raise ValueError("coordinates must have shape [N,2] and [Q,2]")
    if support_xy_m.shape[0] < 1 or support_forecast_ugm3.shape != (support_xy_m.shape[0],):
        raise ValueError("at least one aligned support forecast is required")
    if power <= 0 or not all(torch.isfinite(x).all() for x in (support_xy_m, support_forecast_ugm3, query_xy_m)):
        raise ValueError("finite inputs and positive power required")
    distance = torch.cdist(query_xy_m, support_xy_m).clamp_min(0)
    exact = distance == 0
    weight = distance.clamp_min(1.0).pow(-power)
    if exact.any():
        weight = torch.where(exact, torch.ones_like(weight), torch.zeros_like(weight)) * exact.any(dim=1, keepdim=True) + weight * (~exact.any(dim=1, keepdim=True))
    estimate = (weight @ support_forecast_ugm3) / weight.sum(dim=1)
    return estimate, distance.min(dim=1).values


class CompactSpatialDecoder(nn.Module):
    """Small residual to IDW from forecast and verified spatial covariates.

    Inputs include only support *forecasts*, projected coordinates and verified
    elevation. No target, target-hour observations or graph labels are inputs.
    This class intentionally has no scaler fitting or training logic.
    """

    def __init__(self, hidden: int = 32) -> None:
        super().__init__()
        if hidden < 1 or hidden > 32:
            raise ValueError("hidden width must be 1..32")
        self.net = nn.Sequential(nn.Linear(4, hidden), nn.ReLU(), nn.Linear(hidden, hidden), nn.ReLU(), nn.Linear(hidden, 1))
        nn.init.zeros_(self.net[-1].weight)
        nn.init.zeros_(self.net[-1].bias)

    def forward(
        self,
        support_xy_m: torch.Tensor,
        support_forecast_ugm3: torch.Tensor,
        support_elevation_m: torch.Tensor,
        query_xy_m: torch.Tensor,
        query_elevation_m: torch.Tensor,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        if support_elevation_m.shape != support_forecast_ugm3.shape or query_elevation_m.shape != (query_xy_m.shape[0],):
            raise ValueError("elevation arrays must align with support/query sites")
        base, nearest_m = forecast_idw(support_xy_m, support_forecast_ugm3, query_xy_m)
        if not torch.isfinite(support_elevation_m).all() or not torch.isfinite(query_elevation_m).all():
            raise ValueError("verified elevation must be finite")
        # Fixed physical scales, not fitted on an exposed test set.
        features = torch.stack((base / 100.0, nearest_m / 10_000.0,
                                torch.full_like(base, float(support_xy_m.shape[0]) / 15.0),
                                (query_elevation_m - support_elevation_m.mean()) / 100.0), dim=1)
        return base + 100.0 * self.net(features).squeeze(1), nearest_m
