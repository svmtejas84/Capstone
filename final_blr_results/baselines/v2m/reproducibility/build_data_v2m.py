"""Build v2m arrays with cutoff-safe corrected weather; preserve v2j files."""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

from src.stpignn.data_v2 import build
from src.stpignn.paths import REPO_ROOT


OUT = REPO_ROOT / "final_blr_results/baselines/v2m/data"


def sha(path):
    digest=hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda:stream.read(4*1024*1024),b""):
            digest.update(block)
    return digest.hexdigest()


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    target=OUT/"data_v2m_arrays.npz"
    fit_path=OUT/"data_v2m_fit.json"
    if target.exists() or fit_path.exists():
        raise FileExistsError("v2m arrays already exist; inspect rather than overwrite")
    data,extra=build(REPO_ROOT/"configs/data_v2.yaml",weather_half_hour_rule=True,weather_cutoff_safe=True)
    old=np.load(REPO_ROOT/"results/data_v2j_arrays.npz")
    assert np.array_equal(data.times.asi8,old["times_ns"])
    assert np.array_equal(data.station_ids,old["station_ids"])
    assert np.array_equal(data.observed_mask,old["observed_mask"])
    assert np.array_equal(data.observed_target,old["observed_target"],equal_nan=True)
    assert data.features.shape==(37152,15,13) and data.features.shape[-1]+1+4==18
    assert len(data.raw_wind_degrees)==len(data.times)
    temperature=data.raw_values[:,0,7]
    profile=pd.Series(temperature).groupby(data.times.hour).mean()
    train=data.split_masks["train"]
    features=data.features.copy()
    pm25=np.clip(data.imputed_target,0,500)
    pm10=np.clip(features[:,:,1]*data.fit["feature_stds"][1]+data.fit["feature_means"][1],0,500)
    y_train=data.observed_target[train]
    y_log_train=np.log1p(y_train[np.isfinite(y_train)])
    mean25,sd25=float(y_log_train.mean()),float(y_log_train.std())
    log10=np.log1p(pm10[train])
    mean10,sd10=float(log10.mean()),float(log10.std())
    features[:,:,0]=(np.log1p(pm25)-mean25)/sd25
    features[:,:,1]=(np.log1p(pm10)-mean10)/sd10
    assert np.isfinite(features).all()
    # At c=02:00 UTC the previous corrected observation is at 01:30;
    # v2j's centered feature was 21.45 C, while this cutoff-safe one is 20.7 C.
    sample=data.times.get_loc(pd.Timestamp("2025-09-23T02:00:00Z"))
    assert abs(float(data.raw_values[sample,0,7])-20.7)<1e-4
    assert abs(float(old["features"][sample,0,7]*json.loads((REPO_ROOT/"results/data_v2j_fit.json").read_text())["fit"]["feature_stds"][7]+json.loads((REPO_ROOT/"results/data_v2j_fit.json").read_text())["fit"]["feature_means"][7])-21.45)<1e-4
    temporary=target.with_suffix(".tmp.npz")
    np.savez_compressed(temporary,times_ns=data.times.asi8,station_ids=data.station_ids,
                        node_indices=data.node_indices,coordinates=data.coordinates,
                        elevation_m=data.elevation_m,features=features,
                        raw_wind_degrees=data.raw_wind_degrees,
                        observed_target=data.observed_target,observed_mask=data.observed_mask,
                        imputed_target=pm25,imputation_tier=data.imputation_tier)
    temporary.replace(target)
    report=dict(timestamp_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
                source_commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=REPO_ROOT,text=True).strip(),
                script="final_blr_results/baselines/v2m/reproducibility/build_data_v2m.py",
                config="configs/data_v2.yaml",seed=data.config["seed"],
                weather_half_hour_rule=True,weather_cutoff_safe=True,
                weather_source_policy="latest corrected raw weather record timestamped at or before UTC feature hour; normally c-00:30",
                temperature_peak_utc_hour=int(profile.idxmax()),
                target_log1p_mean=mean25,target_log1p_sd=sd25,
                pm10_log1p_mean=mean10,pm10_log1p_sd=sd10,
                fit=data.fit,provenance=extra["provenance"],
                v2j_array_sha256=sha(REPO_ROOT/"results/data_v2j_arrays.npz"),
                v2m_array_sha256=sha(target),
                unchanged_target_and_mask=True,
                sample_cutoff_utc="2025-09-23T02:00:00Z",sample_temperature_c=20.7)
    tmpfit=fit_path.with_suffix(".tmp.json")
    tmpfit.write_text(json.dumps(report,indent=2,default=str)+"\n")
    tmpfit.replace(fit_path)
    print(json.dumps({"array":str(target.relative_to(REPO_ROOT)),"sha256":report["v2m_array_sha256"],"temperature_peak_utc_hour":report["temperature_peak_utc_hour"]}))


if __name__=="__main__":main()
