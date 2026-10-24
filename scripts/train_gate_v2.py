"""Validation-selected, observed-mask neural comparisons for the persistence gate.

Run from repository root as a module. The selection stage never reads test
targets; the final stage only reads test targets after fixing LR and scaler.
"""
from __future__ import annotations

import os
os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")

import argparse
import datetime as dt
import json
import random
import subprocess
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import yaml

from src.stpignn.evaluation import evaluate_arrays
from src.stpignn.models_v2 import make_model
from src.stpignn.paths import REPO_ROOT
from src.stpignn.physics_v2 import batched_penalty
from src.stpignn.station_graph import directed_knn_graph

MODELS = ["gru_only", "vanilla_gcn", "st_gru_gcn", "stpignn_legacy",
          "stpignn_corrected", "stpignn_laplacian", "stpignn_corrected_imputed"]


def seed_all(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.use_deterministic_algorithms(True)
    torch.backends.cudnn.benchmark = False


def scaler_params(fit, name):
    if name == "standard":
        return fit["target_standard_mean"], fit["target_standard_std"]
    if name == "log1p":
        return fit["target_log1p_mean"], fit["target_log1p_std"]
    raise ValueError(name)


def normalize_y(y, name, mean, std):
    if name == "log1p":
        return (torch.log1p(y.clamp(min=0)) - mean) / std
    return (y - mean) / std


def inverse_y(pred, name, mean, std):
    z = pred * std + mean
    return torch.expm1(z) if name == "log1p" else z


def aligned_mask_arrays(raw_wind, xy, edge_index, legacy_slope, legacy_intercept):
    source, destination = edge_index.numpy()
    delta = xy[destination] - xy[source]
    compass = (np.degrees(np.arctan2(delta[:, 0], delta[:, 1])) + 360) % 360
    math_reverse = (np.degrees(np.arctan2(delta[:, 1], delta[:, 0])) + 540) % 360
    transport = (raw_wind[:, None] + 180) % 360
    corrected_delta = np.abs(compass[None, :] - transport)
    corrected = np.minimum(corrected_delta, 360 - corrected_delta) <= 37.5
    scaled = legacy_slope * raw_wind[:, None] + legacy_intercept
    legacy_delta = np.abs(math_reverse[None, :] - scaled)
    legacy = np.minimum(legacy_delta, 360 - legacy_delta) <= 37.5
    return corrected, legacy


class Context:
    def __init__(self):
        self.cfg = yaml.safe_load((REPO_ROOT / "configs/gate_v2.yaml").read_text())
        self.data_cfg = yaml.safe_load((REPO_ROOT / "configs/data_v2.yaml").read_text())
        self.z = np.load(REPO_ROOT / "results/data_v2_arrays.npz")
        self.fit = json.loads((REPO_ROOT / "results/data_v2_fit.json").read_text())["fit"]
        self.mask_summary = json.loads((REPO_ROOT / "results/physics_v2_mask_summary.json").read_text())
        self.times = pd.DatetimeIndex(pd.to_datetime(self.z["times_ns"], utc=True))
        self.horizon = int(self.cfg["horizon_hours"])
        self.history = int(self.data_cfg["history_hours"])
        self.features = self.z["features"]
        self.observed_y = self.z["observed_target"]
        self.observed_mask = self.z["observed_mask"]
        self.imputed_y = self.z["imputed_target"]
        self.station_ids = self.z["station_ids"]
        self.edge_index, self.edge_attr = directed_knn_graph(self.z["coordinates"],
                                                              int(self.cfg["station_graph_neighbours"]))
        self.corrected_mask, self.legacy_mask = aligned_mask_arrays(
            self.z["raw_wind_degrees"], self.z["coordinates"], self.edge_index,
            self.mask_summary["legacy_direction_slope"], self.mask_summary["legacy_direction_intercept"])
        self.hours = {}
        for split in ("train", "validation", "test"):
            a = pd.Timestamp(self.data_cfg[f"{split}_start_utc"])
            b = pd.Timestamp(self.data_cfg[f"{split}_end_utc"])
            eligible = np.asarray((self.times >= a) & (self.times <= b) & self.observed_mask.any(axis=1))
            eligible[:self.history - 1 + self.horizon] = False
            self.hours[split] = np.flatnonzero(eligible)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.edge_index = self.edge_index.to(self.device)
        self.edge_attr = self.edge_attr.to(self.device)

    def batches(self, split, batch_size, epoch_seed=None):
        hours = self.hours[split].copy()
        if epoch_seed is not None:
            np.random.default_rng(epoch_seed).shuffle(hours)
        for start in range(0, len(hours), batch_size):
            target_idx = hours[start:start + batch_size]
            cutoff = target_idx - self.horizon
            window_idx = cutoff[:, None] - np.arange(self.history - 1, -1, -1)[None, :]
            if np.any(window_idx > cutoff[:, None]) or np.any(window_idx < 0):
                raise AssertionError("Future or invalid input timestamp")
            x = torch.as_tensor(self.features[window_idx].copy(), dtype=torch.float32, device=self.device)
            raw_y = torch.as_tensor(np.nan_to_num(self.observed_y[target_idx], nan=0.0).copy(), dtype=torch.float32, device=self.device)
            mask = torch.as_tensor(self.observed_mask[target_idx].copy(), dtype=torch.bool, device=self.device)
            imputed = torch.as_tensor(self.imputed_y[target_idx].copy(), dtype=torch.float32, device=self.device)
            cmask = torch.as_tensor(self.corrected_mask[cutoff].copy(), dtype=torch.bool, device=self.device)
            lmask = torch.as_tensor(self.legacy_mask[cutoff].copy(), dtype=torch.bool, device=self.device)
            yield target_idx, x, raw_y, mask, imputed, cmask, lmask


def run_model(ctx, name, scaler, lr, seed, max_epochs, test_after=False):
    seed_all(seed)
    cfg = ctx.cfg
    model = make_model(name, ctx.features.shape[-1], int(cfg["neural_hidden_dim"]), ctx.edge_attr.shape[1]).to(ctx.device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=float(lr), weight_decay=float(cfg["neural_weight_decay"]))
    mean, std = scaler_params(ctx.fit, scaler)
    phys_scale = ctx.fit["target_standard_std"]
    batch_size = int(cfg["neural_batch_size"])
    best_val, best_epoch, best_state, bad = float("inf"), 0, None, 0
    curves = []
    for epoch in range(1, max_epochs + 1):
        model.train()
        loss_sum, weight_sum = 0.0, 0
        for _, x, raw_y, observed_mask, imputed, corrected_mask, legacy_mask in ctx.batches("train", batch_size, seed * 1000 + epoch):
            optimizer.zero_grad(set_to_none=True)
            pred = model(x, ctx.edge_index, ctx.edge_attr)
            if name == "stpignn_corrected_imputed":
                weights = torch.where(observed_mask, 1.0, float(cfg["imputed_target_weight"]))
                target_y = imputed
            else:
                weights = observed_mask.float()
                target_y = raw_y
            normalized_target = normalize_y(target_y, scaler, mean, std)
            data_loss = (((pred - normalized_target) ** 2) * weights).sum() / weights.sum().clamp(min=1)
            physical_loss = pred.new_tensor(0.0)
            if name.startswith("stpignn_"):
                p_phys_norm = inverse_y(pred, scaler, mean, std) / phys_scale
                variant = "legacy" if name == "stpignn_legacy" else ("laplacian" if name == "stpignn_laplacian" else "corrected_mask")
                wind_mask = legacy_mask if variant == "legacy" else corrected_mask
                physical_loss = batched_penalty(p_phys_norm, ctx.edge_index, wind_mask, ctx.edge_attr, variant)
            physics_lambda = float(cfg["neural_physics_weight"]) * min(1.0, epoch / 25.0)
            loss = data_loss + physics_lambda * physical_loss
            if not torch.isfinite(loss):
                raise FloatingPointError(f"Non-finite training loss: {name}, {scaler}, seed={seed}, epoch={epoch}")
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 0.3)
            optimizer.step()
            loss_sum += float(loss.detach()) * len(x)
            weight_sum += len(x)
        val_mae = evaluate_split(ctx, model, scaler, mean, std, "validation", collect=False)["mae"]
        curves.append({"model": name, "scaler": scaler, "lr": float(lr), "seed": seed,
                       "epoch": epoch, "train_loss": loss_sum / weight_sum, "val_mae_ug_m3": val_mae,
                       "physics_lambda": physics_lambda})
        if val_mae < best_val:
            best_val, best_epoch, bad = val_mae, epoch, 0
            best_state = {key: value.detach().cpu().clone() for key, value in model.state_dict().items()}
        else:
            bad += 1
            if bad >= int(cfg["neural_early_stopping_patience"]):
                break
    model.load_state_dict(best_state)
    result = {"model": name, "scaler": scaler, "lr": float(lr), "seed": seed,
              "best_val_mae_ug_m3": best_val, "best_epoch": best_epoch}
    predictions = None
    if test_after:
        predictions = evaluate_split(ctx, model, scaler, mean, std, "test", collect=True)
        result.update({k: predictions[k] for k in ("mae", "rmse", "r2", "bias", "nmae", "median_ae", "n")})
        checkpoint = REPO_ROOT / "results/checkpoints_v2" / f"{name}_{scaler}_seed{seed}.pt"
        checkpoint.parent.mkdir(exist_ok=True)
        torch.save({"state_dict": best_state, "model": name, "scaler": scaler, "lr": float(lr),
                    "seed": seed, "best_epoch": best_epoch, "val_mae_ug_m3": best_val,
                    "data_config": "configs/data_v2.yaml", "train_config": "configs/gate_v2.yaml"}, checkpoint)
        result["checkpoint"] = str(checkpoint.relative_to(REPO_ROOT))
    return result, curves, predictions


def evaluate_split(ctx, model, scaler, mean, std, split, collect):
    model.eval()
    pred_all, truth_all, station_all, time_all = [], [], [], []
    with torch.no_grad():
        for target_idx, x, raw_y, mask, _, _, _ in ctx.batches(split, int(ctx.cfg["neural_batch_size"])):
            pred = inverse_y(model(x, ctx.edge_index, ctx.edge_attr), scaler, mean, std)
            selected = mask.cpu().numpy()
            pred_np = pred.cpu().numpy()
            truth_np = raw_y.cpu().numpy()
            row, col = np.where(selected)
            pred_all.append(pred_np[row, col])
            truth_all.append(truth_np[row, col])
            if collect:
                station_all.append(ctx.station_ids[col])
                time_all.append(ctx.times[target_idx[row]].astype(str))
    p = np.concatenate(pred_all)
    y = np.concatenate(truth_all)
    metrics = evaluate_arrays(p, y, np.ones_like(y, dtype=bool))
    if collect:
        metrics["prediction"] = p
        metrics["target"] = y
        metrics["station_id"] = np.concatenate(station_all)
        metrics["target_time_utc"] = np.concatenate(time_all)
    return metrics


def metadata(script, cfg, began):
    return {"timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat(), "script": script,
            "config": "configs/gate_v2.yaml", "data_config": "configs/data_v2.yaml",
            "seed": cfg["seed"], "source_git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True).strip(),
            "hardware": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU",
            "runtime_seconds": time.perf_counter() - began}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=("selection", "final"), required=True)
    parser.add_argument("--models", nargs="*", default=None)
    args = parser.parse_args()
    began = time.perf_counter()
    ctx = Context()
    models = args.models or MODELS
    selection_path = REPO_ROOT / "results/neural_selection_v2.csv"
    curves_path = REPO_ROOT / "results/neural_curves_v2.csv"
    if args.stage == "selection":
        existing = pd.read_csv(selection_path) if selection_path.exists() else pd.DataFrame()
        rows = existing.to_dict("records")
        curves = pd.read_csv(curves_path).to_dict("records") if curves_path.exists() else []
        # Select the target transform on the corrected model before other sweeps.
        ordered_models = (["stpignn_corrected"] if "stpignn_corrected" in models else []) + [
            name for name in models if name != "stpignn_corrected"]
        for name in ordered_models:
            if name == "stpignn_corrected":
                scalers = ctx.cfg["target_scaler_grid"]
            else:
                completed = pd.DataFrame(rows)
                candidate = completed[completed.model == "stpignn_corrected"] if not completed.empty else pd.DataFrame()
                scalers = [candidate.sort_values("best_val_mae_ug_m3").iloc[0].scaler] if len(candidate) else ["log1p"]
            for scaler in scalers:
                for lr in ctx.cfg["neural_lr_grid"]:
                    if not existing.empty and ((existing.model == name) & (existing.scaler == scaler) & (existing.lr == float(lr))).any():
                        continue
                    result, track, _ = run_model(ctx, name, scaler, lr, int(ctx.cfg["neural_seeds"][0]),
                                                 int(ctx.cfg["neural_selection_epochs"]))
                    rows.append(result)
                    curves.extend(track)
                    pd.DataFrame(rows).to_csv(selection_path, index=False)
                    pd.DataFrame(curves).to_csv(curves_path, index=False)
                    print("SELECT", result, flush=True)
        summary = metadata("scripts/train_gate_v2.py --stage selection", ctx.cfg, began)
        (REPO_ROOT / "results/neural_selection_run.json").write_text(json.dumps(summary, indent=2) + "\n")
        return

    choices = pd.read_csv(selection_path)
    corrected = choices[choices.model == "stpignn_corrected"].sort_values("best_val_mae_ug_m3").iloc[0]
    selected_scaler = corrected.scaler
    existing = pd.read_csv(REPO_ROOT / "results/neural_final_v2.csv") if (REPO_ROOT / "results/neural_final_v2.csv").exists() else pd.DataFrame()
    rows = existing.to_dict("records")
    curves = pd.read_csv(curves_path).to_dict("records") if curves_path.exists() else []
    prediction_frames = []
    pred_path = REPO_ROOT / "results/neural_predictions_v2.parquet"
    if pred_path.exists():
        prediction_frames.append(pd.read_parquet(pred_path))
    for name in models:
        subset = choices[(choices.model == name) & (choices.scaler == selected_scaler)]
        if subset.empty:
            raise RuntimeError(f"No selected-scaler LR sweep for {name}")
        selected = subset.sort_values("best_val_mae_ug_m3").iloc[0]
        for seed in ctx.cfg["neural_seeds"]:
            if not existing.empty and ((existing.model == name) & (existing.seed == int(seed))).any():
                continue
            result, track, predictions = run_model(ctx, name, selected_scaler, float(selected.lr), int(seed),
                                                   int(ctx.cfg["neural_max_epochs"]), test_after=True)
            rows.append(result)
            curves.extend(track)
            frame = pd.DataFrame({"model": name, "scaler": selected_scaler, "seed": seed,
                                  "station_id": predictions["station_id"],
                                  "target_time_utc": predictions["target_time_utc"],
                                  "target_ug_m3": predictions["target"],
                                  "prediction_ug_m3": predictions["prediction"]})
            prediction_frames.append(frame)
            pd.DataFrame(rows).to_csv(REPO_ROOT / "results/neural_final_v2.csv", index=False)
            pd.DataFrame(curves).to_csv(curves_path, index=False)
            pd.concat(prediction_frames, ignore_index=True).to_parquet(pred_path, index=False)
            print("FINAL", {k: v for k, v in result.items() if k != "checkpoint"}, flush=True)
    summary = metadata("scripts/train_gate_v2.py --stage final", ctx.cfg, began)
    summary["selected_scaler"] = selected_scaler
    summary["q_variant_status"] = "BLOCKED: no measured traffic index"
    (REPO_ROOT / "results/neural_final_run.json").write_text(json.dumps(summary, indent=2) + "\n")


if __name__ == "__main__":
    main()
