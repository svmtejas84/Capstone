"""Render v2u publication assets exclusively from frozen saved artifacts."""
from __future__ import annotations

import __main__
import hashlib
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/stpignn_v2u_mpl")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
OUT = ROOT / "final_blr_results/ieee_publication_assets"
FIG = OUT / "figures"
SRC = OUT / "source_data"
BLUE, ORANGE, GREEN, PURPLE, GREY = "#277DA1", "#F28E2B", "#59A14F", "#8E6C8A", "#525B66"
plt.rcParams.update({"font.size": 8.5, "axes.titlesize": 9.5, "axes.labelsize": 8.5,
                     "xtick.labelsize": 8, "ytick.labelsize": 8, "legend.fontsize": 7,
                     "pdf.fonttype": 42, "svg.fonttype": "none", "savefig.facecolor": "white"})
manifest = []


def read(path):
    p = ROOT / path
    if not p.exists():
        raise FileNotFoundError(p)
    return p


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def save(fig, group, stem, title, caption, sources, derived=None):
    directory = FIG / group
    directory.mkdir(parents=True, exist_ok=True)
    fig.tight_layout(pad=1.1)
    for ext in ("png", "pdf", "svg"):
        fig.savefig(directory / f"{stem}.{ext}", dpi=300, bbox_inches="tight")
    svg = directory / f"{stem}.svg"
    svg.write_text("\n".join(line.rstrip() for line in svg.read_text().splitlines()) + "\n")
    plt.close(fig)
    (directory / f"{stem}_caption.md").write_text(f"# {title}\n\n{caption}\n\nSource artifacts:\n" +
        "".join(f"- `{s}` (SHA-256 `{sha(read(s))}`)\n" for s in sources) +
        (f"\nDerived source data: `{derived}`.\n" if derived else "") +
        "\nRegenerate: `python final_blr_results/ieee_publication_assets/scripts/build_assets.py`.\n")
    manifest.append({"id": stem, "group": group, "title": title, "caption": caption,
                     "sources": sources, "source_data": derived,
                     "png": str((directory / f"{stem}.png").relative_to(OUT)),
                     "pdf": str((directory / f"{stem}.pdf").relative_to(OUT)),
                     "svg": str((directory / f"{stem}.svg").relative_to(OUT))})


def f01():
    fig, ax = plt.subplots(figsize=(7.1, 3.6)); ax.set_xlim(0, 12); ax.set_ylim(0, 5); ax.axis("off")
    def box(x, y, w, h, s, color):
        ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.06",fc=color,ec="#263238",lw=.8))
        ax.text(x+w/2,y+h/2,s,ha="center",va="center",fontsize=5.8,color="white",weight="bold")
    def arrow(a,b,dashed=False):
        ax.add_patch(FancyArrowPatch(a,b,arrowstyle="-|>",mutation_scale=9,lw=1.1,
                                    linestyle="--" if dashed else "-",color=GREY))
    box(.1,3.55,1.6,.8,"Observations +\nmeteorology",BLUE)
    box(2,3.55,1.65,.8,"Cutoff-safe inputs\n+ missingness flags",BLUE)
    box(4,3.55,1.55,.8,"15-station kNN\n60 directed edges",BLUE)
    box(5.95,3.55,1.4,.8,"12 h × 18\ninput channels",BLUE)
    box(7.75,3.55,1.2,.8,"GINEConv\nspatial",GREEN)
    box(9.35,3.55,1.0,.8,"GRU\ntemporal",GREEN)
    box(10.75,3.55,1.15,.8,"PM₂.₅\n1/3/6/12/24 h",GREEN)
    for a,b in [((1.7,3.95),(2,3.95)),((3.65,3.95),(4,3.95)),((5.55,3.95),(5.95,3.95)),
                ((7.35,3.95),(7.75,3.95)),((8.95,3.95),(9.35,3.95)),((10.35,3.95),(10.75,3.95))]: arrow(a,b)
    box(7.7,2.05,2.4,.62,"Directional hinge loss\n(no conservation)",PURPLE)
    arrow((8.9,2.67),(8.9,3.55))
    box(1.15,.4,2.4,.75,"Station forecasts\nobserved sites",ORANGE)
    box(4.45,.4,2.4,.75,"Compact spatial decoder\n1,249 parameters",ORANGE)
    box(7.75,.4,2.2,.75,"154,902 road-node\nexperimental estimates",ORANGE)
    box(10.35,.4,1.55,.75,"Routing\nprototype",ORANGE)
    ax.plot([11.3,11.3,2.35],[3.55,1.8,1.8],ls="--",lw=1.1,color=GREY)
    arrow((2.35,1.8),(2.35,1.15),True)
    for a,b in [((3.55,.78),(4.45,.78)),((6.85,.78),(7.75,.78)),((9.95,.78),(10.35,.78))]: arrow(a,b,True)
    ax.text(.1,4.75,"Evaluated station forecasting",color=BLUE,weight="bold")
    ax.text(.1,1.55,"Experimental downstream extensions (dashed dataflow)",color=ORANGE,weight="bold")
    save(fig,"F01_architecture","F01_corrected_architecture","Corrected forecasting system and downstream extensions",
         "Solid: evaluated station forecasting and loss. Dashed: experimental decoder and routing dataflow. Road GNN training and mass conservation are not shown because neither was established.",
         ["final_blr_results/final_research_v2r/FINAL_RESEARCH_HANDOFF.md"])


def f02():
    import torch
    from pyproj import Transformer
    from final_blr_results.road_graph.inspect_graph_v2k import SpatialPartition
    __main__.SpatialPartition = SpatialPartition
    nodes = pd.read_parquet(read("data/graphs/bangalore_utm_nodes.parquet"))
    edges = pd.read_parquet(read("data/graphs/bangalore_utm_edges.parquet"), columns=["u","v"])
    index = pd.read_parquet(read("data/processed/graph/topology_nodeid_to_index_map.parquet"))
    assert np.array_equal(nodes.osmid.astype(str).to_numpy(),index.sort_values("node_index").node_id.astype(str).to_numpy())
    ids = dict(zip(index.node_id.astype(str),index.node_index.astype(int)))
    u = edges.u.astype(str).map(ids); v = edges.v.astype(str).map(ids)
    ok = u.notna() & v.notna(); uv=np.stack([u[ok].astype(int),v[ok].astype(int)],axis=1)
    xy = nodes[["x","y"]].to_numpy(); segs = xy[uv]
    parts=torch.load(read("data/processed/graph/partitioned_manifold_64_clusters.pt"),map_location="cpu",weights_only=False)
    labels=np.full(len(nodes),-1,dtype=int)
    for part in parts: labels[part.n_id.numpy().astype(int)]=int(part.cid)
    assert len(nodes)==154902 and len(edges)==393089 and np.all(labels>=0)
    station=pd.read_csv(read("results/stations_v2.csv"))
    tr=Transformer.from_crs(4326,32643,always_xy=True)
    sx,sy=tr.transform(station.longitude.to_numpy(),station.latitude.to_numpy())
    fig,axs=plt.subplots(1,3,figsize=(7.1,2.8),sharex=True,sharey=True)
    axs[0].add_collection(LineCollection(segs,colors="#36454F",linewidths=.12,rasterized=True))
    axs[0].set_title("A  Road topology\n393,089 directed edge rows")
    axs[1].scatter(xy[:,0],xy[:,1],c=labels,cmap="tab20",s=.08,rasterized=True)
    axs[1].set_title("B  Historical 64 partitions\n7,134 omitted cross-boundary arcs")
    axs[2].add_collection(LineCollection(segs,colors="#C8D0D4",linewidths=.08,rasterized=True))
    axs[2].scatter(sx,sy,s=22,c=ORANGE,edgecolors="black",linewidths=.3,zorder=4)
    axs[2].set_title("C  Fifteen monitors\ncorrected forecasting sites")
    for ax in axs: ax.set_aspect("equal"); ax.set_xlabel("UTM easting (m)"); ax.tick_params(axis="x",rotation=35)
    axs[0].set_ylabel("UTM northing (m)")
    derived="source_data/F02_graph_summary.csv"
    pd.DataFrame([{"road_nodes":len(nodes),"raw_directed_edges":len(edges),"processed_message_arcs":424550,
                   "historical_partitions":len(parts),"omitted_cross_boundary_arcs":7134,"forecast_stations":len(station),
                   "mapped_raw_edges":int(ok.sum()),"crs":"EPSG:32643"}]).to_csv(SRC/"F02_graph_summary.csv",index=False)
    save(fig,"F02_graph_partitions","F02_bengaluru_graph","Bengaluru road topology, historical partitions, and monitors",
         "Stored UTM graph and partition IDs; 154,902 nodes. The corrected forecasting model was evaluated on a separate 15-station, 60-edge kNN graph, not on the road graph. Arc and edge-row counts have different preprocessing semantics.",
         ["data/graphs/bangalore_utm_nodes.parquet","data/graphs/bangalore_utm_edges.parquet","data/processed/graph/partitioned_manifold_64_clusters.pt","results/stations_v2.csv"],derived)


def f03():
    a=pd.read_csv(read("final_blr_results/ieee_paper_evidence/results/RECOMPUTED_V2J_BENCHMARK.csv"))
    b=pd.read_csv(read("final_blr_results/baselines/v2m/comparisons/ensemble_metrics.csv"))
    old=[("persistence","Persistence"),("same_hour_yesterday","Yesterday"),("ridge_lag_calendar_weather","Weather ridge"),
         ("vanilla_gcn","GCN"),("gru_only","GRU"),("st_gru_gcn","ST GRU-GCN"),("stpignn_original","ST-PIGNN")]
    new=[("mlp","MLP"),("tcn","TCN")]
    fig,axs=plt.subplots(1,2,figsize=(7.1,3.15),sharey=True)
    colors=[BLUE,ORANGE,GREEN,PURPLE,GREY,"#C17C74","#1B6B6F"]
    for (model,label),c in zip(old,colors):
        z=a[a.model==model].sort_values("horizon_hours")
        axs[0].plot(z.horizon_hours,z.mae_ug_m3,marker="o",ms=3,label=label,color=c)
    for (model,label),c in zip(new,[ORANGE,PURPLE]):
        z=b[b.model==model].sort_values("horizon_hours")
        axs[1].plot(z.horizon_hours,z.mae,marker="s",ms=3,label=label,color=c)
    z=b[b.model=="stpignn_original"].sort_values("horizon_hours")
    axs[1].plot(z.horizon_hours,z.mae,marker="o",ms=3,ls="--",label="Historic ST-PIGNN reference",color=GREY)
    for ax,title in zip(axs,["A  v2j historical-weather protocol","B  v2m cutoff-safe weather protocol"]):
        ax.set_title(title);ax.set_xticks([1,3,6,12,24]);ax.set_xlabel("Forecast horizon (h)");ax.grid(alpha=.2)
        ax.legend(fontsize=6,ncol=2,loc="upper left",frameon=False)
    axs[0].set_ylabel("MAE (µg/m³)")
    derived="source_data/F03_forecasting_metrics.csv"
    pd.concat([a.assign(protocol="v2j historical weather").rename(columns={"mae_ug_m3":"mae","rmse_ug_m3":"rmse"})
               [["protocol","model","horizon_hours","n_pairs","mae","rmse","r2"]],
               b.assign(protocol="v2m cutoff-safe weather")[["protocol","model","horizon_hours","n_pairs","mae","rmse","r2"]]]).to_csv(SRC/"F03_forecasting_metrics.csv",index=False)
    save(fig,"F03_forecasting_benchmarks","F03_multi_horizon_mae","Multi-horizon forecasting MAE by protocol",
         "Five forecast horizons; 14,583 saved evaluation pairs per horizon. v2j ST-PIGNN and v2m MLP/TCN used different weather aggregation and are not identical-input architecture ablations. Negative and unfavorable results are retained.",
         ["final_blr_results/ieee_paper_evidence/results/RECOMPUTED_V2J_BENCHMARK.csv","final_blr_results/baselines/v2m/comparisons/ensemble_metrics.csv"],derived)


def f04():
    e=pd.read_csv(read("final_blr_results/physics_audit/ensemble_analysis/ensemble_decomposition.csv"))
    s=pd.read_csv(read("final_blr_results/physics_audit/seed_analysis/per_seed_physics_comparisons.csv"))
    piv=e.pivot(index="horizon_hours",columns="model",values="ensemble_mae")
    d0=piv.stpignn_original-piv.stpignn_lambda0
    dl=piv.stpignn_original-piv.stpignn_laplacian
    fig,axs=plt.subplots(1,3,figsize=(7.1,2.7))
    for ax,series,title,color in [(axs[0],d0,"A  Directional − λ=0",BLUE),(axs[1],dl,"B  Directional − Laplacian",ORANGE)]:
        ax.bar(range(5),series.values,color=[color if v<0 else "#C76F6F" for v in series]);ax.axhline(0,color="black",lw=.7)
        ax.set_xticks(range(5),[1,3,6,12,24]);ax.set_title(title);ax.set_xlabel("Horizon (h)");ax.set_ylabel("ΔMAE (µg/m³)")
    z=s[s.comparison=="physics-lambda0"]
    for seed,group in z.groupby("seed"):
        axs[2].plot(group.horizon_hours,group.paired_mae_difference,marker="o",ms=2.5,lw=.8,label=f"seed {seed}")
    axs[2].axhline(0,color="black",lw=.7);axs[2].set_xticks([1,3,6,12,24]);axs[2].set_title("C  Individual-seed paired ΔMAE")
    axs[2].set_xlabel("Horizon (h)");axs[2].legend(fontsize=5.5,ncol=2,frameon=False)
    derived="source_data/F04_physics_differences.csv"
    pd.DataFrame({"horizon_hours":piv.index,"ensemble_directional_minus_lambda0":d0.values,
                  "ensemble_directional_minus_laplacian":dl.values,"n_pairs":14583,"seed_count":5}).to_csv(SRC/"F04_physics_differences.csv",index=False)
    save(fig,"F04_physics_ablations","F04_directional_ablation","Directional regularization ablations",
         "Negative ΔMAE favors directional regularization. Panels A/B are five-seed ensemble differences; C shows individual-seed paired differences. No physical-specificity or mass-conservation inference follows. Multiplicity and seven-day block sensitivity are reported in T03.",
         ["final_blr_results/physics_audit/ensemble_analysis/ensemble_decomposition.csv","final_blr_results/physics_audit/seed_analysis/per_seed_physics_comparisons.csv"],derived)


def f05():
    w=pd.read_csv(read("results/loso_per_station_v2j.csv"))
    w=w[w.seasonal_bias_corrected.eq(False)]
    p=w[((w.method=="stpignn_original")&(w.anchor=="train_mean"))|((w.method=="ridge_weather_static")&(w.anchor=="baseline"))]
    pv=p.pivot(index="station_id",columns="method",values="mae").dropna().sort_index()
    counts=p[p.method=="stpignn_original"].set_index("station_id").loc[pv.index,"n"]
    v=pd.read_csv(read("final_blr_results/final_research_v2r/citywide/spatial_decoder/pooled_test_metrics.csv"))
    fig,axs=plt.subplots(1,2,figsize=(7.1,3.1),gridspec_kw={"width_ratios":[2.2,1]})
    x=np.arange(len(pv));axs[0].bar(x-.19,pv.stpignn_original,width=.38,label="ST-PIGNN",color=BLUE)
    axs[0].bar(x+.19,pv.ridge_weather_static,width=.38,label="Weather/static ridge",color=ORANGE)
    axs[0].set_xticks(x,[str(i) for i in pv.index],rotation=65);axs[0].set_ylabel("Held-out MAE (µg/m³)")
    axs[0].set_title("A  W6 LOSO: 11 scored sites; 4 unscored");axs[0].legend(frameon=False)
    methods={"train_only_spatial_mean":"Station mean","forecast_idw":"Forecast-IDW","forecast_decoder":"Decoder"}
    vv=v[v.method.isin(methods)].copy();axs[1].bar(range(len(vv)),vv.mae,color=[GREY,GREEN,PURPLE]);
    axs[1].set_xticks(range(len(vv)),[methods[m] for m in vv.method],rotation=35,ha="right")
    axs[1].set_title("B  v2r separate forecast task\n11 held-out sites")
    axs[1].set_ylabel("MAE (µg/m³)")
    pd.DataFrame({"station_id":pv.index,"stpignn_mae":pv.stpignn_original.values,"ridge_mae":pv.ridge_weather_static.values,
                  "n_test_pairs":counts.values}).to_csv(SRC/"F05_W6_per_station.csv",index=False)
    save(fig,"F05_spatial_validation","F05_spatial_holdouts","Spatial holdout forecasting: W6 and v2r",
         "W6 pooled MAE: ST-PIGNN 22.314 versus ridge 20.624 µg/m³; 11 scored stations, four without test observations. v2r is a separate forecast population: decoder 27.360, forecast-IDW 20.154, station mean 20.634 µg/m³. Timestamps are not independent spatial sites.",
         ["results/loso_per_station_v2j.csv","final_blr_results/final_research_v2r/citywide/spatial_decoder/pooled_test_metrics.csv"],"source_data/F05_W6_per_station.csv")


def f06(path,stem,subtitle):
    z=np.load(read(path),allow_pickle=True)
    records=[json.loads(str(r)) for r in z["records"]]
    mask=np.array([r["baseline"]=="training_mean" for r in records])
    attrs=z["attributions"][mask]
    names=[str(x) for x in z["feature_names"]]
    assert attrs.shape[1]==12
    # Axis order: record, oldest-to-newest lag, graph node, feature.
    abs_feature=np.abs(attrs).sum(axis=(1,2)).mean(axis=0)
    signed_feature=attrs.sum(axis=(1,2)).mean(axis=0)
    temporal_abs=np.abs(attrs).sum(axis=(2,3)).mean(axis=0)
    temporal_signed=attrs.sum(axis=(2,3)).mean(axis=0)
    heat=np.abs(attrs).sum(axis=2).mean(axis=0).T
    fig,axs=plt.subplots(1,3,figsize=(7.1,3.8),gridspec_kw={"width_ratios":[1.25,1,1.25]})
    order=np.argsort(abs_feature)
    axs[0].barh(np.arange(len(names)),abs_feature[order],color=BLUE)
    axs[0].set_yticks(np.arange(len(names)),[names[i].replace("_"," ") for i in order],fontsize=6)
    axs[0].set_xlabel("Mean sum |IG| (µg/m³)");axs[0].set_title("A  Feature attribution")
    lag=np.arange(11,-1,-1)
    axs[1].plot(lag,temporal_abs,marker="o",ms=2.5,color=ORANGE,label="absolute")
    axs[1].plot(lag,temporal_signed,marker="s",ms=2,color=PURPLE,label="signed")
    axs[1].set_xlabel("Hours before cutoff");axs[1].set_ylabel("Mean summed IG (µg/m³)")
    axs[1].set_xticks([11,8,5,2,0]);axs[1].set_title("B  Temporal attribution");axs[1].legend(frameon=False)
    im=axs[2].imshow(heat,aspect="auto",cmap="viridis",origin="lower")
    axs[2].set_yticks(np.arange(len(names)),[x.replace("_"," ") for x in names],fontsize=6)
    axs[2].set_xticks([0,3,6,9,11],[11,8,5,2,0]);axs[2].set_xlabel("Hours before cutoff")
    axs[2].set_title("C  Feature × lag |IG|");fig.colorbar(im,ax=axs[2],fraction=.05,pad=.02,label="Mean |IG| (µg/m³)")
    base=SRC/stem; base.mkdir(exist_ok=True)
    pd.DataFrame({"feature":names,"mean_absolute_ig_ug_m3":abs_feature,"mean_signed_ig_ug_m3":signed_feature}).to_csv(base/"features.csv",index=False)
    pd.DataFrame({"lag_hours_before_cutoff":lag,"mean_absolute_ig_ug_m3":temporal_abs,
                  "mean_signed_ig_ug_m3":temporal_signed}).to_csv(base/"lags.csv",index=False)
    pd.DataFrame(heat,index=names,columns=[str(i) for i in lag]).to_csv(base/"feature_lag.csv")
    selected=[r for r,m in zip(records,mask) if m]
    maxdelta=max(abs(r["completeness_delta_ug_m3"]) for r in selected)
    maxwrap=max(abs(r["wrapper_abs_error_ug_m3"]) for r in selected)
    save(fig,"F06_captum_explainability",stem,f"Integrated Gradients: {subtitle}",
         f"Real saved attribution tensors, primary training-mean baseline, {len(selected)} attributed records, 12 input hours. Mean absolute and signed IG are separate. Maximum completeness |delta| {maxdelta:.2g} µg/m³; wrapper error {maxwrap:.2g} µg/m³. IG is baseline-relative sensitivity, not causality or physics proof. Integration-step count is documented in source methodology.",
         [path],f"source_data/{stem}/")


def f07():
    path="final_blr_results/final_research_v2r/citywide/road_predictions/road_predictions_20251008T0700Z.parquet"
    d=pd.read_parquet(read(path))
    assert len(d)==154902 and d.node_index.nunique()==154902
    fig,axs=plt.subplots(1,2,figsize=(7.1,3.3),sharex=True,sharey=True)
    sc=axs[0].scatter(d.utm_x_m,d.utm_y_m,c=d.forecast_decoder_ug_m3,s=.15,cmap="viridis",rasterized=True)
    fig.colorbar(sc,ax=axs[0],fraction=.04,pad=.02,label="PM₂.₅ estimate (µg/m³)")
    axs[0].set_title("A  Experimental neural-assisted\nroad-node estimates")
    sc=axs[1].scatter(d.utm_x_m,d.utm_y_m,c=d.nearest_support_distance_m/1000,s=.15,cmap="magma",rasterized=True)
    fig.colorbar(sc,ax=axs[1],fraction=.04,pad=.02,label="Nearest monitor (km)")
    bad=d.poor_support_gt5km.astype(bool)
    axs[1].scatter(d.loc[bad,"utm_x_m"],d.loc[bad,"utm_y_m"],s=.06,color="cyan",rasterized=True,label=">5 km")
    station=pd.read_csv(read("results/stations_v2.csv"))
    from pyproj import Transformer
    sx,sy=Transformer.from_crs(4326,32643,always_xy=True).transform(station.longitude.to_numpy(),station.latitude.to_numpy())
    axs[1].scatter(sx,sy,marker="x",s=14,color="white",linewidths=.6,label="Monitor")
    axs[1].set_title("B  Monitoring support distance\ncyan: >5 km; ×: monitors")
    for ax in axs: ax.set_aspect("equal");ax.set_xlabel("UTM easting (m)");ax.tick_params(axis="x",rotation=30)
    axs[0].set_ylabel("UTM northing (m)")
    d[["node_index","utm_x_m","utm_y_m","forecast_decoder_ug_m3","nearest_support_distance_m","outside_station_hull","poor_support_gt5km"]].to_csv(SRC/"F07_snapshot_node_data.csv",index=False)
    save(fig,"F07_citywide_estimation","F07_citywide_snapshot","Experimental neural-assisted road-node estimates and support",
         "Earliest frozen origin, 2025-10-08 07:00 UTC, six-hour forecast; 154,902 saved node values without added smoothing. Station forecaster uses 15-station graph; road values use separate 1,249-parameter decoder. Decoder underperformed simple spatial controls; roadside accuracy is unvalidated. 19.45% of nodes lie >5 km from a monitor; 60.58% are outside the monitor convex hull.",
         [path,"results/stations_v2.csv"],"source_data/F07_snapshot_node_data.csv")


def f08():
    a=pd.read_csv(read("final_blr_results/final_routing_closure/v2t/ROUTING_COMPARISON_RESULTS.csv"))
    p=pd.read_csv(read("final_blr_results/final_routing_closure/v2t/PAIRED_COMPARISONS.csv"))
    orig=a[a.scenario=="original"]
    methods=["shortest","fastest","minimum_dose","original_gs","corrected_da"]
    g=orig[orig.method.isin(methods)].groupby("method").agg(requests=("requests","sum"),assigned=("assigned","sum"),
        violations=("edge_violations","sum"),max_utilization=("max_utilization","max")).reindex(methods)
    pair=p[(p.scenario=="original")&(p.candidate=="corrected_da")&(p.control.isin(["shortest","fastest","minimum_dose"]))]
    trade=pair.groupby("control")[["dose_delta_pct","time_overhead_pct"]].mean().reindex(["shortest","fastest","minimum_dose"])
    fig,axs=plt.subplots(1,2,figsize=(7.1,2.8))
    axs[0].barh(range(len(g)),g.assigned/g.requests*100,color=[GREY,GREEN,PURPLE,ORANGE,BLUE]);
    axs[0].set_yticks(range(len(g)),[x.replace("_"," ") for x in g.index]);axs[0].invert_yaxis()
    axs[0].set_xlim(0,105);axs[0].set_xlabel("Assigned requests (%)")
    axs[0].set_title("A  Original field: 9 demand batches\n0 observed edge-capacity violations")
    for name,row in trade.iterrows():
        axs[1].scatter(row.time_overhead_pct,row.dose_delta_pct,s=35,label=f"vs {name.replace('_',' ')}")
    axs[1].axhline(0,color=GREY,lw=.5);axs[1].axvline(0,color=GREY,lw=.5)
    axs[1].set_xlim(-.5,.5);axs[1].set_ylim(-.5,.5)
    axs[1].set_xlabel("Travel-time difference (%)");axs[1].set_ylabel("Modeled-dose difference (%)")
    axs[1].set_title("B  Corrected allocator, matched requests")
    near=trade.loc["shortest"]
    axs[1].text(-.47,-.46,f"vs shortest: dose {near.dose_delta_pct:+.6f}%\ntime {near.time_overhead_pct:+.6f}%",
                ha="left",va="bottom",fontsize=6.5,bbox=dict(facecolor="white",edgecolor="none",alpha=.9))
    axs[1].legend(frameon=False,fontsize=6)
    g.reset_index().to_csv(SRC/"F08_assignment.csv",index=False)
    trade.reset_index().to_csv(SRC/"F08_tradeoff.csv",index=False)
    save(fig,"F08_routing_evaluation","F08_routing_tradeoff","Routing assignment and modeled-dose trade-off",
         "Original concentration scenario; same nine frozen demand batches, 252 requests per method. Corrected allocator and original matcher assigned all in this low-load case; zero shared-edge violations and maximum utilization about 5.405%. Corrected versus shortest: −0.001207% modeled dose and +0.001324% travel time. Axes intentionally span ±0.5%. This is modeled dose, not measured exposure reduction or classical matching stability.",
         ["final_blr_results/final_routing_closure/v2t/ROUTING_COMPARISON_RESULTS.csv","final_blr_results/final_routing_closure/v2t/PAIRED_COMPARISONS.csv"],"source_data/F08_assignment.csv; F08_tradeoff.csv")


def f08_sensitivity():
    path="final_blr_results/final_routing_closure/v2t/SENSITIVITY_STABILITY.csv"
    d=pd.read_csv(read(path))
    z=d[d.method.isin(["original_gs","corrected_da","minimum_dose"])].copy()
    fig,ax=plt.subplots(figsize=(7.1,2.5))
    order=["uniform_125","spatial_sine","support_distance"]
    x=np.arange(len(order)); offsets={"original_gs":-.23,"corrected_da":0,"minimum_dose":.23}
    colors={"original_gs":ORANGE,"corrected_da":BLUE,"minimum_dose":GREEN}
    for name in offsets:
        q=z[z.method==name].set_index("scenario").reindex(order)
        ax.bar(x+offsets[name],100*q.route_stability,width=.22,color=colors[name],label=name.replace("_"," "))
    ax.set_xticks(x,["Uniform ×1.25","Spatial sine","Support distance"])
    ax.set_ylim(0,105);ax.set_ylabel("Unchanged route (%)")
    ax.set_title("Prespecified concentration perturbations; 252 requests per scenario")
    ax.legend(frameon=False,ncol=3,loc="upper center",bbox_to_anchor=(.5,-.20))
    z.to_csv(SRC/"F08_sensitivity_stability.csv",index=False)
    save(fig,"F08_routing_evaluation","F08b_routing_sensitivity","Routing sensitivity to modeled concentration perturbations",
         "Three frozen perturbations relative to the original field; 252 requests each. Bars show route identity stability, not calibrated exposure uncertainty. Assignment stability was 100% and declared edge-capacity violations zero in saved scenarios. No measured human exposure validation.",
         [path],"source_data/F08_sensitivity_stability.csv")


def main():
    SRC.mkdir(parents=True,exist_ok=True)
    f01();f02();f03();f04();f05()
    f06("final_blr_results/final_three_pillars/captum/attribution_tensors.npz","F06a_v2c_h1","v2c one-hour corrected ST-PIGNN")
    f06("final_blr_results/final_three_pillars/captum/v2r_heldout_h6/attribution_tensors.npz","F06b_v2r_h6","v2r six-hour outer-LOSO ST-PIGNN")
    f07();f08();f08_sensitivity()
    (OUT/"source_data/figure_manifest.json").write_text(json.dumps(manifest,indent=2))
    print("Generated",len(manifest),"figures")


if __name__=="__main__": main()
