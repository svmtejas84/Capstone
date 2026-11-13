"""Build v3 tables and figures from completed, locked evaluation artifacts."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from final_blr_results.controlled_validation_v3.scripts.train_controls import V3,HORIZONS,SEEDS,VARIANTS

LABEL={"zero":"No regularization","true_wind":"True-wind directional",
       "shuffled_wind":"Shuffled-wind directional","rotated_wind":"Rotated-wind directional",
       "laplacian":"Laplacian smoothing","gru_only":"GRU only","vanilla_gcn":"GCN",
       "st_gru_gcn":"GRU–GCN","adaptive_graph_st":"Adaptive graph",
       "weather_ridge":"Weather ridge","same_hour_yesterday":"Same hour yesterday",
       "station_train_mean":"Station train mean","climatology_hod_dow":"Hour/day climatology",
       "persistence":"Persistence","mlp":"MLP","tcn":"TCN"}


def fig(path):
    plt.tight_layout();plt.savefig(path.with_suffix(".png"),dpi=300,bbox_inches="tight")
    plt.savefig(path.with_suffix(".pdf"),bbox_inches="tight")
    plt.savefig(path.with_suffix(".svg"),bbox_inches="tight");plt.close()


def table(df,name):
    path=V3/"metrics"/f"{name}.csv";df.to_csv(path,index=False)
    (V3/"metrics"/f"{name}.tex").write_text(df.to_latex(index=False,float_format=lambda x:f"{x:.3f}",escape=True))


def main():
    assert (V3/"verification/test_unlock.json").exists()
    c=pd.read_csv(V3/"metrics/matched_controls.csv")
    b=pd.read_csv(V3/"metrics/baselines.csv")
    s=pd.read_csv(V3/"statistical_analysis/primary_contrasts.csv")
    out=V3/"figures";out.mkdir(exist_ok=True)
    plt.rcParams.update({"font.size":10,"axes.spines.top":False,"axes.spines.right":False})
    mainc=c[c.seed.astype(str).eq("ensemble")].copy();mainc["model"]=mainc.variant
    mainb=b[b.seed.astype(str).isin(["ensemble","deterministic"])].copy()
    t2=pd.concat([mainc[["horizon_hours","model","mae","rmse","r2","n"]],mainb[["horizon_hours","model","mae","rmse","r2","n"]]])
    t2["input_protocol"]="timestamp-causal historical observations; exposed test"
    table(t2.sort_values(["horizon_hours","mae"]),"T2_MATCHED_FORECASTING")
    table(c,"T3_WIND_CONTROLS_ALL_SEEDS")
    train=[]
    for p in (V3/"training/final").glob("*/COMPLETE.json"):
        train.append(json.loads(p.read_text()))
    table(pd.DataFrame(train).sort_values(["horizon_hours","seed","variant"]),"T4_EFFECTIVE_LAMBDA")
    table(c[c.seed.astype(str).ne("ensemble")],"T5_PER_SEED")
    table(s,"T6_STATISTICAL_INFERENCE")
    table(pd.DataFrame([{"spatial_study":"new v3 station-isolated experiment","status":"NOT EVALUATED","reason":"fold-isolated preprocessing and training not run"}]),"T7_SPATIAL_HOLDOUT")
    t8=pd.DataFrame([
        {"claim":"Cutoff-safe by observation timestamp","status":"SUPPORTED","limit":"release latency unverified"},
        {"claim":"Operational issuance-time validity","status":"NOT EVALUATED","limit":"weather issuance and station ingest times absent"},
        {"claim":"Independent temporal confirmation","status":"NOT EVALUATED","limit":"no untouched sufficiently long later holdout"},
        {"claim":"Atmospheric mass conservation","status":"UNSUPPORTED","limit":"directional hinge is not a balance equation"},
        {"claim":"Independent spatial transfer","status":"NOT EVALUATED","limit":"no new isolated station folds"}])
    table(t8,"T8_CLAIM_BOUNDARIES")
    z=np.load("final_blr_results/baselines/v2m/data/data_v2m_arrays.npz")
    times=pd.to_datetime(z["times_ns"],utc=True)
    t1=pd.DataFrame([{"stations":len(z["station_ids"]),"station_arcs":60,"history_hours":12,
                      "channels":18,"first_utc":str(times.min()),"last_utc":str(times.max()),
                      "exposed_test_observed_pairs":int(np.isfinite(z["observed_target"][times>=pd.Timestamp("2025-09-23",tz="UTC")]).sum()),
                      "weather_rule":"archive record timestamp <= feature hour; release unknown"}])
    table(t1,"T1_DATA_AND_INFORMATION")

    fig1=out/"F1_forecasting";plt.figure(figsize=(7,3.5))
    for name in ["true_wind","zero","adaptive_graph_st","gru_only","mlp","tcn","weather_ridge","same_hour_yesterday"]:
        sub=t2[t2.model.eq(name)].sort_values("horizon_hours")
        if len(sub):plt.plot(sub.horizon_hours,sub.mae,marker="o",label=LABEL[name])
    plt.xlabel("Forecast horizon (h)");plt.ylabel("MAE (µg/m³)");plt.title("Timestamp-causal historical-observation evaluation")
    plt.legend(ncol=2,fontsize=7,loc="upper left",bbox_to_anchor=(1.02,1));fig(fig1)

    fig2=out/"F2_wind_controls";plt.figure(figsize=(7,3.5))
    for name in VARIANTS:
        sub=mainc[mainc.variant.eq(name)].sort_values("horizon_hours")
        plt.plot(sub.horizon_hours,sub.mae,marker="o",label=LABEL[name])
    plt.xlabel("Forecast horizon (h)");plt.ylabel("MAE (µg/m³)");plt.title("Matched regularization controls; exposed test")
    plt.legend(fontsize=8);fig(fig2)

    fig3=out/"F3_paired_differences";plt.figure(figsize=(7,3.5))
    for name in VARIANTS:
        if name=="true_wind":continue
        sub=s[s.contrast.eq(f"true_wind_minus_{name}")].sort_values("horizon_hours")
        plt.errorbar(sub.horizon_hours,sub.paired_delta_mae_ug_m3,
          yerr=[sub.paired_delta_mae_ug_m3-sub.ci95_low_ug_m3,sub.ci95_high_ug_m3-sub.paired_delta_mae_ug_m3],
          marker="o",capsize=2,label=LABEL[name])
    plt.axhline(0,color="black",lw=.8);plt.xlabel("Forecast horizon (h)");plt.ylabel("True wind − control MAE (µg/m³)")
    plt.title("Exploratory seven-day block intervals; negative favors true wind");plt.legend(fontsize=8);fig(fig3)

    fig4=out/"F4_effective_lambda";plt.figure(figsize=(7,3.5))
    t4=pd.DataFrame(train);q=t4[t4.variant.ne("zero")]
    for name in ["true_wind","shuffled_wind","rotated_wind","laplacian"]:
        x=q[q.variant.eq(name)];plt.scatter(x.best_epoch,x.effective_lambda_at_best,label=LABEL[name],alpha=.65,s=20)
    plt.xlabel("Selected validation epoch");plt.ylabel("Effective λ at checkpoint")
    plt.title("Five-epoch warmup; nominal λ = 0.06");plt.legend(fontsize=7);fig(fig4)

    fig5=out/"F5_seed_stability";plt.figure(figsize=(7,3.5))
    indiv=c[c.seed.astype(str).ne("ensemble")]
    for name in VARIANTS:
        x=indiv[indiv.variant.eq(name)];means=x.groupby("horizon_hours").mae.mean();sd=x.groupby("horizon_hours").mae.std()
        plt.errorbar(means.index,means.values,yerr=sd.values,marker="o",capsize=2,label=LABEL[name])
    plt.xlabel("Forecast horizon (h)");plt.ylabel("Mean individual-seed MAE (µg/m³)")
    plt.title("Five fixed seeds; bars show seed SD, not spatial uncertainty");plt.legend(fontsize=8);fig(fig5)

    fig6=out/"F6_coverage_shift";plt.figure(figsize=(7,3.5))
    mask=z["observed_mask"]
    for label,start,end in [("Train","2022-01-01","2025-06-29"),("Validation","2025-07-01","2025-09-21"),("Exposed test","2025-09-23","2026-03-28")]:
        split=(times>=pd.Timestamp(start,tz="UTC"))&(times<=pd.Timestamp(end+"T23:00:00Z"))
        coverage=100*mask[split].mean()
        plt.bar(label,coverage,label=f"{label}: {coverage:.1f}%")
    plt.ylabel("Observed station-hour coverage (%)");plt.title("Monitoring coverage by chronology; 15 stations")
    fig(fig6)
    print("Wrote 8 CSV/LaTeX tables and 6 PNG/PDF/SVG figures; F7 spatial holdout not evaluated")


if __name__=="__main__":main()
