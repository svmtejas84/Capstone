"""Fixed split and daily rolling conformal evaluation; seed 11, 10 epochs, LR 3e-4."""
from __future__ import annotations
import datetime as dt
import glob
import json
from pathlib import Path
import numpy as np
import pandas as pd
import torch
import yaml
from sklearn.linear_model import Ridge
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scripts.benchmark_v2g import Context, seed_all
from src.stpignn.paths import REPO_ROOT
from src.stpignn.physics_v2 import batched_penalty

MODELS=('persistence','same_hour_yesterday','ridge_lag','gru_only','stpignn_original','best_ab')
HORIZONS=(1,3,6,12,24)
LEVELS=(.8,.9)
SEED=11
LR=3e-4
EPOCHS=10
CACHE=REPO_ROOT/'results/conformal_predictions_v2h'

def fit_point(ctx, model_name):
    seed_all(SEED)
    model=ctx.make(model_name)
    opt=torch.optim.AdamW(model.parameters(),lr=LR,weight_decay=.01)
    for epoch in range(1,EPOCHS+1):
        model.train()
        for index,x,y,mask,anchor,wind in ctx.batches('train',SEED*1000+epoch):
            opt.zero_grad(set_to_none=True)
            pred=ctx.forward(model,model_name,x,anchor,wind)
            target=(torch.log1p(y.clamp_min(0))-ctx.mu)/ctx.sd
            loss=((pred-target).square()*mask).sum()/mask.sum().clamp_min(1)
            if model_name=='stpignn_original':
                physical=torch.expm1(pred*ctx.sd+ctx.mu)/ctx.physical_scale
                edge_wind=torch.as_tensor(ctx.corrected_wind_mask[index-ctx.horizon].copy(),device=ctx.device)
                loss=loss+.06*min(1.,epoch/25.)*batched_penalty(
                    physical,ctx.edge_index,edge_wind,ctx.edge_distance,'corrected_mask')
            if not torch.isfinite(loss):raise FloatingPointError((model_name,ctx.horizon,epoch))
            loss.backward();torch.nn.utils.clip_grad_norm_(model.parameters(),.3);opt.step()
    return model

def pair_frame(ctx,split):
    hours=np.zeros(len(ctx.times),bool);hours[ctx.hours[split]]=True
    mask=ctx.observed & hours[:,None]
    if split!='test':
        mask[:ctx.horizon]=False
        mask[ctx.horizon:] &= ctx.observed[:-ctx.horizon]
    ti,sj=np.where(mask)
    return pd.DataFrame({'time_index':ti,'station_index':sj,'time':ctx.times[ti].astype(str),
                         'station_id':ctx.station_ids[sj],'target':ctx.y[ti,sj]})

def baseline(ctx,name,train_hours,frame):
    ti=frame.time_index.to_numpy();sj=frame.station_index.to_numpy();cut=ti-ctx.horizon
    if name=='persistence':return ctx.anchor[cut,sj]
    if name=='same_hour_yesterday':return ctx.anchor[ti-24,sj]
    if name=='ridge_lag':
        train_mask=np.zeros(len(ctx.times),bool);train_mask[train_hours]=True
        mask=ctx.observed & train_mask[:,None]
        mask[:ctx.horizon]=False;mask[ctx.horizon:] &= ctx.observed[:-ctx.horizon]
        i,j=np.where(mask);cols=[0]+list(range(5,ctx.features.shape[-1]))
        x=ctx.features[i-ctx.horizon,j][:,cols]
        y=(np.log1p(ctx.y[i,j])-ctx.mu)/ctx.sd
        ridge=Ridge(alpha=1).fit(x,y)
        return np.expm1(ridge.predict(ctx.features[cut,sj][:,cols])*ctx.sd+ctx.mu)
    raise ValueError(name)

def neural_preds(ctx,model,name,split,frame):
    got=ctx.evaluate(model,name,split,collect=True)
    lookup=pd.DataFrame({'time_index':got['time_index'],'station_index':got['station_index'],'prediction':got['pred']})
    joined=frame[['time_index','station_index']].merge(lookup,on=['time_index','station_index'],how='left',validate='one_to_one')
    if joined.prediction.isna().any():raise AssertionError('prediction mask mismatch')
    return joined.prediction.to_numpy()

def generate():
    CACHE.mkdir(exist_ok=True)
    cfg=yaml.safe_load((REPO_ROOT/'configs/benchmark_v2g.yaml').read_text())
    choice=pd.read_csv(REPO_ROOT/'results/benchmark_selection_v2g.csv')
    for h in HORIZONS:
        ab=choice[(choice.horizon_hours==h)&choice.model.isin(['gine_gru_wind','adaptive_graph_st'])].sort_values('validation_mae').iloc[0].model
        for cal in ('train_tail','validation'):
            ctx=Context(h,cfg)
            original_train=ctx.hours['train'].copy()
            train_end=pd.Timestamp('2025-06-29T23:00:00Z')
            tail_start=train_end-pd.Timedelta(days=30)+pd.Timedelta(hours=1)
            if cal=='train_tail':
                ctx.hours['train']=original_train[ctx.times[original_train]<tail_start]
                ctx.hours['calibration']=original_train[ctx.times[original_train]>=tail_start]
            else:
                ctx.hours['calibration']=ctx.hours['validation'].copy()
            train_hours=ctx.hours['train']
            frames={s:pair_frame(ctx,s) for s in ('calibration','test')}
            for label in MODELS:
                path=CACHE/f'h{h}_{cal}_{label}_seed{SEED}_v2h.parquet'
                if path.exists():continue
                name=ab if label=='best_ab' else label
                model=fit_point(ctx,name) if label not in MODELS[:3] else None
                outputs=[]
                for split,frame in frames.items():
                    pred=baseline(ctx,name,train_hours,frame) if model is None else neural_preds(ctx,model,name,split,frame)
                    out=frame[['time','station_id','target']].copy();out['prediction']=pred
                    out['split']=split;out['model']=label;out['horizon_hours']=h;out['calibration']=cal
                    outputs.append(out)
                pd.concat(outputs,ignore_index=True).to_parquet(path,index=False)
                print('PRED',h,cal,label,len(outputs[0]),len(outputs[1]),flush=True)

def quantile(scores,nominal):
    scores=np.asarray(scores,float)
    rank=min(len(scores),int(np.ceil((len(scores)+1)*nominal)))
    return float(np.partition(scores,rank-1)[rank-1])

def score_interval(y,low,high,nominal):
    alpha=1-nominal
    return high-low+2/alpha*(low-y).clip(min=0)+2/alpha*(y-high).clip(min=0)

def daily_bootstrap(diff,dates,seed=4550):
    days,inv=np.unique(dates,return_inverse=True);count=np.bincount(inv)
    sums=np.bincount(inv,weights=diff)
    rng=np.random.default_rng(seed)
    samples=rng.integers(0,len(days),size=(2000,len(days)))
    vals=sums[samples].sum(1)/count[samples].sum(1)
    return np.quantile(vals,[.025,.975]).tolist()

def summarize():
    output=[];detail=[];all_scores=[]
    for h in HORIZONS:
      for cal in ('train_tail','validation'):
        data={}
        for model in MODELS:
            path=CACHE/f'h{h}_{cal}_{model}_seed{SEED}_v2h.parquet'
            if not path.exists():raise FileNotFoundError(path)
            d=pd.read_parquet(path)
            data[model]={s:d[d.split==s].sort_values(['time','station_id']).reset_index(drop=True) for s in ('calibration','test')}
        ref=data['persistence']['test'][['time','station_id','target']]
        for model in MODELS:
            pd.testing.assert_frame_equal(data[model]['test'][['time','station_id','target']],ref)
        for level in LEVELS:
          for variant in ('fixed','rolling_daily'):
            arrays={}
            for model in MODELS:
                ca=data[model]['calibration'];te=data[model]['test']
                residual=np.abs(ca.target.to_numpy()-ca.prediction.to_numpy())
                q=quantile(residual,level)
                y=te.target.to_numpy();p=te.prediction.to_numpy();dates=pd.to_datetime(te.time,utc=True).dt.date.to_numpy()
                if variant=='fixed':qs=np.full(len(te),q)
                else:
                    qs=np.empty(len(te));history=residual.copy()
                    for day in np.unique(dates):
                        at=np.where(dates==day)[0];qs[at]=quantile(history,level)
                        history=np.r_[history,np.abs(y[at]-p[at])]
                low=np.maximum(0,p-qs);high=p+qs
                scores=score_interval(y,low,high,level);covered=(y>=low)&(y<=high)
                arrays[model]=(scores,covered,high-low)
                for dim in ('station_id','month'):
                    groups=te.station_id.to_numpy() if dim=='station_id' else pd.to_datetime(te.time,utc=True).dt.strftime('%Y-%m').to_numpy()
                    for key in np.unique(groups):
                        m=groups==key
                        detail.append(dict(horizon_hours=h,calibration=cal,nominal=level,variant=variant,model=model,
                                           dimension=dim,group=str(key),n=int(m.sum()),coverage=float(covered[m].mean()),
                                           mean_width=float((high-low)[m].mean())))
                all_scores.append(pd.DataFrame(dict(horizon_hours=h,calibration=cal,nominal=level,variant=variant,
                    model=model,time=te.time,target=y,score=scores,covered=covered,width=high-low)))
            for model in MODELS:
                s,c,w=arrays[model];base=arrays['persistence'][0];ridge=arrays['ridge_lag'][0]
                dates=pd.to_datetime(data[model]['test'].time,utc=True).dt.date.to_numpy()
                ci_p=daily_bootstrap(s-base,dates);ci_r=daily_bootstrap(s-ridge,dates)
                row=dict(horizon_hours=h,calibration=cal,nominal=level,variant=variant,model=model,
                    n=len(s),coverage=float(c.mean()),mean_width=float(w.mean()),interval_score=float(s.mean()),
                    delta_score_vs_persistence=float((s-base).mean()),ci_persistence_low=ci_p[0],ci_persistence_high=ci_p[1],
                    delta_score_vs_ridge=float((s-ridge).mean()),ci_ridge_low=ci_r[0],ci_ridge_high=ci_r[1])
                row['adds_probabilistic_value']=bool(ci_p[1]<0 and ci_r[1]<0 and abs(row['coverage']-level)<=.05)
                output.append(row)
    raw=pd.concat(all_scores,ignore_index=True)
    for (cal,level,variant,model),d in raw.groupby(['calibration','nominal','variant','model']):
        base=raw[(raw.calibration==cal)&(raw.nominal==level)&(raw.variant==variant)&(raw.model=='persistence')].sort_values(['horizon_hours','time'])
        ridge=raw[(raw.calibration==cal)&(raw.nominal==level)&(raw.variant==variant)&(raw.model=='ridge_lag')].sort_values(['horizon_hours','time'])
        d=d.sort_values(['horizon_hours','time']);dates=pd.to_datetime(d.time,utc=True).dt.date.to_numpy()
        s=d.score.to_numpy();b=base.score.to_numpy();r=ridge.score.to_numpy()
        ci_p=daily_bootstrap(s-b,dates);ci_r=daily_bootstrap(s-r,dates)
        cov=float(d.covered.mean())
        output.append(dict(horizon_hours='pooled',calibration=cal,nominal=level,variant=variant,model=model,n=len(d),
                           coverage=cov,mean_width=float(d.width.mean()),interval_score=float(s.mean()),
                           delta_score_vs_persistence=float((s-b).mean()),ci_persistence_low=ci_p[0],ci_persistence_high=ci_p[1],
                           delta_score_vs_ridge=float((s-r).mean()),ci_ridge_low=ci_r[0],ci_ridge_high=ci_r[1],
                           adds_probabilistic_value=bool(ci_p[1]<0 and ci_r[1]<0 and abs(cov-level)<=.05)))
    out=pd.DataFrame(output);out.to_csv(REPO_ROOT/'results/conformal_v2h.csv',index=False)
    pd.DataFrame(detail).to_csv(REPO_ROOT/'results/conformal_station_month_v2h.csv',index=False)
    fig,ax=plt.subplots(figsize=(9,5))
    sub=out[(out.calibration=='train_tail')&(out.variant=='fixed')&(out.horizon_hours!='pooled')]
    for model,g in sub.groupby('model'):
        for level,z in g.groupby('nominal'):
            ax.plot(z.horizon_hours.astype(int),z.coverage,marker='o',label=f'{model} {level:.0%}')
    for level in LEVELS:ax.axhline(level,ls='--',color='grey',lw=.8)
    ax.set(xlabel='Forecast horizon (hours)',ylabel='Test empirical coverage',ylim=(0,1),xticks=list(HORIZONS))
    ax.legend(fontsize=6,ncol=3,bbox_to_anchor=(.5,-.18),loc='upper center')
    fig.tight_layout();fig.savefig(REPO_ROOT/'figures/conformal_coverage.pdf',bbox_inches='tight');plt.close(fig)
    print(out[(out.calibration=='train_tail')&(out.variant=='fixed')&(out.horizon_hours!='pooled')][['horizon_hours','nominal','model','coverage','interval_score','adds_probabilistic_value']].to_string(index=False),flush=True)

if __name__=='__main__':
    generate();summarize()
