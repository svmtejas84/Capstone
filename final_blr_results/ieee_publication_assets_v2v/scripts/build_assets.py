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
OUT = ROOT / "final_blr_results/ieee_publication_assets_v2v"
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
    if stem == "F03_multi_horizon_mae":
        fig.tight_layout(pad=1.1, rect=[0,.24,1,1])
    else:
        fig.tight_layout(pad=1.1)
    for ext in ("png", "pdf", "svg"):
        fig.savefig(directory / f"{stem}.{ext}", dpi=300, bbox_inches="tight")
    svg = directory / f"{stem}.svg"
    svg.write_text("\n".join(line.rstrip() for line in svg.read_text().splitlines()) + "\n")
    plt.close(fig)
    (directory / f"{stem}_caption.md").write_text(f"# {title}\n\n{caption}\n\nSource artifacts:\n" +
        "".join(f"- `{s}` (SHA-256 `{sha(read(s))}`)\n" for s in sources) +
        (f"\nDerived source data: `{derived}`.\n" if derived else "") +
        "\nRegenerate: `python final_blr_results/ieee_publication_assets_v2v/scripts/build_assets.py`.\n")
    manifest.append({"id": stem, "group": group, "title": title, "caption": caption,
                     "sources": sources, "source_data": derived,
                     "png": str((directory / f"{stem}.png").relative_to(OUT)),
                     "pdf": str((directory / f"{stem}.pdf").relative_to(OUT)),
                     "svg": str((directory / f"{stem}.svg").relative_to(OUT))})


def f01():
    # Distinct verified lanes: historical partitioned road implementation,
    # corrected station-graph evaluation, and the later neural-assisted decoder.
    fig, ax = plt.subplots(figsize=(7.15, 4.25)); ax.set_xlim(0, 14); ax.set_ylim(0, 8); ax.axis("off")
    def box(x,y,w,h,s,color,fs=5.5):
        ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.07",fc=color,ec="#263238",lw=.8))
        ax.text(x+w/2,y+h/2,s,ha="center",va="center",fontsize=fs,color="white",weight="bold",wrap=True)
    def arrow(a,b,dashed=False,color=GREY):
        ax.add_patch(FancyArrowPatch(a,b,arrowstyle="-|>",mutation_scale=9,lw=1,
                     linestyle="--" if dashed else "-",color=color))
    ax.text(.15,7.65,"Historical road-network engineering (separate implementation/evaluation protocol)",fontsize=8,weight="bold",color="#37474F")
    box(.2,6.45,2.0,.75,"Road data +\nweather inputs",GREY,5.0)
    box(2.65,6.45,2.3,.75,"154,902 road nodes\n64 partitions",GREY,5.1)
    box(5.4,6.45,2.4,.75,"GINEConv–GRU\n12 h; 16 node /\n16 edge channels; 96 hidden",GREY,4.8)
    box(8.25,6.45,2.2,.75,"Historical road-node\ninference pathway",GREY,5.1)
    box(10.9,6.45,2.7,.75,"Target-hour input\ninformation risk",GREY,5.1)
    for a,b in [((2.2,6.82),(2.65,6.82)),((4.95,6.82),(5.4,6.82)),((7.8,6.82),(8.25,6.82)),((10.45,6.82),(10.9,6.82))]: arrow(a,b)
    ax.text(.15,5.7,"Corrected station forecasting evaluation",fontsize=8,weight="bold",color=BLUE)
    box(.2,4.55,2.0,.78,"Observed PM2.5\n+ weather",BLUE,5.2)
    box(2.65,4.55,2.2,.78,"Retrospective\ncentered weather",BLUE,5.2)
    box(5.25,4.55,2.1,.78,"15 monitors\n60 directed kNN arcs",BLUE,5.0)
    box(7.75,4.55,2.05,.78,"12 h × 15 nodes\n× 18 channels",BLUE,5.0)
    box(10.2,4.55,1.35,.78,"GINEConv\nspace",GREEN,5.2)
    box(11.95,4.55,1.0,.78,"GRU\ntime",GREEN,5.2)
    box(13.2,4.55,.7,.78,"h=1/3/6/\n12/24",GREEN,4.8)
    for a,b in [((2.2,4.94),(2.65,4.94)),((4.85,4.94),(5.25,4.94)),((7.35,4.94),(7.75,4.94)),((9.8,4.94),(10.2,4.94)),((11.55,4.94),(11.95,4.94)),((12.95,4.94),(13.2,4.94))]: arrow(a,b)
    ax.text(2.8,4.27,"Missingness encoded in corrected feature channels; weather protocol differs by experiment family",fontsize=5.8,color="#333")
    # Loss is a training objective computed from predictions, never an input to the forward pass.
    box(6.55,3.15,3.1,.58,"Training-only\ndirectional regularization",PURPLE,5.0)
    arrow((12.45,4.55),(9.65,3.73),True,PURPLE)
    box(9.95,3.15,1.35,.58,"λ = 0",GREY)
    box(11.55,3.15,1.85,.58,"Laplacian smoothing",GREY,5.0)
    ax.text(6.6,2.87,"Separate training conditions; the directional hinge does not guarantee atmospheric mass conservation.",fontsize=5.5,color="#333")
    ax.text(.15,2.1,"Neural-assisted citywide estimation and routing (separate downstream extension; dashed arrows)",fontsize=7.7,weight="bold",color=ORANGE)
    box(.3,.78,2.3,.75,"Forecast-cutoff-safe\nstation forecasts",ORANGE,5.3)
    box(3.15,.78,2.0,.75,"15-station\nforecasts",ORANGE)
    box(5.65,.78,2.15,.75,"1,249-parameter\nspatial decoder",ORANGE,5.2)
    box(8.3,.78,2.15,.75,"154,902 experimental\nroad estimates",ORANGE,5.2)
    box(10.95,.78,2.3,.75,"Exposure-aware\nrouting prototype",ORANGE)
    for a,b in [((2.6,1.15),(3.15,1.15)),((5.15,1.15),(5.65,1.15)),((7.8,1.15),(8.3,1.15)),((10.45,1.15),(10.95,1.15))]: arrow(a,b,True,ORANGE)
    arrow((8.6,4.55),(1.45,1.53),True,ORANGE)
    save(fig,"F01_architecture","F01_corrected_architecture","ST-PIGNN implementations and downstream estimation pathways",
         "The historical road-network lane documents a partitioned GINEConv–GRU implementation and its distinct input protocol; it is not the corrected station-graph benchmark. The corrected forecasting graph has 15 station nodes and 60 directed kNN edges, with a 12-hour window and 18 channels. Weather handling differs across retrospective centered-weather and forecast-cutoff-safe evaluations. The directional hinge is a training-only objective evaluated on predictions; λ=0 and Laplacian are separate conditions. Dashed arrows denote experimental downstream station-to-road decoding and routing. Road-node values are estimates, not observed concentrations; no mass-conservation guarantee is implied.",
         ["final_blr_results/citywide_extension/v2q/ORIGINAL_MODEL_ARCHITECTURE.md","final_blr_results/physics_audit/methodology/PHYSICS_ATTRIBUTION_METHODOLOGY.md","final_blr_results/final_research_v2r/FINAL_RESEARCH_HANDOFF.md"])


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
    labels={"persistence":"Persistence","same_hour_yesterday":"Same hour yesterday","ridge_lag_calendar_weather":"Weather ridge",
            "vanilla_gcn":"Vanilla GCN","gru_only":"GRU-only","st_gru_gcn":"ST GRU-GCN","stpignn_original":"ST-PIGNN directional",
            "stpignn_lambda0":"ST-PIGNN λ=0","stpignn_laplacian":"ST-PIGNN Laplacian","adaptive_graph_st":"Adaptive graph",
            "adaptive_graph_st_fixed_knn":"Adaptive graph (fixed kNN)","station_train_mean":"Station training mean",
            "climatology_hod_dow":"Hour/day climatology","gine_gru_wind":"Wind-conditioned GINE–GRU",
            "stpignn_v2":"ST-PIGNN additional archived variant","stpignn_v2_source_removed":"ST-PIGNN, source term removed",
            "stpignn_v2_transport_removed":"ST-PIGNN, transport term removed"}
    # Focused panels avoid the v2u legend overlap. Full 17-variant grid is F03b.
    fig,axs=plt.subplots(1,2,figsize=(7.1,3.1),sharey=True)
    left=["persistence","same_hour_yesterday","climatology_hod_dow","station_train_mean","ridge_lag_calendar_weather",
          "stpignn_original","stpignn_lambda0","stpignn_laplacian","adaptive_graph_st"]
    palette=plt.get_cmap("tab10").colors
    for i,model in enumerate(left):
        z=a[a.model==model].sort_values("horizon_hours")
        if len(z): axs[0].plot(z.horizon_hours,z.mae_ug_m3,marker="o",ms=2.7,label=labels.get(model,model),color=palette[i%10],lw=1)
    for i,model in enumerate(["mlp","tcn"]):
        z=b[b.model==model].sort_values("horizon_hours")
        if len(z): axs[1].plot(z.horizon_hours,z.mae,marker="s",ms=3,label=model.upper(),color=[ORANGE,PURPLE][i],lw=1.2)
    for ax,title in zip(axs,["A  Retrospective centered-weather protocol","B  Forecast-cutoff-safe MLP/TCN protocol"]):
        ax.set_title(title);ax.set_xticks([1,3,6,12,24]);ax.set_xlabel("Forecast horizon (h)");ax.grid(alpha=.22)
        ax.legend(fontsize=5.0,ncol=2,loc="upper center",bbox_to_anchor=(.5,-.34),frameon=False)
    axs[0].set_ylabel("MAE (µg/m³)")
    fig.tight_layout(rect=[0,.18,1,1],w_pad=1.0)
    derived="source_data/F03_forecasting_metrics.csv"
    pd.concat([a.assign(protocol="v2j historical weather").rename(columns={"mae_ug_m3":"mae","rmse_ug_m3":"rmse"})
               [["protocol","model","horizon_hours","n_pairs","mae","rmse","r2"]],
               b.assign(protocol="v2m cutoff-safe weather")[["protocol","model","horizon_hours","n_pairs","mae","rmse","r2"]]]).to_csv(SRC/"F03_forecasting_metrics.csv",index=False)
    save(fig,"F03_forecasting_benchmarks","F03_multi_horizon_mae","Multi-horizon forecasting MAE by protocol",
         "Five horizons and 14,583 saved pairs per horizon in the retrospective centered-weather panel; MLP/TCN use a separate forecast-cutoff-safe feature protocol. These are not identical-input architecture ablations. The full 17-variant inventory is provided separately; unfavorable results are retained.",
         ["final_blr_results/ieee_paper_evidence/results/RECOMPUTED_V2J_BENCHMARK.csv","final_blr_results/baselines/v2m/comparisons/ensemble_metrics.csv"],derived)

    # Supplementary full-variant visualization, split into readable facets.
    variants=sorted(a.model.unique())
    ncols=4; nrows=int(np.ceil(len(variants)/ncols))
    f,axs=plt.subplots(nrows,ncols,figsize=(7.1,1.65*nrows),sharex=True)
    for ax,model in zip(axs.flat,variants):
        z=a[a.model==model].sort_values("horizon_hours")
        ax.plot(z.horizon_hours,z.mae_ug_m3,marker="o",ms=2.5,color=BLUE,lw=1)
        ax.set_title(labels.get(model,model.replace("_"," ")),fontsize=7)
        ax.grid(alpha=.2);ax.set_xticks([1,6,12,24]);ax.tick_params(labelsize=6)
    for ax in list(axs.flat)[len(variants):]: ax.axis("off")
    f.supxlabel("Forecast horizon (h)");f.supylabel("MAE (µg/m³)");f.tight_layout()
    save(f,"F03_forecasting_benchmarks","F03b_all_v2j_variants","Complete retrospective-weather model variant comparison",
         "Small multiples show all 17 archived model variants separately at five horizons (14,583 pairs per horizon). All curves belong to the retrospective centered-weather station evaluation; variants are exploratory and share an exposed test period. MLP/TCN are not shown because their cutoff-safe protocol differs.",
         ["final_blr_results/ieee_paper_evidence/results/RECOMPUTED_V2J_BENCHMARK.csv"],"source_data/F03_all_variants.csv")
    a.to_csv(SRC/"F03_all_variants.csv",index=False)


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
    # Rebuild paired directional-vs-Laplacian CIs from the five aligned saved predictions.
    ci_rows=[]; root=ROOT/"results"
    for h in [1,3,6,12,24]:
        frames={}
        for model in ["stpignn_original","stpignn_laplacian"]:
            fs=[]
            for seed in [11,23,37,51,79]:
                p=root/f"benchmark_predictions_h{h}_{model}_seed{seed}_v2j.parquet"
                if not p.exists(): p=ROOT/"results/codex_log/runs/benchmark_cpu_v2j"/p.name
                if not p.exists(): raise FileNotFoundError(p)
                fs.append(pd.read_parquet(p))
            key=["target_time_utc","station_id"]
            q=pd.concat(fs,ignore_index=True).pivot(index=key,columns="seed",values="prediction_ug_m3").mean(axis=1).rename(model)
            frames[model]=q
        pair=pd.concat([frames["stpignn_original"],frames["stpignn_laplacian"]],axis=1,join="inner").reset_index()
        # target values are verified equal across model files; use saved target from same rows.
        targ=pd.read_parquet(root/f"benchmark_predictions_h{h}_stpignn_original_seed11_v2j.parquet")[key+['target_ug_m3']].drop_duplicates(key)
        pair=pair.merge(targ,on=key,validate="one_to_one")
        pair["day"]=pd.to_datetime(pair.target_time_utc,utc=True).dt.floor("D")
        days=pair.groupby("day").agg(n=("target_ug_m3","size"),d=("stpignn_original",lambda x:0))
        # pooled paired MAE difference contributions per UTC day
        pair["d"]=np.abs(pair.stpignn_original-pair.target_ug_m3)-np.abs(pair.stpignn_laplacian-pair.target_ug_m3)
        agg=pair.groupby("day").agg(n=("d","size"),d=("d","sum"))
        calendar=pd.date_range(pair.day.min(),pair.day.max(),freq="D",tz="UTC")
        agg=agg.reindex(calendar,fill_value=0); nn=agg.n.to_numpy();dd=agg.d.to_numpy()
        rng=np.random.default_rng(7300+h); nd=len(nn); reps=2000; block=7
        starts=rng.integers(0,nd-block+1,size=(reps,int(np.ceil(nd/block))))
        picks=(starts[...,None]+np.arange(block)).reshape(reps,-1)[:,:nd]
        sims=dd[picks].sum(1)/nn[picks].sum(1)
        ci_rows.append({"horizon_hours":h,"n_pairs":len(pair),"calendar_days":nd,"observed_utc_days":int(pair.day.nunique()),"directional_minus_laplacian_mae":float(pair.d.mean()),
                        "seven_day_block_ci_low":float(np.quantile(sims,.025)),"seven_day_block_ci_high":float(np.quantile(sims,.975)),
                        "bootstrap_replicates":reps,"block_days":block,"seed":7300+h,"sign_convention":"negative favors directional"})
    ci=pd.DataFrame(ci_rows);ci.to_csv(SRC/"F04_directional_vs_laplacian_7day_CI.csv",index=False)
    derived="source_data/F04_physics_differences.csv"
    dd0=pd.DataFrame({"horizon_hours":piv.index,"ensemble_directional_minus_lambda0":d0.values,
                  "ensemble_directional_minus_laplacian":dl.values,"n_pairs":14583,"seed_count":5}).merge(ci,on="horizon_hours")
    dd0.to_csv(SRC/"F04_physics_differences.csv",index=False)
    axs[1].errorbar(range(5),ci.directional_minus_laplacian_mae,
                    yerr=[ci.directional_minus_laplacian_mae-ci.seven_day_block_ci_low,ci.seven_day_block_ci_high-ci.directional_minus_laplacian_mae],
                    fmt="none",ecolor="black",capsize=2,lw=.8)
    save(fig,"F04_physics_ablations","F04_directional_ablation","Directional regularization ablations",
         "Negative ΔMAE favors directional regularization. Panels A/B are five-seed ensemble differences; C shows individual-seed paired differences. No physical-specificity or mass-conservation inference follows. Multiplicity and seven-day block sensitivity are reported in T03.",
         ["final_blr_results/physics_audit/ensemble_analysis/ensemble_decomposition.csv","final_blr_results/physics_audit/seed_analysis/per_seed_physics_comparisons.csv"],derived)


def f05():
    w=pd.read_csv(read("results/loso_per_station_v2j.csv"))
    w=w[~w.seasonal_bias_corrected.astype(bool)]
    p=w[((w.method=="stpignn_original")&(w.anchor=="train_mean"))|((w.method=="ridge_weather_static")&(w.anchor=="baseline"))]
    pv=p.pivot(index="station_id",columns="method",values="mae").dropna().sort_index()
    counts=p[p.method=="stpignn_original"].set_index("station_id").loc[pv.index,"n"]
    station=pd.DataFrame({"station_id":pv.index.astype(int),"n_test_pairs":counts.to_numpy(),
        "stpignn_train_mean_anchor_mae":pv.stpignn_original.to_numpy(),"weather_static_ridge_baseline_anchor_mae":pv.ridge_weather_static.to_numpy()})
    station["paired_difference_stpignn_minus_ridge"]=station.stpignn_train_mean_anchor_mae-station.weather_static_ridge_baseline_anchor_mae
    station["winner"]=np.where(station.paired_difference_stpignn_minus_ridge<0,"ST-PIGNN","Weather/static ridge")
    rng=np.random.default_rng(8127); vals=station.paired_difference_stpignn_minus_ridge.to_numpy()
    draws=vals[rng.integers(0,len(vals),size=(20000,len(vals)))].mean(axis=1); site_ci=np.quantile(draws,[.025,.975])
    station.to_csv(SRC/"F05_station_paired_errors.csv",index=False)
    pd.DataFrame([{"estimand":"equal_station_mean_difference","estimate_ug_m3":vals.mean(),"ci_low_ug_m3":site_ci[0],"ci_high_ug_m3":site_ci[1],"unit":"station","n_sites":len(vals),"replicates":20000,"seed":8127}]).to_csv(SRC/"F05_station_bootstrap_summary.csv",index=False)
    v=pd.read_csv(read("final_blr_results/final_research_v2r/citywide/spatial_decoder/pooled_test_metrics.csv"))
    fig,axs=plt.subplots(1,2,figsize=(7.1,3.1),gridspec_kw={"width_ratios":[2.2,1]})
    x=np.arange(len(pv));axs[0].bar(x-.19,pv.stpignn_original,width=.38,label="ST-PIGNN",color=BLUE)
    axs[0].bar(x+.19,pv.ridge_weather_static,width=.38,label="Weather/static ridge",color=ORANGE)
    axs[0].set_xticks(x,[str(i) for i in pv.index],rotation=65);axs[0].set_ylabel("Held-out MAE (µg/m³)")
    axs[0].set_title("A  Station-isolated evaluation: 11 scored sites");axs[0].legend(frameon=False)
    methods={"train_only_spatial_mean":"Station mean","forecast_idw":"Forecast-IDW","forecast_decoder":"Decoder"}
    vv=v[v.method.isin(methods)].copy();axs[1].bar(range(len(vv)),vv.mae,color=[GREY,GREEN,PURPLE]);
    axs[1].set_xticks(range(len(vv)),[methods[m] for m in vv.method],rotation=35,ha="right")
    axs[1].set_title("B  Separate forecast-origin-safe task\n11 held-out sites")
    axs[1].set_ylabel("MAE (µg/m³)")
    station.rename(columns={"stpignn_train_mean_anchor_mae":"stpignn_mae","weather_static_ridge_baseline_anchor_mae":"ridge_mae"}).to_csv(SRC/"F05_W6_per_station.csv",index=False)
    save(fig,"F05_spatial_validation","F05_spatial_holdouts","Station-isolated and spatial-decoder evaluation",
         f"Station-isolated evaluation uses 11 scored sites (four eligible stations had no test targets). Pooled observation-weighted MAE is ST-PIGNN 22.314 versus weather/static ridge 20.624 µg/m³; equal-site mean paired difference is {vals.mean():+.3f} µg/m³ (station-bootstrap 95% CI {site_ci[0]:+.3f} to {site_ci[1]:+.3f}; 11 sites). Five sites favor ST-PIGNN and six favor ridge. Site 3409385 is influential. Separate six-hour decoder evaluation has pooled MAE 27.360 versus forecast-IDW 20.154; pooled and equal-site differences are distinct estimands. Repeated timestamps are not independent spatial sites.",
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
    save(fig,"F06_captum_explainability",stem,f"Spatio-temporal feature attribution: {subtitle}",
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
    display={"shortest":"Shortest distance","fastest":"Fastest time","minimum_dose":"Minimum modeled dose",
             "original_gs":"Original matcher","corrected_da":"Corrected allocator"}
    axs[0].set_yticks(range(len(g)),[display[x] for x in g.index]);axs[0].invert_yaxis()
    axs[0].set_xlim(0,105);axs[0].set_xlabel("Assigned requests (%)")
    axs[0].set_title("A  Original field: 9 demand batches\n0 violations; max edge use 4.5918%")
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
         "Original concentration scenario; nine frozen demand batches (252 requests per method). Maximum edge utilization in this scenario was 4.5918% (seed 37, demand 48); the 5.4054% maximum belongs to the spatial-sine perturbation across all four saved concentration fields. Corrected allocator and original matcher assigned all low-load requests; zero shared-edge violations. Corrected versus shortest: −0.001207% modeled dose and +0.001324% travel time. Axes span ±0.5% to show the small differences. This is modeled dose, not measured exposure reduction or classical matching stability.",
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
         "The saved routing study contains four fields: one original concentration field plus three prespecified perturbations (uniform scaling, spatial sine, and support-distance perturbation). Each perturbation has 252 requests. Bars show route identity stability, not calibrated exposure uncertainty. Assignment stability was 100% and declared edge-capacity violations zero in these low-load scenarios. No measured human exposure validation.",
         [path],"source_data/F08_sensitivity_stability.csv")


def main():
    SRC.mkdir(parents=True,exist_ok=True)
    f01();f02();f03();f04();f05()
    f06("final_blr_results/final_three_pillars/captum/attribution_tensors.npz","F06a_v2c_h1","One-hour ST-PIGNN variant")
    f06("final_blr_results/final_three_pillars/captum/v2r_heldout_h6/attribution_tensors.npz","F06b_v2r_h6","Six-hour station-isolated ST-PIGNN variant")
    f07();f08();f08_sensitivity()
    (OUT/"source_data/figure_manifest.json").write_text(json.dumps(manifest,indent=2))
    print("Generated",len(manifest),"figures")


if __name__=="__main__": main()
