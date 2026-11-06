"""Rebuild all eligible cutoff-safe outer-fold forecasts from saved checkpoints."""
from __future__ import annotations
import argparse,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
import numpy as np,pandas as pd,torch
from src.stpignn.data_v2 import build
from src.stpignn.models_v2 import make_model
from src.stpignn.station_graph import directed_knn_graph

H=6;HIST=12;BATCH=512

def main():
 ap=argparse.ArgumentParser();ap.add_argument("--station",type=int,required=True);a=ap.parse_args()
 fold=Path(__file__).resolve().parent/"folds"/str(a.station)/"outer"
 ck=torch.load(fold/"best_model.pt",map_location="cpu",weights_only=False)
 data,_=build(ROOT/"configs/data_v2.yaml",excluded_station_id=a.station,weather_half_hour_rule=True,weather_cutoff_safe=True)
 sididx=int(np.flatnonzero(data.station_ids==a.station)[0]);known=data.observed_mask.copy();known[:,sididx]=False
 t=data.times;h=pd.DatetimeIndex(t).hour.to_numpy();dw=pd.DatetimeIndex(t).dayofweek.to_numpy()
 cal=np.stack((np.sin(2*np.pi*h/24),np.cos(2*np.pi*h/24),np.sin(2*np.pi*dw/7),np.cos(2*np.pi*dw/7)),-1).astype(np.float32)
 feat=np.concatenate((data.features,(~known)[...,None].astype(np.float32),np.broadcast_to(cal[:,None,:],(len(t),15,4))),axis=-1)
 feat[:,sididx,:5]=0
 train_y=data.observed_target[data.split_masks["train"]].copy();train_y[:,sididx]=np.nan
 globalmean=float(np.nanmean(train_y));stmean=np.nanmean(train_y,axis=0);stmean=np.where(np.isfinite(stmean),stmean,globalmean)
 ar=data.observed_target.copy();ar[:,sididx]=np.nan
 anchor=pd.DataFrame(ar).ffill().to_numpy(np.float32);anchor=np.where(np.isfinite(anchor),anchor,stmean[None,:])
 mu=float(data.fit["target_log1p_mean"]);sd=float(data.fit["target_log1p_std"])
 edge,length=directed_knn_graph(data.coordinates,4);model=make_model("stpignn_corrected",18,96,1);model.load_state_dict(ck["state_dict"]);model.cuda().eval()
 edge,length=edge.cuda(),length.cuda();rows=[]
 times=np.flatnonzero(data.split_masks["validation"]|data.split_masks["test"])
 with torch.no_grad():
  for lo in range(0,len(times),BATCH):
   target=times[lo:lo+BATCH];target=target[target>=H+HIST-1]
   if not len(target):continue
   cutoff=target-H;win=cutoff[:,None]-np.arange(HIST-1,-1,-1)[None,:]
   assert np.all(win<target[:,None])
   x=torch.as_tensor(feat[win].copy(),device="cuda");an=torch.as_tensor(anchor[cutoff].copy(),device="cuda")
   az=(torch.log1p(an.clamp_min(0))-mu)/sd
   p=torch.expm1((model(x,edge,length)+az)*sd+mu).cpu().numpy()
   if not np.isfinite(p).all():raise ValueError("non-finite source forecast")
   for k,tt in enumerate(target):
    sp="decoder_validation" if data.split_masks["validation"][tt] else "spatial_test"
    for j,sid in enumerate(data.station_ids):
     rows.append((sp,str(t[tt]),str(t[tt-H]),int(sid),float(p[k,j]),a.station))
 out=pd.DataFrame(rows,columns=["split","target_time_utc","cutoff_time_utc","station_id","prediction_ug_m3","outer_heldout_station_id"])
 tmp=fold/"station_forecasts_all.parquet.tmp";out.to_parquet(tmp,index=False);tmp.replace(fold/"station_forecasts_all.parquet")
 print(f"station={a.station} rows={len(out)} validation={int((out.split=='decoder_validation').sum())} test={int((out.split=='spatial_test').sum())}")

if __name__=="__main__":main()
