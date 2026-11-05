"""Restart-safe V100 baseline training. One supervised invocation runs all groups."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import yaml

from scripts.benchmark_v2j import Context, fit
from src.stpignn.paths import REPO_ROOT

BASE = REPO_ROOT / "final_blr_results/baselines/v2m"
DATA = BASE / "data/data_v2m_arrays.npz"
FIT = BASE / "data/data_v2m_fit.json"
CONFIG = REPO_ROOT / "configs/benchmark_v2g.yaml"


class MLP(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(216, 64), nn.ReLU(), nn.Linear(64, 64), nn.ReLU(), nn.Linear(64, 1))

    def forward(self, x):
        b, t, n, f = x.shape
        assert (t, f) == (12, 18)
        return self.net(x.permute(0, 2, 1, 3).reshape(b*n, 216)).reshape(b, n)


class CausalConv(nn.Module):
    def __init__(self, in_channels, dilation):
        super().__init__()
        self.padding = 2 * dilation
        self.conv = nn.Conv1d(in_channels, 64, 3, dilation=dilation, padding=self.padding)

    def forward(self, x):
        return self.conv(x)[..., :-self.padding]


class TCN(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = CausalConv(18, 1)
        self.conv2 = CausalConv(64, 2)
        self.readout = nn.Linear(64 * 12, 1)

    def representations(self, x):
        b, t, n, f = x.shape
        assert (t, f) == (12, 18)
        v = x.permute(0, 2, 3, 1).reshape(b*n, f, t)
        return torch.relu(self.conv2(torch.relu(self.conv1(v))))

    def forward(self, x):
        b, _, n, _ = x.shape
        return self.readout(self.representations(x).flatten(1)).reshape(b, n)


class V2MContext(Context):
    def __init__(self, horizon, config):
        super().__init__(horizon, config, arrays_path=DATA, fit_path=FIT)

    def make(self, name):
        return (MLP() if name == "mlp" else TCN()).to(self.device)

    def forward(self, model, name, x, anchor, wind):
        anchor_z = (torch.log1p(anchor.clamp_min(0)) - self.mu) / self.sd
        return model(x) + anchor_z


def sha(path):
    d = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(4 * 1024 * 1024), b""):
            d.update(chunk)
    return d.hexdigest()


def atomic_json(path, payload):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, default=str) + "\n")
    tmp.replace(path)


def train_group(name, horizon, cfg):
    group = BASE / name / f"h{horizon}"
    group.mkdir(parents=True, exist_ok=True)
    ctx = V2MContext(horizon, cfg)
    candidate_rows = []
    selection = group / "validation_selection.json"
    if selection.exists():
        chosen = json.loads(selection.read_text())
        if [r["lr"] for r in chosen["candidates"]] != [float(x) for x in cfg["neural_lr_grid"]]:
            raise RuntimeError("Frozen LR grid mismatch")
    else:
        for lr in cfg["neural_lr_grid"]:
            result, _ = fit(ctx, name, float(lr), 11)
            candidate_rows.append(result)
            print("SELECT", name, horizon, lr, result["validation_mae"], flush=True)
        best = min(candidate_rows, key=lambda r: (r["validation_mae"], r["lr"]))
        chosen = dict(model=name, horizon=horizon, selected_lr=best["lr"], candidates=candidate_rows,
                      selected_by="seed-11 validation MAE only", dataset_sha256=sha(DATA),
                      config_sha256=sha(CONFIG), timestamp_utc=dt.datetime.now(dt.timezone.utc).isoformat())
        atomic_json(selection, chosen)
    for seed in cfg["neural_seeds"]:
        cell = group / f"seed{seed}"
        marker = cell / "COMPLETE.json"
        if marker.exists():
            manifest = json.loads(marker.read_text())
            for key in ("checkpoint", "predictions", "metrics"):
                p = cell / manifest[key]["path"]
                if not p.exists() or sha(p) != manifest[key]["sha256"]:
                    raise RuntimeError(f"Corrupt completed cell {cell} {key}")
            print("SKIP VERIFIED", name, horizon, seed, flush=True)
            continue
        cell.mkdir(parents=True, exist_ok=True)
        torch.cuda.reset_peak_memory_stats()
        result, tested, model = fit(ctx, name, chosen["selected_lr"], seed, evaluate_test=True, return_model=True)
        result.update(test_rmse=tested["rmse"], gpu_peak_bytes=torch.cuda.max_memory_allocated(),
                      dataset_sha256=sha(DATA), config_sha256=sha(CONFIG),
                      timestamp_utc=dt.datetime.now(dt.timezone.utc).isoformat())
        checkpoint = cell / "checkpoint.pt"
        tmp_ckpt = cell / "checkpoint.tmp.pt"
        torch.save({"state_dict": model.state_dict(), "model": name, "horizon": horizon,
                    "seed": seed, "selected_lr": chosen["selected_lr"], "metrics": result}, tmp_ckpt)
        tmp_ckpt.replace(checkpoint)
        prediction = cell / "predictions.parquet"
        tmp_pred = cell / "predictions.tmp.parquet"
        pd.DataFrame({"model": name, "seed": seed, "horizon_hours": horizon,
                      "target_time_utc": ctx.times[tested["time_index"]].astype(str),
                      "station_id": ctx.station_ids[tested["station_index"]],
                      "target_ug_m3": tested["truth"], "prediction_ug_m3": tested["pred"]}).to_parquet(tmp_pred, index=False)
        tmp_pred.replace(prediction)
        metrics = cell / "metrics.json"
        atomic_json(metrics, result)
        atomic_json(marker, {"model": name, "horizon": horizon, "seed": seed,
                             "checkpoint": {"path": checkpoint.name, "sha256": sha(checkpoint)},
                             "predictions": {"path": prediction.name, "sha256": sha(prediction)},
                             "metrics": {"path": metrics.name, "sha256": sha(metrics)}})
        print("COMPLETE", name, horizon, seed, result["test_mae"], flush=True)
    print("GROUP COMPLETE", name, horizon, flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", choices=["mlp", "tcn"], required=True)
    parser.add_argument("--horizon", type=int, choices=[1, 3, 6, 12, 24], required=True)
    args = parser.parse_args()
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA required; CPU training forbidden")
    cfg = yaml.safe_load(CONFIG.read_text())
    if cfg["neural_seeds"] != [11,23,37,51,79] or cfg["neural_lr_grid"] != [0.0001,0.0003,0.001,0.003]:
        raise RuntimeError("Frozen configuration changed")
    train_group(args.model, args.horizon, cfg)


if __name__ == "__main__":
    main()
