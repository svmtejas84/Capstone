"""Frozen six-member exploratory V4 comparison and common wind-cone diagnostic."""
import csv,json,shutil
import numpy as np,pandas as pd
from src.stpignn.station_graph import directed_knn_graph
from final_blr_results.controlled_validation_v3.scripts.analyze_controls import block_analysis,holm
from final_blr_results.controlled_validation_v3.scripts.train_controls import V3,ARR,SEEDS
from final_blr_results.controlled_validation_v4_review_closure.scripts.train_sensitivity import V4,VARIANTS

def load(v,suffix='_ensemble'):
 root=V3 if v in ('true_wind','zero','laplacian') else V4
 with np.load(root/'predictions'/f'h6_{v}{suffix}.npz') as z:return {k:z[k] for k in ('pred','truth','time_index','station_index')}
def write(rows,path):
 path.parent.mkdir(exist_ok=True)
 with path.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)

assert (V4/'metrics/V4_SENSITIVITY_SCORES.csv').exists()
z=np.load(ARR);times=pd.to_datetime(z['times_ns'],utc=True)
a=load('true_wind');day=times[a['time_index']].floor('D').asi8
rows=[];seeds=[]
for i,v in enumerate(VARIANTS):
 b=load(v)
 for k in ('truth','time_index','station_index'):assert np.array_equal(a[k],b[k])
 delta=abs(a['pred']-a['truth'])-abs(b['pred']-b['truth'])
 ci,p,blocks,days=block_analysis(day,delta,73001+i)
 rows.append(dict(horizon_hours=6,contrast='true_wind_006_minus_'+v,paired_delta_mae_ug_m3=float(delta.mean()),ci95_low_ug_m3=ci[0],ci95_high_ug_m3=ci[1],block_signflip_p=p,paired_pairs=len(delta),utc_days=days,nonoverlap_blocks=blocks,inference='exploratory; exposed test; 6-member V4 family'))
 for seed in SEEDS:
  aa=load('true_wind',f'_seed{seed}');bb=load(v,f'_seed{seed}')
  for k in ('truth','time_index','station_index'):assert np.array_equal(aa[k],bb[k])
  sd=float(np.mean(abs(aa['pred']-aa['truth'])-abs(bb['pred']-bb['truth'])))
  seeds.append(dict(variant=v,seed=seed,true_minus_variant_mae_ug_m3=sd,favors_true=sd<0,paired_pairs=len(aa['pred'])))
for r,p in zip(rows,holm([r['block_signflip_p'] for r in rows])):r['holm_6_p']=p
write(rows,V4/'statistical_analysis/V4_SIX_CONTRASTS.csv')
write(seeds,V4/'statistical_analysis/V4_SEED_CONTRASTS.csv')

# Actual-wind mask, only endpoint-observed arcs, independent of training variant.
edge,_=directed_knn_graph(z['coordinates'],4);src,dst=edge.numpy();xy=z['coordinates']
bearing=np.arctan2((xy[dst]-xy[src])[:,0],(xy[dst]-xy[src])[:,1])
to=np.deg2rad((z['raw_wind_degrees'].astype(float)+180)%360)
angle=np.abs(np.angle(np.exp(1j*(to[:,None]-bearing[None,:]))))
mask=np.isfinite(to[:,None])&(angle<=np.deg2rad(37.5))
scale=float(json.loads((V3.parents[1]/'results/data_v2j_fit.json').read_text())['fit']['target_standard_std'])
vr=[]
for v in ['zero','true_wind','laplacian']+VARIANTS:
 p=load(v);hours,inverse=np.unique(p['time_index'],return_inverse=True)
 pm=np.full((len(hours),len(xy)),np.nan);pm[inverse,p['station_index']]=p['pred']
 eligible=mask[hours-6]&np.isfinite(pm[:,src])&np.isfinite(pm[:,dst])
 d=(pm[:,dst]-pm[:,src])/scale
 n=int(eligible.sum());viol=int(np.count_nonzero((d>.05)&eligible))
 positive=np.maximum(d,0)
 vr.append(dict(variant=v,horizon_hours=6,threshold_normalized=.05,threshold_ug_m3=.05*scale,eligible_observed_pair_arcs=n,violations=viol,violation_percent=100*viol/n if n else np.nan,mean_positive_violation_normalized=float(positive[eligible].mean()),mean_squared_positive_violation_normalized=float((positive[eligible]**2).mean()),zero_eligible_arc_hours=int(np.count_nonzero(~eligible.any(axis=1)))))
write(vr,V4/'PENALTY_DIAGNOSTICS_V4.csv')
shutil.copyfile(V3/'metrics/wind_cone_diagnostics.csv',V4/'PENALTY_DIAGNOSTICS_V3.csv')
print(json.dumps(dict(contrasts=len(rows),seed_contrasts=len(seeds),diagnostic_variants=len(vr))))
