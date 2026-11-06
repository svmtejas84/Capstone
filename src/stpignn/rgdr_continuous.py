"""Causal observation-age reliability for the frozen RGDR_CONTINUOUS_V2 variant."""
from __future__ import annotations

import numpy as np
import torch

from .rgdr import edge_reliability, rgdr_penalty, reliability_weighted_smoothing


def observed_age_hours(observed_mask: np.ndarray, cutoff_indices: np.ndarray) -> np.ndarray:
    """Age of latest observation at or before each cutoff; missing is infinity.

    The integer timeline must be continuous hourly UTC. Only past/present mask
    entries are read for each cutoff. Targets are never an argument.
    """
    obs = np.asarray(observed_mask, dtype=bool)
    cut = np.asarray(cutoff_indices, dtype=np.int64)
    if obs.ndim != 2 or cut.ndim != 1 or np.any(cut < 0) or np.any(cut >= len(obs)):
        raise ValueError("expected observed mask [T,N] and valid cutoff indices [B]")
    steps = np.arange(len(obs), dtype=np.int64)[:, None]
    latest = np.maximum.accumulate(np.where(obs, steps, -1), axis=0)
    last = latest[cut]
    return np.where(last >= 0, cut[:, None] - last, np.inf).astype(np.float32)


def fit_tau_train_only(ages_hours: np.ndarray, max_lookback_hours: float = 24.0) -> float:
    age = np.asarray(ages_hours, dtype=np.float64)
    if max_lookback_hours <= 0:
        raise ValueError("positive lookback required")
    positive = age[np.isfinite(age) & (age > 0) & (age <= max_lookback_hours)]
    return float(np.median(positive)) if len(positive) else 1.0


def age_reliability(ages_hours: np.ndarray | torch.Tensor, tau_hours: float,
                    max_lookback_hours: float = 24.0) -> torch.Tensor:
    if not np.isfinite(tau_hours) or tau_hours <= 0 or max_lookback_hours <= 0:
        raise ValueError("positive finite tau/lookback required")
    age = torch.as_tensor(ages_hours, dtype=torch.float32)
    eligible = torch.isfinite(age) & (age >= 0) & (age <= max_lookback_hours)
    safe_age = torch.where(eligible, age, torch.zeros_like(age))
    return torch.where(eligible, torch.exp(-safe_age / tau_hours), torch.zeros_like(age))


def continuous_directional_penalty(pred_norm: torch.Tensor, edge_index: torch.Tensor,
                                   wind_mask: torch.Tensor, edge_attr: torch.Tensor,
                                   ages_hours: torch.Tensor, tau_hours: float,
                                   max_lookback_hours: float = 24.0) -> torch.Tensor:
    q = age_reliability(ages_hours, tau_hours, max_lookback_hours).to(pred_norm.device)
    return rgdr_penalty(pred_norm, edge_index, wind_mask, edge_attr, q)


def continuous_generic_penalty(pred_norm: torch.Tensor, edge_index: torch.Tensor,
                               edge_attr: torch.Tensor, ages_hours: torch.Tensor,
                               tau_hours: float, max_lookback_hours: float = 24.0) -> torch.Tensor:
    q = age_reliability(ages_hours, tau_hours, max_lookback_hours).to(pred_norm.device)
    return reliability_weighted_smoothing(pred_norm, edge_index, edge_attr, q)


__all__ = ["observed_age_hours", "fit_tau_train_only", "age_reliability",
           "continuous_directional_penalty", "continuous_generic_penalty", "edge_reliability"]
