from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import hashlib,csv,json
base=Path('/home/jupyter-1nt23cb058/Capstone')
package=base/'final_blr_results/ieee_paper_evidence';handover=base/'final_blr_results/second_city_handover'
archive=base/'final_blr_results/ieee_paper_evidence_and_second_city_handover.zip'
# Add an independent checksum ledger for the handover directory; excludes itself to avoid recursion.
checks=[]
for p in sorted(handover.rglob('*')):
 if p.is_file() and p.name!='CHECKSUMS.csv':checks.append([p.relative_to(handover).as_posix(),hashlib.sha256(p.read_bytes()).hexdigest(),p.stat().st_size])
with (handover/'CHECKSUMS.csv').open('w',newline='') as f:
 w=csv.writer(f,lineterminator='\n');w.writerow(['relative_path','sha256','bytes']);w.writerows(checks)
files=[]
for root,prefix in [(package,'ieee_paper_evidence'),(handover,'second_city_handover')]:
 for p in sorted(root.rglob('*')):
  if p.is_file():files.append((p,f'{prefix}/{p.relative_to(root).as_posix()}'))
with ZipFile(archive,'w',ZIP_DEFLATED,compresslevel=6) as z:
 for p,name in files:z.write(p,name)
with ZipFile(archive) as z:
 bad=z.testzip()
 if bad:raise RuntimeError(f'ZIP CRC failed: {bad}')
 names=set(z.namelist())
 expected={name for _,name in files}
 if names!=expected:raise RuntimeError('ZIP member inventory mismatch')
 verified=0
 for p,name in files:
  got=hashlib.sha256(z.read(name)).hexdigest();want=hashlib.sha256(p.read_bytes()).hexdigest()
  if got!=want:raise RuntimeError(f'member checksum mismatch: {name}')
  verified+=1
manifest={'archive_path':str(archive),'bytes':archive.stat().st_size,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'members':verified,'zip_crc':'passed','member_sha256':'passed','included_roots':['final_blr_results/ieee_paper_evidence/','final_blr_results/second_city_handover/']}
(base/'final_blr_results/ieee_paper_evidence_archive_verification.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(manifest,indent=2))
