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
    if path.exists(): return
    tmp=path.with_name(path.stem+".tmp.npz")
    np.savez_compressed(tmp,pred=pred,truth=truth,time_index=ti,station_index=sj)
    tmp.replace(path)


def main():
    assert (V3/"verification/test_unlock.json").exists(),"Do not evaluate baselines before frozen test unlock"
    assert (V3/"training/baselines/final_COMPLETE").exists()
    out=V3/"predictions";out.mkdir(exist_ok=True)
    path=V3/"metrics/baselines.csv";path.parent.mkdir(exist_ok=True)
    if path.exists(): raise RuntimeError("Baseline evaluation already complete; do not repeat")
    rows=[]
    for h in HORIZONS:
        c=CutoffContext(h,BASE_CFG,ARR,FIT)
        i,j=np.where(c.observed & np.isin(np.arange(len(c.times)),c.hours["test"])[:,None])
        y=c.y[i,j]
        anchor=c.anchor[i-h,j]
        train_i,train_j=np.where(c.observed & c.train_period[:,None])
        eligible=(train_i-h>=11)&c.input_observed[np.maximum(train_i-h,0),train_j]
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
        # The exact previous-day hour is available strictly before issue for
        # h<24. At h=24 (or when missing), use the strictly prior causal fill.
        yesterday_idx=i-24
        yesterday=np.where((h<24)&np.isfinite(c.y[yesterday_idx,j]),
                           c.y[yesterday_idx,j],c.anchor[yesterday_idx,j])
        classical={"persistence":anchor,"same_hour_yesterday":yesterday,
                   "station_train_mean":c.station_mean[j],"climatology_hod_dow":climat,
                   "weather_ridge":np.expm1(ridge.predict(c.features[i-h,j][:,ridge_cols])*c.sd+c.mu)}
        for name,p in classical.items():
            saved=out/f"h{h}_{name}.npz"
            if saved.exists():
                with np.load(saved) as z:
                    assert np.array_equal(z["truth"],y) and np.array_equal(z["time_index"],i)
                    assert np.array_equal(z["station_index"],j)
                    p=z["pred"]
            m=evaluate_arrays(p,y,np.ones(len(y),bool))
            assert np.isfinite(p).all() and np.isfinite(y).all()
            rows.append(dict(horizon_hours=h,model=name,seed="deterministic",mae=m["mae"],rmse=m["rmse"],r2=m["r2"],n=m["n"],source="v3 recomputed from train-only fit"))
            write_pred(saved,p,y,i,j)
        for name in MODELS:
            bc=BaselineContext(name,h)
            preds=[]
            for s in SEEDS:
                cell=V3/"training/baselines"/name/"final"/f"h{h}_seed{s}"
                rec=json.loads((cell/"COMPLETE.json").read_text())
                ckpt=cell/"best.pt";assert rec["checkpoint_sha256"]==hash_file(ckpt)
                saved=out/f"h{h}_{name}_seed{s}.npz"
                if saved.exists():
                    with np.load(saved) as z:
                        result={k:z[k] for k in ("pred","truth","time_index","station_index")}
                    result.update(evaluate_arrays(result["pred"],result["truth"],np.ones(len(result["pred"]),bool)))
                else:
                    payload=torch.load(ckpt,map_location="cpu",weights_only=False)
                    model=bc.make("stpignn_lambda0");model.load_state_dict(payload["state_dict"],strict=True)
                    result=bc.evaluate(model,"stpignn_lambda0","test",collect=True)
                    write_pred(saved,result["pred"],result["truth"],result["time_index"],result["station_index"])
                assert np.array_equal(result["time_index"],i) and np.array_equal(result["station_index"],j)
                assert np.array_equal(result["truth"],y)
                assert np.isfinite(result["pred"]).all()
                preds.append(result["pred"])
                rows.append(dict(horizon_hours=h,model=name,seed=s,mae=result["mae"],rmse=result["rmse"],r2=result["r2"],n=result["n"],source="new v3 same-input fit"))
            mean=np.mean(np.stack(preds),axis=0);m=evaluate_arrays(mean,y,np.ones(len(y),bool))
            rows.append(dict(horizon_hours=h,model=name,seed="ensemble",mae=m["mae"],rmse=m["rmse"],r2=m["r2"],n=m["n"],source="new v3 same-input fit"))
            write_pred(out/f"h{h}_{name}_ensemble.npz",mean,y,i,j)
    tmp=path.with_suffix(".csv.tmp")
    with tmp.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    tmp.replace(path)
    print(f"Wrote {len(rows)} baseline rows")


if __name__=="__main__":main()
