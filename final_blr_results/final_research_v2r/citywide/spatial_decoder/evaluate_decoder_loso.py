"""Fit frozen compact decoder by outer LOSO using cross-fitted forecast support."""
from __future__ import annotations
import json,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import numpy as np,pandas as pd,torch
from final_blr_results.citywide_extension.v2q.spatial_decoder import CompactSpatialDecoder

H=6;LR=1e-3;MAX_EPOCHS=10;PATIENCE=3;SEED=42

def make_examples(frame, z, split, query_ids, heldout, xy, elev):
    times=pd.DatetimeIndex(pd.to_datetime(z["times_ns"],utc=True)); sid_to_j={int(s):j for j,s in enumerate(z["station_ids"])}
    time_to_i={str(t):i for i,t in enumerate(times.astype(str))}
    if not time_to_i: raise RuntimeError("empty target timeline")
    forecast=frame.loc[frame.split==split].copy()
    forecast["target_time_utc"]=pd.to_datetime(forecast.target_time_utc,utc=True).astype(str)
    groups={t:g.set_index("station_id").prediction_ug_m3.to_dict() for t,g in forecast.groupby("target_time_utc")}
    target=z["observed_target"];obs=z["observed_mask"]
    rec=[]
    for t,vals in groups.items():
        ix=time_to_i.get(t)
        if ix is None: continue
        for qid in query_ids:
            qj=sid_to_j[int(qid)]
            if not obs[ix,qj]:continue
            candidates=[int(s) for s in z["station_ids"] if int(s)!=int(qid) and int(s)!=int(heldout) and int(s) in vals]
            if len(candidates)<1:continue
            qxy=xy[qj];d=np.array([np.linalg.norm(xy[sid_to_j[s]]-qxy) for s in candidates])
            take=np.argsort(d,kind="stable")[:13]
            supports=np.array(candidates,dtype=int)[take]
            sj=np.array([sid_to_j[s] for s in supports])
            rec.append((int(qid),t,xy[sj],np.asarray([vals[s] for s in supports],np.float32),
                        elev[sj],qxy,float(elev[qj]),float(target[ix,qj]),float(d[take[0]])))
    return rec

def features_for(rec,device="cpu"):
    if not rec: raise ValueError("no eligible decoder examples")
    bases=[];nearest=[];features=[]
    for _,_,sxy,sy,se,qxy,qe,_,_ in rec:
        dist=np.linalg.norm(sxy-qxy[None,:],axis=1)
        w=np.maximum(dist,1.0)**-2; base=float(w@sy/w.sum()); near=float(dist.min())
        bases.append(base);nearest.append(near)
        features.append([base/100.0,near/10000.0,len(sy)/15.0,(qe-float(np.mean(se)))/100.0])
    return torch.tensor(features,dtype=torch.float32,device=device),torch.tensor(bases,dtype=torch.float32,device=device),torch.tensor(nearest,dtype=torch.float32,device=device)

def metrics(pred,y):
    e=np.asarray(pred)-np.asarray(y);ss=np.sum((np.asarray(y)-np.mean(y))**2)
    return {"n":int(len(e)),"mae":float(np.mean(np.abs(e))),"rmse":float(np.sqrt(np.mean(e*e))),
            "r2":float(1-np.sum(e*e)/ss) if ss>0 else None}

def main():
    started=time.perf_counter(); z=np.load(ROOT/"results/data_v2j_arrays.npz")
    ids=z["station_ids"].astype(int);xy=z["coordinates"].astype(float);elev=z["elevation_m"].astype(float)
    foldroot=BASE/"station_forecasts"/"folds";out=BASE/"spatial_decoder"/"folds";out.mkdir(parents=True,exist_ok=True)
    all_test=[]; summaries=[]
    for hidden in ids:
        fold=foldroot/str(int(hidden)); inn=pd.read_parquet(fold/"inner"/"station_forecasts.parquet")
        outer=pd.read_parquet(fold/"outer"/"station_forecasts_all.parquet")
        known=ids[ids!=hidden]
        tr=make_examples(inn,z,"crossfit_train",known,hidden,xy,elev)
        va=make_examples(outer,z,"decoder_validation",known,hidden,xy,elev)
        te=make_examples(outer,z,"spatial_test",[hidden],hidden,xy,elev)
        if not tr or not va or not te:
            summaries.append({"station_id":int(hidden),"status":"UNSCORED","train_n":len(tr),"val_n":len(va),"test_n":len(te)})
            continue
        tx,tbase,_=features_for(tr);ty=torch.tensor([r[7] for r in tr],dtype=torch.float32)
        vx,vbase,_=features_for(va);vy=np.asarray([r[7] for r in va],float)
        torch.manual_seed(SEED+int(hidden));model=CompactSpatialDecoder(hidden=32);opt=torch.optim.AdamW(model.parameters(),lr=LR,weight_decay=.01)
        best=np.inf;best_state=None;best_epoch=0;stale=0;curve=[]
        gen=torch.Generator().manual_seed(SEED+int(hidden))
        for epoch in range(1,MAX_EPOCHS+1):
            model.train();perm=torch.randperm(len(tr),generator=gen);losses=[]
            for ix in perm.split(1024):
                opt.zero_grad(set_to_none=True);p=tbase[ix]+100*model.net(tx[ix]).squeeze(-1)
                loss=((p-ty[ix])**2).mean();loss.backward();torch.nn.utils.clip_grad_norm_(model.parameters(),1.0);opt.step();losses.append(float(loss.detach()))
            model.eval()
            with torch.no_grad(): vp=(vbase+100*model.net(vx).squeeze(-1)).numpy()
            vm=metrics(vp,vy);curve.append({"epoch":epoch,"train_rmse_loss":float(np.mean(losses)),"validation_mae":vm["mae"]})
            if vm["mae"]<best:best=vm["mae"];best_epoch=epoch;stale=0;best_state={k:v.detach().clone() for k,v in model.state_dict().items()}
            else:
                stale+=1
                if stale>=PATIENCE:break
        model.load_state_dict(best_state);model.eval()
        qx,qbase,qdist=features_for(te)
        with torch.no_grad():qpred=(qbase+100*model.net(qx).squeeze(-1)).numpy()
        qtrue=np.asarray([r[7] for r in te]);qtime=[r[1] for r in te]
        idw=qbase.numpy();mean=float(np.nanmean(z["observed_target"][(pd.DatetimeIndex(pd.to_datetime(z["times_ns"],utc=True))<=pd.Timestamp("2025-06-29T23:00:00Z"))][:,ids!=hidden]))
        records=[]
        for k,r in enumerate(te):
            records.append({"station_id":int(hidden),"target_time_utc":r[1],"target_ug_m3":qtrue[k],
                            "train_only_spatial_mean":mean,"forecast_idw":float(idw[k]),"forecast_decoder":float(qpred[k]),
                            "nearest_support_distance_m":float(qdist[k]),"support_count":13})
        pd.DataFrame(records).to_parquet(out/f"station_{int(hidden)}_predictions.parquet",index=False)
        pd.DataFrame(curve).to_csv(out/f"station_{int(hidden)}_curve.csv",index=False)
        torch.save({"state_dict":best_state,"station_id":int(hidden),"best_epoch":best_epoch,
                    "parameter_count":sum(p.numel() for p in model.parameters()),"seed":SEED},out/f"station_{int(hidden)}_decoder.pt")
        all_test.extend(records)
        summaries.append({"station_id":int(hidden),"status":"SCORED","train_examples":len(tr),"validation_examples":len(va),
                          "test_n":len(te),"best_epoch":best_epoch,"validation_mae":best,
                          "train_only_mean":metrics(np.full(len(te),mean),qtrue),"forecast_idw":metrics(idw,qtrue),
                          "decoder":metrics(qpred,qtrue),"mean_nearest_support_m":float(qdist.mean()),
                          "decoder_parameters":sum(p.numel() for p in model.parameters())})
        print(f"fold={hidden} train={len(tr)} val={len(va)} test={len(te)} decoder_mae={summaries[-1]['decoder']['mae']:.4f}",flush=True)
    pd.DataFrame(all_test).to_parquet(out/"all_spatial_test_predictions.parquet",index=False)
    (out/"fold_metrics.json").write_text(json.dumps(summaries,indent=2)+"\n")
    print(json.dumps({"scored_station_count":sum(x.get("status")=="SCORED" for x in summaries),
                      "total_seconds":time.perf_counter()-started,"test_predictions":len(all_test)},indent=2))

if __name__=="__main__":main()
