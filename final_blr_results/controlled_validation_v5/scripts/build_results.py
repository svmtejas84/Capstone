"""Build numerical V5 tables from verified metrics without changing models."""
import csv
from pathlib import Path

import numpy as np
import pandas as pd

V5=Path(__file__).resolve().parents[1]


def save(df,name):
    out=V5/"tables";out.mkdir(exist_ok=True)
    df.to_csv(out/f"{name}.csv",index=False,float_format="%.9g")
    with (out/f"{name}.tex").open("w") as f:
        f.write("% Numeric evidence only; exposed Bengaluru test; source: "+name+".csv\n")
        f.write(df.to_latex(index=False,escape=True,float_format=lambda x:f"{x:.3f}"))


def main():
    new=pd.read_csv(V5/"metrics/NEW_TEST_SCORES.csv")
    old=pd.read_csv(V5/"COMPLETE_MODEL_AND_BASELINE_REGISTER.csv")
    ens=new[new.seed.astype(str)=="ensemble"].copy()
    graph=ens[ens.variant.isin(("self_loops","rewired"))][["horizon_hours","variant","mae","rmse","r2","scored_pairs"]]
    ref=old[old.method=="zero"][["horizon_hours","method","mae_ug_m3","rmse_ug_m3","r2","scored_pairs"]].copy()
    ref.columns=graph.columns;graph=pd.concat((ref,graph),ignore_index=True).sort_values(["horizon_hours","variant"])
    save(graph,"T1_GRAPH_TOPOLOGY")
    temporal=ens[ens.variant.isin(("lag24","lookback36","lag24_self_loops","lag24_rewired"))][["horizon_hours","variant","mae","rmse","r2","scored_pairs"]]
    old_temporal=old[old.method.isin(("zero","same_hour_yesterday"))][["horizon_hours","method","mae_ug_m3","rmse_ug_m3","r2","scored_pairs"]].copy()
    old_temporal.columns=temporal.columns
    temporal=pd.concat((old_temporal,temporal),ignore_index=True).sort_values(["horizon_hours","variant"])
    save(temporal,"T2_LAG_INFORMATION")
    val=pd.read_csv(V5/"metrics/FAIRNESS_GRID_VALIDATION.csv")
    score=ens[ens.variant.str.contains("_lambda",na=False)][["variant","mae","rmse","r2","scored_pairs"]].copy()
    score["family"]=score.variant.str.rsplit("_lambda",n=1).str[0]
    score["lambda_max"]=score.variant.str.rsplit("_lambda",n=1).str[1].astype(float)
    selection=pd.read_json(V5/"metrics/FAIRNESS_VALIDATION_SELECTION.json",typ="series").to_dict()
    grid=val.merge(score.drop(columns="variant"),on=["family","lambda_max"],validate="one_to_one")
    grid["selected_on_validation"]=grid.apply(lambda r:bool(np.isclose(r.lambda_max,selection[r.family])),axis=1)
    save(grid,"T3_REGULARIZER_GRID")
    contrasts=[]
    for file in ("GRAPH_TOPOLOGY_CONTRASTS.csv","LAG_INFORMATION_CONTRASTS.csv",
                 "LAG_MATCHED_GRAPH_CONTRASTS.csv","FAIRNESS_SELECTED_CONTRASTS.csv"):
        d=pd.read_csv(V5/"statistical_analysis"/file)
        d["source_table"]=file
        contrasts.append(d)
    save(pd.concat(contrasts,ignore_index=True),"T4_PAIRED_CONTRASTS")
    save(pd.read_csv(V5/"TRAINING_SELECTION_REGISTER.csv"),"T5_TRAINING_SELECTION")
    save(pd.read_csv(V5/"ANCHOR_AGE_ALL_METHODS.csv"),"S1_ANCHOR_AGE_ALL_METHODS")
    print("6 numerical CSV/LaTeX pairs written")


if __name__=="__main__":main()
