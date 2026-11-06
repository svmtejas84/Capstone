"""Bounded h=6 corrected station GINE-GRU fit; validation selection only.

Inputs end at target minus 6 hours. The original notebook's road-timeline
copying, modulo indexing and target-hour pollutant input are never used.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import random
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd
import torch

from src.stpignn.data_v2 import build
from src.stpignn.models_v2 import make_model
from src.stpignn.physics_v2 import batched_penalty
from src.stpignn.station_graph import directed_knn_graph

H, HISTORY, SEED, BATCH, MAX_EPOCHS, PATIENCE = 6, 12, 11, 512, 20, 4
LR, WEIGHT_DECAY, LAMBDA = 1e-4, .01, .06


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def atomic_torch(obj, path: Path) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    torch.save(obj, tmp)
    tmp.replace(path)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    args = ap.parse_args()
    out = Path(args.run_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)
    if not torch.cuda.is_available():
        raise RuntimeError("V100 CUDA required for bounded source fit")
    random.seed(SEED); np.random.seed(SEED); torch.manual_seed(SEED); torch.cuda.manual_seed_all(SEED)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    started = time.perf_counter()
    data, _ = build(ROOT / "configs/data_v2.yaml", weather_half_hour_rule=True, weather_cutoff_safe=True)
    times = data.times
    observed = data.observed_mask
    train_hours = np.flatnonzero(data.split_masks["train"] & observed.any(axis=1) & (np.arange(len(times)) >= H+HISTORY-1))
    val_hours = np.flatnonzero(data.split_masks["validation"] & observed.any(axis=1) & (np.arange(len(times)) >= H+HISTORY-1))
    assert len(train_hours) and len(val_hours)
    hour = pd.DatetimeIndex(times).hour.to_numpy()
    dow = pd.DatetimeIndex(times).dayofweek.to_numpy()
    calendar = np.stack((np.sin(2*np.pi*hour/24),np.cos(2*np.pi*hour/24),
                         np.sin(2*np.pi*dow/7),np.cos(2*np.pi*dow/7)),-1).astype(np.float32)
    features = np.concatenate((data.features, (~observed)[...,None].astype(np.float32),
                               np.broadcast_to(calendar[:,None,:],(len(times),len(data.station_ids),4))),axis=-1)
    assert features.shape[-1] == 18
    train_target = data.observed_target[data.split_masks["train"]]
    mean_station = np.nanmean(train_target, axis=0)
    mean_global = float(np.nanmean(train_target))
    mean_station = np.where(np.isfinite(mean_station),mean_station,mean_global)
    anchor = pd.DataFrame(data.observed_target).ffill().to_numpy(dtype=np.float32)
    anchor = np.where(np.isfinite(anchor),anchor,mean_station[None,:]).astype(np.float32)
    mu = float(data.fit["target_log1p_mean"])
    sd = float(data.fit["target_log1p_std"])
    phys_sd = float(data.fit["target_standard_std"])
    edge, length = directed_knn_graph(data.coordinates,4)
    xy = data.coordinates.astype(float); s,d=edge.numpy(); dv=xy[d]-xy[s]
    bearing=(np.rad2deg(np.arctan2(dv[:,0],dv[:,1]))+360)%360
    wind_to=(data.raw_wind_degrees.astype(float)+180)%360
    edge,length=edge.cuda(),length.cuda()
    model=make_model("stpignn_corrected",18,96,1).cuda()
    opt=torch.optim.AdamW(model.parameters(),lr=LR,weight_decay=WEIGHT_DECAY)
    state_path=out/"last_state.pt"; best_path=out/"best_model.pt"; curves_path=out/"curves.csv"
    best=float("inf"); best_epoch=0; stale=0; start_epoch=1; curves=[]
    if state_path.exists():
        state=torch.load(state_path,map_location="cpu",weights_only=False)
        model.load_state_dict(state["model"]);opt.load_state_dict(state["optimizer"])
        best=float(state["best"]);best_epoch=int(state["best_epoch"]);stale=int(state["stale"])
        start_epoch=int(state["epoch"])+1;curves=list(state["curves"])

    def batches(indices,shuffle=False):
        ids=indices.copy()
        if shuffle: np.random.default_rng(SEED*1000+epoch).shuffle(ids)
        for lo in range(0,len(ids),BATCH):
            t=ids[lo:lo+BATCH]; cutoff=t-H
            win=cutoff[:,None]-np.arange(HISTORY-1,-1,-1)[None,:]
            assert win.min()>=0 and np.all(win.max(axis=1)==cutoff) and np.all(win<t[:,None])
            x=torch.as_tensor(features[win].copy(),device="cuda")
            y=torch.as_tensor(np.nan_to_num(data.observed_target[t],nan=0).copy(),device="cuda")
            m=torch.as_tensor(observed[t].copy(),device="cuda")
            a=torch.as_tensor(anchor[cutoff].copy(),device="cuda")
            ang=np.abs((wind_to[cutoff,None]-bearing[None,:]+180)%360-180)
            wm=torch.as_tensor(np.isfinite(wind_to[cutoff,None])&(ang<=37.5),device="cuda")
            yield t,x,y,m,a,wm

    def forward(x,a):
        anchor_z=(torch.log1p(a.clamp_min(0))-mu)/sd
        return model(x,edge,length)+anchor_z

    def validate(collect=False):
        model.eval(); errs=[]; records=[]
        with torch.no_grad():
            for t,x,y,m,a,wm in batches(val_hours):
                pred=torch.expm1(forward(x,a)*sd+mu)
                rr,cc=np.where(m.cpu().numpy())
                pv=pred.cpu().numpy()[rr,cc]; truth=y.cpu().numpy()[rr,cc]
                errs.extend(np.abs(pv-truth).tolist())
                if collect:
                    records.extend(dict(target_time_utc=str(times[t[r]]),station_id=int(data.station_ids[c]),
                                        target_ug_m3=float(truth[k]),prediction_ug_m3=float(pv[k]),
                                        cutoff_time_utc=str(times[t[r]-H])) for k,(r,c) in enumerate(zip(rr,cc)))
        return float(np.mean(errs)), records

    epoch=start_epoch-1
    for epoch in range(start_epoch,MAX_EPOCHS+1):
        model.train(); losses=[]
        for t,x,y,m,a,wm in batches(train_hours,True):
            opt.zero_grad(set_to_none=True)
            z=forward(x,a)
            target_z=(torch.log1p(y.clamp_min(0))-mu)/sd
            data_loss=(((z-target_z).square())*m).sum()/m.sum().clamp_min(1)
            physical=torch.expm1(z*sd+mu)/phys_sd
            phys=batched_penalty(physical,edge,wm,length,"corrected_mask")
            loss=data_loss+LAMBDA*min(1.0,epoch/25.0)*phys
            if not torch.isfinite(loss): raise FloatingPointError(f"nonfinite loss epoch {epoch}")
            loss.backward();torch.nn.utils.clip_grad_norm_(model.parameters(),.3);opt.step()
            losses.append(float(loss.detach()))
        val,_=validate();curves.append({"epoch":epoch,"train_loss":float(np.mean(losses)),"validation_mae":val})
        if val<best:
            best=val;best_epoch=epoch;stale=0
            atomic_torch({"state_dict":{k:v.detach().cpu() for k,v in model.state_dict().items()},
                          "input_channels":18,"edge_dim":1,"horizon_hours":H,"seed":SEED,
                          "feature_fit":data.fit,"weather_cutoff_safe":True,"epoch":epoch},best_path)
        else: stale+=1
        atomic_torch({"model":model.state_dict(),"optimizer":opt.state_dict(),"epoch":epoch,
                      "best":best,"best_epoch":best_epoch,"stale":stale,"curves":curves},state_path)
        pd.DataFrame(curves).to_csv(curves_path,index=False)
        print(f"epoch={epoch} train_loss={np.mean(losses):.6f} val_mae={val:.6f} best={best:.6f}",flush=True)
        if stale>=PATIENCE:break
    ckpt=torch.load(best_path,map_location="cpu",weights_only=False);model.load_state_dict(ckpt["state_dict"])
    val,rows=validate(True)
    pd.DataFrame(rows).to_parquet(out/"validation_predictions.parquet",index=False)
    torch.cuda.synchronize()
    summary={"horizon_hours":H,"seed":SEED,"best_epoch":best_epoch,"epochs_run":epoch,
             "validation_mae_ug_m3":val,"validation_pairs":len(rows),
             "train_target_hours":len(train_hours),"validation_target_hours":len(val_hours),
             "parameter_count":sum(p.numel() for p in model.parameters()),
             "peak_gpu_bytes":torch.cuda.max_memory_allocated(),"wall_seconds":time.perf_counter()-started,
             "best_model_sha256":sha(best_path),"weather_cutoff_safe":True,"target_time_in_input":False}
    (out/"summary.json.tmp").write_text(json.dumps(summary,indent=2)+"\n")
    (out/"summary.json.tmp").replace(out/"summary.json")
    (out/"COMPLETE.tmp").write_text("success\n");(out/"COMPLETE.tmp").replace(out/"COMPLETE")
    print(json.dumps(summary),flush=True)


if __name__=="__main__":main()
