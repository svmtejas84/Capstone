"""Verify all V4 training artifacts, then one-time exploratory test scorer."""
import argparse,csv,json,datetime as dt
from pathlib import Path
import numpy as np,torch
from src.stpignn.evaluation import evaluate_arrays
from final_blr_results.controlled_validation_v3.scripts.smoke_gpu import CutoffContext,ARR,FIT,V3
from final_blr_results.controlled_validation_v3.scripts.train_controls import BASE_CFG,SEEDS,hash_file,atomic_json
from final_blr_results.controlled_validation_v4_review_closure.scripts.train_sensitivity import V4,VARIANTS

def verify():
 assert (V4/'training/final_COMPLETE').exists()
 assert hash_file(ARR)=='bd08d733f924387da82e758d1060703dfcdd121f360b7e8765189d8b7446e202'
 rows=[]
 for seed in SEEDS:
  for v in VARIANTS:
   cell=V4/'training/final'/f'h6_seed{seed}_{v}'
   rec=json.loads((cell/'COMPLETE.json').read_text())
   ckpt=cell/'best.pt';assert hash_file(ckpt)==rec['checkpoint_sha256']
   assert rec['variant']==v and rec['seed']==seed and rec['horizon_hours']==6
   assert rec['learning_rate']==.0003 and rec['array_sha256']==hash_file(ARR)
   assert 10<=rec['best_epoch']<=rec['epochs_run']<=30
   ep=json.loads((cell/'epochs.json').read_text())
   assert len(ep)==rec['epochs_run'] and abs(ep[rec['best_epoch']-1]['validation_mae']-rec['validation_mae'])<1e-7
   assert all(np.isfinite(r['validation_mae']) and np.isfinite(r['mean_data_loss']) and np.isfinite(r['mean_penalty']) for r in ep)
   assert abs(rec['effective_lambda_at_best']-ep[rec['best_epoch']-1]['lambda_effective'])<1e-12
   rows.append(rec)
 assert len(rows)==30
 (V4/'verification').mkdir(exist_ok=True)
 atomic_json(V4/'verification/training_verified.json',dict(status='PASS',cells=30,array_sha256=hash_file(ARR),utc=dt.datetime.now(dt.timezone.utc).isoformat()))
 return rows

def save_once(path, **arrays):
 if path.exists():return
 path.parent.mkdir(parents=True,exist_ok=True)
 tmp=path.with_name(path.stem+'.tmp.npz');np.savez_compressed(tmp,**arrays);tmp.replace(path)

def score():
 verify()
 assert not (V4/'metrics/V4_SENSITIVITY_SCORES.csv').exists()
 atomic_json(V4/'verification/test_unlock.json',dict(utc=dt.datetime.now(dt.timezone.utc).isoformat(),array_sha256=hash_file(ARR),reason='all 30 validation-selected fits verified',population='historically exposed test; exploratory'))
 ctx=CutoffContext(6,BASE_CFG,ARR,FIT)
 with np.load(V3/'predictions/h6_true_wind_ensemble.npz') as z:
  reference={k:z[k] for k in ('truth','time_index','station_index')}
 rows=[]
 for v in VARIANTS:
  preds=[]
  for seed in SEEDS:
   cell=V4/'training/final'/f'h6_seed{seed}_{v}'
   ckpt=cell/'best.pt';rec=json.loads((cell/'COMPLETE.json').read_text())
   assert hash_file(ckpt)==rec['checkpoint_sha256']
   saved=V4/'predictions'/f'h6_{v}_seed{seed}.npz'
   if saved.exists():
    with np.load(saved) as z: result={k:z[k] for k in ('pred','truth','time_index','station_index')}
   else:
    payload=torch.load(ckpt,map_location='cpu',weights_only=False)
    assert payload['variant']==v and payload['seed']==seed and payload['horizon']==6 and payload['protocol']=='v4'
    model=ctx.make('stpignn_lambda0');model.load_state_dict(payload['state_dict'],strict=True)
    result=ctx.evaluate(model,'stpignn_lambda0','test',collect=True)
    save_once(saved,**{k:result[k] for k in ('pred','truth','time_index','station_index')})
   for k in reference:assert np.array_equal(result[k],reference[k])
   assert len(result['pred'])==14583 and np.isfinite(result['pred']).all()
   m=evaluate_arrays(result['pred'],result['truth'],np.ones(len(result['pred']),bool))
   rows.append(dict(horizon_hours=6,variant=v,seed=seed,mae=m['mae'],rmse=m['rmse'],r2=m['r2'],n=m['n'],checkpoint_sha256=rec['checkpoint_sha256'],population='exposed exploratory'))
   preds.append(result['pred'])
  p=np.mean(np.stack(preds),axis=0)
  save_once(V4/'predictions'/f'h6_{v}_ensemble.npz',pred=p,**reference)
  m=evaluate_arrays(p,reference['truth'],np.ones(len(p),bool))
  rows.append(dict(horizon_hours=6,variant=v,seed='ensemble',mae=m['mae'],rmse=m['rmse'],r2=m['r2'],n=m['n'],checkpoint_sha256='',population='exposed exploratory'))
 path=V4/'metrics/V4_SENSITIVITY_SCORES.csv';path.parent.mkdir(exist_ok=True)
 tmp=path.with_suffix('.tmp')
 with tmp.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
 tmp.replace(path)
 print(json.dumps(dict(rows=len(rows),variants=len(VARIANTS),n=14583)),flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--stage',choices=['verify','score'],required=True);a=p.parse_args()
 if a.stage=='verify':print(json.dumps(dict(cells=len(verify()),status='PASS')))
 else:score()
