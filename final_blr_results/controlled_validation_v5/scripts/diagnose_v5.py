"""Common actual-wind post-hoc diagnostics for every V5 comparison output."""
import csv
import json

import numpy as np
import pandas as pd

from src.stpignn.station_graph import directed_knn_graph
from final_blr_results.controlled_validation_v3.scripts.smoke_gpu import ARR, V3
from final_blr_results.controlled_validation_v5.scripts.train_graph_lag import V5
from final_blr_results.controlled_validation_v5.scripts.verify_and_score import HISTORICAL
from final_blr_results.controlled_validation_v5.scripts.analyze_v5 import load, load_fair


def main():
    assert (V5/"metrics/NEW_TEST_SCORES.csv").exists()
    z=np.load(ARR)
    xy=z["coordinates"]
    edge,_=directed_knn_graph(xy,4)
    src,dst=edge.numpy()
    bearing=np.arctan2((xy[dst]-xy[src])[:,0],(xy[dst]-xy[src])[:,1])
    towards=np.deg2rad((z["raw_wind_degrees"].astype(float)+180)%360)
    angle=np.abs(np.angle(np.exp(1j*(towards[:,None]-bearing[None,:]))))
    mask=np.isfinite(towards[:,None])&(angle<=np.deg2rad(37.5))
    scale=float(json.loads((V3.parents[1]/"results/data_v2j_fit.json").read_text())["fit"]["target_standard_std"])
    replay=pd.read_csv(V5/"metrics/FAIRNESS_GRADIENT_REPLAY.csv")
    rows=[]

    def add(h,condition,p,family=None,strength=None):
        hours,inverse=np.unique(p["time_index"],return_inverse=True)
        pm=np.full((len(hours),len(xy)),np.nan)
        pm[inverse,p["station_index"]]=p["pred"]
        eligible=mask[hours-h]&np.isfinite(pm[:,src])&np.isfinite(pm[:,dst])
        diff=(pm[:,dst]-pm[:,src])/scale
        positive=np.maximum(diff,0)
        n=int(eligible.sum());v=int(np.count_nonzero((diff>.05)&eligible))
        row=dict(condition=condition,horizon_hours=h,family=family or "unregularized graph/temporal control",
                 lambda_max=strength if strength is not None else 0.,
                 eligible_observed_endpoint_arcs=n,violations=v,
                 violation_frequency=v/n if n else np.nan,
                 mean_squared_positive_ordering_difference_normalized=float(np.mean(positive[eligible]**2)) if n else np.nan,
                 threshold_normalized=.05,threshold_ug_m3=.05*scale,
                 zero_eligible_arc_hours=int(np.count_nonzero(~eligible.any(axis=1))),
                 posthoc_mask="original G0 actual-wind arcs at issue, both endpoints scored; used for every model regardless of training topology",
                 raw_train_penalty_first_batch_seed11=np.nan,weighted_train_penalty_first_batch_seed11=np.nan,
                 gradient_ratio_first_batch_seed11=np.nan)
        if family:
            r=replay[(replay.family==family)&(np.isclose(replay.lambda_max,strength))&(replay.seed==11)]
            assert len(r)==1
            row.update(raw_train_penalty_first_batch_seed11=float(r.iloc[0].raw_penalty),
                       weighted_train_penalty_first_batch_seed11=float(r.iloc[0].weighted_penalty),
                       gradient_ratio_first_batch_seed11=float(r.iloc[0].gradient_ratio))
        rows.append(row)

    for h in (1,3,6,12,24):
        for variant in ("self_loops","rewired","lag24","lookback36"):
            add(h,variant,load(h,variant))
    for variant in ("lag24_self_loops","lag24_rewired"):
        add(6,variant,load(6,variant))
    for family in HISTORICAL:
        for strength in (.06,.3,1.):
            add(6,f"{family}_lambda{strength:g}",load_fair(family,strength),family,strength)
    assert len(rows)==40
    p=V5/"PENALTY_DIAGNOSTICS_NEW_CONDITIONS.csv"
    with p.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    print(json.dumps(dict(rows=len(rows),six_hour_eligible_arcs=int(pd.DataFrame(rows).query("horizon_hours==6").eligible_observed_endpoint_arcs.iloc[0]))))


if __name__=="__main__":main()
