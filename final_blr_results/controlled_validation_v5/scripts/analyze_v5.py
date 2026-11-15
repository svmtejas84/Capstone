"""Exploratory matched comparisons from frozen V3 and one-time V5 predictions."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
import pandas as pd

from final_blr_results.controlled_validation_v3.scripts.analyze_controls import block_analysis, holm
from final_blr_results.controlled_validation_v3.scripts.smoke_gpu import ARR, V3
from final_blr_results.controlled_validation_v5.scripts.verify_and_score import V4, V5, HISTORICAL


def load(h, variant, seed=None):
    suffix = "_ensemble" if seed is None else f"_seed{seed}"
    root = V3 if variant == "zero" else V5
    path = root / "predictions" / f"h{h}_{variant}{suffix}.npz"
    with np.load(path) as z:
        return {k:z[k] for k in ("pred","truth","time_index","station_index")}


def fair_path(family, strength, seed=None):
    if family == "zero":
        root,name=V3,"zero"
    elif strength in HISTORICAL[family]:
        root,name=HISTORICAL[family][strength]
    else:
        root,name=V5,f"{family}_lambda{strength:g}"
    suffix="_ensemble" if seed is None else f"_seed{seed}"
    return root/"predictions"/f"h6_{name}{suffix}.npz"


def load_fair(family,strength,seed=None):
    with np.load(fair_path(family,strength,seed)) as z:
        return {k:z[k] for k in ("pred","truth","time_index","station_index")}


def paired(a,b,day,seed):
    for k in ("truth","time_index","station_index"):
        assert np.array_equal(a[k],b[k]),k
    delta=np.abs(a["pred"]-a["truth"])-np.abs(b["pred"]-b["truth"])
    ci,p,blocks,days=block_analysis(day,delta,seed)
    return dict(paired_delta_mae_ug_m3=float(np.mean(delta)),ci95_low_ug_m3=float(ci[0]),
                ci95_high_ug_m3=float(ci[1]),block_signflip_p=float(p),
                scored_pairs=len(delta),utc_days=days,nonoverlap_7day_blocks=blocks)


def save(rows,name):
    path=V5/name;path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def main():
    assert (V5/"metrics/NEW_TEST_SCORES.csv").exists()
    times=pd.to_datetime(np.load(ARR)["times_ns"],utc=True)
    graph=[];lag=[];cross=[];family=[];seedrows=[]
    for h in (1,3,6,12,24):
        ref=load(h,"zero")
        day=times[ref["time_index"]].floor("D").asi8
        for i,v in enumerate(("self_loops","rewired")):
            x=load(h,v);r=paired(ref,x,day,55000+h*10+i)
            graph.append(dict(horizon_hours=h,contrast=f"original_graph_minus_{v}",**r,
                              family="V5 graph topology 10",inference="exploratory exposed test"))
            for s in (11,23,37,51,79):
                a=load(h,"zero",s);b=load(h,v,s)
                for k in ("truth","time_index","station_index"):assert np.array_equal(a[k],b[k])
                d=float(np.mean(np.abs(a["pred"]-a["truth"])-np.abs(b["pred"]-b["truth"])))
                seedrows.append(dict(family="graph",horizon_hours=h,contrast=f"original_graph_minus_{v}",seed=s,
                                     paired_delta_mae_ug_m3=d,favors_first=d<0,scored_pairs=len(a["pred"])))
        for i,v in enumerate(("lag24","lookback36")):
            x=load(h,v);r=paired(ref,x,day,56000+h*10+i)
            lag.append(dict(horizon_hours=h,contrast=f"existing_12h_minus_{v}",**r,
                            family="V5 lag information 10",inference="exploratory exposed test"))
            for s in (11,23,37,51,79):
                a=load(h,"zero",s);b=load(h,v,s)
                for k in ("truth","time_index","station_index"):assert np.array_equal(a[k],b[k])
                d=float(np.mean(np.abs(a["pred"]-a["truth"])-np.abs(b["pred"]-b["truth"])))
                seedrows.append(dict(family="temporal",horizon_hours=h,contrast=f"existing_12h_minus_{v}",seed=s,
                                     paired_delta_mae_ug_m3=d,favors_first=d<0,scored_pairs=len(a["pred"])))
    for rows in (graph,lag):
        for r,p in zip(rows,holm([r["block_signflip_p"] for r in rows])):r["holm_family_p"]=float(p)
    lag_ref=load(6,"lag24")
    lag_day=times[lag_ref["time_index"]].floor("D").asi8
    for i,v in enumerate(("lag24_self_loops","lag24_rewired")):
        other=load(6,v);r=paired(lag_ref,other,lag_day,56500+i)
        cross.append(dict(horizon_hours=6,contrast=f"lag24_original_graph_minus_{v}",**r,
                          family="V5 secondary lag-matched graph 2",inference="exploratory exposed test"))
        for s in (11,23,37,51,79):
            a=load(6,"lag24",s);b=load(6,v,s)
            for k in ("truth","time_index","station_index"):assert np.array_equal(a[k],b[k])
            d=float(np.mean(np.abs(a["pred"]-a["truth"])-np.abs(b["pred"]-b["truth"])))
            seedrows.append(dict(family="lag-matched graph",horizon_hours=6,
                                 contrast=f"lag24_original_graph_minus_{v}",seed=s,
                                 paired_delta_mae_ug_m3=d,favors_first=d<0,scored_pairs=len(a["pred"])))
    for r,p in zip(cross,holm([r["block_signflip_p"] for r in cross])):r["holm_family_p"]=float(p)
    selected=json.loads((V5/"metrics/FAIRNESS_VALIDATION_SELECTION.json").read_text())
    true=load_fair("true_wind",selected["true_wind"])
    day=times[true["time_index"]].floor("D").asi8
    others=("zero","within_month_shuffle","full_shuffle","reverse_wind","constant_north","laplacian")
    for i,v in enumerate(others):
        other_strength=selected.get(v,0.0)
        other=load_fair(v,other_strength);r=paired(true,other,day,57000+i)
        family.append(dict(horizon_hours=6,contrast=f"validation_selected_true_minus_{v}",
                           true_lambda=selected["true_wind"],comparator_lambda=other_strength,**r,
                           family="V5 exploratory selected-family 6",inference="exploratory exposed test"))
        for s in (11,23,37,51,79):
            a=load_fair("true_wind",selected["true_wind"],s);b=load_fair(v,other_strength,s)
            for k in ("truth","time_index","station_index"):assert np.array_equal(a[k],b[k])
            d=float(np.mean(np.abs(a["pred"]-a["truth"])-np.abs(b["pred"]-b["truth"])))
            seedrows.append(dict(family="regularizer",horizon_hours=6,contrast=f"selected_true_minus_{v}",seed=s,
                                 paired_delta_mae_ug_m3=d,favors_first=d<0,scored_pairs=len(a["pred"])))
    for r,p in zip(family,holm([r["block_signflip_p"] for r in family])):r["holm_family_p"]=float(p)
    save(graph,"statistical_analysis/GRAPH_TOPOLOGY_CONTRASTS.csv")
    save(lag,"statistical_analysis/LAG_INFORMATION_CONTRASTS.csv")
    save(cross,"statistical_analysis/LAG_MATCHED_GRAPH_CONTRASTS.csv")
    save(family,"statistical_analysis/FAIRNESS_SELECTED_CONTRASTS.csv")
    save(seedrows,"statistical_analysis/V5_SEED_LEVEL.csv")
    summary=dict(graph_contrasts=len(graph),lag_contrasts=len(lag),lag_matched_graph_contrasts=len(cross),regularizer_contrasts=len(family),
                 seed_rows=len(seedrows),family_strengths=selected)
    (V5/"statistical_analysis/ANALYSIS_SUMMARY.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,indent=2))


if __name__=="__main__":main()
