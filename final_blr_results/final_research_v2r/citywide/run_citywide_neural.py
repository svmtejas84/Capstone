"""Fit the frozen compact bridge and run issue-time-safe Bengaluru road estimates."""
from __future__ import annotations
import hashlib, json, resource, sys, time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
from scipy.spatial import cKDTree, Delaunay, QhullError

ROOT=Path(__file__).resolve().parents[3]
BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from final_blr_results.citywide_extension.v2q.spatial_decoder import CompactSpatialDecoder

HIDDEN=32; SEED=42; LR=1e-3; MAX_EPOCHS=10; PATIENCE=3
ORIGINS=pd.to_datetime(["2025-10-08T07:00:00Z","2026-02-10T01:00:00Z","2026-03-28T17:00:00Z"],utc=True)

def sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for b in iter(lambda:f.read(1<<20),b""):h.update(b)
 return h.hexdigest()

def features(sxy,sy,se,qxy,qe):
 d=np.linalg.norm(qxy[:,None,:]-sxy[None,:,:],axis=2)
 nearest=d.min(axis=1); w=np.maximum(d,1.)**-2
 base=(w@sy)/w.sum(axis=1)
 x=np.column_stack((base/100.,nearest/10000.,np.full(len(qxy),len(sy)/15.),(qe-float(np.mean(se)))/100.))
 return x.astype(np.float32),base,nearest

def main():
 torch.set_num_threads(1)
 torch.manual_seed(SEED)
 torch.use_deterministic_algorithms(True)
 start=time.perf_counter(); out=BASE/"road_predictions"; out.mkdir(parents=True,exist_ok=True)
 z=np.load(ROOT/"results/data_v2j_arrays.npz"); ids=z["station_ids"].astype(int); xy=z["coordinates"].astype(float); elev=z["elevation_m"].astype(float)
 # Fit final compact decoder from target-time-cross-fitted station forecasts.
 foldroot=BASE/"station_forecasts"/"folds"; train_rows=[]; val_rows=[]
 for iq,q in enumerate(ids):
  # Each training example uses a frozen inner model that excluded q from support
  # and whose source fitting ended before this target block.
  hidden=int(ids[(iq+1)%len(ids)])
  f=pd.read_parquet(foldroot/str(hidden)/"inner"/"station_forecasts.parquet")
  train_rows.extend(__import__("final_blr_results.final_research_v2r.citywide.spatial_decoder.evaluate_decoder_loso",fromlist=["make_examples"]).make_examples(f,z,"crossfit_train",[int(q)],hidden,xy,elev))
  # Validation forecasts come from the outer model that excluded the query site.
  f=pd.read_parquet(foldroot/str(int(q))/"outer"/"station_forecasts_all.parquet")
  val_rows.extend(__import__("final_blr_results.final_research_v2r.citywide.spatial_decoder.evaluate_decoder_loso",fromlist=["make_examples"]).make_examples(f,z,"decoder_validation",[int(q)],int(q),xy,elev))
 if not train_rows or not val_rows: raise RuntimeError("empty final decoder train/validation set")
 def tensors(rows):
  xx=[];bb=[];yy=[]
  for _,_,sxy,sy,se,qxy,qe,y,_ in rows:
   d=np.linalg.norm(sxy-qxy[None,:],axis=1); w=np.maximum(d,1.)**-2; b=float(w@sy/w.sum())
   xx.append([b/100.,float(d.min())/10000.,len(sy)/15.,(qe-float(np.mean(se)))/100.]);bb.append(b);yy.append(y)
  return torch.tensor(xx),torch.tensor(bb),np.asarray(yy,float)
 tx,tb,ty=tensors(train_rows); vx,vb,vy=tensors(val_rows)
 torch.manual_seed(SEED);model=CompactSpatialDecoder(hidden=HIDDEN);opt=torch.optim.AdamW(model.parameters(),lr=LR,weight_decay=.01)
 gen=torch.Generator().manual_seed(SEED);best=np.inf;best_state=None;best_epoch=0;stale=0;curve=[]
 for epoch in range(1,MAX_EPOCHS+1):
  model.train(); perm=torch.randperm(len(tx),generator=gen); losses=[]
  for ix in perm.split(1024):
   opt.zero_grad(set_to_none=True); pred=tb[ix]+100*model.net(tx[ix]).squeeze(-1);loss=((pred- torch.tensor(ty[ix.numpy()],dtype=torch.float32))**2).mean();loss.backward();torch.nn.utils.clip_grad_norm_(model.parameters(),1.);opt.step();losses.append(float(loss.detach()))
  model.eval()
  with torch.no_grad():vp=(vb+100*model.net(vx).squeeze(-1)).numpy()
  mae=float(np.mean(np.abs(vp-vy)));curve.append({"epoch":epoch,"train_mse":float(np.mean(losses)),"validation_mae":mae})
  if mae<best:best=mae;best_epoch=epoch;stale=0;best_state={k:v.detach().clone() for k,v in model.state_dict().items()}
  else:
   stale+=1
   if stale>=PATIENCE:break
 model.load_state_dict(best_state);model.eval();torch.save({"state_dict":best_state,"hidden":HIDDEN,"seed":SEED,"best_epoch":best_epoch,"parameter_count":sum(p.numel() for p in model.parameters()),"train_examples":len(train_rows),"validation_examples":len(val_rows)},out/"compact_decoder_final.pt")
 pd.DataFrame(curve).to_csv(out/"compact_decoder_training_curve.csv",index=False)
 (out/"compact_decoder_fit.json").write_text(json.dumps({"train_examples":len(train_rows),"validation_examples":len(val_rows),"best_epoch":best_epoch,"validation_mae_ug_m3":best,"parameter_count":sum(p.numel() for p in model.parameters()),"seed":SEED,"selection":"frozen validation MAE patience 3"},indent=2)+"\n")
 # Canonical road-node index: raw graph parquet row index and osmid, joined to
 # SRTM elevation by the validated ordered osmid mapping.
 nodes=pd.read_parquet(ROOT/"data/graphs/bangalore_utm_nodes.parquet"); ev=pd.read_parquet(ROOT/"data/processed/graph/nodes_elevation_true.parquet")
 if len(nodes)!=154902 or not np.array_equal(nodes.osmid.to_numpy(),ev.osmid.to_numpy()) or not np.allclose(nodes[["x","y"]].to_numpy(),ev[["utm_x","utm_y"]].to_numpy()):raise RuntimeError("road node/elevation mapping mismatch")
 road_xy=nodes[["x","y"]].to_numpy(float); road_e=ev.elevation_true.to_numpy(float); osmid=nodes.osmid.to_numpy()
 # For each station support j, use the forecast from the model whose outer LOSO
 # fit excluded j. This is a station-isolated forecast, not an observation.
 test_arrays={}; target_times=ORIGINS+pd.Timedelta(hours=6)
 for j,sid in enumerate(ids):
  p=foldroot/str(int(sid))/"outer"/"station_forecasts_all.parquet"; fr=pd.read_parquet(p)
  fr=fr[(fr.station_id==int(sid)) & (fr.split=="spatial_test")]
  table=fr.set_index(pd.to_datetime(fr.target_time_utc,utc=True)).prediction_ug_m3
  vals=[]
  for tt in target_times:
   if tt not in table.index:raise RuntimeError(f"missing forecast {sid} {tt}")
   vals.append(float(table.loc[tt]))
  test_arrays[int(sid)]=vals
 # Select 13 nearest supports per road node; calculate methods in chunks to cap RAM.
 rows=[]; bench=[]; support_meta=[]
 for k,(origin,target) in enumerate(zip(ORIGINS,target_times)):
  st=time.perf_counter(); dist,order=cKDTree(xy).query(road_xy,k=13,workers=1); elapsed_query=time.perf_counter()-st
  supports=ids[order]; sy=np.column_stack([np.asarray(test_arrays[int(i)]) for i in ids])[k]
  # reorder predictions and static attributes for each query's 13 supports.
  idx=order; vals=np.asarray([test_arrays[int(i)][k] for i in ids],float)
  staged=[]
  for n in (1000,10000):
   tst=time.perf_counter();dd=dist[:n];ii=idx[:n];sv=vals[ii];ww=np.maximum(dd,1.)**-2;bb=(ww*sv).sum(axis=1)/ww.sum(axis=1)
   xx=np.column_stack((bb/100.,dd[:,0]/10000.,np.full(n,13/15.),(road_e[:n]-elev[ii].mean(axis=1))/100.)).astype(np.float32)
   with torch.no_grad():dp=(torch.tensor(bb,dtype=torch.float32)+100*model.net(torch.tensor(xx)).squeeze(-1)).numpy()
   if not np.isfinite(dp).all() or not np.isfinite(bb).all():raise RuntimeError(f"{n}-node staged inference failed")
   staged.append({"nodes":n,"wall_seconds":time.perf_counter()-tst,"idw":bb.copy(),"decoder":dp.copy()})
  chunk=[]; maxerr=0.; small_checks={}
  for lo in range(0,len(road_xy),4096):
   hi=min(lo+4096,len(road_xy)); oi=idx[lo:hi]; d=dist[lo:hi]
   sv=vals[oi]; w=np.maximum(d,1.)**-2; base=(w*sv).sum(axis=1)/w.sum(axis=1)
   near=d[:,0]; se=elev[oi]
   xx=np.column_stack((base/100.,near/10000.,np.full(len(base),13/15.),(road_e[lo:hi]-se.mean(axis=1))/100.)).astype(np.float32)
   with torch.no_grad(): dec=(torch.tensor(base,dtype=torch.float32)+100*model.net(torch.tensor(xx)).squeeze(-1)).numpy()
   # Same-coordinate station support diagnostic, not calibrated uncertainty.
   hullout=np.ones(len(base),dtype=bool)
   try:
    # Hull evaluated against all 15 station support coordinates.
    hullout=Delaunay(xy).find_simplex(road_xy[lo:hi])<0
   except QhullError:pass
   frame=pd.DataFrame({"node_index":np.arange(lo,hi),"osmid":osmid[lo:hi],"utm_x_m":road_xy[lo:hi,0],"utm_y_m":road_xy[lo:hi,1],"forecast_origin_utc":str(origin),"target_time_utc":str(target),"horizon_hours":6,"forecast_idw_ug_m3":base,"forecast_decoder_ug_m3":dec,"nearest_support_distance_m":near,"support_count":13,"outside_station_hull":hullout,"poor_support_gt5km":near>5000,"support_station_ids":[ids[r].astype(int).tolist() for r in oi]})
   chunk.append(frame)
   if lo==0:
    small_checks={"1000":base[:1000].copy(),"10000":base[:10000].copy()}
  res=pd.concat(chunk,ignore_index=True)
  if len(res)!=154902 or not np.isfinite(res[["forecast_idw_ug_m3","forecast_decoder_ug_m3"]]).all().all():raise RuntimeError("full road output incomplete/nonfinite")
  if (res[["forecast_idw_ug_m3","forecast_decoder_ug_m3"]].to_numpy()<0).any():raise RuntimeError("negative concentration forecast")
  p=out/f"road_predictions_{origin.strftime('%Y%m%dT%H%MZ')}.parquet";res.to_parquet(p,index=False)
  # exact prefix/full determinism checks for both methods
  for stage in staged:
   n=stage["nodes"]
   # Recompute prefix independently from the selected full support matrix.
   check_start=time.perf_counter();d=dist[:n];oi=idx[:n];sv=vals[oi];w=np.maximum(d,1.)**-2;b=(w*sv).sum(axis=1)/w.sum(axis=1)
   xx=np.column_stack((b/100.,d[:,0]/10000.,np.full(n,13/15.),(road_e[:n]-elev[oi].mean(axis=1))/100.)).astype(np.float32)
   with torch.no_grad():db=(torch.tensor(b,dtype=torch.float32)+100*model.net(torch.tensor(xx)).squeeze(-1)).numpy()
   elapsed_prefix=time.perf_counter()-check_start
   err=float(max(np.max(np.abs(b-res.forecast_idw_ug_m3.to_numpy()[:n])),np.max(np.abs(db-res.forecast_decoder_ug_m3.to_numpy()[:n]))))
   if err>1e-6:raise RuntimeError("prefix/full IDW mismatch")
   bench.append({"origin_utc":str(origin),"nodes":n,"staged_seconds":stage["wall_seconds"],"verification_seconds":elapsed_prefix,"nodes_per_second":n/stage["wall_seconds"],"max_abs_diff_ug_m3":err})
  bench.append({"origin_utc":str(origin),"nodes":154902,"wall_seconds":time.perf_counter()-st,"query_seconds":elapsed_query,"nodes_per_second":154902/(time.perf_counter()-st),"peak_rss_kib":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,"gpu_vram_bytes":0,"finite_predictions":int(res.forecast_decoder_ug_m3.notna().sum()),"sha256":sha(p)})
  pd.DataFrame(res.iloc[::20][["utm_x_m","utm_y_m","forecast_decoder_ug_m3","poor_support_gt5km"]]).to_csv(out/f"map_points_{origin.strftime('%Y%m%dT%H%MZ')}.csv",index=False)
  fig,ax=plt.subplots(figsize=(9,8));sc=ax.scatter(res.utm_x_m,res.utm_y_m,c=res.forecast_decoder_ug_m3,s=1,cmap="magma",vmin=0,vmax=np.quantile(res.forecast_decoder_ug_m3,.98));ax.scatter(res.loc[res.poor_support_gt5km,"utm_x_m"],res.loc[res.poor_support_gt5km,"utm_y_m"],s=1,c="#38bdf8",alpha=.3,label=">5 km from station");ax.set_title(f"Experimental neural-assisted estimate, target {target:%Y-%m-%d %H:%M UTC}");ax.set_xlabel("UTM x (m)");ax.set_ylabel("UTM y (m)");fig.colorbar(sc,ax=ax,label="Estimated PM2.5 (µg/m³)");ax.legend(markerscale=6);fig.tight_layout();fig.savefig(BASE/"figures"/f"city_{origin.strftime('%Y%m%dT%H%MZ')}.png",dpi=160);plt.close(fig)
  support_meta.append({"origin_utc":str(origin),"target_utc":str(target),"support_stations":ids.tolist(),"station_forecast_method":"diagonal outer-LOSO prediction: each support station predicted by corrected GINE-GRU fold that excluded its own labels","forecast_hashes":{str(int(s)):sha(foldroot/str(int(s))/"outer"/"station_forecasts_all.parquet") for s in ids}})
 pd.DataFrame(bench).to_csv(out/"citywide_benchmarks.csv",index=False)
 (out/"citywide_manifest.json").write_text(json.dumps({"nodes":154902,"origins_utc":[str(x) for x in ORIGINS],"targets_utc":[str(x) for x in target_times],"method":"h6 corrected station GINE-GRU diagonal outer-LOSO support forecasts + frozen 1249-param compact spatial decoder; IDW comparator","node_order":"data/graphs/bangalore_utm_nodes.parquet row order; node_index 0..154901; elevation joined by ordered osmid","road_nodes_are_not_observations":True,"support_forecast_provenance":support_meta,"decoder_sha256":sha(out/"compact_decoder_final.pt"),"coordinate_source_sha256":sha(ROOT/"data/graphs/bangalore_utm_nodes.parquet"),"elevation_source_sha256":sha(ROOT/"data/processed/graph/nodes_elevation_true.parquet"),"runtime_seconds":time.perf_counter()-start,"peak_rss_kib":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,"gpu_vram_bytes":0},indent=2)+"\n")
 print(json.dumps({"nodes":154902,"timestamps":len(target_times),"runtime_seconds":time.perf_counter()-start,"peak_rss_kib":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss},indent=2))

if __name__=="__main__":main()
