"""Recompute saved decoder inference for the frozen three target times."""
from __future__ import annotations
import json,sys
from pathlib import Path
import numpy as np,pandas as pd,torch
from scipy.spatial import cKDTree
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from final_blr_results.citywide_extension.v2q.spatial_decoder import CompactSpatialDecoder
def main():
 torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
 z=np.load(ROOT/"results/data_v2j_arrays.npz");ids=z["station_ids"].astype(int);xy=z["coordinates"].astype(float);e=z["elevation_m"].astype(float)
 nodes=pd.read_parquet(ROOT/"data/graphs/bangalore_utm_nodes.parquet");ev=pd.read_parquet(ROOT/"data/processed/graph/nodes_elevation_true.parquet")
 qxy=nodes[["x","y"]].to_numpy(float);qe=ev.elevation_true.to_numpy(float);tree=cKDTree(xy)
 model=CompactSpatialDecoder(hidden=32);state=torch.load(BASE/"road_predictions/compact_decoder_final.pt",map_location="cpu",weights_only=False);model.load_state_dict(state["state_dict"]);model.eval()
 folds=BASE/"station_forecasts/folds";origins=pd.to_datetime(["2025-10-08T07:00:00Z","2026-02-10T01:00:00Z","2026-03-28T17:00:00Z"],utc=True);out=[]
 for origin in origins:
  target=origin+pd.Timedelta(hours=6);vals=[]
  for sid in ids:
   f=pd.read_parquet(folds/str(int(sid))/"outer"/"station_forecasts_all.parquet");f=f[(f.station_id==int(sid))&(f.split=="spatial_test")]
   t=pd.to_datetime(f.target_time_utc,utc=True);vals.append(float(f.loc[t==target,"prediction_ug_m3"].iloc[0]))
  d,ix=tree.query(qxy,k=13,workers=1);sv=np.asarray(vals)[ix];w=np.maximum(d,1.)**-2;base=(w*sv).sum(1)/w.sum(1)
  x=np.column_stack((base/100.,d[:,0]/10000.,np.full(len(qe),13/15.),(qe-e[ix].mean(1))/100.)).astype(np.float32)
  with torch.no_grad():pred=(torch.tensor(base,dtype=torch.float32)+100*model.net(torch.tensor(x)).squeeze(-1)).numpy()
  p=BASE/"road_predictions"/f"road_predictions_{origin.strftime('%Y%m%dT%H%MZ')}.parquet";saved=pd.read_parquet(p)
  diff=np.abs(pred-saved.forecast_decoder_ug_m3.to_numpy());out.append({"target_time_utc":str(target),"rows":len(pred),"finite":bool(np.isfinite(pred).all()),"max_abs_difference_ug_m3":float(diff.max()),"exact_equal":bool(np.array_equal(pred,saved.forecast_decoder_ug_m3.to_numpy()))})
 if any(x["rows"]!=154902 or not x["finite"] or x["max_abs_difference_ug_m3"]>1e-6 for x in out):raise RuntimeError("repeat inference mismatch")
 (BASE/"road_predictions/reproducibility_check.json").write_text(json.dumps(out,indent=2)+"\n");print(json.dumps(out,indent=2))
if __name__=="__main__":main()
