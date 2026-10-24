"""One observed-target scoring and synchronized inference timing path."""
from __future__ import annotations

import time

import numpy as np
from sklearn.metrics import r2_score


def evaluate_arrays(prediction, target, observed_mask, normalizer=None):
    p = np.asarray(prediction, dtype=float)
    y = np.asarray(target, dtype=float)
    mask = np.asarray(observed_mask, dtype=bool) & np.isfinite(p) & np.isfinite(y)
    if p.shape != y.shape or p.shape != mask.shape:
        raise ValueError("Prediction, target and observed mask must have identical shape")
    error = p[mask] - y[mask]
    truth = y[mask]
    if not len(error):
        return {"n": 0, "mae": None, "rmse": None, "r2": None, "bias": None,
                "nmae": None, "median_ae": None}
    mae = float(np.mean(np.abs(error)))
    norm = float(np.mean(np.abs(truth))) if normalizer is None else float(normalizer)
    return {"n": len(error), "mae": mae, "rmse": float(np.sqrt(np.mean(error ** 2))),
            "r2": float(r2_score(truth, p[mask])) if len(error) > 1 and np.var(truth) > 0 else None,
            "bias": float(np.mean(error)), "nmae": mae / norm if norm > 0 else None,
            "median_ae": float(np.median(np.abs(error)))}


def synchronized_latency_ms(forward, device, warmup=50, timed=200):
    """Call a no-grad forward closure on fixed inputs using one device."""
    import torch
    for _ in range(warmup):
        forward()
    if device.type == "cuda":
        torch.cuda.synchronize(device)
    durations = []
    for _ in range(timed):
        if device.type == "cuda":
            torch.cuda.synchronize(device)
        start = time.perf_counter()
        forward()
        if device.type == "cuda":
            torch.cuda.synchronize(device)
        durations.append((time.perf_counter() - start) * 1000)
    return {"mean_ms": float(np.mean(durations)), "std_ms": float(np.std(durations)),
            "warmup": warmup, "timed": timed}
