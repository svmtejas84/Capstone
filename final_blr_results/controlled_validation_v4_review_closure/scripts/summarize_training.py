"""Generate lightweight training and invalidated-attempt manifests from saved V4 cells."""
import csv,hashlib,json
from pathlib import Path
from final_blr_results.controlled_validation_v4_review_closure.scripts.train_sensitivity import V4
rows=[]
for p in sorted((V4/'training/final').glob('*/COMPLETE.json')):
 r=json.loads(p.read_text());h=json.loads((p.parent/'epochs.json').read_text());e=h[r['best_epoch']-1]
 rows.append(dict(variant=r['variant'],seed=r['seed'],learning_rate=r['learning_rate'],best_epoch=r['best_epoch'],epochs_run=r['epochs_run'],validation_mae=r['validation_mae'],effective_lambda_at_best=r['effective_lambda_at_best'],best_epoch_mean_data_loss=e['mean_data_loss'],best_epoch_mean_raw_penalty=e['mean_penalty'],best_epoch_weighted_penalty=e['mean_penalty']*e['lambda_effective'],best_epoch_active_arcs=e['active_arcs'],best_epoch_zero_arc_batches=e['zero_arc_batches'],elapsed_seconds=r['elapsed_seconds'],checkpoint_sha256=r['checkpoint_sha256']))
assert len(rows)==30
with (V4/'TRAINING_SUMMARY.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
invalid=[]
for d in sorted((V4/'training/invalidated_pre_amendment').glob('*')):
 for p in sorted(d.glob('*')):
  if p.is_file():invalid.append(dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size,reason='target-availability-indexed shuffle; no test scoring'))
assert len(list((V4/'training/invalidated_pre_amendment').glob('*/COMPLETE.json')))==4
with (V4/'verification/INVALIDATED_ATTEMPT_MANIFEST.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(invalid[0]),lineterminator='\n');w.writeheader();w.writerows(invalid)
print('valid',len(rows),'invalidated_files',len(invalid))
