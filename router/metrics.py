from __future__ import annotations

from typing import Iterable, Sequence, Dict
import math


def rmse(preds: Sequence[float], targets: Sequence[float]) -> float:
    n = len(preds)
    if n == 0:
        return float("nan")
    s = 0.0
    for p, t in zip(preds, targets):
        d = float(p) - float(t)
        s += d * d
    return math.sqrt(s / n)


def mae(preds: Sequence[float], targets: Sequence[float]) -> float:
    n = len(preds)
    if n == 0:
        return float("nan")
    s = 0.0
    for p, t in zip(preds, targets):
        s += abs(float(p) - float(t))
    return s / n


def bias(preds: Sequence[float], targets: Sequence[float]) -> float:
    n = len(preds)
    if n == 0:
        return float("nan")
    s = 0.0
    for p, t in zip(preds, targets):
        s += float(p) - float(t)
    return s / n


def evaluate(preds: Sequence[float], scaled: Sequence[float], targets: Sequence[float]) -> Dict[str, float]:
    return {
        "rmse_raw": rmse(preds, targets),
        "rmse_scaled": rmse(scaled, targets),
        "mae_raw": mae(preds, targets),
        "mae_scaled": mae(scaled, targets),
        "bias_raw": bias(preds, targets),
        "bias_scaled": bias(scaled, targets),
    }


__all__ = ["rmse", "mae", "bias", "evaluate"]
