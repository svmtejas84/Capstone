"""Descriptive numerical figures from verified V5 CSVs; no model execution."""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

V5=Path(__file__).resolve().parents[1]
H=[1,3,6,12,24]
COLORS={"Original station graph":"#0072B2","Self loops":"#D55E00","Rewired degree-preserving graph":"#009E73",
        "Existing 12-hour window":"#0072B2","Daily-lag augmented":"#D55E00","36-hour window":"#009E73",
        "Same-hour-yesterday":"#999999"}


def save(fig,name):
    out=V5/"figures";out.mkdir(exist_ok=True)
    for ext in ("png","pdf","svg"):
        fig.savefig(out/f"{name}.{ext}",dpi=300,bbox_inches="tight")
    plt.close(fig)


def main():
    plt.rcParams.update({"font.size":9,"axes.titlesize":10,"axes.labelsize":9,"legend.fontsize":8,
                         "pdf.fonttype":42,"svg.fonttype":"none"})
    score=pd.read_csv(V5/"metrics/NEW_TEST_SCORES.csv")
    old=pd.read_csv(V5/"COMPLETE_MODEL_AND_BASELINE_REGISTER.csv")
    ensemble=score[score.seed.astype(str)=="ensemble"]
    graph=pd.read_csv(V5/"statistical_analysis/GRAPH_TOPOLOGY_CONTRASTS.csv")
    fig,ax=plt.subplots(1,2,figsize=(10,3.5),layout="constrained")
    for name,variant in (("Original station graph","zero"),("Self loops","self_loops"),
                         ("Rewired degree-preserving graph","rewired")):
        data=(old[old.method==variant] if variant=="zero" else ensemble[ensemble.variant==variant])
        col="mae_ug_m3" if variant=="zero" else "mae"
        ax[0].plot(data.horizon_hours,data[col],marker="o",color=COLORS[name],label=name)
    ax[0].set(title="Station-graph topology: ensemble MAE",xlabel="Forecast horizon (h)",ylabel="MAE (µg/m³)",xticks=H)
    ax[0].legend(loc="lower right",frameon=False)
    for label,color in (("original_graph_minus_self_loops",COLORS["Self loops"]),
                        ("original_graph_minus_rewired",COLORS["Rewired degree-preserving graph"])):
        d=graph[graph.contrast==label]
        ax[1].errorbar(d.horizon_hours,d.paired_delta_mae_ug_m3,
                       yerr=np.array([d.paired_delta_mae_ug_m3-d.ci95_low_ug_m3,d.ci95_high_ug_m3-d.paired_delta_mae_ug_m3]),
                       marker="o",capsize=3,color=color,label=label.replace("original_graph_minus_","G0 minus ").replace("_"," "))
    ax[1].axhline(0,color="black",lw=.8)
    ax[1].set(title="Paired error difference, seven-day block CI",xlabel="Forecast horizon (h)",ylabel="ΔMAE (µg/m³); negative favors G0",xticks=H)
    ax[1].legend(frameon=False)
    fig.suptitle("Exploratory exposed-test graph comparison; 14,583 paired station-hours per horizon",fontsize=10)
    save(fig,"F1_graph_topology")

    lag=pd.read_csv(V5/"statistical_analysis/LAG_INFORMATION_CONTRASTS.csv")
    fig,ax=plt.subplots(1,2,figsize=(10,3.5),layout="constrained")
    for name,variant in (("Existing 12-hour window","zero"),("Daily-lag augmented","lag24"),
                         ("36-hour window","lookback36"),("Same-hour-yesterday","same_hour_yesterday")):
        data=(old[old.method==variant] if variant in ("zero","same_hour_yesterday") else ensemble[ensemble.variant==variant])
        col="mae_ug_m3" if variant in ("zero","same_hour_yesterday") else "mae"
        ax[0].plot(data.horizon_hours,data[col],marker="o",color=COLORS[name],label=name)
    ax[0].set(title="Temporal information and simple daily-lag control",xlabel="Forecast horizon (h)",ylabel="MAE (µg/m³)",xticks=H)
    ax[0].legend(frameon=False)
    for label,color in (("existing_12h_minus_lag24",COLORS["Daily-lag augmented"]),
                        ("existing_12h_minus_lookback36",COLORS["36-hour window"])):
        d=lag[lag.contrast==label]
        ax[1].errorbar(d.horizon_hours,d.paired_delta_mae_ug_m3,
                       yerr=np.array([d.paired_delta_mae_ug_m3-d.ci95_low_ug_m3,d.ci95_high_ug_m3-d.paired_delta_mae_ug_m3]),
                       marker="o",capsize=3,color=color,label=label.replace("existing_12h_minus_","L0 minus "))
    ax[1].axhline(0,color="black",lw=.8)
    ax[1].set(title="Paired error difference, seven-day block CI",xlabel="Forecast horizon (h)",ylabel="ΔMAE (µg/m³); negative favors L0",xticks=H)
    ax[1].legend(frameon=False)
    fig.suptitle("Exploratory exposed-test temporal comparison; 14,583 paired station-hours per horizon",fontsize=10)
    save(fig,"F2_lag_information")

    val=pd.read_csv(V5/"metrics/FAIRNESS_GRID_VALIDATION.csv")
    test=ensemble[ensemble.variant.str.contains("lambda",na=False)]
    fig,ax=plt.subplots(1,2,figsize=(10,3.5),layout="constrained")
    palette=plt.cm.tab10.colors
    for i,family in enumerate(val.family.unique()):
        a=val[val.family==family].sort_values("lambda_max")
        b=test[test.variant.str.startswith(family+"_lambda")].copy()
        b["lambda_max"]=b.variant.str.rsplit("lambda",n=1).str[-1].astype(float)
        b=b.sort_values("lambda_max")
        ax[0].plot(a.lambda_max,a.mean_five_seed_validation_mae,marker="o",color=palette[i],label=family.replace("_"," "))
        ax[1].plot(b.lambda_max,b.mae,marker="o",color=palette[i],label=family.replace("_"," "))
    for panel,title in ((ax[0],"Five-seed mean validation MAE"),(ax[1],"Exposed-test ensemble MAE")):
        panel.set(title=title,xlabel="Maximum regularization coefficient λ",ylabel="MAE (µg/m³)",xticks=[.06,.3,1.0])
    ax[0].legend(ncol=2,frameon=False,fontsize=7)
    fig.suptitle("Six-hour regularizer families; selection uses validation only",fontsize=10)
    save(fig,"F3_regularizer_grid")

    age=pd.read_csv(V5/"ANCHOR_AGE_ALL_METHODS.csv")
    fresh=age[(age.method=="zero")&(age.anchor_age_bucket=="1h")]
    fig,ax=plt.subplots(figsize=(5.3,3.2),layout="constrained")
    ax.bar(fresh.horizon_hours,fresh.fraction_of_scored_pairs*100,width=[.8,1.1,1.6,2,3],color="#56B4E9")
    ax.set(title="Genuine one-hour anchors among scored targets",xlabel="Forecast horizon (h)",
           ylabel="Fraction of scored pairs (%)",xticks=H,ylim=(0,100))
    ax.text(.02,.06,"14,583 observed targets per horizon; unscored hours excluded",transform=ax.transAxes,
            ha="left",va="bottom",fontsize=7,
            bbox={"facecolor":"white","alpha":.95,"edgecolor":"none","pad":2})
    save(fig,"F4_anchor_coverage")
    print("4 figure triplets written")


if __name__=="__main__":main()
