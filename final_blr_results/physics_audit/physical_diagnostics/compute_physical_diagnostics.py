"""Read-only transport-proxy diagnostics on existing observed station pairs."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from src.stpignn.station_graph import directed_knn_graph


ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
MODELS=("stpignn_original","stpignn_lambda0","stpignn_laplacian")
SEEDS=(11,23,37,51,79)


def main():
    z=np.load(ROOT/"results/data_v2j_arrays.npz")
    fit=json.loads((ROOT/"results/data_v2j_fit.json").read_text())
    assert fit["weather_half_hour_rule"] is True and fit["temperature_peak_utc_hour"] in (8,9,10)
    times=pd.to_datetime(z["times_ns"],utc=True)
    station=z["station_ids"].tolist()
    xy=z["coordinates"]
    edges,dist=directed_knn_graph(xy,4)
    src,dst=edges.numpy();length=dist.numpy().reshape(-1)
    delta=xy[dst]-xy[src]
    bearings=np.arctan2(delta[:,0],delta[:,1])
    scale=float(fit["fit"]["target_standard_std"])
    ts_index=pd.Index(times)
    pvr=[];spatial=[]
    for h in (1,3,6,12,24):
        pred_frames={}
        for model in MODELS:
            individual=[]
            for seed in SEEDS:
                path=ROOT/f"results/benchmark_predictions_h{h}_{model}_seed{seed}_v2j.parquet"
                frame=pd.read_parquet(path)
                frame["target_time_utc"]=pd.to_datetime(frame.target_time_utc,utc=True)
                individual.append(frame)
            pred_frames[model]=individual
        base=pred_frames[MODELS[0]][0]
        target_times=pd.DatetimeIndex(sorted(base.target_time_utc.unique()))
        time_idx=ts_index.get_indexer(target_times)
        assert (time_idx>=h).all()
        wind_from=z["raw_wind_degrees"][time_idx-h]
        transport_to=np.deg2rad((wind_from+180)%360)
        angle=np.abs(np.angle(np.exp(1j*(transport_to[:,None]-bearings[None,:]))))
        windmask=np.isfinite(wind_from[:,None])&(angle<=np.deg2rad(37.5))
        truth=base.pivot(index="target_time_utc",columns="station_id",values="target_ug_m3").reindex(index=target_times,columns=station).to_numpy(float)
        observed_diff=truth[:,dst]-truth[:,src]
        valid_truth=np.isfinite(observed_diff)
        for model in MODELS:
            matrices=[]
            for frame in pred_frames[model]:
                mat=frame.pivot(index="target_time_utc",columns="station_id",values="prediction_ug_m3").reindex(index=target_times,columns=station).to_numpy(float)
                assert np.array_equal(np.isfinite(mat),np.isfinite(truth))
                matrices.append(mat)
            for seed,mat in list(zip(SEEDS,matrices))+[("ensemble",np.mean(matrices,axis=0))]:
                diff=mat[:,dst]-mat[:,src]
                active=valid_truth&np.isfinite(diff)&windmask
                inactive=valid_truth&np.isfinite(diff)&~windmask
                assert active.sum()>0
                a=diff[active];observed=observed_diff[active]
                resistance=np.broadcast_to(1/(1+np.exp(-length[None,:]/1000)),diff.shape)[active]
                norm=a/scale
                row=dict(horizon_hours=h,model=model,seed=seed,utc_hours=len(target_times),stations=len(station),directed_edges=len(src),active_wind_edges=int(active.sum()),non_wind_edges=int(inactive.sum()),observed_edge_pairs=int(valid_truth.sum()),weather_half_hour_rule=True,temperature_peak_utc_hour=fit["temperature_peak_utc_hour"],wind_from_cone_half_angle_degrees=37.5,threshold_scale_ug_m3=scale,pvr_0_percent=100*np.mean(norm>0),pvr_0_01_percent=100*np.mean(norm>.01),pvr_0_05_percent=100*np.mean(norm>.05),pvr_0_1_percent=100*np.mean(norm>.1),mean_positive_upwind_difference_ug_m3=float(np.maximum(a,0).mean()),mean_positive_weighted_hinge_ug_m3=float(np.maximum(a*resistance,0).mean()),mean_squared_penalty_normalized=float(np.square(np.maximum(norm*resistance,0)).mean()),observed_pvr_0_percent=float(100*np.mean(observed>0)),observed_mean_positive_difference_ug_m3=float(np.maximum(observed,0).mean()))
                pvr.append(row)
                nvalid=np.isfinite(mat).sum(1)
                useful=nvalid>=2
                sd=np.nanstd(mat[useful],axis=1)
                std_t=[np.nanstd(mat[:,j]) for j in range(mat.shape[1]) if np.isfinite(mat[:,j]).sum()>=2]
                obs_sd=np.nanstd(truth[useful],axis=1)
                spatial.append(dict(horizon_hours=h,model=model,seed=seed,n_station_hours=int(np.isfinite(mat).sum()),hours_with_2plus_stations=int(useful.sum()),mean_abs_wind_edge_difference_ug_m3=float(np.abs(a).mean()),mean_abs_nonwind_edge_difference_ug_m3=float(np.abs(diff[inactive]).mean()),mean_abs_observed_wind_edge_difference_ug_m3=float(np.abs(observed).mean()),mean_abs_observed_nonwind_edge_difference_ug_m3=float(np.abs(observed_diff[inactive]).mean()),mean_abs_wind_gradient_ug_m3_per_km=float(np.mean(np.abs(a)/(np.broadcast_to(length[None,:],diff.shape)[active]/1000))),mean_spatial_sd_ug_m3=float(sd.mean()),mean_temporal_sd_ug_m3=float(np.mean(std_t)),near_constant_hour_count=int((sd<1).sum()),near_constant_hour_fraction=float(np.mean(sd<1)),collapsed_edge_pair_fraction=float(np.mean(np.abs(a)<1)),observed_mean_spatial_sd_ug_m3=float(obs_sd.mean())))
    pd.DataFrame(pvr).to_csv(OUT/"physical_metrics.csv",index=False)
    pd.DataFrame(spatial).to_csv(OUT/"spatial_behavior.csv",index=False)
    print("physical rows",len(pvr),"spatial rows",len(spatial))


if __name__=="__main__":main()
