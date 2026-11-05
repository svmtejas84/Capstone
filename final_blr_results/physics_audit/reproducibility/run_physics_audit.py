"""Read-only v2l statistics from saved corrected-weather v2j predictions.

No model creation, fitting, checkpoint writing, or historical output mutation.
"""
from __future__ import annotations

import hashlib
import json
import math
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "final_blr_results/physics_audit"
MODELS = ("stpignn_original", "stpignn_lambda0", "stpignn_laplacian")
LABELS = {"stpignn_original": "physics", "stpignn_lambda0": "lambda0", "stpignn_laplacian": "laplacian"}
PAIRS = (("stpignn_original", "stpignn_lambda0"),
         ("stpignn_original", "stpignn_laplacian"),
         ("stpignn_laplacian", "stpignn_lambda0"))
HORIZONS = (1, 3, 6, 12, 24)
SEEDS = (11, 23, 37, 51, 79)
REPS = 2000


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(4 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def write_csv(rel: str, rows: list[dict]):
    target = OUT / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(target, index=False)


def load_predictions(h, model, seed):
    path = ROOT / f"results/benchmark_predictions_h{h}_{model}_seed{seed}_v2j.parquet"
    frame = pd.read_parquet(path)
    key = ["target_time_utc", "station_id"]
    problems = []
    if len(frame) != 14583: problems.append("pair count differs from 14583")
    if frame.duplicated(key).any(): problems.append("duplicate key")
    if frame.model.nunique() != 1 or frame.model.iloc[0] != model: problems.append("model label mismatch")
    if frame.seed.nunique() != 1 or frame.seed.iloc[0] != seed: problems.append("seed mismatch")
    if frame.horizon_hours.nunique() != 1 or frame.horizon_hours.iloc[0] != h: problems.append("horizon mismatch")
    if not np.isfinite(frame[["target_ug_m3", "prediction_ug_m3"]].to_numpy()).all(): problems.append("nonfinite target or prediction")
    if not ((frame.target_ug_m3>=0)&(frame.target_ug_m3<=500)).all(): problems.append("target outside 0-500")
    frame = frame.set_index(key).sort_index()
    return frame, path, problems


def day_sums(y, a, b, dates):
    days, idx = np.unique(dates, return_inverse=True)
    n = np.bincount(idx, minlength=len(days))
    d = np.bincount(idx, weights=np.abs(a-y)-np.abs(b-y), minlength=len(days))
    return days, n, d


def day_ci(n, d, seed, block=1):
    rng = np.random.default_rng(seed)
    nd = len(n)
    if block == 1:
        picks = rng.integers(0, nd, size=(REPS, nd))
    else:
        starts = rng.integers(0, nd-block+1, size=(REPS, math.ceil(nd/block)))
        picks = (starts[..., None]+np.arange(block)).reshape(REPS,-1)[:,:nd]
    sims = d[picks].sum(1)/n[picks].sum(1)
    return np.quantile(sims,[.025,.975]).tolist(), sims


def metrics(y, p):
    return float(np.abs(p-y).mean()), float(np.sqrt(np.square(p-y).mean())), float(1-np.square(p-y).sum()/np.square(y-y.mean()).sum())


def holm(pvalues):
    order=np.argsort(pvalues)
    out=np.empty(len(pvalues),float)
    prior=0.0
    for rank,i in enumerate(order):
        prior=max(prior,min(1.0,(len(pvalues)-rank)*pvalues[i]))
        out[i]=prior
    return out


def main():
    for part in ("methodology","provenance","seed_analysis","ensemble_analysis","selection_audit","statistical_robustness","physical_diagnostics","reconciliation","figures","reproducibility"):
        (OUT/part).mkdir(parents=True,exist_ok=True)
    fit=json.loads((ROOT/"results/data_v2j_fit.json").read_text())
    assert fit["weather_half_hour_rule"] is True
    runs=pd.read_csv(ROOT/"results/benchmark_runs_v2j.csv")
    select=pd.read_csv(ROOT/"results/benchmark_selection_v2j.csv")
    prior=pd.read_csv(ROOT/"final_blr_results/baselines/paired_architecture_comparisons.csv")
    dataset=ROOT/"results/data_v2j_arrays.npz"
    datahash=sha(dataset)
    inventory=[]; configs=[]; selection=[]; per_seed=[]; ensemble=[]; stability=[]; monthly=[]; blocks=[]; multiplicity=[]; sign_replay=[]
    caches={}; paths=[]
    for h in HORIZONS:
        for model in MODELS:
            for seed in SEEDS:
                frame,path,problems=load_predictions(h,model,seed)
                caches[h,model,seed]=frame
                paths.append(path)
                rr=runs[(runs.model==model)&(runs.horizon_hours==h)&(runs.split=="test")&(runs.seed==seed)]
                assert len(rr)==1, (h,model,seed,len(rr))
                rr=rr.iloc[0]
                candidates=select[(select.model==model)&(select.horizon_hours==h)].sort_values("lr")
                assert len(candidates)==4 and set(np.round(candidates.lr,7))=={.0001,.0003,.001,.003}
                picked=candidates.sort_values("validation_mae").iloc[0]
                if not np.isclose(rr.lr,picked.lr): problems.append("selected LR not validation minimum")
                keyhash=hashlib.sha256(pd.util.hash_pandas_object(frame.index.to_frame(index=False),index=False).values.tobytes()).hexdigest()
                targethash=hashlib.sha256(frame.target_ug_m3.to_numpy().tobytes()).hexdigest()
                inventory.append(dict(horizon_hours=h,model=model,seed=seed,path=path.relative_to(ROOT),sha256=sha(path),rows=len(frame),utc_days=len(pd.unique(pd.to_datetime(frame.index.get_level_values(0),utc=True).date)),station_count=frame.index.get_level_values(1).nunique(),key_sha256=keyhash,target_sha256=targethash,problems="; ".join(problems) or "none"))
                configs.append(dict(horizon_hours=h,model=model,seed=seed,implementation="gnn.model.STPIGNN via src/stpignn/models_v2.py",source_commit="9a299f1bf01787f26750515cad8dff370e9c9aa0",dataset="results/data_v2j_arrays.npz",dataset_sha256=datahash,split="configs/data_v2.yaml",lr=rr.lr,weight_decay=.01,best_epoch=int(rr.best_epoch),epochs_run=int(rr.epochs_run),max_epochs=30,early_stopping_patience=5,validation_mae=rr.validation_mae,input="12x15x18; 13 fitted+lag_is_imputed+4 calendar",graph="directed 4-nearest station graph",edge="distance_m",loss="MSE standardized log1p residual + warmup coefficient * regularizer",regularizer="upwind hinge" if model==MODELS[0] else "none" if model==MODELS[1] else "Laplacian squared gradient",lambda_max=.06 if model!=MODELS[1] else 0.0,target="observed PM2.5 0-500; log1p train standardized",mask="all observed test station-hours",prediction_path=path.relative_to(ROOT),checkpoint_path="NONE SAVED",execution_log="results/codex_log/runs/benchmark_gpu_v2j/attempt_0_20261105T130158Z.log"))
                selection.append(dict(horizon_hours=h,model=model,seed=seed,lr_candidates="0.0001,0.0003,0.001,0.003",selected_lr=rr.lr,best_epoch=int(rr.best_epoch),epochs_run=int(rr.epochs_run),validation_mae=rr.validation_mae,lr_grid_boundary=rr.lr in (.0001,.003),early_stopped=rr.epochs_run<30,completed=True,search_seed=11,search_budget=4,selection="minimum validation MAE across LR candidates; seed 11 only",test_used_for_selection=False))
        reference=caches[h,MODELS[0],SEEDS[0]]
        ref_index=reference.index; ref_y=reference.target_ug_m3.to_numpy()
        for model in MODELS:
            for seed in SEEDS:
                frame=caches[h,model,seed]
                assert frame.index.equals(ref_index) and np.array_equal(frame.target_ug_m3.to_numpy(),ref_y), (h,model,seed,"population mismatch")
        days=pd.to_datetime(ref_index.get_level_values(0),utc=True).date
        for first,second in PAIRS:
            for seed in SEEDS:
                a=caches[h,first,seed].prediction_ug_m3.to_numpy();b=caches[h,second,seed].prediction_ug_m3.to_numpy()
                ma=metrics(ref_y,a)[0];mb=metrics(ref_y,b)[0]
                all_mae={LABELS[name]:metrics(ref_y,caches[h,name,seed].prediction_ug_m3.to_numpy())[0] for name in MODELS}
                unique,n,d=day_sums(ref_y,a,b,days)
                ci,_=day_ci(n,d,4303+h*10000+seed*10+PAIRS.index((first,second)))
                per_seed.append(dict(horizon_hours=h,comparison=f"{LABELS[first]}-{LABELS[second]}",seed=seed,physics_mae=all_mae["physics"],lambda0_mae=all_mae["lambda0"],laplacian_mae=all_mae["laplacian"],first_mae=ma,second_mae=mb,paired_mae_difference=ma-mb,relative_difference_percent=100*(ma-mb)/mb,n_pairs=len(ref_y),utc_days=len(unique),ci_low=ci[0],ci_high=ci[1],direction="first" if ma<mb else "second" if ma>mb else "tie"))
        for model in MODELS:
            matrix=np.stack([caches[h,model,s].prediction_ug_m3.to_numpy() for s in SEEDS])
            maes=np.mean(np.abs(matrix-ref_y),axis=1);ens=matrix.mean(axis=0)
            ensemble.append(dict(horizon_hours=h,model=model,mean_individual_mae=float(maes.mean()),median_individual_mae=float(np.median(maes)),ensemble_mae=metrics(ref_y,ens)[0],ensemble_gain=float(maes.mean()-metrics(ref_y,ens)[0]),n_pairs=len(ref_y),seed_count=5))
        a=np.mean([caches[h,MODELS[0],s].prediction_ug_m3.to_numpy() for s in SEEDS],axis=0)
        b=np.mean([caches[h,MODELS[1],s].prediction_ug_m3.to_numpy() for s in SEEDS],axis=0)
        unique,n,d=day_sums(ref_y,a,b,days)
        # Preserve calendar order; missing days (if any) contribute zero pairs.
        calendar=pd.date_range(unique.min(),unique.max(),freq="D").date
        full=pd.DataFrame({"day":calendar}).merge(pd.DataFrame({"day":unique,"n":n,"d":d}),on="day",how="left").fillna(0)
        n7=full.n.to_numpy(int);d7=full.d.to_numpy(float)
        ci7,_=day_ci(n7,d7,4303+h*1000+7,7)
        priorrow=prior[(prior.horizon_hours==h)&(prior.model==MODELS[0])&(prior.baseline==MODELS[1])].iloc[0]
        original_row_index=HORIZONS.index(h)*7+3
        original_seed=4303+h*100+original_row_index
        replay_rng=np.random.default_rng(original_seed)
        replay_pick=replay_rng.integers(0,len(unique),size=(REPS,len(unique)))
        replay_boot=d[replay_pick].sum(1)/n[replay_pick].sum(1)
        replay_sign=replay_rng.choice((-1,1),size=(REPS,len(unique)))
        replay_null=(replay_sign*d).sum(1)/n.sum()
        replay_p=(1+np.count_nonzero(np.abs(replay_null)>=abs(d.sum()/n.sum())))/(REPS+1)
        replay_ci=np.quantile(replay_boot,[.025,.975])
        assert abs(replay_p-priorrow.sign_flip_p_two_sided)<1e-12
        assert max(abs(replay_ci[0]-priorrow.nominal_ci_low),abs(replay_ci[1]-priorrow.nominal_ci_high))<1e-5
        sign_replay.append(dict(horizon_hours=h,original_seed=original_seed,original_row_index=original_row_index,replayed_p=replay_p,v2k_p=priorrow.sign_flip_p_two_sided,replayed_ci_low=replay_ci[0],replayed_ci_high=replay_ci[1],v2k_ci_low=priorrow.nominal_ci_low,v2k_ci_high=priorrow.nominal_ci_high,status="REPRODUCED"))
        blocks.append(dict(horizon_hours=h,n_pairs=len(ref_y),observed_utc_days=len(unique),calendar_days=len(calendar),difference=float(d.sum()/n.sum()),utc_day_ci_low=priorrow.nominal_ci_low,utc_day_ci_high=priorrow.nominal_ci_high,seven_day_ci_low=ci7[0],seven_day_ci_high=ci7[1],utc_day_excludes_zero=bool(priorrow.nominal_ci_low*priorrow.nominal_ci_high>0),seven_day_excludes_zero=bool(ci7[0]*ci7[1]>0)))
        month=pd.to_datetime(ref_index.get_level_values(0),utc=True).strftime("%Y-%m")
        for mo in sorted(set(month)):
            mask=np.asarray(month==mo)
            monthly.append(dict(horizon_hours=h,month_utc=mo,n_pairs=int(mask.sum()),utc_days=len(set(np.asarray(days)[mask])),physics_mae=float(np.abs(a[mask]-ref_y[mask]).mean()),lambda0_mae=float(np.abs(b[mask]-ref_y[mask]).mean()),paired_mae_difference=float((np.abs(a[mask]-ref_y[mask])-np.abs(b[mask]-ref_y[mask])).mean())))
        top=np.argsort(np.abs(d))[::-1][:5]
        multiplicity.append(dict(horizon_hours=h,comparison="physics-lambda0",difference=float(d.sum()/n.sum()),nominal_ci_low=priorrow.nominal_ci_low,nominal_ci_high=priorrow.nominal_ci_high,sign_flip_p=priorrow.sign_flip_p_two_sided,original_35_holm_p=priorrow.holm_adjusted_p,original_35_holm_reject=priorrow.holm_reject_0_05,top5_abs_day_fraction=float(np.abs(d[top]).sum()/np.abs(d).sum()),top5_day_contribution_to_pooled=float(d[top].sum()/n.sum()),top5_days=",".join(map(str,np.asarray(unique)[top]))))
    five=holm(np.asarray([x["sign_flip_p"] for x in multiplicity]))
    for row,p in zip(multiplicity,five):
        row["retrospective_5_holm_p"]=p;row["retrospective_5_holm_reject_0_05"]=p<.05
    for h in HORIZONS:
        for first,second in PAIRS:
            sub=[r for r in per_seed if r["horizon_hours"]==h and r["comparison"]==f"{LABELS[first]}-{LABELS[second]}"]
            diff=np.array([r["paired_mae_difference"] for r in sub])
            stability.append(dict(horizon_hours=h,comparison=sub[0]["comparison"],mean=float(diff.mean()),median=float(np.median(diff)),sd_sample=float(diff.std(ddof=1)),minimum=float(diff.min()),maximum=float(diff.max()),seeds_favor_first=int((diff<0).sum()),seeds_favor_second=int((diff>0).sum()),ties=int((diff==0).sum()),n_seeds=5))
    write_csv("provenance/prediction_integrity.csv",inventory)
    write_csv("provenance/model_configurations.csv",configs)
    write_csv("selection_audit/selected_configurations.csv",selection)
    write_csv("seed_analysis/per_seed_physics_comparisons.csv",per_seed)
    write_csv("seed_analysis/seed_stability_summary.csv",stability)
    write_csv("ensemble_analysis/ensemble_decomposition.csv",ensemble)
    write_csv("statistical_robustness/monthly_effects.csv",monthly)
    write_csv("statistical_robustness/block_bootstrap_sensitivity.csv",blocks)
    write_csv("statistical_robustness/multiplicity_analysis.csv",multiplicity)
    write_csv("statistical_robustness/sign_flip_reproduction.csv",sign_replay)
    old_sweep=pd.read_csv(ROOT/"results/lambda_sweep_v2g.csv")
    limited=pd.read_csv(ROOT/"results/lambda_check_v2j.csv")
    matrix=[]
    for h in HORIZONS:
        old=old_sweep[(old_sweep.horizon_hours==h)&(old_sweep.model==MODELS[0])&(np.isclose(old_sweep["lambda"],.06))].iloc[0]
        check=limited[(limited.horizon_hours==h)&(limited.model==MODELS[0])&(np.isclose(limited["lambda"],.06))]
        current=next(r for r in multiplicity if r["horizon_hours"]==h)
        st=next(r for r in stability if r["horizon_hours"]==h and r["comparison"]=="physics-lambda0")
        block=next(r for r in blocks if r["horizon_hours"]==h)
        matrix.append(dict(horizon_hours=h,w7_shifted_lambda_0_06_delta=old.delta_mae_vs_zero_ug_m3,w7_shifted_ci_low=old.mae_ci_low,w7_shifted_ci_high=old.mae_ci_high,v2j_limited_lambda_delta=check.delta_mae_vs_zero_ug_m3.iloc[0] if len(check) else np.nan,v2j_limited_lambda_ci_low=check.mae_ci_low.iloc[0] if len(check) else np.nan,v2j_limited_lambda_ci_high=check.mae_ci_high.iloc[0] if len(check) else np.nan,v2j_benchmark_ensemble_delta=current["difference"],v2k_original_35_holm_p=current["original_35_holm_p"],v2l_mean_individual_delta=st["mean"],v2l_seeds_favor_physics=st["seeds_favor_first"],v2l_seven_day_ci_low=block["seven_day_ci_low"],v2l_seven_day_ci_high=block["seven_day_ci_high"],comparison_note="W7 shifted weather; v2j corrected; different run/selection; exposed test set"))
    write_csv("reconciliation/experiment_comparison_matrix.csv",matrix)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,2,figsize=(10,4))
    hs=np.array(HORIZONS)
    observed=np.array([r["difference"] for r in blocks])
    for label,low,high,offset,color in (("UTC day", "utc_day_ci_low","utc_day_ci_high",-.18,"#255c99"),("7-day block","seven_day_ci_low","seven_day_ci_high",.18,"#b45f25")):
        lo=np.array([r[low] for r in blocks]);hi=np.array([r[high] for r in blocks])
        axes[0].errorbar(np.arange(5)+offset,observed,yerr=[observed-lo,hi-observed],fmt="o",capsize=3,label=label,color=color)
    axes[0].axhline(0,color="black",lw=.8);axes[0].set_xticks(range(5),hs);axes[0].set(xlabel="Horizon (h)",ylabel="Physics − λ=0 MAE (µg/m³)");axes[0].legend(frameon=False)
    for h in HORIZONS:
        vals=[r["paired_mae_difference"] for r in per_seed if r["horizon_hours"]==h and r["comparison"]=="physics-lambda0"]
        axes[1].scatter(np.repeat(HORIZONS.index(h),5),vals,color="#4c7a40",s=15,alpha=.75)
    axes[1].plot(range(5),[r["mean"] for r in stability if r["comparison"]=="physics-lambda0"],"ks-",ms=4,label="seed mean")
    axes[1].axhline(0,color="black",lw=.8);axes[1].set_xticks(range(5),hs);axes[1].set(xlabel="Horizon (h)",ylabel="Individual-seed ΔMAE (µg/m³)")
    fig.tight_layout();fig.savefig(OUT/"figures/physics_effect_and_seed_stability.png",dpi=160);plt.close(fig)
    # Record exact input checksums; no caches copied.
    ancillary=[dataset,ROOT/"results/data_v2j_fit.json",ROOT/"results/benchmark_runs_v2j.csv",ROOT/"results/benchmark_selection_v2j.csv",ROOT/"results/benchmark_v2j.csv",ROOT/"results/lambda_check_v2j.csv",ROOT/"results/lambda_sweep_v2g.csv",ROOT/"configs/data_v2.yaml",ROOT/"configs/benchmark_v2g.yaml",ROOT/"scripts/benchmark_v2j.py",ROOT/"scripts/summarize_benchmark_v2j.py",ROOT/"src/stpignn/physics_v2.py",ROOT/"src/stpignn/station_graph.py",ROOT/"final_blr_results/baselines/paired_architecture_comparisons.csv",ROOT/"results/codex_log/runs/benchmark_gpu_v2j/execution_manifest.json",ROOT/"results/codex_log/runs/benchmark_gpu_v2j/attempt_0_20261105T130158Z.log"]
    artifacts=sorted(set(paths+ancillary))
    write_csv("reproducibility/artifact_checksums.csv",[dict(path=p.relative_to(ROOT),size_bytes=p.stat().st_size,sha256=sha(p),workspace_exists=True,verified_independent_durable_backup=False) for p in artifacts])
    source=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
    manifest=dict(schema_version="v2l-1",analysis_base_commit=source,analysis_script_sha256=sha(Path(__file__)),physical_script_sha256=sha(OUT/"physical_diagnostics/compute_physical_diagnostics.py"),dataset_build_commit=fit["source_commit"],benchmark_training_commit="9a299f1bf01787f26750515cad8dff370e9c9aa0",dataset_sha256=datahash,inputs=[str(p.relative_to(ROOT)) for p in artifacts],output_root="final_blr_results/physics_audit",outputs=sorted({str(p.relative_to(OUT)) for p in OUT.rglob("*.csv")} | {"figures/physics_effect_and_seed_stability.png","physical_diagnostics/physical_metrics.csv","physical_diagnostics/spatial_behavior.csv"}),horizons=HORIZONS,seeds=SEEDS,bootstrap_replicates=REPS,original_35_family="final_blr_results/baselines/paired_architecture_comparisons.csv",regeneration_command="bash final_blr_results/physics_audit/reproducibility/regenerate_v2l.sh",durable_backup="No verified independent durable copy of required local prediction caches")
    (OUT/"reproducibility/analysis_manifest.json").write_text(json.dumps(manifest,indent=2,default=str)+"\n")
    print("integrity",len(inventory),"per-seed",len(per_seed),"monthly",len(monthly),"block",len(blocks))


if __name__=="__main__":main()
