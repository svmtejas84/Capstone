"""Regenerate v2m results from saved paired predictions only; no training."""
from __future__ import annotations

import glob
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from src.stpignn.paths import REPO_ROOT

BASE = REPO_ROOT / "final_blr_results/baselines/v2m"
OUT = BASE / "comparisons"
OUT.mkdir(parents=True, exist_ok=True)
SEEDS = (11,23,37,51,79)
HORIZONS = (1,3,6,12,24)
HIST_NEURAL = ("stpignn_original", "stpignn_lambda0", "gru_only", "vanilla_gcn", "st_gru_gcn")
HIST_STAT = ("persistence", "same_hour_yesterday", "ridge_lag_calendar_weather", "climatology_hod_dow", "station_train_mean")
KEY = ["target_time_utc", "station_id"]


def sha(path):
    d = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(4*1024*1024), b""):
            d.update(chunk)
    return d.hexdigest()


def load(path, model=None, seed=None):
    z = pd.read_parquet(path)
    if model is not None:
        assert set(z.model) == {model}, path
    if seed is not None:
        assert set(z.seed) == {seed}, path
    assert not z.duplicated(KEY).any(), path
    assert np.isfinite(z[["target_ug_m3", "prediction_ug_m3"]].to_numpy()).all(), path
    return z.set_index(KEY).sort_index()[["target_ug_m3", "prediction_ug_m3"]]


def same_population(a, b):
    if not a.index.equals(b.index) or not np.array_equal(a.target_ug_m3.to_numpy(), b.target_ug_m3.to_numpy()):
        raise ValueError("Evaluation populations or targets differ; no silent intersection")


def ensemble(frames):
    ref = frames[0]
    for z in frames[1:]: same_population(ref,z)
    out = ref.copy()
    out["prediction_ug_m3"] = np.mean([z.prediction_ug_m3.to_numpy() for z in frames], axis=0)
    return out


def metrics(z):
    y=z.target_ug_m3.to_numpy(float); p=z.prediction_ug_m3.to_numpy(float)
    e=p-y
    return dict(mae=float(np.abs(e).mean()),rmse=float(np.sqrt(np.square(e).mean())),
                r2=float(1-np.square(e).sum()/np.square(y-y.mean()).sum()),n_pairs=len(y))


def paired(a,b,seed):
    same_population(a,b)
    y=a.target_ug_m3.to_numpy(float);pa=a.prediction_ug_m3.to_numpy(float);pb=b.prediction_ug_m3.to_numpy(float)
    days,idx=np.unique(pd.to_datetime(a.index.get_level_values(0),utc=True).date,return_inverse=True)
    n=np.bincount(idx);d=np.bincount(idx,weights=np.abs(pa-y)-np.abs(pb-y))
    rng=np.random.default_rng(seed)
    picks=rng.integers(0,len(days),size=(2000,len(days)))
    boot=d[picks].sum(1)/n[picks].sum(1)
    effect=float(d.sum()/n.sum())
    signs=rng.choice((-1,1),size=(2000,len(days)))
    null=(signs*d).sum(1)/n.sum()
    return dict(paired_mae_difference=effect,relative_difference_percent=100*effect/metrics(b)["mae"],
                ci_low=float(np.quantile(boot,.025)),ci_high=float(np.quantile(boot,.975)),
                raw_sign_flip_p=float((1+np.count_nonzero(np.abs(null)>=abs(effect)))/2001),
                utc_days=len(days),n_pairs=len(y))


def holm(rows):
    order=sorted(range(len(rows)),key=lambda i:rows[i]["raw_sign_flip_p"])
    prior=0.0
    for rank,i in enumerate(order):
        prior=max(prior,min(1.0,(len(rows)-rank)*rows[i]["raw_sign_flip_p"]))
        rows[i]["holm_p_10"]=prior
        rows[i]["holm_reject_0_05"]=prior<.05


def write_csv(name,rows):
    pd.DataFrame(rows).to_csv(OUT/name,index=False)


def main():
    individual=[];summary=[];primary=[];secondary=[];artifacts=[]
    for h in HORIZONS:
        cache={}
        for model in ("mlp","tcn"):
            frames=[]
            for seed in SEEDS:
                cell=BASE/model/f"h{h}"/f"seed{seed}"
                marker=json.loads((cell/"COMPLETE.json").read_text())
                for key in ("checkpoint","predictions","metrics"):
                    path=cell/marker[key]["path"]
                    assert sha(path)==marker[key]["sha256"], path
                    artifacts.append(dict(path=str(path.relative_to(REPO_ROOT)),bytes=path.stat().st_size,sha256=sha(path),status="LOCAL ONLY"))
                z=load(cell/"predictions.parquet",model,seed)
                frames.append(z)
                individual.append(dict(model=model,horizon_hours=h,seed=seed,**metrics(z)))
            cache[model]=ensemble(frames)
            summary.append(dict(model=model,horizon_hours=h,aggregation="five-seed mean prediction",**metrics(cache[model]),
                                mean_individual_mae=float(np.mean([metrics(z)["mae"] for z in frames])),
                                sd_individual_mae=float(np.std([metrics(z)["mae"] for z in frames],ddof=1)),
                                mean_individual_rmse=float(np.mean([metrics(z)["rmse"] for z in frames])),
                                mean_individual_r2=float(np.mean([metrics(z)["r2"] for z in frames]))))
        for model in HIST_NEURAL:
            paths=[REPO_ROOT/f"results/benchmark_predictions_h{h}_{model}_seed{s}_v2j.parquet" for s in SEEDS]
            if not all(p.exists() for p in paths):
                secondary.append(dict(horizon_hours=h,model=model,status="MISSING HISTORICAL PREDICTIONS"))
                continue
            cache[model]=ensemble([load(p,model,s) for p,s in zip(paths,SEEDS)])
        path=REPO_ROOT/f"results/benchmark_predictions_h{h}_baselines_v2j.parquet"
        z=pd.read_parquet(path)
        for model in HIST_STAT:
            sub=z[z.model==model]
            if len(sub)==0:
                secondary.append(dict(horizon_hours=h,model=model,status="MISSING HISTORICAL PREDICTIONS"))
                continue
            cache[model]=load_frame(sub)
        for model,z in cache.items():
            same_population(cache["mlp"],z)
            if model in HIST_NEURAL or model in HIST_STAT:
                summary.append(dict(model=model,horizon_hours=h,aggregation="historical v2j ensemble" if model in HIST_NEURAL else "historical v2j deterministic",**metrics(z)))
        for model in ("mlp","tcn"):
            base=dict(horizon_hours=h,model="stpignn_original",baseline=model,
                      comparison_type="exploratory cross-protocol; weather information sets differ",
                      stpignn_mae=metrics(cache["stpignn_original"])["mae"],baseline_mae=metrics(cache[model])["mae"])
            primary.append({**base,**paired(cache["stpignn_original"],cache[model],4303+h*100+(0 if model=="mlp" else 1))})
        for model in ("mlp","tcn"):
            for baseline in (*HIST_NEURAL,*HIST_STAT):
                if baseline not in cache:continue
                secondary.append(dict(horizon_hours=h,model=model,baseline=baseline,
                                      comparison_type="descriptive cross-protocol; weather information sets differ",
                                      model_mae=metrics(cache[model])["mae"],baseline_mae=metrics(cache[baseline])["mae"],
                                      difference=metrics(cache[model])["mae"]-metrics(cache[baseline])["mae"],status="VERIFIED MATCHED TARGETS"))
    holm(primary)
    for row in primary:
        row["nominal_ci_excludes_zero"]=row["ci_low"]>0 or row["ci_high"]<0
        row["verdict"]="ST-PIGNN LOWER MAE" if row["paired_mae_difference"]<0 and row["holm_reject_0_05"] else "NO HOLM-SUPPORTED ST-PIGNN ADVANTAGE"
    write_csv("individual_seed_metrics.csv",individual)
    write_csv("ensemble_metrics.csv",summary)
    write_csv("primary_ten_comparisons.csv",primary)
    write_csv("secondary_comparisons.csv",secondary)
    (BASE/"reproducibility/artifact_checksums.csv").parent.mkdir(parents=True,exist_ok=True)
    pd.DataFrame(artifacts).to_csv(BASE/"reproducibility/artifact_checksums.csv",index=False)
    print(f"50 cells, {len(primary)} primary comparisons, {len(secondary)} secondary comparisons")


def load_frame(z):
    assert not z.duplicated(KEY).any()
    return z.set_index(KEY).sort_index()[["target_ug_m3","prediction_ug_m3"]]


if __name__=="__main__":main()
