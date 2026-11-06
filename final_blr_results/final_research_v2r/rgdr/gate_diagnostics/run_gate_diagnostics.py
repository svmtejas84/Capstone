"""Frozen h=6 train/validation-only RGDR V2 feasibility diagnostic."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import yaml

from src.stpignn.physics_v2 import batched_penalty
from src.stpignn.rgdr import rgdr_penalty, reliability_weighted_smoothing
from src.stpignn.rgdr_continuous import age_reliability, fit_tau_train_only, observed_age_hours
from src.stpignn.station_graph import directed_knn_graph

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
H = 6


def main() -> None:
    z = np.load(ROOT / "results/data_v2j_arrays.npz")
    cfg = yaml.safe_load((ROOT / "configs/data_v2.yaml").read_text())
    times = pd.DatetimeIndex(pd.to_datetime(z["times_ns"], utc=True))
    obs = z["observed_mask"].astype(bool)
    xy = z["coordinates"].astype(np.float64)
    edge, distance = directed_knn_graph(xy, 4)
    src, dst = edge.numpy()
    delta = xy[dst] - xy[src]
    bearing = (np.rad2deg(np.arctan2(delta[:, 0], delta[:, 1])) + 360) % 360
    wind_to = (z["raw_wind_degrees"].astype(float) + 180) % 360
    periods = {}
    for split in ("train", "validation"):
        in_period = (times >= pd.Timestamp(cfg[f"{split}_start_utc"])) & (times <= pd.Timestamp(cfg[f"{split}_end_utc"]))
        target = np.flatnonzero(in_period & obs.any(axis=1) & (np.arange(len(times)) >= H + 11))
        periods[split] = target - H
    train_age = observed_age_hours(obs, periods["train"])
    tau = fit_tau_train_only(train_age)
    train_target = z["observed_target"][((times >= pd.Timestamp(cfg["train_start_utc"])) &
                                          (times <= pd.Timestamp(cfg["train_end_utc"])))].astype(float)
    station_mean = np.nanmean(train_target, axis=0)
    station_mean = np.where(np.isfinite(station_mean), station_mean, np.nanmean(train_target))
    scale = float(np.nanstd(train_target))
    if not np.isfinite(scale) or scale <= 0:
        raise ValueError("invalid train target scale")
    records = []
    for split, cutoff in periods.items():
        age = observed_age_hours(obs, cutoff)
        q = age_reliability(age, tau).numpy()
        binary = obs[cutoff].astype(np.float32)
        angle = np.abs((wind_to[cutoff, None] - bearing[None, :] + 180) % 360 - 180)
        mask = np.isfinite(wind_to[cutoff, None]) & (angle <= 37.5)
        fixed = mask.sum(axis=1)
        rb = binary[:, src] * binary[:, dst]
        rc = q[:, src] * q[:, dst]
        wb = mask * rb
        wc = mask * rc
        nz = fixed > 0
        pos_age = age[np.isfinite(age) & (age > 0) & (age <= 24)]
        row = {"split": split, "target_hours": len(cutoff), "tau_hours": tau,
               "train_target_sd_ug_m3": scale, "fixed_edge_instances": int(fixed.sum()),
               "binary_edge_mass": float(wb.sum()), "continuous_edge_mass": float(wc.sum()),
               "binary_retention_fraction": float(wb.sum() / fixed.sum()) if fixed.sum() else 0,
               "continuous_retention_fraction": float(wc.sum() / fixed.sum()) if fixed.sum() else 0,
               "continuous_effective_edge_sample_size": float(wc.sum()**2 / (wc**2).sum()) if (wc**2).sum() else 0,
               "continuous_mean_positive_edges_per_hour": float((wc > 0).sum(axis=1).mean()),
               "zero_fixed_hours_fraction": float((fixed == 0).mean()),
               "zero_binary_hours_fraction": float((wb.sum(axis=1) == 0).mean()),
               "zero_continuous_hours_fraction": float((wc.sum(axis=1) == 0).mean()),
               "continuous_positive_weight_p10": float(np.quantile(wc[wc > 0], .1)) if (wc > 0).any() else 0,
               "continuous_positive_weight_p50": float(np.quantile(wc[wc > 0], .5)) if (wc > 0).any() else 0,
               "continuous_positive_weight_p90": float(np.quantile(wc[wc > 0], .9)) if (wc > 0).any() else 0,
               "positive_age_median_hours": float(np.median(pos_age)) if len(pos_age) else None,
               "positive_age_p90_hours": float(np.quantile(pos_age, .9)) if len(pos_age) else None,
               "eligible_positive_age_count": int(len(pos_age)),
               "hours_with_fixed_mask": int(nz.sum())}
        # Fixed deterministic cutoff-only proxy field; not a trained model score.
        sample = np.flatnonzero(nz)[:64]
        proxy = z["observed_target"][cutoff[sample]].astype(np.float32)
        proxy = np.where(np.isfinite(proxy), proxy, station_mean[None, :]).astype(np.float32) / scale
        pred = torch.tensor(proxy, requires_grad=True)
        eattr = distance.float()
        m = torch.as_tensor(mask[sample])
        qb = torch.as_tensor(binary[sample])
        qc = torch.as_tensor(q[sample])
        penalties = {
            "fixed": batched_penalty(pred, edge, m, eattr, "corrected_mask"),
            "binary": rgdr_penalty(pred, edge, m, eattr, qb),
            "continuous": rgdr_penalty(pred, edge, m, eattr, qc),
            "continuous_generic": reliability_weighted_smoothing(pred, edge, eattr, qc),
        }
        for name, value in penalties.items():
            grad = torch.autograd.grad(value, pred, retain_graph=True)[0]
            row[f"proxy_{name}_penalty"] = float(value.detach())
            row[f"proxy_{name}_prediction_gradient_l2"] = float(torch.linalg.vector_norm(grad))
            row[f"proxy_{name}_finite"] = bool(torch.isfinite(value) and torch.isfinite(grad).all())
        records.append(row)
    table = pd.DataFrame(records)
    table.to_csv(OUT / "gate_diagnostics_v2r.csv", index=False)
    (OUT / "gate_diagnostics_config.json").write_text(json.dumps({
        "horizon_hours": H, "max_lookback_hours": 24, "tau_fit_split": "train",
        "tau_hours": tau, "proxy_samples_per_split": 64, "sample_rule": "first 64 cutoff hours with fixed wind mask",
        "no_test_target_access": True, "predictive_training": False}, indent=2) + "\n")
    print(table.to_string(index=False))


if __name__ == "__main__":
    main()
