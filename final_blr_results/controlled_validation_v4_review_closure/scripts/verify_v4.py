"""Read-only scientific checks; outputs a V4-only verification record."""
import csv,hashlib,json,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np,pandas as pd
from PIL import Image
from final_blr_results.controlled_validation_v3.scripts.train_controls import V3,ARR,hash_file
from final_blr_results.controlled_validation_v4_review_closure.scripts.train_sensitivity import V4,VARIANTS

def ck(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
rows=list(csv.DictReader((V4/'SOURCE_HASHES.csv').open()))
for r in rows:
 p=Path(r['path']);assert p.exists() and ck(p)==r['sha256'] and p.stat().st_size==int(r['bytes']),r['path']
assert len(rows)==11
assert hash_file(ARR)=='bd08d733f924387da82e758d1060703dfcdd121f360b7e8765189d8b7446e202'
reg=pd.read_csv(V4/'COMPLETE_MODEL_AND_BASELINE_REGISTER.csv');assert len(reg)==80 and reg.method.nunique()==16 and set(reg.horizon_hours)=={1,3,6,12,24}
assert (reg.scored_pairs==14583).all()
prior=pd.read_csv(V4/'COMPLETE_20_CONTRAST_RESULTS.csv');assert len(prior)==20
arch=pd.read_csv(V4/'statistical_analysis/GRAPH_ARCHITECTURE_CONTRASTS.csv');assert len(arch)==15
scores=pd.read_csv(V4/'metrics/V4_SENSITIVITY_SCORES.csv');assert len(scores)==36 and set(scores.variant)==set(VARIANTS) and (scores.n==14583).all()
contr=pd.read_csv(V4/'statistical_analysis/V4_SIX_CONTRASTS.csv');assert len(contr)==6
assert (V4/'verification/training_verified.json').exists() and (V4/'verification/test_unlock.json').exists()
assert (V4/'training/final_COMPLETE').exists() and (V4/'logs/sensitivity/COMPLETE').exists() and (V4/'logs/test_score/COMPLETE').exists()
ref=np.load(V3/'predictions/h6_true_wind_ensemble.npz')
ckrows=[];predrows=[]
for v in VARIANTS:
 for seed in [11,23,37,51,79]:
  cell=V4/'training/final'/f'h6_seed{seed}_{v}'
  rec=json.loads((cell/'COMPLETE.json').read_text());p=cell/'best.pt'
  assert ck(p)==rec['checkpoint_sha256'] and rec['array_sha256']==hash_file(ARR)
  ckrows.append(dict(variant=v,seed=seed,path=str(p),sha256=ck(p),bytes=p.stat().st_size,best_epoch=rec['best_epoch']))
 for suffix in [f'_seed{s}' for s in [11,23,37,51,79]]+['_ensemble']:
  p=V4/'predictions'/f'h6_{v}{suffix}.npz'
  with np.load(p) as z:
   for k in ('truth','time_index','station_index'):assert np.array_equal(z[k],ref[k])
   pred=z['pred'];truth=z['truth'];assert len(pred)==14583 and np.isfinite(pred).all()
   actual=float(np.mean(abs(pred-truth)))
  seed='ensemble' if suffix=='_ensemble' else int(suffix.removeprefix('_seed'))
  row=scores[(scores.variant==v)&(scores.seed.astype(str)==str(seed))]
  assert len(row)==1 and abs(actual-float(row.iloc[0].mae))<1e-5
  predrows.append(dict(variant=v,seed=seed,path=str(p),sha256=ck(p),bytes=p.stat().st_size,mae=actual))
assert len(ckrows)==30 and len(predrows)==36
for _,r in contr.iterrows():
 v=r.contrast.removeprefix('true_wind_006_minus_')
 with np.load(V4/'predictions'/f'h6_{v}_ensemble.npz') as z:
  delta=np.mean(abs(ref['pred']-ref['truth'])-abs(z['pred']-z['truth']))
 assert abs(delta-r.paired_delta_mae_ug_m3)<2e-5
assert len(pd.read_csv(V4/'PENALTY_GRADIENT_REPLAY.csv'))==21
assert len(pd.read_csv(V4/'PENALTY_DIAGNOSTICS_V3.csv'))==100
assert len(pd.read_csv(V4/'PENALTY_DIAGNOSTICS_V4.csv'))==9
fig=V4/'figures';assert len(list(fig.glob('*.png')))==5
for p in fig.glob('*.png'):
 im=Image.open(p);im.verify()
 assert p.with_suffix('.pdf').read_bytes().startswith(b'%PDF')
 ET.parse(p.with_suffix('.svg'))
latex=list((V4/'tables').glob('*.tex'))
assert len(latex)==4
for p in latex:
 s=p.read_text();assert '\\begin{tabular}' in s and '\\end{tabular}' in s
(V4/'verification').mkdir(exist_ok=True)
for name,data in [('CHECKPOINT_MANIFEST.csv',ckrows),('PREDICTION_MANIFEST.csv',predrows)]:
 with (V4/'verification'/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(data[0]),lineterminator='\n');w.writeheader();w.writerows(data)
result=dict(status='PASS',v3_source_hashes=len(rows),complete_model_horizon_rows=len(reg),frozen_wind_contrasts=len(prior),graph_architecture_contrasts=len(arch),v4_fit_cells=len(ckrows),v4_prediction_files=len(predrows),v4_contrasts=len(contr),gradient_replay_rows=21,figures=5,latex_tables=len(latex),invalidated_shuffle_attempts=len(list((V4/'training/invalidated_pre_amendment').glob('*/COMPLETE.json'))),historical_v3_tracked_diff_files=[])
# Git history check uses tracked files only; local V3 run-control files predate V4.
diff=subprocess.check_output(['git','diff','--name-only','ffe03f8dd77abdc1e96e96f7a113a403e735c249','--','final_blr_results/controlled_validation_v3'],text=True).strip()
assert not diff,diff
(V4/'verification/VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n')
(V4/'verification/VERIFICATION.md').write_text('# V4 verification\n\n'+json.dumps(result,indent=2)+'\n\nCommands: `PYTHONPATH=. python final_blr_results/controlled_validation_v4_review_closure/scripts/verify_v4.py`; `PYTHONPATH=. pytest -q tests/test_physics_v2.py` (3 passed). The V3 source-hash manifest was checked independently before and after scoring (7/7 unchanged). The test period remains exposed; computation verification is not independent validation.\n')
print(json.dumps(result,indent=2))
