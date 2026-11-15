"""Describe saved v3 chronology, observed targets and repaired input coverage."""
import csv
import numpy as np
import pandas as pd
import yaml
from final_blr_results.controlled_validation_v3.scripts.train_controls import V3,ARR,HORIZONS


def main():
    z=np.load(ARR)
    times=pd.DatetimeIndex(pd.to_datetime(z["times_ns"],utc=True))
    cfg=yaml.safe_load((V3.parents[1]/"configs/data_v2.yaml").read_text())
    obs=z["observed_mask"]; inp=z["input_observed_mask"]; y=z["observed_target"]
    rows=[]
    for split in ("train","validation","test"):
        period=np.asarray((times>=pd.Timestamp(cfg[f"{split}_start_utc"]))&
                          (times<=pd.Timestamp(cfg[f"{split}_end_utc"])))
        target=y[period&obs.any(axis=1)]
        target=target[np.isfinite(target)]
        for h in HORIZONS:
            indices=np.arange(len(times));issue=indices-h
            valid_time=period&(issue>=11)
            scored=obs&valid_time[:,None]
            if split!="test":
                scored&=inp[np.maximum(issue,0)]
            active_hours=np.flatnonzero(scored.any(axis=1))
            if len(active_hours):
                window=(active_hours-h)[:,None]-np.arange(11,-1,-1)[None,:]
                assert window.min()>=0
                input_fraction=1-float(inp[window].mean())
            else: input_fraction=float("nan")
            rows.append(dict(split=split,horizon_hours=h,utc_hours=int(period.sum()),stations=obs.shape[1],
                             possible_station_hours=int(period.sum()*obs.shape[1]),
                             observed_target_pairs=int(obs[period].sum()),
                             observed_target_coverage_percent=float(100*obs[period].mean()),
                             scored_pairs=int(scored.sum()),scored_target_hours=len(active_hours),
                             input_pollutant_imputed_fraction_all_stations_12h=input_fraction,
                             target_mean_ug_m3=float(np.mean(target)) if len(target) else "",
                             target_median_ug_m3=float(np.median(target)) if len(target) else "",
                             target_sd_ug_m3=float(np.std(target)) if len(target) else "",
                             target_n=int(len(target)),
                             note="historical observation timestamps; release latency unverified"))
    out=V3/"metrics/data_coverage_shift.csv";out.parent.mkdir(exist_ok=True)
    with out.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    print(f"Wrote {len(rows)} chronology/coverage records")


if __name__=="__main__":main()
