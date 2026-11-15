"""Create and verify lossless V4 evidence ZIP, excluding restart intermediates."""
import csv,hashlib,json,zipfile
from pathlib import Path
from final_blr_results.controlled_validation_v4_review_closure.scripts.train_sensitivity import V4

def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
archive=V4/'archives/ST_PIGNN_V4_SCIENTIFIC_REVIEW_CLOSURE.zip'
archive.parent.mkdir(exist_ok=True)
manifest=V4/'verification/ARTIFACT_MANIFEST.json'
manifest.write_text(json.dumps(dict(research_round='V4 review closure',protocol_sha256=sha(V4/'PROTOCOL_FREEZE.md'),amendment='PROTOCOL_AMENDMENT_01.md',source_array_sha256='bd08d733f924387da82e758d1060703dfcdd121f360b7e8765189d8b7446e202',selected_checkpoint_count=30,prediction_array_count=36,invalidated_pretest_shuffle_attempts=4,exposed_test=True,excluded=['partial.pt restart files','pre-amendment invalidated checkpoint tensors','historical V3 datasets/checkpoints']),indent=2)+'\n')
paths=[]
for p in V4.rglob('*'):
 if not p.is_file():continue
 rel=p.relative_to(V4)
 if 'archives' in rel.parts or '__pycache__' in rel.parts:continue
 if p.name in ('partial.pt','CHECKSUMS.csv','ZIP_VERIFICATION.json'):continue
 if 'invalidated_pre_amendment' in rel.parts and p.name=='best.pt':continue
 paths.append(p)
paths.sort(key=lambda x:str(x.relative_to(V4)))
rows=[dict(path=str(p.relative_to(V4)),sha256=sha(p),bytes=p.stat().st_size) for p in paths]
checks=V4/'verification/CHECKSUMS.csv'
with checks.open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=['path','sha256','bytes'],lineterminator='\n');w.writeheader();w.writerows(rows)
paths.append(checks)
tmp=archive.with_suffix('.tmp')
with zipfile.ZipFile(tmp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
 for p in paths:z.write(p,arcname=str(p.relative_to(V4)))
tmp.replace(archive)
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 expected={r['path']:r for r in rows}
 assert set(z.namelist())==set(expected)|{'verification/CHECKSUMS.csv'}
 for name,r in expected.items():
  data=z.read(name)
  assert hashlib.sha256(data).hexdigest()==r['sha256'] and len(data)==r['bytes'],name
receipt=dict(path=str(archive.resolve()),bytes=archive.stat().st_size,sha256=sha(archive),members=len(paths),verified_member_hashes=len(rows),crc='PASS',excluded_restart_intermediates=True)
(V4/'verification/ZIP_VERIFICATION.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
