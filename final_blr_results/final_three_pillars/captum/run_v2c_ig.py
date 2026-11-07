"""Bounded IG reproduction for saved v2c h=1 ST-PIGNN checkpoints only."""
from __future__ import annotations

import csv
import hashlib
import json
import os
from pathlib import Path

os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")
ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
os.environ.setdefault("MPLCONFIGDIR", str(OUT / ".mplconfig"))
import sys
sys.path.insert(0, str(ROOT))
import numpy as np
import pandas as pd
import torch
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from captum.attr import IntegratedGradients

from scripts.train_gate_v2 import Context, inverse_y, make_model, scaler_params

FEATURES = ["pm25_lagged", "pm10", "no2", "so2", "co", "wind_speed", "wind_gusts",
            "temperature", "humidity", "surface_pressure", "wind_direction_sin",
            "wind_direction_cos", "elevation"]
SEEDS = (11, 23, 37, 51, 79)


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(4 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def atomic_csv(path: Path, rows: list[dict]) -> None:
    temp = path.with_suffix(path.suffix + ".tmp")
    pd.DataFrame(rows).to_csv(temp, index=False)
    temp.replace(path)


def main() -> None:
    torch.set_num_threads(1)
    torch.manual_seed(20261107)
    np.random.seed(20261107)
    ctx = Context("configs/gate_v2c.yaml", output_prefix="v2c")
    ctx.device = torch.device("cpu")
    ctx.edge_index = ctx.edge_index.cpu()
    ctx.edge_attr = ctx.edge_attr.cpu()
    history, horizon = int(ctx.history), int(ctx.horizon)
    if horizon != 1 or ctx.features.shape[-1] != 13:
        raise RuntimeError(f"Unexpected v2c interface: h={horizon}, F={ctx.features.shape[-1]}")

    # Frozen ID/mask-only sample selection: first, median, last eligible station;
    # first, median, last observed h=1 test target at each station.
    station_ids = ctx.station_ids
    eligible = [j for j in range(len(station_ids)) if np.any(ctx.observed_mask[ctx.hours["test"], j])]
    eligible.sort(key=lambda j: int(station_ids[j]))
    chosen = [eligible[0], eligible[len(eligible) // 2], eligible[-1]]
    samples = []
    for j in chosen:
        ix = ctx.hours["test"][ctx.observed_mask[ctx.hours["test"], j]]
        for i in (int(ix[0]), int(ix[len(ix) // 2]), int(ix[-1])):
            samples.append({"station_index": j, "station_id": int(station_ids[j]),
                            "target_index": i, "target_time_utc": str(ctx.times[i]),
                            "cutoff_time_utc": str(ctx.times[i-horizon]),
                            "input_last_time_utc": str(ctx.times[i-horizon])})
    (OUT / "sample_selection.json").write_text(json.dumps({"rule": "mask-and-ID-only first/median/last station and first/median/last eligible h=1 test target",
                                                            "dataset": "v2c / results/data_v2_arrays.npz",
                                                            "samples": samples}, indent=2) + "\n")

    # Checkpoint-specific train-fitted input baseline, in exact model feature space.
    train_idx = ctx.hours["train"]
    train_reference = ctx.features[train_idx].mean(axis=0).astype(np.float32)  # [station,feature]
    ref = np.broadcast_to(train_reference[None, :, :], (history, *train_reference.shape)).copy()
    zeros = np.zeros_like(ref)
    saved = pd.read_parquet(ROOT / "results/neural_predictions_v2c.parquet")
    saved = saved[(saved.model == "stpignn_corrected") & (saved.scaler == "log1p")]
    saved["target_time_utc"] = pd.to_datetime(saved.target_time_utc, utc=True)
    saved_lookup = {(int(r.seed), int(r.station_id), r.target_time_utc): float(r.prediction_ug_m3)
                    for r in saved.itertuples(index=False)}
    mean, std = scaler_params(ctx.fit, "log1p")
    records, tensors = [], []
    attr_rows, lag_rows, neighbor_rows = [], [], []
    record_dir = OUT / "records"
    record_dir.mkdir(exist_ok=True)

    for seed in SEEDS:
        ckpt_path = ROOT / f"results/checkpoints_v2c/final_stpignn_corrected_log1p_seed{seed}.pt"
        checkpoint = torch.load(ckpt_path, map_location="cpu", weights_only=False)
        if (checkpoint.get("model"), checkpoint.get("scaler"), checkpoint.get("seed")) != ("stpignn_corrected", "log1p", seed):
            raise RuntimeError(f"Checkpoint metadata mismatch: {ckpt_path}")
        model = make_model("stpignn_corrected", ctx.features.shape[-1], int(ctx.cfg["neural_hidden_dim"]),
                           ctx.edge_attr.shape[1]).cpu()
        model.load_state_dict(checkpoint["state_dict"], strict=True)
        model.eval()
        for parameter in model.parameters():
            parameter.requires_grad_(False)

        for sample_index, sample in enumerate(samples):
            i, j = sample["target_index"], sample["station_index"]
            cutoff = i - horizon
            indices = cutoff - np.arange(history - 1, -1, -1)
            if indices[-1] != cutoff or indices.max() > cutoff:
                raise AssertionError("forecast cutoff violation")
            x_np = ctx.features[indices].copy().astype(np.float32)  # [T,N,F]
            x = torch.from_numpy(x_np[None])
            anchor = float(ctx.anchor[cutoff, j])
            anchor_z = (np.log1p(max(anchor, 0.0)) - mean) / std
            target_station = j
            key = (seed, int(station_ids[j]), pd.Timestamp(ctx.times[i]))
            saved_prediction = saved_lookup.get(key)
            if saved_prediction is None:
                raise KeyError(f"Missing saved prediction for {key}")

            def forward(inp):
                residual = model(inp, ctx.edge_index, ctx.edge_attr)
                anchor_tensor = residual.new_full((residual.shape[0], residual.shape[1]), float(anchor_z))
                pred = inverse_y(residual + anchor_tensor, "log1p", mean, std)
                return pred[:, target_station]

            with torch.no_grad():
                pred = float(forward(x)[0])
            wrapper_error = abs(pred - saved_prediction)
            if wrapper_error > 1e-4:
                raise RuntimeError(f"Saved-prediction mismatch seed={seed}, site={key[1]}, time={key[2]}: {wrapper_error}")
            baselines = [("training_mean", torch.from_numpy(ref[None]))]
            if seed == 11:
                baselines.append(("zero_input", torch.from_numpy(zeros[None])))
            for baseline_name, baseline in baselines:
                checkpoint_hash = sha(ckpt_path)
                record_path = record_dir / f"seed{seed}_sample{sample_index}_{baseline_name}.npz"
                if record_path.exists():
                    saved_record = np.load(record_path, allow_pickle=False)
                    arr = saved_record["attribution"]
                    rec = json.loads(str(saved_record["metadata"].item()))
                    if rec["checkpoint_sha256"] != checkpoint_hash or rec["wrapper_abs_error_ug_m3"] > 1e-4:
                        raise RuntimeError(f"Saved IG record provenance mismatch: {record_path}")
                else:
                    ig = IntegratedGradients(forward)
                    attributions, delta = ig.attribute(x, baselines=baseline, n_steps=64,
                                                       method="gausslegendre", internal_batch_size=1,
                                                       return_convergence_delta=True)
                    arr = attributions.detach().cpu().numpy()[0].astype(np.float32)  # [T,N,F]
                    delta_value = float(delta[0])
                    with torch.no_grad():
                        baseline_prediction = float(forward(baseline)[0])
                    relative_delta = abs(delta_value) / max(1.0, abs(pred - baseline_prediction))
                    if not np.isfinite(arr).all() or not np.isfinite(delta_value):
                        raise RuntimeError("Nonfinite IG")
                    rec = {"model_version": "v2c corrected ST-PIGNN; not v2j",
                           "model": "stpignn_corrected", "seed": seed, "horizon_hours": horizon,
                           "station_id": int(station_ids[j]), "target_time_utc": str(ctx.times[i]),
                           "cutoff_time_utc": str(ctx.times[cutoff]), "baseline": baseline_name,
                           "prediction_ug_m3": pred, "saved_prediction_ug_m3": saved_prediction,
                           "wrapper_abs_error_ug_m3": wrapper_error, "baseline_prediction_ug_m3": baseline_prediction,
                           "completeness_delta_ug_m3": delta_value, "completeness_relative": relative_delta,
                           "nonfinite_count": int((~np.isfinite(arr)).sum()),
                           "quality_flag": int(abs(delta_value) > 0.05 or relative_delta > 0.01),
                           "attribution_sum_ug_m3": float(arr.sum()),
                           "absolute_attribution_sum_ug_m3": float(np.abs(arr).sum()),
                           "checkpoint_path": str(ckpt_path.relative_to(ROOT)), "checkpoint_sha256": checkpoint_hash}
                    record_tmp = record_path.with_suffix(".npz.tmp")
                    with record_tmp.open("wb") as f:
                        np.savez_compressed(f, attribution=arr, metadata=np.array(json.dumps(rec)))
                    record_tmp.replace(record_path)
                rec["record"] = len(records)
                records.append(rec)
                tensors.append(arr)
                for t in range(history):
                    lag = history - 1 - t
                    lag_rows.append({**{k: rec[k] for k in ("record", "seed", "station_id", "target_time_utc", "baseline")},
                                     "lag_hours_before_cutoff": lag,
                                     "signed_ug_m3": float(arr[t].sum()),
                                     "absolute_ug_m3": float(np.abs(arr[t]).sum())})
                for n in range(arr.shape[1]):
                    neighbor_rows.append({**{k: rec[k] for k in ("record", "seed", "station_id", "target_time_utc", "baseline")},
                                          "input_station_id": int(station_ids[n]),
                                          "signed_ug_m3": float(arr[:, n, :].sum()),
                                          "absolute_ug_m3": float(np.abs(arr[:, n, :]).sum())})
                for f, name in enumerate(FEATURES):
                    attr_rows.append({**{k: rec[k] for k in ("record", "seed", "station_id", "target_time_utc", "baseline")},
                                      "feature": name, "signed_ug_m3": float(arr[:, :, f].sum()),
                                      "absolute_ug_m3": float(np.abs(arr[:, :, f]).sum())})

    atomic_csv(OUT / "IG_RESULTS_v2c.csv", records)
    atomic_csv(OUT / "feature_attributions.csv", attr_rows)
    atomic_csv(OUT / "temporal_attributions.csv", lag_rows)
    atomic_csv(OUT / "station_attributions.csv", neighbor_rows)
    tmp = OUT / "attribution_tensors.npz.tmp"
    with tmp.open("wb") as f:
        np.savez_compressed(f, attributions=np.stack(tensors), feature_names=np.array(FEATURES),
                            records=np.array([json.dumps(r) for r in records]))
    tmp.replace(OUT / "attribution_tensors.npz")

    # Aggregate signed and absolute independently; never take abs after averaging signed values.
    primary = pd.DataFrame(attr_rows).query("baseline == 'training_mean'")
    summary = primary.groupby(["seed", "feature"], as_index=False).agg(
        mean_signed_ug_m3=("signed_ug_m3", "mean"), mean_absolute_ug_m3=("absolute_ug_m3", "mean"))
    summary.to_csv(OUT / "feature_summary.csv", index=False)
    p = primary.groupby(["record", "seed", "station_id", "target_time_utc"], as_index=False).agg(
        absolute_sum=("absolute_ug_m3", "sum"))
    p = p.groupby("seed").absolute_sum.mean()
    summary_seed = summary.groupby("seed").mean_absolute_ug_m3.sum()
    conv = {"record_count": len(records), "unique_samples": len(samples), "unique_checkpoints": len(SEEDS),
            "max_wrapper_error_ug_m3": max(r["wrapper_abs_error_ug_m3"] for r in records),
            "max_abs_completeness_delta_ug_m3": max(abs(r["completeness_delta_ug_m3"]) for r in records),
            "median_abs_completeness_delta_ug_m3": float(np.median([abs(r["completeness_delta_ug_m3"]) for r in records])),
            "flagged_records": int(sum(r["quality_flag"] for r in records)),
            "nonfinite_records": int(sum(r["nonfinite_count"] > 0 for r in records)),
            "mean_absolute_attribution_sum_by_seed": {str(k): float(v) for k, v in summary_seed.items()},
            "seed_variability_scope": "descriptive across 3 selected h1 samples; same Bengaluru test population"}
    (OUT / "diagnostics.json").write_text(json.dumps(conv, indent=2) + "\n")

    # Compact, publication-style descriptive figure for the recovered v2c model.
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    base = summary.groupby("feature").mean_absolute_ug_m3.mean().sort_values()
    axes[0].barh(base.index, base.values, color="#276678")
    axes[0].set_xlabel("Mean absolute IG sum (µg/m³)")
    axes[0].set_title("Feature attribution | v2c corrected ST-PIGNN, h=1")
    temporal = pd.DataFrame(lag_rows).query("baseline == 'training_mean'").groupby("lag_hours_before_cutoff").absolute_ug_m3.mean()
    axes[1].plot(temporal.index, temporal.values, marker="o", color="#d1495b")
    axes[1].set_xlabel("Input lag (hours before issue cutoff)")
    axes[1].set_ylabel("Mean absolute IG sum (µg/m³)")
    axes[1].set_title("Temporal attribution")
    fig.suptitle("Descriptive baseline-relative attribution; 3 fixed stations × 3 times, 5 seeds; not v2j")
    fig.tight_layout()
    fig.savefig(OUT / "figures/ig_v2c_feature_temporal.png", dpi=220)
    fig.savefig(OUT / "figures/ig_v2c_feature_temporal.pdf")
    plt.close(fig)
    completion = f"{len(records)} records; 5 strict-loaded h1 checkpoints; wrapper equivalence passed\n"
    (OUT / "COMPLETE").write_text(completion)
    run_marker = OUT / "runs/ig_v2c/COMPLETE"
    run_marker.parent.mkdir(parents=True, exist_ok=True)
    temp_marker = run_marker.with_suffix(".tmp")
    temp_marker.write_text(completion)
    temp_marker.replace(run_marker)
    print(json.dumps(conv, indent=2))


if __name__ == "__main__":
    main()
