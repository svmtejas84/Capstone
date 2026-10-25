"""W6 fold-isolated LOSO with train-mean and train-tail-fitted IDW-blend anchors."""
from __future__ import annotations

import datetime as dt
import json
import subprocess
import warnings

import numpy as np
import pandas as pd
import torch
import yaml
from scipy.stats import norm
from sklearn.linear_model import Ridge
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import ConstantKernel, RBF, WhiteKernel
from pykrige.ok import OrdinaryKriging

from scripts.benchmark_v2g import Context, fit
from scripts.evaluate_loso_v2 import CFG as LOSO_CFG
from src.stpignn.data_v2 import build
from src.stpignn.evaluation import evaluate_arrays
from src.stpignn.paths import REPO_ROOT

BASELINES = ["ridge_weather_static", "station_train_mean", "idw", "gp_rbf", "ordinary_kriging"]


def fold_anchors(data, hidden, horizon=1):
    known = np.ones(len(data.station_ids), bool)
    known[hidden] = False
    y = data.observed_target.copy()
    known_train = y[data.split_masks["train"]][:, known]
    global_mean = float(np.nanmean(known_train))
    train_values = y[data.split_masks["train"]].copy()
    train_values[:, hidden] = np.nan
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        station_mean = np.nanmean(train_values, axis=0)
    station_mean[hidden] = global_mean
    station_mean = np.where(np.isfinite(station_mean), station_mean, global_mean)
    xy = data.coordinates.astype(float)
    distance = np.linalg.norm(xy[:, None] - xy[None, :], axis=2)
    weights = 1 / np.maximum(distance, 1.0) ** float(LOSO_CFG["idw_power"])
    np.fill_diagonal(weights, 0)
    weights[:, hidden] = 0
    source = y.copy(); source[:, hidden] = np.nan
    finite = np.isfinite(source)
    den = finite.astype(float) @ weights.T
    num = np.nan_to_num(source, nan=0).astype(float) @ weights.T
    idw = np.divide(num, den, out=np.broadcast_to(station_mean, num.shape).copy(), where=den>0)
    end = pd.Timestamp(data.config["train_end_utc"])
    start = end - pd.Timedelta(days=30) + pd.Timedelta(hours=1)
    tail = np.asarray(data.split_masks["train"] & (data.times >= start) & (data.times <= end))
    target_i, target_j = np.where(data.observed_mask & tail[:, None] & known[None, :])
    eligible = (target_i >= horizon) & data.observed_mask[target_i-horizon, target_j]
    target_i, target_j = target_i[eligible], target_j[eligible]
    if not len(target_i):
        raise ValueError("No known-station train-tail targets for blend")
    grid = np.linspace(0, 1, 101)
    scores = [float(np.mean(np.abs((1-a)*station_mean[target_j] + a*idw[target_i-horizon, target_j]
                                   - y[target_i,target_j]))) for a in grid]
    alpha = float(grid[int(np.argmin(scores))])
    mean_anchor = np.broadcast_to(station_mean, y.shape).astype(np.float32).copy()
    blended = ((1-alpha)*mean_anchor + alpha*idw).astype(np.float32)
    return mean_anchor, blended, alpha, known, tail


class FoldContext(Context):
    def __init__(self, data, hidden, anchor, known, tail, cfg):
        super().__init__(1, cfg)
        assert np.array_equal(self.station_ids, data.station_ids)
        self.y = data.observed_target
        self.observed = data.observed_mask
        self.mu = float(data.fit["target_log1p_mean"])
        self.sd = float(data.fit["target_log1p_std"])
        self.physical_scale = float(data.fit["target_standard_std"])
        pm25 = np.clip(data.imputed_target, 0, 500)
        pm10 = np.clip(data.features[:,:,1]*data.fit["feature_stds"][1]+data.fit["feature_means"][1], 0, 500)
        known_pm10 = pm10[data.split_masks["train"]][:, known]
        mu10 = float(np.log1p(known_pm10).mean()); sd10 = float(np.log1p(known_pm10).std())
        base = data.features.copy()
        base[:,:,0] = (np.log1p(pm25)-self.mu)/self.sd
        base[:,:,1] = (np.log1p(pm10)-mu10)/sd10
        hour = self.times.hour.to_numpy(); dow = self.times.dayofweek.to_numpy()
        calendar = np.stack((np.sin(2*np.pi*hour/24), np.cos(2*np.pi*hour/24),
                             np.sin(2*np.pi*dow/7), np.cos(2*np.pi*dow/7)), -1).astype(np.float32)
        indicator = (~self.observed).astype(np.float32)
        indicator[:, hidden] = 1.0
        self.features = np.concatenate((base, indicator[...,None],
                                        np.broadcast_to(calendar[:,None,:], (len(self.times),self.n,4))), -1)
        self.features[:,hidden,:5] = 0.0
        self.anchor = anchor
        self.known = known
        self.hidden = hidden
        self.hours = {}
        for name in ("train", "validation", "test", "tail"):
            period = tail if name == "tail" else data.split_masks[name]
            target_station = ~known if name == "test" else known
            valid = self.observed & period[:,None] & target_station[None,:]
            if name != "test":
                valid[1:] &= self.observed[:-1]
            valid[:self.history] = False
            self.hours[name] = np.flatnonzero(valid.any(1))

    def batches(self, name, shuffle_seed=None):
        for idx, x, y, mask, anchor, wind in super().batches(name, shuffle_seed):
            x[:,:,self.hidden,:5] = 0.0
            x[:,:,self.hidden,13] = 1.0
            station_mask = ~self.known if name == "test" else self.known
            mask &= torch.as_tensor(station_mask[None,:], device=self.device)
            yield idx, x, y, mask, anchor, wind


def baseline_tail_shifts(data, hidden, known, tail):
    y = data.observed_target
    i, j = np.where(data.observed_mask & tail[:,None] & known[None,:])
    good = (i >= 12) & data.observed_mask[i-1,j]
    i,j = i[good],j[good]
    rng = np.random.default_rng(4200+hidden)
    if len(i) > 128:
        chosen = rng.choice(len(i), 128, replace=False); i,j = i[chosen],j[chosen]
    if not len(i):
        raise ValueError("No train-tail pairs for seasonal baseline check")
    global_mean = float(np.nanmean(y[data.split_masks["train"]][:,known]))
    xy = data.coordinates.astype(float)
    rr,cc = np.where(data.observed_mask & data.split_masks["train"][:,None] & known[None,:])
    valid = rr >= 12
    rr,cc = rr[valid],cc[valid]
    ridge = Ridge(alpha=1.0).fit(data.features[rr-1,cc,5:13],y[rr,cc])
    kernel = ConstantKernel(1.0,constant_value_bounds="fixed")*RBF(float(LOSO_CFG["gp_length_scale_m"]),length_scale_bounds="fixed")+WhiteKernel(float(LOSO_CFG["gp_noise_variance"]),noise_level_bounds="fixed")
    residuals = {name:[] for name in BASELINES}
    for hour,node in zip(i,j):
        cutoff = hour-1
        available = known.copy(); available[node]=False
        idx = np.flatnonzero(available & np.isfinite(y[cutoff]))
        value = y[cutoff,idx]
        dist = np.linalg.norm(xy[idx]-xy[node],axis=1)
        pred = {name:global_mean for name in BASELINES}
        pred["ridge_weather_static"] = float(ridge.predict(data.features[cutoff,node,5:13][None,:])[0])
        if len(value):
            weight=1/np.maximum(dist,1)**float(LOSO_CFG["idw_power"])
            pred["idw"]=float(np.dot(weight,value)/weight.sum())
        if len(value)>=2:
            try:
                gp=GaussianProcessRegressor(kernel=kernel,optimizer=None,normalize_y=True,alpha=1e-6)
                gp.fit(xy[idx],value)
                pred["gp_rbf"]=float(gp.predict(xy[node:node+1])[0])
            except (ValueError,np.linalg.LinAlgError):
                pass
        if len(value)>=4:
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    ok=OrdinaryKriging(xy[idx,0],xy[idx,1],value,variogram_model=LOSO_CFG["kriging_variogram_model"],
                                       variogram_parameters=None,enable_plotting=False,verbose=False,exact_values=False)
                    estimate,_=ok.execute("points",[xy[node,0]],[xy[node,1]])
                pred["ordinary_kriging"]=float(estimate[0])
            except (ValueError,RuntimeError,np.linalg.LinAlgError,ZeroDivisionError):
                pass
        for name in BASELINES:
            residuals[name].append(pred[name]-y[hour,node])
    return {name:float(np.mean(values)) for name,values in residuals.items()},len(i)


def main():
    benchmark = yaml.safe_load((REPO_ROOT/"configs/benchmark_v2g.yaml").read_text())
    choices = pd.read_csv(REPO_ROOT/"results/benchmark_selection_v2g.csv")
    candidates = choices[(choices.horizon_hours==1) & choices.model.isin(
        ["gine_gru_wind","adaptive_graph_st","stpignn_v2"])].sort_values("validation_mae")
    top = candidates.drop_duplicates("model").model.head(2).tolist()
    if len(top)!=2:
        raise RuntimeError("Need two validation-ranked W2 models")
    methods = top+["stpignn_original"]
    cfg=dict(benchmark,neural_seeds=[11,23,37],neural_hidden_dim=96,neural_batch_size=512,
             neural_max_epochs=20,neural_early_stopping_patience=4,lambda_original=0.06)
    out=REPO_ROOT/"results"
    raw_path=out/"loso_predictions_v2g.parquet"
    raw=pd.read_parquet(raw_path) if raw_path.exists() else pd.DataFrame()
    old=pd.read_parquet(out/"loso_predictions_v2c.parquet")
    old=old[(old.seed==-1)&old.method.isin(BASELINES)].copy()
    for fold,station_id in enumerate(pd.read_csv(out/"stations_v2.csv").station_id.astype(int)):
        if not (old.station_id==station_id).any():
            print(f"fold {fold+1} station {station_id} unscored",flush=True)
            continue
        data,_=build(REPO_ROOT/"configs/data_v2.yaml",excluded_station_id=station_id)
        hidden=int(np.flatnonzero(data.station_ids==station_id)[0])
        assert station_id not in data.fit["fitted_station_ids"]
        mean_anchor,blend_anchor,alpha,known,tail=fold_anchors(data,hidden)
        shifts,tail_n=baseline_tail_shifts(data,hidden,known,tail)
        if raw.empty or not ((raw.station_id==station_id)&(raw.seed==-1)).any():
            base=old[old.station_id==station_id].copy()
            base["anchor"]="baseline"; base["blend_weight"]=np.nan
            base["train_tail_bias"]=base.method.map(shifts)
            base["train_tail_pairs"]=tail_n
            raw=pd.concat([raw,base],ignore_index=True)
            raw.to_parquet(raw_path,index=False)
        for anchor_name,anchor in (("train_mean",mean_anchor),("train_mean_idw_blend",blend_anchor)):
            ctx=FoldContext(data,hidden,anchor,known,tail,cfg)
            for name in methods:
                for seed in cfg["neural_seeds"]:
                    if not raw.empty and ((raw.station_id==station_id)&(raw.method==name)&
                                          (raw.anchor==anchor_name)&(raw.seed==seed)).any():
                        continue
                    result,tested=fit(ctx,name,0.0001,seed,evaluate_test=True)
                    frame=pd.DataFrame({"station_id":station_id,"method":name,"anchor":anchor_name,
                                        "seed":seed,"target_time_utc":ctx.times[tested["time_index"]].astype(str),
                                        "target":tested["truth"],"prediction":tested["pred"],
                                        "blend_weight":alpha if anchor_name=="train_mean_idw_blend" else 0,
                                        "train_tail_bias":result["train_tail_bias"],"train_tail_pairs":tail_n,
                                        "validation_mae":result["validation_mae"],"train_seconds":result["train_seconds"]})
                    raw=pd.concat([raw,frame],ignore_index=True)
                    raw.to_parquet(raw_path,index=False)
                    print(f"fold={fold+1}/15 station={station_id} {anchor_name} {name} seed={seed} n={len(frame)}",flush=True)
    neural=raw[raw.seed>=0].copy()
    neural["bias_adjusted_prediction"]=neural.prediction-neural.train_tail_bias
    ensemble=neural.groupby(["station_id","method","anchor","target_time_utc","target"],as_index=False).agg(
        prediction=("prediction","mean"),bias_adjusted_prediction=("bias_adjusted_prediction","mean"))
    base=raw[raw.seed==-1].copy()
    base["bias_adjusted_prediction"]=base.prediction-base.train_tail_bias
    scored=pd.concat([ensemble,base],ignore_index=True)
    rows=[]
    for (anchor,method),part in scored.groupby(["anchor","method"]):
        for corrected,column in ((False,"prediction"),(True,"bias_adjusted_prediction")):
            m=evaluate_arrays(part[column],part.target,np.ones(len(part),bool))
            rows.append({"anchor":anchor,"method":method,"seasonal_bias_corrected":corrected,**m})
    summary=pd.DataFrame(rows)
    from scripts.evaluate_loso_v2 import paired_ci
    baseline_summary=summary[(summary.anchor=="baseline")&(~summary.seasonal_bias_corrected)]
    best=baseline_summary.sort_values("mae").iloc[0].method
    b=scored[(scored.anchor=="baseline")&(scored.method==best)]
    decision=[]
    for anchor in ("train_mean","train_mean_idw_blend"):
        for method in methods:
            a=scored[(scored.anchor==anchor)&(scored.method==method)]
            ci=paired_ci(a,b,int(benchmark["bootstrap_seed"]),int(benchmark["bootstrap_replicates"]))
            ma=summary[(summary.anchor==anchor)&(summary.method==method)&(~summary.seasonal_bias_corrected)].iloc[0]
            mb=baseline_summary[baseline_summary.method==best].iloc[0]
            verdict="TIE" if ci[0][0]<=0<=ci[1][0] else ("WIN" if ci[1][0]<0 and ma.r2>mb.r2 else "LOSS")
            decision.append({"anchor":anchor,"method":method,"best_baseline":best,"verdict":verdict,
                             "delta_mae":ma.mae-mb.mae,"mae_ci_low":ci[0][0],"mae_ci_high":ci[1][0],
                             "delta_r2":ma.r2-mb.r2})
    dec=pd.DataFrame(decision)
    summary=summary.merge(dec,on=["anchor","method"],how="left")
    summary.to_csv(out/"loso_summary_v2g.csv",index=False)
    dec.to_csv(out/"loso_decision_v2g.csv",index=False)
    print(json.dumps({"top_two_by_validation":top,"best_baseline":best,
                      "decisions":decision,"source_commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=REPO_ROOT,text=True).strip(),
                      "timestamp_utc":dt.datetime.now(dt.timezone.utc).isoformat()},indent=2),flush=True)


if __name__=="__main__":
    main()
