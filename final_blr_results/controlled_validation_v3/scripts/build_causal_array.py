"""Versioned station-input delay; preserve observed targets and historical files."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from final_blr_results.controlled_validation_v3.scripts.train_controls import hash_file

ROOT=Path(__file__).resolve().parents[3]
SOURCE=ROOT/"final_blr_results/baselines/v2m/data/data_v2m_arrays.npz"
OUT=ROOT/"final_blr_results/controlled_validation_v3/data_manifests/data_v3_causal_arrays.npz"


def main():
    if OUT.exists(): raise FileExistsError(OUT)
    z=np.load(SOURCE)
    d={k:z[k].copy() for k in z.files}
    features=d["features"].copy()
    features[1:,:,:5]=d["features"][:-1,:,:5]
    features[0,:,:5]=0.
    d["features"]=features
    input_obs=np.zeros_like(d["observed_mask"])
    input_obs[1:]=d["observed_mask"][:-1]
    d["input_observed_mask"]=input_obs
    tier=d["imputation_tier"].copy();tier[1:]=d["imputation_tier"][:-1];tier[0]="M"
    d["imputation_tier"]=tier
    y=d["observed_target"]
    times=pd.to_datetime(d["times_ns"],utc=True)
    train=times<=pd.Timestamp("2025-06-29T23:00:00Z")
    with np.errstate(all="ignore"):
        station_mean=np.nanmean(y[train],axis=0)
        station_mean=np.where(np.isfinite(station_mean),station_mean,np.nanmean(y[train]))
    ffill=pd.DataFrame(y).ffill().to_numpy(dtype=np.float32)
    anchor=np.empty_like(y,dtype=np.float32);anchor[0]=station_mean
    anchor[1:]=np.where(np.isfinite(ffill[:-1]),ffill[:-1],station_mean[None,:])
    d["input_anchor"]=anchor
    assert np.isfinite(features).all() and np.isfinite(anchor).all()
    assert np.array_equal(d["observed_target"],z["observed_target"],equal_nan=True)
    assert np.array_equal(d["observed_mask"],z["observed_mask"])
    tmp=OUT.with_suffix(".tmp.npz")
    np.savez_compressed(tmp,**d);tmp.replace(OUT)
    info=dict(source=str(SOURCE.relative_to(ROOT)),source_sha256=hash_file(SOURCE),
              output=str(OUT.relative_to(ROOT)),output_sha256=hash_file(OUT),
              rule="pollutant channels and observation mask lagged one row; anchor strictly before issue",
              targets_unchanged=True)
    (OUT.parent/"causal_array_build.json").write_text(json.dumps(info,indent=2)+"\n")
    print(json.dumps(info,indent=2))


if __name__=="__main__":main()
