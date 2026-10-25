"""W3 paired SRTM node/edge ablation against shuffled, absent, and northing inputs."""
from __future__ import annotations

import datetime as dt
import json
import subprocess

import numpy as np
import pandas as pd
import torch
from torch import nn
import yaml

from scripts.benchmark_v2g import Context, fit
from scripts.summarize_benchmark_v2g import paired_ci
from src.stpignn.evaluation import evaluate_arrays
from src.stpignn.paths import REPO_ROOT


class TerrainEdgeModel(nn.Module):
    def __init__(self, base, terrain):
        super().__init__()
        self.base = base
        self.register_buffer("terrain", terrain)
        self.edge_gate = nn.Linear(3, 1, bias=False)

    def forward(self, x, edge_index, edge_attr, wind, anchor_z):
        edge_effect = self.edge_gate(self.terrain).squeeze(-1)
        conditioned_wind = wind + edge_effect[None,:] * (wind > 0).float()
        return self.base(x, edge_index, edge_attr, conditioned_wind, anchor_z)


class DemContext(Context):
    def __init__(self, horizon, variant, best_model, cfg, seed=42):
        super().__init__(horizon, cfg)
        self.variant = variant
        self.best_model = best_model
        z = np.load(REPO_ROOT/"results/data_v2g_arrays.npz")
        elev = z["elevation_m"].astype(float)
        rng = np.random.default_rng(seed)
        midpoint = self._midpoint_elevation()
        if variant.startswith("shuffle"):
            order = rng.permutation(self.n)
            variant_elev = elev[order]
            midpoint = midpoint[rng.permutation(len(midpoint))]
        elif variant == "none":
            variant_elev = np.zeros_like(elev)
            midpoint = np.zeros_like(midpoint)
        elif variant == "northing_only":
            variant_elev = self.xy[:,1].astype(float)
            midpoint = np.zeros_like(midpoint)
        else:
            variant_elev = elev
        if variant == "none":
            self.features[:,:,12] = 0.0
        else:
            values = (variant_elev-variant_elev.mean())/max(variant_elev.std(),1)
            self.features[:,:,12] = values[None,:]
        s,d = self.edge_index.cpu().numpy()
        length = self.edge_length
        if variant in ("none","northing_only"):
            terrain = np.zeros((len(s),3),np.float32)
        else:
            dz = variant_elev[d]-variant_elev[s]
            slope = dz/np.maximum(length,1)
            crossing = (midpoint > np.maximum(variant_elev[s],variant_elev[d])+5).astype(float)
            terrain = np.stack((dz/100,slope*100,crossing),-1).astype(np.float32)
        self.terrain=torch.as_tensor(terrain,device=self.device)
        self.elevation_used=variant_elev

    def _midpoint_elevation(self):
        s,d=self.edge_index.cpu().numpy()
        path=REPO_ROOT/"results/dem_midpoint_v2g.npy"
        if not path.exists():
            subprocess.run([str(REPO_ROOT/".venv/bin/python"),"-m","scripts.sample_dem_midpoints_v2g"],
                           cwd=REPO_ROOT,check=True)
        values=np.load(path)
        if len(values)!=len(s):
            raise AssertionError("SRTM midpoint array does not match station graph edges")
        endpoint=np.load(REPO_ROOT/"results/data_v2g_arrays.npz")["elevation_m"]
        fallback=(endpoint[s]+endpoint[d])/2
        return np.where(np.isfinite(values),values,fallback)

    def make(self,name):
        model=super().make(name)
        if name==self.best_model:
            return TerrainEdgeModel(model,self.terrain).to(self.device)
        return model

    def forward(self,model,name,x,anchor,wind):
        if isinstance(model,TerrainEdgeModel):
            anchor_z=(torch.log1p(anchor.clamp_min(0))-self.mu)/self.sd
            return model(x,self.edge_index,self.edge_attr,wind,anchor_z)+anchor_z
        return super().forward(model,name,x,anchor,wind)


def main():
    cfg = yaml.safe_load((REPO_ROOT / "configs/benchmark_v2g.yaml").read_text())
    choices = pd.read_csv(REPO_ROOT / "results/benchmark_selection_v2g.csv")
    variants = ["srtm", "none", "northing_only"] + [f"shuffle_{k}" for k in range(1, 6)]
    raw_path = REPO_ROOT / "results/dem_predictions_v2g.parquet"
    raw = pd.read_parquet(raw_path) if raw_path.exists() else pd.DataFrame()
    station_path = REPO_ROOT / "results/dem_station_values_v2g.csv"
    chosen = {}
    for horizon in (1, 24):
        candidates = choices[(choices.horizon_hours == horizon) & choices.model.isin(
            ["gine_gru_wind", "adaptive_graph_st", "stpignn_v2"])].sort_values("validation_mae")
        best = candidates.iloc[0].model
        chosen[horizon] = best
        model_lr = {name: float(choices[(choices.horizon_hours == horizon) &
                                         (choices.model == name)].sort_values("validation_mae").iloc[0].lr)
                    for name in (best, "gru_only")}
        for variant in variants:
            seed_for_variant = 4200 + int(variant.split("_")[-1]) if variant.startswith("shuffle") else 42
            ctx = DemContext(horizon, variant, best, cfg, seed_for_variant)
            for name in (best, "gru_only"):
                for seed in cfg["neural_seeds"]:
                    done = (not raw.empty and ((raw.horizon_hours == horizon) & (raw.variant == variant) &
                                               (raw.model == name) & (raw.seed == seed)).any())
                    if done:
                        continue
                    result, tested = fit(ctx, name, model_lr[name], seed, evaluate_test=True)
                    frame = pd.DataFrame({"horizon_hours": horizon, "variant": variant, "model": name,
                                          "seed": seed, "target_time_utc": ctx.times[tested["time_index"]].astype(str),
                                          "station_id": ctx.station_ids[tested["station_index"]],
                                          "target": tested["truth"], "prediction": tested["pred"]})
                    raw = pd.concat([raw, frame], ignore_index=True)
                    raw.to_parquet(raw_path, index=False)
                    print("DEM", horizon, variant, name, seed, result["test_mae"], flush=True)
            if variant == "srtm" and not station_path.exists():
                station = pd.DataFrame({"station_id": ctx.station_ids, "elevation_m": ctx.elevation_used,
                                        "northing_m": ctx.xy[:, 1]})
                graph = REPO_ROOT / "data/processed/graph"
                mapping = pd.read_parquet(graph / "station_to_topology_node_map.parquet")[["location_id", "node_id"]]
                raw_elevation = pd.read_parquet(graph / "nodes_elevation_true.parquet")[["osmid", "elevation_true"]]
                station = station.merge(mapping, left_on="station_id", right_on="location_id", validate="one_to_one")
                station = station.merge(raw_elevation, left_on="node_id", right_on="osmid", validate="one_to_one")
                if not np.allclose(station.elevation_m, station.elevation_true, rtol=0, atol=1e-4):
                    raise AssertionError("Station SRTM node feature differs from nodes_elevation_true.parquet")
                station.to_csv(station_path, index=False)
    nseeds = raw.groupby(["horizon_hours", "variant", "model", "target_time_utc", "station_id"],
                         sort=False).seed.nunique()
    if nseeds.min() != 5:
        raise AssertionError("Incomplete DEM seed set")
    pooled = raw.groupby(["horizon_hours", "variant", "model", "target_time_utc", "station_id"],
                         as_index=False).agg(target=("target", "first"), prediction=("prediction", "mean"))
    station = pd.read_csv(station_path)
    corr = float(station.elevation_m.corr(station.northing_m))
    rows = []
    comparison = []
    for (horizon, variant, name), part in pooled.groupby(["horizon_hours", "variant", "model"]):
        m = evaluate_arrays(part.prediction, part.target, np.ones(len(part), bool))
        rows.append({"horizon_hours": horizon, "best_validation_model": chosen[horizon],
                     "variant": variant, "model": name, "record_type": "variant", "test_n": m["n"],
                     "test_mae_ug_m3": m["mae"], "test_r2": m["r2"],
                     "elevation_northing_correlation": corr})
    key = ["target_time_utc", "station_id"]
    for horizon, best in chosen.items():
        for name in (best, "gru_only"):
            subset = pooled[(pooled.horizon_hours == horizon) & (pooled.model == name)]
            base = subset[subset.variant == "srtm"].sort_values(key)
            shuffled = subset[subset.variant.str.startswith("shuffle")].groupby(key, as_index=False).agg(
                target=("target", "first"), prediction=("prediction", "mean"))
            for label, other in (("none", subset[subset.variant == "none"]), ("shuffled_mean", shuffled)):
                joined = base[key + ["target", "prediction"]].merge(other[key + ["prediction"]],
                    on=key, suffixes=("_srtm", "_other"), validate="one_to_one")
                if len(joined) != len(base):
                    raise AssertionError("Unequal DEM test masks")
                y = joined.target.to_numpy()
                dates = pd.to_datetime(joined.target_time_utc, utc=True).dt.date.to_numpy()
                dmae, ci, dr2, r2ci = paired_ci(joined.prediction_srtm.to_numpy(),
                    joined.prediction_other.to_numpy(), y, dates, 4303 + horizon, 2000)
                comparison.append({"horizon_hours": horizon, "best_validation_model": best,
                    "model": name, "variant": f"srtm_minus_{label}", "record_type": "paired_bootstrap",
                    "comparison": f"srtm_minus_{label}", "test_n": len(joined),
                    "delta_mae_ug_m3": dmae, "mae_ci_low": ci[0], "mae_ci_high": ci[1],
                    "delta_r2": dr2, "r2_ci_low": r2ci[0], "r2_ci_high": r2ci[1], "met": ci[1] < 0,
                    "elevation_northing_correlation": corr})
    pd.DataFrame(rows + comparison).to_csv(REPO_ROOT / "results/dem_study_v2g.csv", index=False)
    verdict = {h: bool(all(row["met"] for row in comparison if row["horizon_hours"] == h and
                           row["model"] == chosen[h])) for h in chosen}
    print(json.dumps({"best_validation_model_by_horizon": chosen,
                      "elevation_northing_correlation": corr,
                      "dem_criterion_met_by_horizon": verdict,
                      "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"],
                          cwd=REPO_ROOT, text=True).strip(),
                      "timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat()}, indent=2))


if __name__ == "__main__":
    main()
