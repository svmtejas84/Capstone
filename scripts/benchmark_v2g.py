"""Validation-selected five-seed W2 horizon benchmark on repaired inputs."""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import json
import random
import shutil
import subprocess
import time
import warnings

import numpy as np
import pandas as pd
import torch
import yaml
from sklearn.linear_model import Ridge

from src.stpignn.evaluation import evaluate_arrays
from src.stpignn.models_v2 import make_model
from src.stpignn.models_v3 import make_model_v3
from src.stpignn.paths import REPO_ROOT
from src.stpignn.physics_v2 import batched_penalty
from src.stpignn.station_graph import directed_knn_graph

NAMES = ["gine_gru_wind", "adaptive_graph_st", "adaptive_graph_st_fixed_knn",
         "stpignn_v2", "stpignn_v2_source_removed", "stpignn_v2_transport_removed",
         "gru_only", "vanilla_gcn", "st_gru_gcn", "stpignn_original",
         "stpignn_lambda0", "stpignn_laplacian"]
BASELINES = ["persistence", "same_hour_yesterday", "climatology_hod_dow",
             "station_train_mean", "ridge_lag_calendar_weather"]


def seed_all(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.benchmark = False


def score(p, y):
    return evaluate_arrays(np.asarray(p), np.asarray(y), np.ones(len(y), bool))


class Context:
    def __init__(self, horizon, config):
        self.cfg = config
        self.horizon = horizon
        data_cfg = yaml.safe_load((REPO_ROOT / "configs/data_v2.yaml").read_text())
        z = np.load(REPO_ROOT / "results/data_v2g_arrays.npz")
        old_fit = json.loads((REPO_ROOT / "results/input_fix_v2g.json").read_text())
        self.mu = float(old_fit["channels"][0]["log1p_mean"])
        self.sd = float(old_fit["channels"][0]["log1p_sd"])
        self.physical_scale = float(json.loads((REPO_ROOT / "results/data_v2_fit.json").read_text())["fit"]["target_standard_std"])
        self.times = pd.DatetimeIndex(pd.to_datetime(z["times_ns"], utc=True))
        self.y = z["observed_target"]
        self.observed = z["observed_mask"]
        self.station_ids = z["station_ids"]
        self.xy = z["coordinates"]
        self.n = len(self.station_ids)
        self.history = int(data_cfg["history_hours"])
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        train_period = np.asarray((self.times >= pd.Timestamp(data_cfg["train_start_utc"])) &
                                  (self.times <= pd.Timestamp(data_cfg["train_end_utc"])))
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            station_mean = np.nanmean(self.y[train_period], axis=0)
        station_mean = np.where(np.isfinite(station_mean), station_mean, np.nanmean(self.y[train_period]))
        self.station_mean = station_mean.astype(np.float32)
        ffill = pd.DataFrame(self.y).ffill().to_numpy(dtype=np.float32)
        self.anchor = np.where(np.isfinite(ffill), ffill, self.station_mean[None, :]).astype(np.float32)
        hour = self.times.hour.to_numpy()
        dow = self.times.dayofweek.to_numpy()
        calendar = np.stack((np.sin(2*np.pi*hour/24), np.cos(2*np.pi*hour/24),
                             np.sin(2*np.pi*dow/7), np.cos(2*np.pi*dow/7)), -1).astype(np.float32)
        self.features = np.concatenate((z["features"], (~self.observed)[..., None].astype(np.float32),
                                        np.broadcast_to(calendar[:, None, :], (len(self.times), self.n, 4))), -1)
        self.edge_index, distance = directed_knn_graph(self.xy, int(config["station_graph_neighbours"]))
        self.edge_length = distance.numpy()[:, 0]
        self.edge_distance = distance.to(self.device)
        self.edge_attr = torch.log1p(distance).to(self.device)
        s, d = self.edge_index.numpy()
        delta = self.xy[d] - self.xy[s]
        bearing = np.arctan2(delta[:, 0], delta[:, 1])
        wind_towards = np.deg2rad((z["raw_wind_degrees"].astype(float) + 180) % 360)
        speed = np.maximum(0, z["features"][:, 0, 5] * self._old_feature_sd(5) + self._old_feature_mean(5))
        along = speed[:, None] * np.cos(wind_towards[:, None] - bearing[None, :])
        self.wind_along = np.nan_to_num(along, nan=0).astype(np.float32)
        angle = np.abs(np.angle(np.exp(1j * (wind_towards[:, None] - bearing[None, :]))))
        self.corrected_wind_mask = np.isfinite(wind_towards[:, None]) & (angle <= np.deg2rad(37.5))
        self.edge_index = self.edge_index.to(self.device)
        self.hours = {}
        for name in ("train", "validation", "test"):
            period = np.asarray((self.times >= pd.Timestamp(data_cfg[f"{name}_start_utc"])) &
                                (self.times <= pd.Timestamp(data_cfg[f"{name}_end_utc"])))
            period[:self.history - 1 + horizon] = False
            eligible = self.observed & period[:, None]
            if name != "test":
                eligible &= self.observed[np.arange(len(self.times)) - horizon]
            self.hours[name] = np.flatnonzero(eligible.any(1))
        self.train_period = train_period

    def _old_feature_mean(self, j):
        if not hasattr(self, "_old_fit"):
            self._old_fit = json.loads((REPO_ROOT / "results/data_v2_fit.json").read_text())["fit"]
        return self._old_fit["feature_means"][j]

    def _old_feature_sd(self, j):
        if not hasattr(self, "_old_fit"):
            self._old_fit = json.loads((REPO_ROOT / "results/data_v2_fit.json").read_text())["fit"]
        return self._old_fit["feature_stds"][j]

    def batches(self, name, shuffle_seed=None):
        hours = self.hours[name].copy()
        if shuffle_seed is not None:
            np.random.default_rng(shuffle_seed).shuffle(hours)
        for start in range(0, len(hours), int(self.cfg["neural_batch_size"])):
            index = hours[start:start + int(self.cfg["neural_batch_size"])]
            cutoff = index - self.horizon
            window = cutoff[:, None] - np.arange(self.history - 1, -1, -1)[None, :]
            assert (window >= 0).all() and (window <= cutoff[:, None]).all()
            x = torch.as_tensor(self.features[window].copy(), device=self.device)
            y = torch.as_tensor(np.nan_to_num(self.y[index], nan=0).copy(), device=self.device)
            valid = self.observed[index].copy()
            if name != "test":
                valid &= self.observed[cutoff]
            mask = torch.as_tensor(valid, device=self.device)
            anchor = torch.as_tensor(self.anchor[cutoff].copy(), device=self.device)
            wind = torch.as_tensor(self.wind_along[cutoff].copy(), device=self.device)
            yield index, x, y, mask, anchor, wind

    def make(self, name):
        if name in ("gru_only", "vanilla_gcn", "st_gru_gcn"):
            return make_model(name, self.features.shape[-1], int(self.cfg["neural_hidden_dim"]), 1).to(self.device)
        if name.startswith("stpignn_") and name not in ("stpignn_v2", "stpignn_v2_source_removed", "stpignn_v2_transport_removed"):
            return make_model("stpignn_corrected", self.features.shape[-1], int(self.cfg["neural_hidden_dim"]), 1).to(self.device)
        return make_model_v3(name, self.features.shape[-1], int(self.cfg["neural_hidden_dim"]),
                             self.n, self.mu, self.sd).to(self.device)

    def forward(self, model, name, x, anchor, wind):
        anchor_z = (torch.log1p(anchor.clamp_min(0)) - self.mu) / self.sd
        if name in ("gru_only", "vanilla_gcn", "st_gru_gcn") or name.startswith("stpignn_original") or name in ("stpignn_lambda0", "stpignn_laplacian"):
            residual = model(x, self.edge_index, self.edge_distance)
        else:
            residual = model(x, self.edge_index, self.edge_attr, wind, anchor_z)
        return residual + anchor_z

    def evaluate(self, model, name, split, collect=False):
        model.eval()
        preds, truths, ti, sj = [], [], [], []
        with torch.no_grad():
            for index, x, y, mask, anchor, wind in self.batches(split):
                z = self.forward(model, name, x, anchor, wind)
                pred = torch.expm1(z * self.sd + self.mu)
                rows, cols = np.where(mask.cpu().numpy())
                preds.append(pred.cpu().numpy()[rows, cols])
                truths.append(y.cpu().numpy()[rows, cols])
                if collect:
                    ti.append(index[rows]); sj.append(cols)
        p, y = np.concatenate(preds), np.concatenate(truths)
        result = score(p, y)
        if collect:
            result.update(pred=p, truth=y, time_index=np.concatenate(ti), station_index=np.concatenate(sj))
        return result


def fit(ctx, name, lr, seed, evaluate_test=False, return_model=False):
    seed_all(seed)
    model = ctx.make(name)
    optimizer = torch.optim.AdamW(model.parameters(), lr=float(lr), weight_decay=float(ctx.cfg["neural_weight_decay"]))
    best, best_state, best_epoch, stale = float("inf"), None, 0, 0
    started = time.perf_counter()
    for epoch in range(1, int(ctx.cfg["neural_max_epochs"]) + 1):
        model.train()
        for index, x, y, mask, anchor, wind in ctx.batches("train", seed*1000+epoch):
            optimizer.zero_grad(set_to_none=True)
            z = ctx.forward(model, name, x, anchor, wind)
            target_z = (torch.log1p(y.clamp_min(0)) - ctx.mu) / ctx.sd
            loss = ((z - target_z).square() * mask).sum() / mask.sum().clamp_min(1)
            if name in ("stpignn_original", "stpignn_laplacian"):
                physical = torch.expm1(z * ctx.sd + ctx.mu) / ctx.physical_scale
                edge_wind = torch.as_tensor(ctx.corrected_wind_mask[index - ctx.horizon].copy(),
                                            device=ctx.device)
                variant = "laplacian" if name.endswith("laplacian") else "corrected_mask"
                loss = loss + float(ctx.cfg["lambda_original"]) * min(1.0, epoch / 25.0) * batched_penalty(
                    physical, ctx.edge_index, edge_wind, ctx.edge_distance, variant)
            if not torch.isfinite(loss):
                raise FloatingPointError(f"nonfinite loss {name} h{ctx.horizon} seed{seed} epoch{epoch}")
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 0.3)
            optimizer.step()
        val = ctx.evaluate(model, name, "validation")["mae"]
        if val < best:
            best, best_epoch, stale = val, epoch, 0
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
        else:
            stale += 1
            if stale >= int(ctx.cfg["neural_early_stopping_patience"]):
                break
    model.load_state_dict(best_state)
    result = {"model": name, "horizon_hours": ctx.horizon, "seed": seed, "lr": float(lr),
              "best_epoch": best_epoch, "validation_mae": best, "epochs_run": epoch,
              "parameter_count": sum(p.numel() for p in model.parameters()),
              "train_seconds": time.perf_counter() - started}
    if "tail" in ctx.hours:
        result["train_tail_bias"] = ctx.evaluate(model, name, "tail")["bias"]
    if evaluate_test:
        tested = ctx.evaluate(model, name, "test", collect=True)
        result.update(test_mae=tested["mae"], test_r2=tested["r2"], test_n=tested["n"])
        if hasattr(model, "diffusion_raw"):
            result["learned_diffusion"] = float(torch.nn.functional.softplus(model.diffusion_raw).detach())
            result["learned_source_mean"] = (float(model.last_source_mean) if model.last_source_mean is not None else None)
        return (result, tested, model) if return_model else (result, tested)
    return (result, None, model) if return_model else (result, None)


def baselines(ctx):
    y = ctx.y
    station_mean = ctx.station_mean
    keys = ctx.times.hour.to_numpy() * 7 + ctx.times.dayofweek.to_numpy()
    climat = np.full((168, ctx.n), np.nan, dtype=np.float32)
    for key in range(168):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            climat[key] = np.nanmedian(y[ctx.train_period & (keys == key)], axis=0)
    i_train, j_train = np.where(ctx.observed & ctx.train_period[:, None] &
                                np.roll(ctx.observed, ctx.horizon, axis=0))
    valid_train = i_train >= ctx.history - 1 + ctx.horizon
    i_train, j_train = i_train[valid_train], j_train[valid_train]
    ridge_cols = [0] + list(range(5, ctx.features.shape[-1]))
    x_train = ctx.features[i_train - ctx.horizon, j_train][:, ridge_cols]
    target_z = (np.log1p(y[i_train, j_train]) - ctx.mu) / ctx.sd
    ridge = Ridge(alpha=1.0).fit(x_train, target_z)
    rows = []
    for split in ("validation", "test"):
        i, j = np.where(ctx.observed & np.isin(np.arange(len(ctx.times)), ctx.hours[split])[:, None])
        cutoff = i - ctx.horizon
        anchor = ctx.anchor[cutoff, j]
        yesterday = ctx.anchor[i - 24, j]
        climate = climat[keys[i], j]
        climate = np.where(np.isfinite(climate), climate, station_mean[j])
        pred = {"persistence": anchor, "same_hour_yesterday": yesterday,
                "climatology_hod_dow": climate, "station_train_mean": station_mean[j],
                "ridge_lag_calendar_weather": np.expm1(ridge.predict(ctx.features[cutoff, j][:, ridge_cols]) * ctx.sd + ctx.mu)}
        for name, values in pred.items():
            m = score(values, y[i, j])
            rows.append({"model": name, "horizon_hours": ctx.horizon, "split": split,
                         "seed": None, "test_mae": m["mae"], "test_r2": m["r2"], "test_n": m["n"]})
        if split == "test":
            frame = pd.DataFrame({"model": np.repeat(list(pred), len(i)),
                                  "seed": 0, "horizon_hours": ctx.horizon,
                                  "target_time_utc": np.tile(ctx.times[i].astype(str), len(pred)),
                                  "station_id": np.tile(ctx.station_ids[j], len(pred)),
                                  "target_ug_m3": np.tile(y[i, j], len(pred)),
                                  "prediction_ug_m3": np.concatenate(list(pred.values()))})
            frame.to_parquet(REPO_ROOT / f"results/benchmark_predictions_h{ctx.horizon}_baselines_v2g.parquet", index=False)
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--horizon", type=int, required=True)
    parser.add_argument("--models", nargs="*", default=NAMES)
    parser.add_argument("--refresh-baselines", action="store_true")
    parser.add_argument("--refresh-models", nargs="*", default=[])
    args = parser.parse_args()
    cfg = yaml.safe_load((REPO_ROOT / "configs/benchmark_v2g.yaml").read_text())
    if args.horizon not in cfg["horizons_hours"]:
        raise ValueError(args.horizon)
    ctx = Context(args.horizon, cfg)
    rows_path = REPO_ROOT / "results/benchmark_runs_v2g.csv"
    rows = pd.read_csv(rows_path).to_dict("records") if rows_path.exists() else []
    selection_path = REPO_ROOT / "results/benchmark_selection_v2g.csv"
    if args.refresh_models:
        old_rows = [r for r in rows if r["horizon_hours"] == args.horizon and r["model"] in args.refresh_models]
        if old_rows:
            pd.DataFrame(old_rows).to_csv(REPO_ROOT / f"results/benchmark_provisional_h{args.horizon}_v2g.csv", index=False)
        rows = [r for r in rows if not (r["horizon_hours"] == args.horizon and r["model"] in args.refresh_models)]
        pd.DataFrame(rows).to_csv(rows_path, index=False)
        if selection_path.exists():
            choices = pd.read_csv(selection_path)
            old_choices = choices[(choices.horizon_hours == args.horizon) & choices.model.isin(args.refresh_models)]
            if len(old_choices):
                old_choices.to_csv(REPO_ROOT / f"results/benchmark_selection_provisional_h{args.horizon}_v2g.csv", index=False)
            choices = choices[~((choices.horizon_hours == args.horizon) & choices.model.isin(args.refresh_models))]
            choices.to_csv(selection_path, index=False)
        for name in args.refresh_models:
            for path in glob.glob(str(REPO_ROOT / f"results/benchmark_predictions_h{args.horizon}_{name}_seed*_v2g.parquet")):
                shutil.copy2(path, path.replace("_v2g.parquet", "_provisional_v2g.parquet"))
    if args.refresh_baselines:
        rows = [r for r in rows if not (r["horizon_hours"] == args.horizon and r["model"] in BASELINES)]
    if not any(r["horizon_hours"] == args.horizon and r["model"] == "persistence" and r["split"] == "test" for r in rows):
        rows.extend(baselines(ctx)); pd.DataFrame(rows).to_csv(rows_path, index=False)
    for name in args.models:
        choices = pd.read_csv(selection_path).to_dict("records") if selection_path.exists() else []
        for lr in cfg["neural_lr_grid"]:
            if any(r["model"] == name and r["horizon_hours"] == args.horizon and np.isclose(r["lr"], lr) for r in choices):
                continue
            result, _ = fit(ctx, name, lr, cfg["neural_seeds"][0])
            choices.append(result)
            pd.DataFrame(choices).to_csv(selection_path, index=False)
            print("SELECT", result, flush=True)
        candidate = pd.DataFrame(choices)
        chosen = candidate[(candidate.model == name) & (candidate.horizon_hours == args.horizon)].sort_values("validation_mae").iloc[0]
        for seed in cfg["neural_seeds"]:
            if any(r["model"] == name and r["horizon_hours"] == args.horizon and r["split"] == "test" and r["seed"] == seed for r in rows):
                continue
            result, tested = fit(ctx, name, float(chosen.lr), seed, evaluate_test=True)
            result["split"] = "test"
            rows.append(result)
            pd.DataFrame(rows).to_csv(rows_path, index=False)
            frame = pd.DataFrame({"model": name, "seed": seed, "horizon_hours": args.horizon,
                                  "target_time_utc": ctx.times[tested["time_index"]].astype(str),
                                  "station_id": ctx.station_ids[tested["station_index"]],
                                  "target_ug_m3": tested["truth"], "prediction_ug_m3": tested["pred"]})
            frame.to_parquet(REPO_ROOT / f"results/benchmark_predictions_h{args.horizon}_{name}_seed{seed}_v2g.parquet", index=False)
            print("FINAL", result, flush=True)
    print("DONE", args.horizon, dt.datetime.now(dt.timezone.utc).isoformat(),
          subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True).strip(), flush=True)


if __name__ == "__main__":
    main()
