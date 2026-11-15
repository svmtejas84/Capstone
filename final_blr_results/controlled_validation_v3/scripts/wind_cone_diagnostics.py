"""Descriptive ordering diagnostics on the matched observed-pair population.

All variants are scored against the same *actual-wind* mask. Only arcs whose
two endpoint predictions have observed targets are included; this is narrower
than the all-node training penalty. A lower rate is not physical validation.
"""
import csv
import json
import numpy as np
from src.stpignn.station_graph import directed_knn_graph
from final_blr_results.controlled_validation_v3.scripts.train_controls import V3,ARR,FIT,HORIZONS,VARIANTS


def main():
    assert (V3/"metrics/matched_controls.csv").exists()
    z=np.load(ARR)
    edge,_=directed_knn_graph(z["coordinates"],4)
    src,dst=edge.numpy()
    xy=z["coordinates"]
    delta=xy[dst]-xy[src]
    bearing=np.arctan2(delta[:,0],delta[:,1])
    wind_to=np.deg2rad((z["raw_wind_degrees"].astype(float)+180)%360)
    angle=np.abs(np.angle(np.exp(1j*(wind_to[:,None]-bearing[None,:]))))
    true_mask=np.isfinite(wind_to[:,None])&(angle<=np.deg2rad(37.5))
    scale=float(json.loads((V3.parents[1]/"results/data_v2j_fit.json").read_text())["fit"]["target_standard_std"])
    rows=[]
    for h in HORIZONS:
        reference=None
        for v in VARIANTS:
            with np.load(V3/"predictions"/f"h{h}_{v}_ensemble.npz") as p:
                ti=p["time_index"]; sj=p["station_index"]; pred=p["pred"]; truth=p["truth"]
            keys=np.stack((ti,sj),axis=1)
            if reference is None: reference=(keys,truth)
            else:
                assert np.array_equal(keys,reference[0]) and np.array_equal(truth,reference[1])
            hours,inverse=np.unique(ti,return_inverse=True)
            pm=np.full((len(hours),len(xy)),np.nan,dtype=float)
            pm[inverse,sj]=pred
            issue=hours-h
            assert np.all(issue>=0)
            eligible=true_mask[issue]&np.isfinite(pm[:,src])&np.isfinite(pm[:,dst])
            diff=(pm[:,dst]-pm[:,src])/scale
            n=int(eligible.sum())
            for threshold in (0.,.01,.05,.1):
                count=int(np.count_nonzero((diff>threshold)&eligible))
                rows.append(dict(horizon_hours=h,variant=v,threshold_normalized=threshold,
                                 threshold_ug_m3=threshold*scale,violations=count,
                                 eligible_observed_pair_arcs=n,
                                 violation_percent=100*count/n if n else "",
                                 target_hours=len(hours),zero_eligible_arc_hours=int(np.count_nonzero(~eligible.any(axis=1))),
                                 comparison_mask="actual-wind cone; both endpoints observed",
                                 interpretation="descriptive station-space ordering only"))
    out=V3/"metrics/wind_cone_diagnostics.csv"
    with out.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    print(f"Wrote {len(rows)} descriptive wind-cone rows")


if __name__=="__main__":main()
