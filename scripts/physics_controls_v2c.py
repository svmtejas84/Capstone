"""Matched residual physics controls and held-out graph PVR/smoothness."""
from __future__ import annotations

import datetime as dt
import json
import subprocess

import numpy as np
import pandas as pd
import torch
import yaml
from scipy.stats import t

from scripts.train_gate_v2 import Context, inverse_y, make_model, normalize_y, run_model, seed_all
from src.stpignn.paths import REPO_ROOT

NAMES = ("stpignn_corrected", "stpignn_lambda0", "stpignn_laplacian")
THRESHOLDS = (0.0, 0.01, 0.05, 0.1)


def graph_metrics(ctx, checkpoint, model_name):
    state = torch.load(REPO_ROOT / checkpoint, map_location=ctx.device, weights_only=False)
    model = make_model(model_name, ctx.features.shape[-1], int(ctx.cfg["neural_hidden_dim"]),
                       ctx.edge_attr.shape[1]).to(ctx.device)
    model.load_state_dict(state["state_dict"])
    model.eval()
    scale = float(ctx.fit["target_standard_std"])
    mean = float(ctx.fit["target_log1p_mean"])
    std = float(ctx.fit["target_log1p_std"])
    src, dst = ctx.edge_index
    active_total = 0
    edge_total = 0
    abs_total = 0.0
    squared_total = 0.0
    violations = {threshold: 0 for threshold in THRESHOLDS}
    with torch.no_grad():
        for target_idx, x, _, _, _, corrected, _ in ctx.batches("test", int(ctx.cfg["neural_batch_size"])):
            residual = model(x, ctx.edge_index, ctx.edge_attr)
            anchor = torch.as_tensor(ctx.anchor[target_idx - ctx.horizon].copy(), dtype=torch.float32, device=ctx.device)
            pred = inverse_y(residual + normalize_y(anchor, "log1p", mean, std), "log1p", mean, std)
            difference_ug = pred[:, dst] - pred[:, src]
            difference_norm = difference_ug / scale
            active_total += int(corrected.sum().item())
            edge_total += difference_ug.numel()
            abs_total += float(difference_ug.abs().sum().item())
            squared_total += float((difference_ug ** 2).sum().item())
            for threshold in THRESHOLDS:
                violations[threshold] += int(((difference_norm > threshold) & corrected).sum().item())
    if active_total <= 0 or edge_total <= 0:
        raise AssertionError("No active test edges for physics control")
    return [{"threshold_normalized": threshold, "threshold_ug_m3": threshold * scale,
             "active_edges": active_total, "all_edges": edge_total,
             "violations": violations[threshold], "pvr_percent": 100.0 * violations[threshold] / active_total,
             "mean_abs_edge_difference_ug_m3": abs_total / edge_total,
             "dirichlet_energy_mean_squared_ug_m6": squared_total / edge_total,
             "with_q": False} for threshold in THRESHOLDS]


def paired_interval(a, b):
    delta = np.asarray(a, float) - np.asarray(b, float)
    mean = float(delta.mean())
    sd = float(delta.std(ddof=1))
    half = float(t.ppf(0.975, len(delta) - 1) * sd / np.sqrt(len(delta)))
    return {"mean": mean, "sd": sd, "ci95": [mean - half, mean + half]}


def main():
    cfg = yaml.safe_load((REPO_ROOT / "configs/gate_v2c.yaml").read_text())
    ctx = Context("configs/gate_v2c.yaml", "v2c")
    selection = pd.read_csv(REPO_ROOT / "results/neural_selection_v2c.csv")
    selected = selection.loc[selection.model.eq("stpignn_corrected")].sort_values("best_val_mae_ug_m3").iloc[0]
    lr = float(selected.lr)
    final = pd.read_csv(REPO_ROOT / "results/neural_final_v2c.csv")
    lambda_path = REPO_ROOT / "results/physics_lambda0_final_v2c.csv"
    existing = pd.read_csv(lambda_path) if lambda_path.exists() else pd.DataFrame()
    lambda_rows = existing.to_dict("records")
    for seed in cfg["neural_seeds"]:
        if not existing.empty and ((existing.seed == seed)).any():
            continue
        result, curves, _ = run_model(ctx, "stpignn_lambda0", "log1p", lr, int(seed),
                                      int(cfg["neural_max_epochs"]), test_after=True,
                                      patience=int(cfg["neural_early_stopping_patience"]), budget="physics_lambda0")
        lambda_rows.append(result)
        pd.DataFrame(lambda_rows).to_csv(lambda_path, index=False)
        pd.DataFrame(curves).to_csv(REPO_ROOT / f"results/physics_lambda0_curves_seed{seed}_v2c.csv", index=False)
        print("LAMBDA0", {key: result[key] for key in ("seed", "mae", "r2", "best_epoch")}, flush=True)
    lambda_final = pd.DataFrame(lambda_rows)
    if lambda_final.seed.nunique() != len(cfg["neural_seeds"]):
        raise AssertionError("Incomplete lambda=0 seeds")
    all_final = pd.concat([final.loc[final.model.isin(("stpignn_corrected", "stpignn_laplacian"))],
                           lambda_final], ignore_index=True)
    rows = []
    for name in NAMES:
        for seed in cfg["neural_seeds"]:
            entry = all_final.loc[(all_final.model == name) & (all_final.seed == seed)].iloc[0]
            for value in graph_metrics(ctx, entry.checkpoint, name):
                rows.append({"model": name, "seed": int(seed), "test_mae_ug_m3": float(entry.mae),
                             "test_r2": float(entry.r2), "selected_lr": float(entry.lr),
                             "physics_weight_max": 0.0 if name == "stpignn_lambda0" else float(cfg["neural_physics_weight"]),
                             **value})
            print("METRICS", name, seed, flush=True)
    out = pd.DataFrame(rows)
    out.to_csv(REPO_ROOT / "results/physics_controls_v2c.csv", index=False)
    threshold0 = out.loc[out.threshold_normalized.eq(0)]
    wide_mae = threshold0.pivot(index="seed", columns="model", values="test_mae_ug_m3")
    wide_pvr = threshold0.pivot(index="seed", columns="model", values="pvr_percent")
    comparisons = {}
    for reference in ("stpignn_lambda0", "stpignn_laplacian"):
        comparisons[reference] = {"mae": paired_interval(wide_mae.stpignn_corrected, wide_mae[reference]),
                                  "pvr_at_zero": paired_interval(wide_pvr.stpignn_corrected, wide_pvr[reference])}
    changed = any(not (item[key]["ci95"][0] <= 0 <= item[key]["ci95"][1])
                  for item in comparisons.values() for key in ("mae", "pvr_at_zero"))
    meta = {"timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
            "script": "scripts/physics_controls_v2c.py", "config": "configs/gate_v2c.yaml",
            "source_git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True).strip(),
            "seeds": cfg["neural_seeds"], "lambda0_matched_lr": lr,
            "threshold_scale_train_target_sd_ug_m3": float(ctx.fit["target_standard_std"]),
            "q_status": "unavailable: no measured traffic index", "paired_seed_t_intervals": comparisons,
            "change_beyond_seed_noise_at_mae_or_pvr_zero": changed}
    (REPO_ROOT / "results/physics_controls_v2c.json").write_text(json.dumps(meta, indent=2) + "\n")
    lines = ["# S3 residual physics controls", "",
             f"Source `scripts/physics_controls_v2c.py`, `configs/gate_v2c.yaml`, seeds {cfg['neural_seeds']}, commit `{meta['source_git_commit']}`, {meta['timestamp_utc']}. Q absent (no measured traffic index).",
             "", "| Model | MAE mean±SD (µg/m³) | PVR at zero mean±SD (%) | Mean edge gradient (µg/m³) | Dirichlet energy (µg²/m⁶) |",
             "|---|---:|---:|---:|---:|"]
    for model, group in threshold0.groupby("model"):
        lines.append(f"| {model} | {group.test_mae_ug_m3.mean():.6f}±{group.test_mae_ug_m3.std():.6f} | {group.pvr_percent.mean():.6f}±{group.pvr_percent.std():.6f} | {group.mean_abs_edge_difference_ug_m3.mean():.6f} | {group.dirichlet_energy_mean_squared_ug_m6.mean():.6f} |")
    for reference, item in comparisons.items():
        lines.append(f"Corrected minus {reference}: MAE paired mean {item['mae']['mean']:.6f}, 95% seed-t CI {item['mae']['ci95']}; PVR(0) paired mean {item['pvr_at_zero']['mean']:.6f} percentage points, CI {item['pvr_at_zero']['ci95']}.")
    lines += ["", f"Physics penalty changes MAE or PVR(0) beyond five-seed paired noise under the predeclared 95% seed-t rule: {'YES' if changed else 'NO'}.",
              "source: results/physics_controls_v2c.csv and results/physics_controls_v2c.json; produced by scripts/physics_controls_v2c.py.", ""]
    (REPO_ROOT / "results/physics_controls_v2c.md").write_text("\n".join(lines))
    print("\n".join(lines), flush=True)


if __name__ == "__main__":
    main()
