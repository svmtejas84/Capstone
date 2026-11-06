from __future__ import annotations
import json
from pathlib import Path
import numpy as np,pandas as pd

OUT=Path(__file__).resolve().parent

def met(p,y):
 e=np.asarray(p)-np.asarray(y);ss=float(np.sum((y-np.mean(y))**2))
 return {"n":len(e),"mae":float(np.mean(np.abs(e))),"rmse":float(np.sqrt(np.mean(e**2))),"r2":float(1-np.sum(e**2)/ss) if ss>0 else None}

def main():
 p=pd.read_parquet(OUT/"folds/all_spatial_test_predictions.parquet")
 rows=[]
 for sid,g in p.groupby("station_id"):
  r={"station_id":int(sid),"n_observations":len(g)}
  for m in ("train_only_spatial_mean","forecast_idw","forecast_decoder"):
   mm=met(g[m].to_numpy(),g.target_ug_m3.to_numpy())
   for k,v in mm.items():r[f"{m}_{k}"]=v
  r["mean_nearest_support_distance_m"]=float(g.nearest_support_distance_m.mean())
  rows.append(r)
 stations=pd.DataFrame(rows);stations.to_csv(OUT/"per_station_test_metrics.csv",index=False)
 all_rows=[]
 for m in ("train_only_spatial_mean","forecast_idw","forecast_decoder"):
  mm=met(p[m].to_numpy(),p.target_ug_m3.to_numpy());all_rows.append({"method":m,**mm,"coverage_pairs":len(p),"scored_stations":len(stations),"decoder_parameter_count":1249 if m=="forecast_decoder" else 0})
 pd.DataFrame(all_rows).to_csv(OUT/"pooled_test_metrics.csv",index=False)
 rng=np.random.default_rng(4303);ci=[]
 site_mae=stations.set_index("station_id")
 for control in ("train_only_spatial_mean","forecast_idw"):
  delta=(site_mae.forecast_decoder_mae-site_mae[f"{control}_mae"]).to_numpy()
  boots=np.array([rng.choice(delta,size=len(delta),replace=True).mean() for _ in range(2000)])
  ci.append({"contrast":"decoder_minus_"+control,"station_equal_weighted_delta_mae":float(delta.mean()),
             "station_bootstrap_95ci_low":float(np.quantile(boots,.025)),"station_bootstrap_95ci_high":float(np.quantile(boots,.975)),
             "bootstrap_replicates":2000,"seed":4303,"independent_sites":len(delta)})
 pd.DataFrame(ci).to_csv(OUT/"station_bootstrap_comparisons.csv",index=False)
 print(pd.DataFrame(all_rows).to_string(index=False));print(pd.DataFrame(ci).to_string(index=False))

if __name__=="__main__":main()
