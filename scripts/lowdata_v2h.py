"""W4 fixed-draw low-data station holdout at horizons 1 and 24."""
from __future__ import annotations

import datetime as dt
import json
import subprocess

import numpy as np
import pandas as pd
import torch
import yaml
from sklearn.linear_model import Ridge
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from scripts.benchmark_v2g import Context, fit, score
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
    best_by_horizon={h:choices[(choices.horizon_hours==h)&choices.model.isin(
        ["gine_gru_wind","adaptive_graph_st"])].sort_values("validation_mae").iloc[0].model
        for h in (1,24)}
    out=REPO_ROOT/"results/sensor_density_v2h.csv"
    rows=pd.read_csv(out).to_dict("records") if out.exists() else []
    z=np.load(REPO_ROOT/"results/data_v2g_arrays.npz")
    station_ids=z["station_ids"]
    times=pd.DatetimeIndex(pd.to_datetime(z["times_ns"],utc=True))
    train_period=np.asarray((times>=pd.Timestamp("2022-01-01T00:00:00Z"))&
                            (times<=pd.Timestamp("2025-06-29T23:00:00Z")))
    val_period=np.asarray((times>=pd.Timestamp("2025-07-01T00:00:00Z"))&
                          (times<=pd.Timestamp("2025-09-21T23:00:00Z")))
    observed=z["observed_mask"]
    eligible_by_horizon={}
    for horizon in (1,24):
        best=best_by_horizon[horizon]
        methods=list(dict.fromkeys([best,"gru_only","stpignn_lambda0","stpignn_original","ridge_lag_weather"]))
        train_pairs=(observed[horizon:]&observed[:-horizon]&train_period[horizon:,None]).sum(0)
        val_pairs=(observed[horizon:]&observed[:-horizon]&val_period[horizon:,None]).sum(0)
        eligible=station_ids[train_pairs>0]
        eligible_by_horizon[horizon]=len(eligible)
        val_eligible=set(station_ids[val_pairs>0].tolist())
        lr={name:float(choices[(choices.horizon_hours==horizon)&(choices.model==name)].sort_values("validation_mae").iloc[0].lr)
            for name in methods if name!="ridge_lag_weather"}
        for count in (3,5,10):
            for draw,seed in enumerate(cfg["neural_seeds"],start=1):
                if count>len(eligible):
                    for name in methods:
                        if any(r["horizon_hours"]==horizon and r["train_station_count"]==count and
                               r["draw"]==draw and r["model"]==name for r in rows):
                            continue
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
                    if name=="ridge_lag_weather":
                        train_mask=ctx.observed & ctx.train_period[:,None] & ctx.train_nodes[None,:]
                        train_mask[:horizon]=False
                        train_mask[horizon:] &= ctx.observed[:-horizon]
                        ii,jj=np.where(train_mask)
                        cols=[0]+list(range(5,ctx.features.shape[-1]))
                        x=ctx.features[ii-horizon,jj][:,cols]
                        target=(np.log1p(ctx.y[ii,jj])-ctx.mu)/ctx.sd
                        ridge=Ridge(alpha=1.0).fit(x,target)
                        test_hours=np.zeros(len(ctx.times),bool);test_hours[ctx.hours["test"]]=True
                        ti,sj=np.where(ctx.observed & test_hours[:,None] & ctx.test_nodes[None,:])
                        pred=np.expm1(ridge.predict(ctx.features[ti-horizon,sj][:,cols])*ctx.sd+ctx.mu)
                        metric=score(pred,ctx.y[ti,sj]);result={"test_n":metric["n"],"test_mae":metric["mae"],
                            "test_r2":metric["r2"],"validation_mae":float('nan'),"parameter_count":len(cols)+1,"train_seconds":0.0}
                    else:
                        result,_=fit(ctx,name,lr[name],seed,evaluate_test=True)
                    row={"horizon_hours":horizon,"train_station_count":count,"draw":draw,
                         "draw_seed":4400+count*100+draw,"model_seed":seed,"model":name,
                         "train_station_ids":";".join(map(str,sorted(stations.tolist()))),
                         "test_station_count":int(ctx.test_nodes.sum()),"test_n":result["test_n"],
                         "test_mae_ug_m3":result["test_mae"],"test_r2":result["test_r2"],
                         "validation_mae":result["validation_mae"],"lr":lr.get(name),
                         "parameter_count":result["parameter_count"],"train_seconds":result["train_seconds"]}
                    row["status"]="scored"
                    rows.append(row)
                    pd.DataFrame(rows).to_csv(out,index=False)
                    print("LOWDATA",horizon,count,draw,name,row["test_mae_ug_m3"],flush=True)
    frame=pd.DataFrame(rows)
    means=frame[frame.status=="scored"].groupby(["horizon_hours","model","train_station_count"]).test_mae_ug_m3.mean()
    verdict={}
    for horizon in (1,24):
        best=best_by_horizon[horizon]
        methods=list(dict.fromkeys([best,"gru_only","stpignn_lambda0","stpignn_original","ridge_lag_weather"]))
        change={name:float(means[horizon,name,3]-means[horizon,name,5]) for name in methods}
        verdict[horizon]={"mae_change_3_minus_5":change,
                          "ten_station_case":f"BLOCKED: only {eligible_by_horizon[horizon]} stations have observed-lag training pairs",
                          "physics_degrades_less_than_controls_3_vs_5":all(change["stpignn_original"]<change[c]
                              for c in (best,"gru_only","stpignn_lambda0"))}
    (REPO_ROOT/"results/sensor_density_verdict_v2h.json").write_text(json.dumps({
        "best_validation_model_by_horizon":best_by_horizon,"verdict":verdict,"script":"scripts/lowdata_v2h.py",
        "config":"configs/benchmark_v2g.yaml","seeds":cfg["neural_seeds"],
        "source_commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=REPO_ROOT,text=True).strip(),
        "timestamp_utc":dt.datetime.now(dt.timezone.utc).isoformat()},indent=2)+"\n")
    summary=frame[frame.status=="scored"].groupby(["horizon_hours","model","train_station_count"]).agg(
        mae_mean=("test_mae_ug_m3","mean"),mae_sd=("test_mae_ug_m3","std"),
        r2_mean=("test_r2","mean"),r2_sd=("test_r2","std"),draws=("draw","nunique")).reset_index()
    summary.to_csv(REPO_ROOT/"results/sensor_density_summary_v2h.csv",index=False)
    fig,axes=plt.subplots(2,2,figsize=(10,7),sharex=True)
    for col,h in enumerate((1,24)):
        for name,g in summary[summary.horizon_hours==h].groupby("model"):
            axes[0,col].errorbar(g.train_station_count,g.mae_mean,yerr=g.mae_sd,marker='o',capsize=3,label=name)
            axes[1,col].errorbar(g.train_station_count,g.r2_mean,yerr=g.r2_sd,marker='o',capsize=3,label=name)
        axes[0,col].set_title(f'h={h} hours')
        for row in (0,1):
            ax=axes[row,col];ax.set_xticks([3,5,10]);ax.set_xlabel('Training stations')
            ax.text(10,ax.get_ylim()[1]*.94,'10 blocked',ha='right',fontsize=8)
    axes[0,0].set_ylabel('Held-out station MAE (µg/m³)')
    axes[1,0].set_ylabel('Held-out station R²')
    axes[0,1].legend(fontsize=7,loc='upper left',bbox_to_anchor=(1,1))
    fig.tight_layout();fig.savefig(REPO_ROOT/'figures/sensor_density.pdf',bbox_inches='tight');plt.close(fig)
    print(json.dumps(verdict,indent=2))


if __name__=="__main__":
    main()
