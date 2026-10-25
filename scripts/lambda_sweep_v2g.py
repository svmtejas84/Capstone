"""W7 fixed lambda sweep for corrected and Laplacian ST-PIGNN references."""
from __future__ import annotations

import datetime as dt
import json
import subprocess

import numpy as np
import pandas as pd
import torch
import yaml
from scipy.stats import t

from scripts.benchmark_v2g import Context, fit
from src.stpignn.paths import REPO_ROOT

LAMBDAS=(0.0,0.06,0.3,1.0,3.0,10.0)
THRESHOLDS=(0.0,0.01,0.05,0.1)


def physics_stats(ctx,model,name):
    counts=np.zeros(len(THRESHOLDS),float)
    violations=np.zeros(len(THRESHOLDS),float)
    abs_sum=0.0; edges=0
    source,dest=ctx.edge_index
    model.eval()
    with torch.no_grad():
        for idx,x,_,_,anchor,wind in ctx.batches("test"):
            z=ctx.forward(model,name,x,anchor,wind)
            physical=torch.expm1(z*ctx.sd+ctx.mu)
            diff=(physical[:,dest]-physical[:,source])/ctx.physical_scale
            wind_mask=torch.as_tensor(ctx.corrected_wind_mask[idx-ctx.horizon].copy(),device=ctx.device)
            active=diff[wind_mask]
            for k,threshold in enumerate(THRESHOLDS):
                counts[k]+=active.numel()
                violations[k]+=(active>threshold).sum().item()
            abs_sum+=torch.abs(physical[:,dest]-physical[:,source]).sum().item()
            edges+=diff.numel()
    return {**{f"pvr_{threshold:g}_percent":float(100*violations[k]/counts[k]) if counts[k] else None
               for k,threshold in enumerate(THRESHOLDS)},
            "mean_abs_edge_difference_ug_m3":abs_sum/edges,"active_edges":int(counts[0])}


def paired_seed_ci(a,b):
    difference=np.asarray(a,float)-np.asarray(b,float)
    mean=float(difference.mean())
    half=float(t.ppf(0.975,len(difference)-1)*difference.std(ddof=1)/np.sqrt(len(difference)))
    return mean,[mean-half,mean+half]


def main():
    cfg=yaml.safe_load((REPO_ROOT/"configs/benchmark_v2g.yaml").read_text())
    choices=pd.read_csv(REPO_ROOT/"results/benchmark_selection_v2g.csv")
    names=("stpignn_original","stpignn_laplacian")
    lr={name:float(choices[(choices.horizon_hours==1)&(choices.model==name)].sort_values("validation_mae").iloc[0].lr)
        for name in names}
    path=REPO_ROOT/"results/lambda_sweep_v2g.csv"
    rows=pd.read_csv(path).to_dict("records") if path.exists() else []
    for name in names:
        for lam in LAMBDAS:
            local=dict(cfg,lambda_original=lam)
            ctx=Context(1,local)
            for seed in cfg["neural_seeds"]:
                if any(r["model"]==name and np.isclose(r["lambda"],lam) and r["seed"]==seed for r in rows):
                    continue
                result,_,model=fit(ctx,name,lr[name],seed,evaluate_test=True,return_model=True)
                row={"model":name,"lambda":lam,"seed":seed,"lr":lr[name],
                     "best_epoch":result["best_epoch"],"validation_mae":result["validation_mae"],
                     "test_n":result["test_n"],"test_mae_ug_m3":result["test_mae"],
                     "test_r2":result["test_r2"],"parameter_count":result["parameter_count"],
                     "train_seconds":result["train_seconds"],**physics_stats(ctx,model,name)}
                rows.append(row)
                pd.DataFrame(rows).to_csv(path,index=False)
                print("LAMBDA",name,lam,seed,row["test_mae_ug_m3"],flush=True)
    frame=pd.DataFrame(rows)
    result={}
    for name in names:
        val=frame[frame.model==name].groupby("lambda").validation_mae.mean()
        selected=float(val.idxmin())
        sub=frame[frame.model==name].set_index(["lambda","seed"])
        a=sub.loc[selected].sort_index(); b=sub.loc[0.0].sort_index()
        dmae,mae_ci=paired_seed_ci(a.test_mae_ug_m3,b.test_mae_ug_m3)
        dpvr,pvr_ci=paired_seed_ci(a["pvr_0_percent"],b["pvr_0_percent"])
        result[name]={"validation_selected_lambda":selected,"delta_test_mae_vs_zero":dmae,
                      "delta_test_mae_ci":mae_ci,"delta_pvr0_vs_zero":dpvr,"delta_pvr0_ci":pvr_ci,
                      "mae_and_pvr_improve":bool(mae_ci[1]<0 and pvr_ci[1]<0)}
    (REPO_ROOT/"results/lambda_verdict_v2g.json").write_text(json.dumps({
        "verdict":result,"script":"scripts/lambda_sweep_v2g.py","config":"configs/benchmark_v2g.yaml",
        "seeds":cfg["neural_seeds"],"source_commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=REPO_ROOT,text=True).strip(),
        "timestamp_utc":dt.datetime.now(dt.timezone.utc).isoformat()},indent=2)+"\n")
    print(json.dumps(result,indent=2))


if __name__=="__main__":
    main()
