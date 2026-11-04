"""LOSO attribute-embedded GINE+GRU with ERM and station group-DRO."""
from __future__ import annotations
import datetime as dt
import json
import subprocess
from pathlib import Path
import numpy as np
import pandas as pd
import torch
from torch import nn
from torch.nn import functional as F
from torch_geometric.nn import GINEConv
import yaml
from scripts.benchmark_v2g import seed_all
from scripts.evaluate_loso_v2g import FoldContext,fold_anchors,BASELINES
from scripts.evaluate_loso_v2 import paired_ci
from src.stpignn.data_v2 import build
from src.stpignn.evaluation import evaluate_arrays
from src.stpignn.models_v2 import expanded_edges
from src.stpignn.paths import REPO_ROOT

SEEDS=(11,23,37)
ETAS=(.01,.1)
METHODS=('erm','dro_eta_0.01','dro_eta_0.1')
LR=1e-4
CFG=dict(yaml.safe_load((REPO_ROOT/'configs/benchmark_v2g.yaml').read_text()),
         neural_hidden_dim=96,neural_batch_size=512,neural_max_epochs=20,neural_early_stopping_patience=4)
OUT=REPO_ROOT/'results/loso_groupdro_predictions_v2h.parquet'

class AttributeGineGRU(nn.Module):
    def __init__(self,inputs,hidden,attributes):
        super().__init__()
        self.register_buffer('attributes',torch.as_tensor(attributes,dtype=torch.float32))
        self.gru=nn.GRU(inputs,hidden,batch_first=True)
        self.attr_net=nn.Sequential(nn.Linear(3,hidden),nn.ReLU(),nn.Linear(hidden,hidden))
        self.gine=GINEConv(nn.Sequential(nn.Linear(hidden,hidden),nn.ReLU(),nn.Linear(hidden,hidden)),edge_dim=2)
        self.head=nn.Linear(hidden,1)
    def forward(self,x,edge_index,edge_attr,wind):
        b,t,n,f=x.shape
        seq=x.permute(0,2,1,3).reshape(b*n,t,f)
        h=self.gru(seq)[0][:,-1].reshape(b,n,-1)
        h=h+self.attr_net(self.attributes)[None]
        edge=expanded_edges(edge_index,n,b)
        attrs=torch.stack((edge_attr[:,0][None,:].expand(b,-1),wind),-1).reshape(-1,2)
        h=F.relu(self.gine(h.reshape(b*n,-1),edge,attrs)).reshape(b,n,-1)
        return self.head(h).squeeze(-1)

def static_attributes(data,known):
    raw=np.column_stack([data.elevation_m,data.coordinates])
    assert raw.shape[1]==3 and np.isfinite(raw).all()
    mean=raw[known].mean(0);sd=raw[known].std(0)
    return ((raw-mean)/np.maximum(sd,1e-6)).astype(np.float32)

def predict(ctx,model,split):
    model.eval();parts=[]
    with torch.no_grad():
        for index,x,y,mask,anchor,wind in ctx.batches(split):
            az=(torch.log1p(anchor.clamp_min(0))-ctx.mu)/ctx.sd
            z=model(x,ctx.edge_index,ctx.edge_attr,wind)+az
            pred=torch.expm1(z*ctx.sd+ctx.mu)
            rr,cc=np.where(mask.cpu().numpy())
            parts.append(pd.DataFrame({'station_id':ctx.station_ids[cc],
                'target_time_utc':ctx.times[index[rr]].astype(str),
                'target':y.cpu().numpy()[rr,cc],
                'prediction':pred.cpu().numpy()[rr,cc]}))
    return pd.concat(parts,ignore_index=True)

def train(ctx,attributes,method,seed):
    seed_all(seed)
    model=AttributeGineGRU(ctx.features.shape[-1],96,attributes).to(ctx.device)
    opt=torch.optim.AdamW(model.parameters(),lr=LR,weight_decay=.01)
    eta=0. if method=='erm' else float(method.split('_')[-1])
    q=torch.as_tensor(ctx.known,dtype=torch.float32,device=ctx.device)
    q=q/q.sum();best=float('inf');best_state=None;stale=0;best_epoch=0
    for epoch in range(1,21):
        model.train()
        for _,x,y,mask,anchor,wind in ctx.batches('train',seed*1000+epoch):
            opt.zero_grad(set_to_none=True)
            az=(torch.log1p(anchor.clamp_min(0))-ctx.mu)/ctx.sd
            z=model(x,ctx.edge_index,ctx.edge_attr,wind)+az
            target=(torch.log1p(y.clamp_min(0))-ctx.mu)/ctx.sd
            per_pair=(z-target).square()*mask
            if eta:
                counts=mask.sum(0);present=counts>0
                group=per_pair.sum(0)/counts.clamp_min(1)
                with torch.no_grad():
                    q[present]*=torch.exp(eta*group[present].detach().clamp(max=20))
                    q=q/q.sum()
                weights=q*present;weights=weights/weights.sum().clamp_min(1e-8)
                loss=(weights*group).sum()
            else:loss=per_pair.sum()/mask.sum().clamp_min(1)
            if not torch.isfinite(loss):raise FloatingPointError((method,seed,epoch))
            loss.backward();torch.nn.utils.clip_grad_norm_(model.parameters(),.3);opt.step()
        val=predict(ctx,model,'validation')
        mae=float(np.mean(np.abs(val.prediction-val.target)))
        if mae<best:
            best=mae;best_epoch=epoch;stale=0
            best_state={k:v.detach().cpu().clone() for k,v in model.state_dict().items()}
        else:
            stale+=1
            if stale>=4:break
    model.load_state_dict(best_state)
    return model,best,best_epoch

def generate():
    old=pd.read_parquet(REPO_ROOT/'results/loso_predictions_v2c.parquet')
    baselines=old[(old.seed==-1)&old.method.isin(BASELINES)]
    raw=pd.read_parquet(OUT) if OUT.exists() else pd.DataFrame()
    for fold,station in enumerate(pd.read_csv(REPO_ROOT/'results/stations_v2.csv').station_id.astype(int),1):
        if not (baselines.station_id==station).any():
            print('UNSCORED',fold,station,flush=True);continue
        data,_=build(REPO_ROOT/'configs/data_v2.yaml',excluded_station_id=station)
        hidden=int(np.flatnonzero(data.station_ids==station)[0])
        mean_anchor,_,_,known,tail=fold_anchors(data,hidden)
        ctx=FoldContext(data,hidden,mean_anchor,known,tail,CFG)
        attr=static_attributes(data,known)
        for method in METHODS:
            for seed in SEEDS:
                if not raw.empty and ((raw.station_id==station)&(raw.method==method)&(raw.seed==seed)).any():continue
                model,val,epoch=train(ctx,attr,method,seed)
                pred=predict(ctx,model,'test')
                pred['method']=method;pred['seed']=seed;pred['validation_mae']=val;pred['best_epoch']=epoch
                raw=pd.concat([raw,pred],ignore_index=True)
                raw.to_parquet(OUT,index=False)
                print('FOLD',fold,station,method,seed,len(pred),val,flush=True)

def summarize():
    raw=pd.read_parquet(OUT)
    baselines=pd.read_parquet(REPO_ROOT/'results/loso_predictions_v2c.parquet')
    baselines=baselines[(baselines.seed==-1)&baselines.method.isin(BASELINES)].copy()
    summary_val=raw[['station_id','method','seed','validation_mae']].drop_duplicates()
    selected=summary_val[summary_val.method!='erm'].groupby('method').validation_mae.mean().idxmin()
    ensemble=raw.groupby(['station_id','method','target_time_utc','target'],as_index=False).prediction.mean()
    expected=baselines[baselines.method=='ridge_weather_static'][['station_id','target_time_utc']]
    for method,g in ensemble.groupby('method'):
        assert len(g)==len(expected) and set(map(tuple,g[['station_id','target_time_utc']].to_numpy()))==set(map(tuple,expected.to_numpy())),method
    methods={'ERM':'erm','group-DRO':selected}
    pooled=[];station_rows=[]
    for label,method in methods.items():
        g=ensemble[ensemble.method==method]
        metric=evaluate_arrays(g.prediction,g.target,np.ones(len(g),bool))
        pooled.append({'method':label,'selected_eta':0. if label=='ERM' else float(selected.split('_')[-1]),**metric})
        for station,d in g.groupby('station_id'):
            m=evaluate_arrays(d.prediction,d.target,np.ones(len(d),bool))
            station_rows.append({'station_id':station,'method':label,**m})
    base_metrics=[]
    for name,g in baselines.groupby('method'):
        m=evaluate_arrays(g.prediction,g.target,np.ones(len(g),bool))
        base_metrics.append({'method':name,**m})
    best=min(base_metrics,key=lambda x:x['mae'])
    b=baselines[baselines.method==best['method']]
    for row in pooled:
        a=ensemble[ensemble.method==methods[row['method']]]
        ci=paired_ci(a,b,4303,2000)
        row.update(best_baseline=best['method'],baseline_mae=best['mae'],baseline_r2=best['r2'],
                   delta_mae=row['mae']-best['mae'],mae_ci_low=ci[0][0],mae_ci_high=ci[1][0],
                   verdict=('TIE' if ci[0][0]<=0<=ci[1][0] else ('WIN' if ci[1][0]<0 and row['r2']>best['r2'] else 'LOSS')),
                   seeds='11;23;37',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO_ROOT,text=True).strip(),
                   timestamp_utc=dt.datetime.now(dt.timezone.utc).isoformat())
    unscored=sorted(set(pd.read_csv(REPO_ROOT/'results/stations_v2.csv').station_id.astype(int))-set(ensemble.station_id))
    for station in unscored:
        station_rows.append({'station_id':station,'method':'unscored','status':'zero observed test targets'})
    pd.DataFrame(pooled).to_csv(REPO_ROOT/'results/loso_groupdro_v2h.csv',index=False)
    pd.DataFrame(station_rows).to_csv(REPO_ROOT/'results/loso_station_predictability_v2h.csv',index=False)
    print(json.dumps({'selected_eta':selected,'pooled':pooled,'unscored_stations':unscored},indent=2),flush=True)

if __name__=='__main__':generate();summarize()
