"""W4 fixed-draw low-data station holdout at horizons 1 and 6."""
from __future__ import annotations

import datetime as dt
import json
import subprocess

import numpy as np
import pandas as pd
import torch
import yaml

from scripts.benchmark_v2g import Context, fit
from src.stpignn.paths import REPO_ROOT


class LowDataContext(Context):
    def __init__(self,horizon,cfg,train_stations):
        super().__init__(horizon,cfg)
        self.train_nodes=np.isin(self.station_ids,train_stations)
        self.test_nodes=~self.train_nodes
        self.features[:,self.test_nodes,:5]=0.0
        self.features[:,self.test_nodes,13]=1.0
        train_period=np.asarray((self.times>=pd.Timestamp("2022-01-01T00:00:00Z"))&
                                (self.times<=pd.Timestamp("2025-06-29T23:00:00Z")))
        global_mean=float(np.nanmean(self.y[train_period][:,self.train_nodes]))
        self.anchor[:,self.test_nodes]=global_mean
        for split in ("train","validation","test"):
            nodes=self.test_nodes if split=="test" else self.train_nodes
            eligible=np.zeros(len(self.times),bool)
            eligible[self.hours[split]]=True
            mask=self.observed & eligible[:,None] & nodes[None,:]
            if split!="test":
                mask[self.horizon:] &= self.observed[:-self.horizon]
            self.hours[split]=np.flatnonzero(mask.any(1))

    def batches(self,name,shuffle_seed=None):
        for idx,x,y,mask,anchor,wind in super().batches(name,shuffle_seed):
            x[:,:,self.test_nodes,:5]=0.0
            x[:,:,self.test_nodes,13]=1.0
            selected=self.test_nodes if name=="test" else self.train_nodes
            mask &= torch.as_tensor(selected[None,:],device=self.device)
            yield idx,x,y,mask,anchor,wind


def main():
    cfg=yaml.safe_load((REPO_ROOT/"configs/benchmark_v2g.yaml").read_text())
    choices=pd.read_csv(REPO_ROOT/"results/benchmark_selection_v2g.csv")
    h1=choices[(choices.horizon_hours==1)&choices.model.isin(
        ["gine_gru_wind","adaptive_graph_st","stpignn_v2"])].sort_values("validation_mae")
    best=h1.iloc[0].model
    methods=list(dict.fromkeys([best,"stpignn_v2","gru_only","stpignn_lambda0"]))
    out=REPO_ROOT/"results/lowdata_v2g.csv"
    rows=pd.read_csv(out).to_dict("records") if out.exists() else []
    z=np.load(REPO_ROOT/"results/data_v2g_arrays.npz")
    station_ids=z["station_ids"]
    times=pd.DatetimeIndex(pd.to_datetime(z["times_ns"],utc=True))
    train_period=np.asarray((times>=pd.Timestamp("2022-01-01T00:00:00Z"))&
                            (times<=pd.Timestamp("2025-06-29T23:00:00Z")))
    val_period=np.asarray((times>=pd.Timestamp("2025-07-01T00:00:00Z"))&
                          (times<=pd.Timestamp("2025-09-21T23:00:00Z")))
    observed=z["observed_mask"]
    for horizon in (1,6):
        train_pairs=(observed[horizon:]&observed[:-horizon]&train_period[horizon:,None]).sum(0)
        val_pairs=(observed[horizon:]&observed[:-horizon]&val_period[horizon:,None]).sum(0)
        eligible=station_ids[train_pairs>0]
        val_eligible=set(station_ids[val_pairs>0].tolist())
        lr={name:float(choices[(choices.horizon_hours==horizon)&(choices.model==name)].sort_values("validation_mae").iloc[0].lr)
            for name in methods}
        for count in (3,5,10):
            for draw,seed in enumerate(cfg["neural_seeds"],start=1):
                if count>len(eligible):
                    for name in methods:
                        rows.append({"horizon_hours":horizon,"train_station_count":count,"draw":draw,
                                     "draw_seed":4400+count*100+draw,"model_seed":seed,"model":name,
                                     "status":f"BLOCKED: only {len(eligible)} stations have observed-lag training pairs"})
                    pd.DataFrame(rows).to_csv(out,index=False)
                    continue
                rng=np.random.default_rng(4400+count*100+draw)
                for _ in range(100):
                    stations=rng.choice(eligible,count,replace=False)
                    if any(int(s) in val_eligible for s in stations):
                        break
                else:
                    raise RuntimeError("No validation-covered station draw")
                ctx=LowDataContext(horizon,cfg,stations)
                for name in methods:
                    if any(r["horizon_hours"]==horizon and r["train_station_count"]==count and
                           r["draw"]==draw and r["model"]==name for r in rows):
                        continue
                    result,tested=fit(ctx,name,lr[name],seed,evaluate_test=True)
                    row={"horizon_hours":horizon,"train_station_count":count,"draw":draw,
                         "draw_seed":4400+count*100+draw,"model_seed":seed,"model":name,
                         "train_station_ids":";".join(map(str,sorted(stations.tolist()))),
                         "test_station_count":int(ctx.test_nodes.sum()),"test_n":result["test_n"],
                         "test_mae_ug_m3":result["test_mae"],"test_r2":result["test_r2"],
                         "validation_mae":result["validation_mae"],"lr":lr[name],
                         "parameter_count":result["parameter_count"],"train_seconds":result["train_seconds"]}
                    row["status"]="scored"
                    rows.append(row)
                    pd.DataFrame(rows).to_csv(out,index=False)
                    print("LOWDATA",horizon,count,draw,name,row["test_mae_ug_m3"],flush=True)
    frame=pd.DataFrame(rows)
    means=frame[frame.status=="scored"].groupby(["horizon_hours","model","train_station_count"]).test_mae_ug_m3.mean()
    verdict={}
    for horizon in (1,6):
        change={name:float(means[horizon,name,3]-means[horizon,name,5]) for name in methods}
        verdict[horizon]={"mae_change_3_minus_5":change,
                          "ten_station_case":f"BLOCKED: only {len(eligible)} stations have observed-lag training pairs",
                          "physics_degrades_less_than_controls_3_vs_5":all(change["stpignn_v2"]<change[c]
                              for c in ("gru_only","stpignn_lambda0"))}
    (REPO_ROOT/"results/lowdata_verdict_v2g.json").write_text(json.dumps({
        "best_validation_model":best,"verdict":verdict,"script":"scripts/lowdata_v2g.py",
        "config":"configs/benchmark_v2g.yaml","seeds":cfg["neural_seeds"],
        "source_commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=REPO_ROOT,text=True).strip(),
        "timestamp_utc":dt.datetime.now(dt.timezone.utc).isoformat()},indent=2)+"\n")
    print(json.dumps(verdict,indent=2))


if __name__=="__main__":
    main()
