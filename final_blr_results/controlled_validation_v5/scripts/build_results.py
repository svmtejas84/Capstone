"""Build numerical V5 tables from verified metrics without changing models."""
import re
from pathlib import Path

import numpy as np
import pandas as pd

V5=Path(__file__).resolve().parents[1]


def latex_cell(value):
    if pd.isna(value):
        return "NA"
    if isinstance(value, (float, np.floating)):
        return f"{value:.6g}"
    if isinstance(value, (bool, np.bool_)):
        return "yes" if value else "no"
    return re.sub(r"[\\&%$#_{}~^]", lambda m: "\\textbackslash{}" if m.group() == "\\" else "\\" + m.group(), str(value))


def save(df,name):
    out=V5/"tables";out.mkdir(exist_ok=True)
    df.to_csv(out/f"{name}.csv",index=False,float_format="%.9g",lineterminator="\n")
    with (out/f"{name}.tex").open("w") as f:
        f.write("% Numeric evidence only; exposed Bengaluru test; source: "+name+".csv\n")
        f.write("\\begin{tabular}{"+"l"+"r"*(len(df.columns)-1)+"}\n\\hline\n")
        f.write(" & ".join(latex_cell(c) for c in df.columns)+" \\\\\n\\hline\n")
        for row in df.itertuples(index=False,name=None):
            f.write(" & ".join(latex_cell(v) for v in row)+" \\\\\n")
        f.write("\\hline\n\\end{tabular}\n")


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
    save(pd.read_csv(V5/"statistical_analysis/V5_SEED_LEVEL.csv"),"T6_SEED_LEVEL")
    save(pd.read_csv(V5/"statistical_analysis/DAILY_LAG_SIMPLE_BASELINE.csv"),"T7_DAILY_BASELINE")
    save(pd.read_csv(V5/"PENALTY_DIAGNOSTICS_NEW_CONDITIONS.csv"),"T8_PENALTY_DIAGNOSTICS")
    print("9 numerical CSV/LaTeX pairs written")


if __name__=="__main__":main()
