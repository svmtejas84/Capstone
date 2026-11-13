"""Evaluate frozen same-information baselines on the exposed test, once unlocked."""
import csv
import json
import warnings
from pathlib import Path
import numpy as np
import pandas as pd
import torch
from sklearn.linear_model import Ridge
from src.stpignn.evaluation import evaluate_arrays
from final_blr_results.controlled_validation_v3.scripts.smoke_gpu import CutoffContext, ARR, FIT, V3
from final_blr_results.controlled_validation_v3.scripts.train_controls import BASE_CFG,HORIZONS,SEEDS,hash_file
from final_blr_results.controlled_validation_v3.scripts.train_baselines import BaselineContext, MODELS


def write_pred(path, pred, truth, ti, sj):
    np.savez_compressed(path,pred=pred,truth=truth,time_index=ti,station_index=sj)


def main():
    assert (V3/"verification/test_unlock.json").exists(),"Do not evaluate baselines before frozen test unlock"
    assert (V3/"training/baselines/final_COMPLETE").exists()
    out=V3/"predictions";out.mkdir(exist_ok=True)
    rows=[]
    for h in HORIZONS:
        c=CutoffContext(h,BASE_CFG,ARR,FIT)
        i,j=np.where(c.observed & np.isin(np.arange(len(c.times)),c.hours["test"])[:,None])
        y=c.y[i,j]
        anchor=c.anchor[i-h,j]
        train_i,train_j=np.where(c.observed & c.train_period[:,None])
        eligible=(train_i-h>=11)&c.observed[np.maximum(train_i-h,0),train_j]
        train_i,train_j=train_i[eligible],train_j[eligible]
        features=c.features[train_i-h,train_j]
        train_y=(np.log1p(c.y[train_i,train_j])-c.mu)/c.sd
        ridge_cols=[0]+list(range(5,c.features.shape[-1]))
        ridge=Ridge(alpha=1.).fit(features[:,ridge_cols],train_y)
        keys=c.times.hour.to_numpy()*7+c.times.dayofweek.to_numpy()
        climate=np.full((168,c.n),np.nan,dtype=np.float32)
        for k in range(168):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore",RuntimeWarning)
                climate[k]=np.nanmedian(c.y[c.train_period & (keys==k)],axis=0)
        climat=climate[keys[i],j]
        climat=np.where(np.isfinite(climat),climat,c.station_mean[j])
        classical={"persistence":anchor,"same_hour_yesterday":c.anchor[i-24,j],
                   "station_train_mean":c.station_mean[j],"climatology_hod_dow":climat,
                   "weather_ridge":np.expm1(ridge.predict(c.features[i-h,j][:,ridge_cols])*c.sd+c.mu)}
        for name,p in classical.items():
            m=evaluate_arrays(p,y,np.ones(len(y),bool))
            rows.append(dict(horizon_hours=h,model=name,seed="deterministic",mae=m["mae"],rmse=m["rmse"],r2=m["r2"],n=m["n"],source="v3 recomputed from train-only fit"))
            write_pred(out/f"h{h}_{name}.npz",p,y,i,j)
        for name in MODELS:
            bc=BaselineContext(name,h)
            preds=[]
            for s in SEEDS:
                cell=V3/"training/baselines"/name/"final"/f"h{h}_seed{s}"
                rec=json.loads((cell/"COMPLETE.json").read_text())
                ckpt=cell/"best.pt";assert rec["checkpoint_sha256"]==hash_file(ckpt)
                payload=torch.load(ckpt,map_location="cpu",weights_only=False)
                model=bc.make("stpignn_lambda0");model.load_state_dict(payload["state_dict"],strict=True)
                result=bc.evaluate(model,"stpignn_lambda0","test",collect=True)
                assert np.array_equal(result["time_index"],i) and np.array_equal(result["station_index"],j)
                preds.append(result["pred"])
                rows.append(dict(horizon_hours=h,model=name,seed=s,mae=result["mae"],rmse=result["rmse"],r2=result["r2"],n=result["n"],source="new v3 same-input fit"))
                write_pred(out/f"h{h}_{name}_seed{s}.npz",result["pred"],y,i,j)
            mean=np.mean(np.stack(preds),axis=0);m=evaluate_arrays(mean,y,np.ones(len(y),bool))
            rows.append(dict(horizon_hours=h,model=name,seed="ensemble",mae=m["mae"],rmse=m["rmse"],r2=m["r2"],n=m["n"],source="new v3 same-input fit"))
            write_pred(out/f"h{h}_{name}_ensemble.npz",mean,y,i,j)
        for name in ("mlp","tcn"):
            preds=[]
            for s in SEEDS:
                path=V3.parent/"baselines/v2m"/name/f"h{h}"/f"seed{s}"/"predictions.parquet"
                f=pd.read_parquet(path)
                assert np.array_equal(pd.to_datetime(f.target_time_utc,utc=True).asi8,c.times[i].asi8)
                assert np.array_equal(f.station_id.to_numpy(),c.station_ids[j])
                assert np.array_equal(f.target_ug_m3.to_numpy(),y)
                p=f.prediction_ug_m3.to_numpy();preds.append(p)
                m=evaluate_arrays(p,y,np.ones(len(y),bool))
                rows.append(dict(horizon_hours=h,model=name,seed=s,mae=m["mae"],rmse=m["rmse"],r2=m["r2"],n=m["n"],source="saved v2m same-input fit; different selection schedule"))
            mean=np.mean(np.stack(preds),axis=0);m=evaluate_arrays(mean,y,np.ones(len(y),bool))
            rows.append(dict(horizon_hours=h,model=name,seed="ensemble",mae=m["mae"],rmse=m["rmse"],r2=m["r2"],n=m["n"],source="saved v2m same-input fit; different selection schedule"))
            write_pred(out/f"h{h}_{name}_ensemble.npz",mean,y,i,j)
    path=V3/"metrics/baselines.csv";path.parent.mkdir(exist_ok=True)
    with path.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    print(f"Wrote {len(rows)} baseline rows")


if __name__=="__main__":main()
