"""Post-hoc IG for saved v2r h6 corrected ST-PIGNN outer-LOSO folds; no fitting."""
from __future__ import annotations
import hashlib, json, os, sys
from pathlib import Path

os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")
ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent / "v2r_heldout_h6"
os.environ.setdefault("MPLCONFIGDIR", str(OUT / ".mplconfig"))
sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd
import torch
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from captum.attr import IntegratedGradients
import yaml

from src.stpignn.data_v2 import build
from src.stpignn.models_v2 import make_model
from src.stpignn.station_graph import directed_knn_graph

H, HIST, SEED = 6, 12, 11
FEATURES = ["pm25_lagged", "pm10", "no2", "so2", "co", "wind_speed", "wind_gusts",
            "temperature", "humidity", "surface_pressure", "wind_direction_sin",
            "wind_direction_cos", "elevation", "lag_is_imputed", "hour_sin", "hour_cos",
            "weekday_sin", "weekday_cos"]


def sha(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):h.update(b)
    return h.hexdigest()


def atomic_json(path,obj):
    tmp=path.with_suffix(path.suffix+".tmp");tmp.write_text(json.dumps(obj,indent=2)+"\n");tmp.replace(path)


def main():
    torch.set_num_threads(1);torch.manual_seed(20261107);np.random.seed(20261107)
    OUT.mkdir(parents=True,exist_ok=True);records_dir=OUT/"records";records_dir.mkdir(exist_ok=True)
    figure_dir=OUT/"figures";figure_dir.mkdir(parents=True,exist_ok=True)
    base=ROOT/"final_blr_results/final_research_v2r/citywide/station_forecasts"
    # Identify eligible sites/time solely from observed masks and IDs, not errors.
    z=np.load(ROOT/"results/data_v2j_arrays.npz")
    times=pd.DatetimeIndex(pd.to_datetime(z["times_ns"],utc=True));ids=z["station_ids"]
    obs=z["observed_mask"]
    test=(times>=pd.Timestamp("2025-09-23T00:00:00Z"))&(times<=pd.Timestamp("2026-03-28T23:00:00Z"))
    valid=np.flatnonzero(test);valid=valid[valid>=H+HIST-1]
    scored=[j for j in range(len(ids)) if np.any(obs[valid,j])]
    scored.sort(key=lambda j:int(ids[j]));chosen=[scored[0],scored[len(scored)//2],scored[-1]]
    # One saved outer fold per selected held-out station; these models exclude that site's labels.
    manifest=[];records=[];tensors=[];lag_rows=[];station_rows=[];feature_rows=[]
    for j in chosen:
        sid=int(ids[j]);fold=base/"folds"/str(sid)/"outer"
        config=yaml.safe_load((fold/"fold_data_config.yaml").read_text())
        data,_=build(fold/"fold_data_config.yaml",excluded_station_id=sid,
                     weather_half_hour_rule=True,weather_cutoff_safe=True)
        station_idx=int(np.flatnonzero(data.station_ids==sid)[0])
        known=data.observed_mask.copy();known[:,station_idx]=False
        target_idxs=valid[obs[valid,station_idx]]
        chosen_targets=[int(target_idxs[0]),int(target_idxs[len(target_idxs)//2]),int(target_idxs[-1])]
        all_path=fold/"station_forecasts_all.parquet"
        saved=pd.read_parquet(all_path)
        saved=saved[(saved.split=="spatial_test")&(saved.station_id==sid)]
        saved["target_time_utc"]=pd.to_datetime(saved.target_time_utc,utc=True)
        pred_lookup={r.target_time_utc:float(r.prediction_ug_m3) for r in saved.itertuples(index=False)}

        hour=pd.DatetimeIndex(data.times).hour.to_numpy();dow=pd.DatetimeIndex(data.times).dayofweek.to_numpy()
        calendar=np.stack((np.sin(2*np.pi*hour/24),np.cos(2*np.pi*hour/24),
                           np.sin(2*np.pi*dow/7),np.cos(2*np.pi*dow/7)),-1).astype(np.float32)
        missing=(~known).astype(np.float32)
        features=np.concatenate((data.features,missing[...,None],
                                 np.broadcast_to(calendar[:,None,:],(len(data.times),len(data.station_ids),4))),axis=-1)
        features[:,station_idx,:5]=0.0
        train_mask=np.asarray(data.split_masks["train"])
        train_y=data.observed_target[train_mask].copy();train_y[:,station_idx]=np.nan
        mean_station=np.nanmean(train_y,axis=0);mean_global=float(np.nanmean(train_y))
        mean_station=np.where(np.isfinite(mean_station),mean_station,mean_global)
        anchor_raw=data.observed_target.copy();anchor_raw[:,station_idx]=np.nan
        anchor=pd.DataFrame(anchor_raw).ffill().to_numpy(dtype=np.float32)
        anchor=np.where(np.isfinite(anchor),anchor,mean_station[None,:]).astype(np.float32)
        mu=float(data.fit["target_log1p_mean"]);sd=float(data.fit["target_log1p_std"])
        edge,edge_attr=directed_knn_graph(data.coordinates,4)
        ckpt_path=fold/"best_model.pt";checkpoint=torch.load(ckpt_path,map_location="cpu",weights_only=False)
        if checkpoint.get("input_channels")!=18 or checkpoint.get("edge_dim")!=1 or checkpoint.get("horizon_hours")!=H or checkpoint.get("seed")!=SEED:
            raise RuntimeError(f"Checkpoint metadata mismatch: {ckpt_path}")
        model=make_model("stpignn_corrected",18,96,1).cpu()
        model.load_state_dict(checkpoint["state_dict"],strict=True);model.eval()
        for p in model.parameters():p.requires_grad_(False)
        sid_reference=features[train_mask].mean(axis=0).astype(np.float32)

        for target_i in chosen_targets:
            cutoff=target_i-H
            win=cutoff-np.arange(HIST-1,-1,-1)
            if win.max()>cutoff or win[-1]!=cutoff or np.any(win>=target_i):raise AssertionError("forecast cutoff violation")
            x_np=features[win].copy().astype(np.float32)
            x=torch.from_numpy(x_np[None])
            primary=np.broadcast_to(sid_reference[None],(HIST,*sid_reference.shape)).copy()
            sensitivity=np.zeros_like(x_np);sensitivity[...,13:]=x_np[...,13:]
            sample_time=pd.Timestamp(data.times[target_i])
            saved_prediction=pred_lookup.get(sample_time)
            if saved_prediction is None:raise KeyError(f"No saved heldout forecast for station={sid}, time={sample_time}")
            anchor_at_cutoff=torch.from_numpy(anchor[cutoff][None])
            anchor_z=(torch.log1p(anchor_at_cutoff.clamp_min(0))-mu)/sd

            def forward(inp):
                resid=model(inp,edge,edge_attr)
                p=torch.expm1((resid+anchor_z)*sd+mu)
                return p[:,station_idx]

            with torch.no_grad():prediction=float(forward(x)[0])
            wrapper_error=abs(prediction-saved_prediction)
            if wrapper_error>1e-4:raise RuntimeError(f"saved prediction mismatch {sid} {sample_time}: {wrapper_error}")
            for baseline_name,baseline_np in (("training_mean",primary),("zero_env_keep_missing_calendar",sensitivity)):
                rec_path=records_dir/f"station{sid}_{sample_time.strftime('%Y%m%dT%H%M%SZ')}_{baseline_name}.npz"
                ckhash=sha(ckpt_path)
                if rec_path.exists():
                    f=np.load(rec_path,allow_pickle=False);arr=f["attribution"];rec=json.loads(str(f["metadata"].item()))
                    if rec["checkpoint_sha256"]!=ckhash or rec["wrapper_abs_error_ug_m3"]>1e-4:raise RuntimeError(f"record mismatch {rec_path}")
                else:
                    baseline=torch.from_numpy(baseline_np[None])
                    attr,delta=IntegratedGradients(forward).attribute(x,baselines=baseline,n_steps=64,
                                  method="gausslegendre",internal_batch_size=1,return_convergence_delta=True)
                    arr=attr.detach().numpy()[0].astype(np.float32);delta=float(delta[0])
                    base_pred=float(forward(baseline)[0]);relative=abs(delta)/max(1.0,abs(prediction-base_pred))
                    if not np.isfinite(arr).all() or not np.isfinite(delta):raise FloatingPointError("nonfinite IG")
                    rec={"model_version":"v2r corrected ST-PIGNN outer-LOSO","model":"stpignn_corrected",
                         "horizon_hours":H,"seed":SEED,"heldout_station_id":sid,"station_id":sid,
                         "target_time_utc":str(sample_time),"cutoff_time_utc":str(data.times[cutoff]),
                         "baseline":baseline_name,"prediction_ug_m3":prediction,"saved_prediction_ug_m3":saved_prediction,
                         "wrapper_abs_error_ug_m3":wrapper_error,"baseline_prediction_ug_m3":base_pred,
                         "completeness_delta_ug_m3":delta,"completeness_relative":relative,
                         "quality_flag":int(abs(delta)>0.05 or relative>0.01),"nonfinite_count":int((~np.isfinite(arr)).sum()),
                         "checkpoint_path":str(ckpt_path.relative_to(ROOT)),"checkpoint_sha256":ckhash,
                         "source_forecast_artifact":str(all_path.relative_to(ROOT)),"n_lags":HIST,"n_nodes":len(ids),"n_features":18}
                    tmp=rec_path.with_suffix(".npz.tmp")
                    with tmp.open("wb") as f:np.savez_compressed(f,attribution=arr,metadata=np.array(json.dumps(rec)))
                    tmp.replace(rec_path)
                rec["record"]=len(records);records.append(rec);tensors.append(arr)
                for lag in range(HIST):
                    t=HIST-1-lag
                    lag_rows.append({"record":rec["record"],"seed":SEED,"station_id":sid,
                        "target_time_utc":str(sample_time),"baseline":baseline_name,"lag_hours_before_cutoff":lag,
                        "signed_ug_m3":float(arr[t].sum()),"absolute_ug_m3":float(np.abs(arr[t]).sum())})
                for node_idx,node_id in enumerate(ids):
                    station_rows.append({"record":rec["record"],"seed":SEED,"target_station_id":sid,
                        "target_time_utc":str(sample_time),"baseline":baseline_name,"input_station_id":int(node_id),
                        "signed_ug_m3":float(arr[:,node_idx,:].sum()),"absolute_ug_m3":float(np.abs(arr[:,node_idx,:]).sum())})
                for f,name in enumerate(FEATURES):
                    feature_rows.append({"record":rec["record"],"seed":SEED,"station_id":sid,
                        "target_time_utc":str(sample_time),"baseline":baseline_name,"feature":name,
                        "signed_ug_m3":float(arr[:,:,f].sum()),"absolute_ug_m3":float(np.abs(arr[:,:,f]).sum())})
        manifest.append({"station_id":sid,"checkpoint":str(ckpt_path.relative_to(ROOT)),"checkpoint_sha256":sha(ckpt_path),
                         "prediction_artifact":str(all_path.relative_to(ROOT)),"prediction_rows":len(saved),
                         "selected_target_times":[str(data.times[i]) for i in chosen_targets],
                         "input_schema":FEATURES,"input_cutoff_verified":True,"heldout_label_excluded":True})
        del model

    results_dir=OUT
    pd.DataFrame(records).to_csv(results_dir/"IG_RESULTS.csv",index=False)
    pd.DataFrame(feature_rows).to_csv(results_dir/"feature_attributions.csv",index=False)
    pd.DataFrame(lag_rows).to_csv(results_dir/"temporal_attributions.csv",index=False)
    pd.DataFrame(station_rows).to_csv(results_dir/"station_attributions.csv",index=False)
    tmp=results_dir/"attribution_tensors.npz.tmp"
    with tmp.open("wb") as f:np.savez_compressed(f,attributions=np.stack(tensors),
        feature_names=np.array(FEATURES),records=np.array([json.dumps(r) for r in records]))
    tmp.replace(results_dir/"attribution_tensors.npz")
    atomic_json(results_dir/"sample_selection.json",{"selection":"sorted eligible outer-heldout station IDs: first/median/last; per site first/median/last observed test time; masks and IDs only","horizon_hours":H,"seed":SEED,"samples":manifest})
    primary=pd.DataFrame(feature_rows).query("baseline == 'training_mean'")
    summary=primary.groupby("feature",as_index=False).agg(mean_signed_ug_m3=("signed_ug_m3","mean"),mean_absolute_ug_m3=("absolute_ug_m3","mean"))
    summary.to_csv(results_dir/"feature_summary.csv",index=False)
    diag={"record_count":len(records),"examples":sum(len(x["selected_target_times"]) for x in manifest),
          "checkpoints":len(manifest),"max_wrapper_abs_error_ug_m3":max(r["wrapper_abs_error_ug_m3"] for r in records),
          "max_abs_completeness_delta_ug_m3":max(abs(r["completeness_delta_ug_m3"]) for r in records),
          "median_abs_completeness_delta_ug_m3":float(np.median([abs(r["completeness_delta_ug_m3"]) for r in records])),
          "flagged_records":sum(r["quality_flag"] for r in records),"nonfinite_records":sum(r["nonfinite_count"]>0 for r in records),
          "scope":"post-hoc exploratory explanation on repeatedly exposed Bengaluru test period; heldout-station model predictions"}
    atomic_json(results_dir/"diagnostics.json",diag)
    fig,ax=plt.subplots(figsize=(8,6));v=summary.sort_values("mean_absolute_ug_m3")
    ax.barh(v.feature,v.mean_absolute_ug_m3,color="#276678");ax.set_xlabel("Mean absolute IG sum (µg/m³)")
    ax.set_title("v2r corrected ST-PIGNN, h=6, held-out station forecasts\n3 stations × 3 fixed times × 1 seed; training-mean baseline")
    fig.tight_layout();fig.savefig(figure_dir/"ig_v2r_h6_features.png",dpi=220);fig.savefig(figure_dir/"ig_v2r_h6_features.pdf");plt.close(fig)
    comp=f"{len(records)} IG records; 3 heldout fold checkpoints; wrapper-equivalence and cutoff checks passed\n"
    (results_dir/"COMPLETE").write_text(comp)
    run_marker=results_dir/"runs/ig_v2r/COMPLETE";run_marker.parent.mkdir(parents=True,exist_ok=True)
    tmpm=run_marker.with_suffix(".tmp");tmpm.write_text(comp);tmpm.replace(run_marker)
    print(json.dumps(diag,indent=2))

if __name__=="__main__":main()
