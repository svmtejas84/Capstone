"""Frozen v2n descriptive IG for compatible v2m station MLP/TCN checkpoints only."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from captum.attr import IntegratedGradients

from final_blr_results.baselines.v2m.reproducibility.train_v2m import MLP, TCN

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "final_blr_results/baselines/v2m"
OUT = Path(__file__).resolve().parent
HORIZONS = (1, 3, 6, 12, 24)
SEEDS = (11, 23, 37, 51, 79)
FEATURES = ("pm25_lagged", "pm10", "no2", "so2", "co", "wind_speed", "wind_gusts",
            "temperature", "humidity", "surface_pressure", "wind_direction_sin",
            "wind_direction_cos", "srtm_elevation", "lag_is_imputed", "hour_sin", "hour_cos",
            "weekday_sin", "weekday_cos")


def sha(path):
    d = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(4 * 1024 * 1024), b""):
            d.update(b)
    return d.hexdigest()


def write_csv(path, rows):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def main():
    torch.set_num_threads(1)
    torch.manual_seed(20261106)
    np.random.seed(20261106)
    z = np.load(BASE / "data/data_v2m_arrays.npz")
    fit = json.loads((BASE / "data/data_v2m_fit.json").read_text())
    mu, sd = float(fit["target_log1p_mean"]), float(fit["target_log1p_sd"])
    times = pd.DatetimeIndex(pd.to_datetime(z["times_ns"], utc=True))
    ids = z["station_ids"]
    observed = z["observed_mask"]
    y = z["observed_target"]
    train = (times >= pd.Timestamp("2022-01-01T00:00:00Z")) & (times <= pd.Timestamp("2025-06-29T23:00:00Z"))
    test = (times >= pd.Timestamp("2025-09-23T00:00:00Z")) & (times <= pd.Timestamp("2026-03-28T23:00:00Z"))
    train_mean = np.nanmean(y[train], axis=0)
    train_mean = np.where(np.isfinite(train_mean), train_mean, np.nanmean(y[train]))
    anchor = pd.DataFrame(y).ffill().to_numpy(dtype=np.float32)
    anchor = np.where(np.isfinite(anchor), anchor, train_mean[None, :]).astype(np.float32)
    hour = times.hour.to_numpy()
    dow = times.dayofweek.to_numpy()
    calendar = np.stack((np.sin(2*np.pi*hour/24), np.cos(2*np.pi*hour/24),
                         np.sin(2*np.pi*dow/7), np.cos(2*np.pi*dow/7)), -1).astype(np.float32)
    xall = np.concatenate((z["features"], (~observed)[..., None].astype(np.float32),
                           np.broadcast_to(calendar[:, None, :], (len(times), len(ids), 4))), -1)
    assert xall.shape == (37152, 15, 18)
    eligible_stations = [j for j in range(len(ids)) if np.any(observed[test, j])]
    chosen = [eligible_stations[k] for k in (0, len(eligible_stations)//2, len(eligible_stations)-1)]
    samples = []
    for h in HORIZONS:
        for j in chosen:
            ix = np.flatnonzero(observed[:, j] & test & (np.arange(len(times)) >= h+11))
            for i in (ix[0], ix[len(ix)//2], ix[-1]):
                samples.append(dict(horizon=h, station_id=int(ids[j]), station_index=int(j),
                                    target_index=int(i), target_time_utc=str(times[i]),
                                    cutoff_time_utc=str(times[i-h])))
    (OUT / "sample_selection.json").write_text(json.dumps({"rule": "first/middle/last observed station and first/middle/last observed test target per horizon; masks only",
                                                         "samples": samples}, indent=2) + "\n")
    # Per-station training mean, the same reference at every lag. No test input enters its fit.
    reference = xall[train].mean(axis=0).astype(np.float32)
    np.save(OUT / "training_reference.npy", reference)
    predictions = {}
    for model_name in ("mlp", "tcn"):
        for h in HORIZONS:
            for seed in SEEDS:
                if seed != 11 and h != 6:
                    continue
                cell = BASE / model_name / f"h{h}" / f"seed{seed}"
                marker = json.loads((cell / "COMPLETE.json").read_text())
                for key in ("checkpoint", "predictions", "metrics"):
                    assert sha(cell / marker[key]["path"]) == marker[key]["sha256"]
                ck = torch.load(cell / "checkpoint.pt", map_location="cpu", weights_only=False)
                assert (ck["model"], ck["horizon"], ck["seed"]) == (model_name, h, seed)
                net = MLP() if model_name == "mlp" else TCN()
                net.load_state_dict(ck["state_dict"], strict=True)
                net.eval()
                predictions[model_name, h, seed] = (net, pd.read_parquet(cell / "predictions.parquet").set_index(["station_id", "target_time_utc"]))

    rows, feature_rows, lag_rows, attr_arrays = [], [], [], []
    for model_name in ("mlp", "tcn"):
        for sample in samples:
            h, j, i = sample["horizon"], sample["station_index"], sample["target_index"]
            for seed in (SEEDS if h == 6 and sample == next(s for s in samples if s["horizon"] == 6 and s["station_index"] == j and s["target_index"] == np.sort([t["target_index"] for t in samples if t["horizon"] == 6 and t["station_index"] == j])[1]) else (11,)):
                net, saved = predictions[model_name, h, seed]
                x = torch.tensor(xall[i-h-11:i-h+1, j][None, :, None, :].copy(), dtype=torch.float32)
                a = float(anchor[i-h, j])
                key = (int(ids[j]), str(times[i]))
                saved_pred = float(saved.loc[key, "prediction_ug_m3"])

                def forward(inp):
                    pred_z = net(inp)[:, 0] + (torch.log1p(torch.tensor(a)) - mu) / sd
                    return torch.expm1(pred_z * sd + mu)

                with torch.no_grad():
                    pred = float(forward(x)[0])
                eq = abs(pred - saved_pred)
                if eq > 1e-4:
                    raise RuntimeError(f"wrapper mismatch {model_name} h{h} seed{seed} {key}: {eq}")
                primary = np.broadcast_to(reference[j][None, None, None, :], (1, 12, 1, 18)).copy()
                secondary = np.zeros((1, 12, 1, 18), dtype=np.float32)
                secondary[..., 14:] = reference[j, 14:]
                for baseline_name, baseline_array in (("training_mean", primary), ("zero_standardized", secondary)):
                    b = torch.tensor(baseline_array, dtype=torch.float32)
                    attr, delta = IntegratedGradients(forward).attribute(x, baselines=b, n_steps=64,
                                                                       method="gausslegendre", internal_batch_size=16,
                                                                       return_convergence_delta=True)
                    arr = attr.detach().numpy()[0, :, 0, :]
                    delta = float(delta[0])
                    with torch.no_grad():
                        baseline_pred = float(forward(b)[0])
                    relative_delta = abs(delta) / max(1.0, abs(pred - baseline_pred))
                    if not np.isfinite(arr).all() or not np.isfinite(delta):
                        raise RuntimeError("nonfinite IG")
                    row = dict(model=model_name, horizon=h, seed=seed, station_id=int(ids[j]),
                               target_time_utc=str(times[i]), baseline=baseline_name,
                               prediction_ug_m3=pred, saved_prediction_ug_m3=saved_pred,
                               wrapper_abs_error_ug_m3=eq, baseline_prediction_ug_m3=baseline_pred,
                               completeness_delta_ug_m3=delta, completeness_relative=relative_delta,
                               attribution_sum_ug_m3=float(arr.sum()), nonfinite_count=0,
                               quality_flag=int(abs(delta)>0.05 or relative_delta>0.01))
                    rows.append(row)
                    attr_arrays.append(arr)
                    for k, name in enumerate(FEATURES):
                        feature_rows.append(dict(**{q:row[q] for q in ("model","horizon","seed","station_id","target_time_utc","baseline")},
                                                 feature=name, signed_ug_m3=float(arr[:, k].sum()),
                                                 absolute_ug_m3=float(np.abs(arr[:, k]).sum())))
                    for t in range(12):
                        lag_rows.append(dict(**{q:row[q] for q in ("model","horizon","seed","station_id","target_time_utc","baseline")},
                                             lag_hours_before_cutoff=11-t, signed_ug_m3=float(arr[t].sum()),
                                             absolute_ug_m3=float(np.abs(arr[t]).sum())))
                    print("IG", model_name, h, seed, int(ids[j]), str(times[i]), baseline_name, "delta", delta, flush=True)
    write_csv(OUT / "convergence_diagnostics.csv", rows)
    write_csv(OUT / "feature_attributions.csv", feature_rows)
    write_csv(OUT / "temporal_attributions.csv", lag_rows)
    np.savez_compressed(OUT / "attribution_tensors.npz", attributions=np.stack(attr_arrays).astype(np.float32),
                        feature_names=np.array(FEATURES), record_count=len(rows))
    summary = pd.DataFrame(feature_rows).query("seed == 11 and baseline == 'training_mean'").groupby(["model","horizon","station_id","feature"], as_index=False).agg(mean_signed_ug_m3=("signed_ug_m3","mean"),mean_absolute_ug_m3=("absolute_ug_m3","mean"))
    summary.to_csv(OUT / "station_horizon_feature_summary.csv", index=False)
    run_dir = OUT / "runs/ig_v2n"
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "COMPLETE.tmp").write_text("228 IG records and output tables written\n")
    (run_dir / "COMPLETE.tmp").replace(run_dir / "COMPLETE")
    print(json.dumps({"records":len(rows), "max_wrapper_error":max(r["wrapper_abs_error_ug_m3"] for r in rows),
                      "max_abs_delta":max(abs(r["completeness_delta_ug_m3"]) for r in rows),
                      "quality_flags":sum(r["quality_flag"] for r in rows)}), flush=True)


if __name__ == "__main__":
    main()
