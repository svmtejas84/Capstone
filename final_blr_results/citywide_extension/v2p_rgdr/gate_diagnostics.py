"""Train/validation-only diagnostic for RGDR eligible-edge density; no model fit."""
from pathlib import Path
import numpy as np
import pandas as pd
import yaml

from src.stpignn.station_graph import directed_knn_graph

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
z=np.load(ROOT/"final_blr_results/baselines/v2m/data/data_v2m_arrays.npz")
cfg=yaml.safe_load((ROOT/"configs/data_v2.yaml").read_text())
times=pd.DatetimeIndex(pd.to_datetime(z["times_ns"],utc=True))
obs=z["observed_mask"]
xy=z["coordinates"].astype(float)
edge,length=directed_knn_graph(xy,4)
src,dst=edge.numpy()
delta=xy[dst]-xy[src]
bearing=(np.rad2deg(np.arctan2(delta[:,0],delta[:,1]))+360)%360
wind_to=(z["raw_wind_degrees"].astype(float)+180)%360
rows=[]
for h in (1,3,6,12,24):
    for split in ("train","validation"):
        in_split=(times>=pd.Timestamp(cfg[f"{split}_start_utc"]))&(times<=pd.Timestamp(cfg[f"{split}_end_utc"]))
        ix=np.flatnonzero(in_split & obs.any(axis=1) & (np.arange(len(times))>=h+11))
        cutoff=ix-h
        angle=np.abs((wind_to[cutoff,None]-bearing[None,:]+180)%360-180)
        mask=np.isfinite(wind_to[cutoff,None])&(angle<=37.5)
        reliable=obs[cutoff][:,src]&obs[cutoff][:,dst]
        active=mask.sum(axis=1)
        gated=(mask&reliable).sum(axis=1)
        rows.append(dict(horizon_hours=h,split=split,target_hours=len(ix),station_nodes=len(xy),directed_edges=len(src),
                         fixed_eligible_edge_instances=int(active.sum()),rgdr_eligible_edge_instances=int(gated.sum()),
                         gate_retention_fraction=float(gated.sum()/active.sum()) if active.sum() else None,
                         zero_fixed_hours=int((active==0).sum()),zero_rgdr_hours=int((gated==0).sum()),
                         mean_fixed_edges_per_hour=float(active.mean()),mean_rgdr_edges_per_hour=float(gated.mean()),
                         generic_reliable_edge_instances=int(reliable.sum()),
                         observed_cutoff_node_fraction=float(obs[cutoff].mean())))
pd.DataFrame(rows).to_csv(OUT/"gate_diagnostics.csv",index=False)
print(pd.DataFrame(rows).to_string(index=False))
