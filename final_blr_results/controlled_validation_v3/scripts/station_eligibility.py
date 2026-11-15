"""Machine-readable station coverage and scored-population eligibility."""
import csv
import numpy as np
import pandas as pd
import yaml
from final_blr_results.controlled_validation_v3.scripts.train_controls import V3,ARR,HORIZONS


def main():
    z=np.load(ARR)
    times=pd.DatetimeIndex(pd.to_datetime(z["times_ns"],utc=True))
    cfg=yaml.safe_load((V3.parents[1]/"configs/data_v2.yaml").read_text())
    obs=z["observed_mask"];inp=z["input_observed_mask"]
    rows=[]
    for split in ("train","validation","test"):
        period=np.asarray((times>=pd.Timestamp(cfg[f"{split}_start_utc"]))&
                          (times<=pd.Timestamp(cfg[f"{split}_end_utc"])))
        for j,sid in enumerate(z["station_ids"]):
            seen=np.flatnonzero(obs[:,j]&period)
            row=dict(split=split,station_id=str(sid),utm_easting_m=float(z["coordinates"][j,0]),
                     utm_northing_m=float(z["coordinates"][j,1]),
                     possible_hours=int(period.sum()),observed_target_hours=int(len(seen)),
                     target_coverage_percent=float(100*len(seen)/period.sum()),
                     input_imputed_hours=int((~inp[period,j]).sum()),
                     input_imputed_fraction=float((~inp[period,j]).mean()),
                     first_observed_target_utc=str(times[seen[0]]) if len(seen) else "",
                     last_observed_target_utc=str(times[seen[-1]]) if len(seen) else "")
            for h in HORIZONS:
                issue=seen-h
                eligible=issue>=11
                if split!="test":eligible&=inp[np.maximum(issue,0),j]
                row[f"scored_h{h}_pairs"]=int(eligible.sum())
            rows.append(row)
    out=V3/"data_manifests/station_eligibility.csv"
    with out.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator="\n");w.writeheader();w.writerows(rows)
    print(f"Wrote {len(rows)} station/split eligibility rows")


if __name__=="__main__":main()
