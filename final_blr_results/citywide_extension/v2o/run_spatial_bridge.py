"""Frozen retrospective station-to-road IDW bridge; no neural training or labels."""
from __future__ import annotations

import hashlib
import json
import resource
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.spatial import Delaunay, QhullError, distance

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
DATA = ROOT / "final_blr_results/baselines/v2m/data/data_v2m_arrays.npz"


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(4 * 1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def metrics(truth, pred):
    use = np.isfinite(pred)
    yy, pp = truth[use], pred[use]
    n = len(yy)
    return dict(n=int(n), coverage=float(n / len(truth)) if len(truth) else 0.0,
                mae=float(np.mean(np.abs(pp-yy))) if n else None,
                rmse=float(np.sqrt(np.mean((pp-yy)**2))) if n else None,
                r2=float(1-np.sum((pp-yy)**2)/np.sum((yy-yy.mean())**2)) if n>1 and np.sum((yy-yy.mean())**2)>0 else None)


def estimate(xy, support_xy, values):
    d = distance.cdist(xy, support_xy, metric="euclidean")
    nearest = np.argmin(d, axis=1)
    nd = d[np.arange(len(xy)), nearest]
    weights = 1 / np.maximum(d, 1e-6)**2
    pred = (weights @ values) / weights.sum(axis=1)
    exact = nd <= 1e-6
    pred[exact] = values[nearest[exact]]
    try:
        outside = Delaunay(support_xy).find_simplex(xy) < 0
        hull_status = "computed"
    except QhullError:
        outside = np.full(len(xy), True)
        hull_status = "unavailable_degenerate_support"
    return pred, nd, outside, hull_status


def validate(y, observed, times, ids, xy, train, test):
    per_pair = []
    train_means = np.nanmean(np.where(observed[train], y[train], np.nan), axis=0)
    for j in range(len(ids)):
        target_times = np.flatnonzero(test & observed[:, j])
        for t in target_times:
            good = np.flatnonzero(observed[t] & (np.arange(len(ids)) != j))
            pred_nearest = np.nan
            pred_idw = np.nan
            nearest_distance = np.nan
            if len(good):
                d = np.linalg.norm(xy[good] - xy[j], axis=1)
                k = np.argmin(d)
                pred_nearest = float(y[t, good[k]])
                nearest_distance = float(d[k])
                if len(good) >= 2:
                    w = 1 / np.maximum(d, 1e-6)**2
                    pred_idw = float(np.dot(w, y[t, good]) / w.sum())
            other = np.arange(len(ids)) != j
            train_mean = float(np.nanmean(train_means[other]))
            per_pair.append(dict(station_id=int(ids[j]), time_index=int(t), target_time_utc=str(times[t]),
                                 truth_ug_m3=float(y[t,j]), idw_ug_m3=pred_idw,
                                 nearest_ug_m3=pred_nearest, train_other_station_mean_ug_m3=train_mean,
                                 support_count=int(len(good)), nearest_support_distance_m=nearest_distance))
    pairs = pd.DataFrame(per_pair)
    pairs.to_parquet(OUT / "spatial_validation_pairs.parquet", index=False)
    rows = []
    for station_id, part in pairs.groupby("station_id"):
        for method, field in (("idw_p2","idw_ug_m3"),("nearest","nearest_ug_m3"),
                              ("train_other_station_mean","train_other_station_mean_ug_m3")):
            row = dict(station_id=int(station_id), method=method, observed_target_count=len(part))
            row.update(metrics(part.truth_ug_m3.to_numpy(),part[field].to_numpy()))
            rows.append(row)
    for station_id in sorted(set(map(int, ids)) - set(map(int, pairs.station_id.unique()))):
        for method in ("idw_p2", "nearest", "train_other_station_mean"):
            rows.append(dict(station_id=station_id, method=method, observed_target_count=0,
                             n=0, coverage=0.0, mae=None, rmse=None, r2=None))
    for method, field in (("idw_p2","idw_ug_m3"),("nearest","nearest_ug_m3"),
                          ("train_other_station_mean","train_other_station_mean_ug_m3")):
        row=dict(station_id="POOLED",method=method,observed_target_count=len(pairs))
        row.update(metrics(pairs.truth_ug_m3.to_numpy(),pairs[field].to_numpy()))
        rows.append(row)
    pd.DataFrame(rows).to_csv(OUT / "SPATIAL_VALIDATION_RESULTS.csv",index=False)
    return pairs, rows


def main():
    started = time.perf_counter()
    z = np.load(DATA)
    y, observed, station_xy = z["observed_target"], z["observed_mask"], z["coordinates"].astype(float)
    ids = z["station_ids"]
    times = pd.DatetimeIndex(pd.to_datetime(z["times_ns"], utc=True))
    train = (times >= pd.Timestamp("2022-01-01T00:00:00Z")) & (times <= pd.Timestamp("2025-06-29T23:00:00Z"))
    test = (times >= pd.Timestamp("2025-09-23T00:00:00Z")) & (times <= pd.Timestamp("2026-03-28T23:00:00Z"))
    pairs, rows = validate(y, observed, times, ids, station_xy, train, test)
    nodes = pd.read_parquet(ROOT / "data/graphs/bangalore_utm_nodes.parquet")
    elev = pd.read_parquet(ROOT / "data/processed/graph/nodes_elevation_true.parquet")
    assert len(nodes) == 154902 and len(elev) == len(nodes)
    assert np.array_equal(nodes.osmid.to_numpy(), elev.osmid.to_numpy())
    assert np.allclose(nodes[["x","y"]].to_numpy(), elev[["utm_x","utm_y"]].to_numpy())
    assert elev.elevation_true.notna().all()
    road_xy = nodes[["x","y"]].to_numpy(dtype=float)
    eligible = np.flatnonzero(test & (observed.sum(axis=1) >= 4))
    chosen = [int(eligible[k]) for k in (0, len(eligible)//2, len(eligible)-1)]
    (OUT / "selected_snapshots.json").write_text(json.dumps({"rule":"first median last test UTC hour with >=4 observed PM2.5 stations; mask only",
            "indices":chosen,"times_utc":[str(times[t]) for t in chosen],"station_array_sha256":sha(DATA)},indent=2)+"\n")
    all_outputs = []
    benchmarks = []
    for t in chosen:
        good = np.flatnonzero(observed[t])
        if len(good) < 4:
            raise RuntimeError("frozen support gate failed")
        chunks = []
        st = time.perf_counter()
        for a in range(0,len(road_xy),16384):
            p,nd,outside,hull = estimate(road_xy[a:a+16384],station_xy[good],y[t,good].astype(float))
            chunks.append((p,nd,outside))
        pred = np.concatenate([x[0] for x in chunks])
        nd = np.concatenate([x[1] for x in chunks])
        outside = np.concatenate([x[2] for x in chunks])
        elapsed = time.perf_counter()-st
        if not np.isfinite(pred).all() or (pred < 0).any() or len(pred)!=154902:
            raise RuntimeError("invalid full output")
        for size in (1000,10000):
            ss=time.perf_counter()
            small,_,_,_=estimate(road_xy[:size],station_xy[good],y[t,good].astype(float))
            small_elapsed=time.perf_counter()-ss
            err=float(np.max(np.abs(small-pred[:size])))
            if err>1e-6:
                raise RuntimeError("prefix/full mismatch")
            benchmarks.append(dict(time_utc=str(times[t]),nodes=size,seconds=small_elapsed,
                                   nodes_per_second=size/small_elapsed,prefix_max_abs_error_ug_m3=err,
                                   support_stations=len(good),peak_ram_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss))
        benchmarks.append(dict(time_utc=str(times[t]),nodes=len(road_xy),seconds=elapsed,
                               nodes_per_second=len(road_xy)/elapsed,prefix_max_abs_error_ug_m3=0.0,
                               support_stations=len(good),peak_ram_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss))
        frame = pd.DataFrame(dict(road_row_index=np.arange(len(nodes),dtype=np.int32),osmid=nodes.osmid.to_numpy(),
                    utm_x_m=road_xy[:,0],utm_y_m=road_xy[:,1],elevation_srtm_m=elev.elevation_true.to_numpy(),
                    target_time_utc=str(times[t]),method="retrospective_idw_p2",estimate_ug_m3=pred,
                    nearest_support_distance_m=nd,support_station_count=len(good),outside_support_hull=outside,
                    poor_support=outside | (nd>5000),observed_road_label=False))
        all_outputs.append(frame)
        fig,ax=plt.subplots(figsize=(9,8),constrained_layout=True)
        poor=frame[frame.poor_support]; supported=frame[~frame.poor_support]
        ax.scatter(poor.utm_x_m,poor.utm_y_m,c="lightgray",s=0.15,rasterized=True,label="poor support")
        s=ax.scatter(supported.utm_x_m,supported.utm_y_m,c=supported.estimate_ug_m3,s=0.3,cmap="viridis",rasterized=True)
        ax.scatter(station_xy[good,0],station_xy[good,1],c="red",s=25,marker="x",label="same-hour monitors")
        fig.colorbar(s,ax=ax,label="retrospective IDW estimate (µg/m³), supported subset")
        ax.set_title(f"Bengaluru {times[t]} — IDW estimate; gray nodes poorly supported")
        ax.set_xlabel("UTM east (m)");ax.set_ylabel("UTM north (m)");ax.legend()
        fig.savefig(OUT / f"citywide_idw_{t}.png",dpi=150);plt.close(fig)
        print("SNAPSHOT",str(times[t]),"support",len(good),"seconds",elapsed,flush=True)
    full = pd.concat(all_outputs,ignore_index=True)
    temp=OUT / "road_node_estimates.tmp.parquet"
    full.to_parquet(temp,index=False)
    temp.replace(OUT / "road_node_estimates.parquet")
    pd.DataFrame(benchmarks).to_csv(OUT / "execution_benchmarks.csv",index=False)
    summary=dict(source_data_sha256=sha(DATA),road_nodes_sha256=sha(ROOT / "data/graphs/bangalore_utm_nodes.parquet"),
                 elevation_sha256=sha(ROOT / "data/processed/graph/nodes_elevation_true.parquet"),
                 output_sha256=sha(OUT / "road_node_estimates.parquet"),snapshot_count=3,row_count=len(full),
                 selected_times_utc=[str(times[t]) for t in chosen],support_counts=[int(observed[t].sum()) for t in chosen],
                 poor_support_fraction=[float(f.poor_support.mean()) for f in all_outputs],
                 max_estimate_ug_m3=float(full.estimate_ug_m3.max()),min_estimate_ug_m3=float(full.estimate_ug_m3.min()),
                 total_seconds=time.perf_counter()-started,peak_ram_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                 gpu_vram_bytes=None,semantic_class="retrospective IDW spatial estimates; not forecasts or observations")
    (OUT / "execution_summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    run_dir=OUT / "runs/v2o_bridge";run_dir.mkdir(parents=True,exist_ok=True)
    (run_dir / "COMPLETE.tmp").write_text(summary["output_sha256"]+"\n")
    (run_dir / "COMPLETE.tmp").replace(run_dir / "COMPLETE")
    print(json.dumps(summary),flush=True)


if __name__=="__main__":
    main()
