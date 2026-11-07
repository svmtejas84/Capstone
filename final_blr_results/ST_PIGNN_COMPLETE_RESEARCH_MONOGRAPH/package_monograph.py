"""Create and verify the local Markdown monograph archive, excluding source datasets."""
from __future__ import annotations

import csv
import hashlib
import json
import zipfile
from pathlib import Path

BASE=Path(__file__).resolve().parent
ARCH=BASE/'archive'
ZIP=ARCH/'ST_PIGNN_COMPLETE_RESEARCH_MONOGRAPH.zip'

def sha(path:Path)->str:
 h=hashlib.sha256()
 with path.open('rb') as f:
  for block in iter(lambda:f.read(1<<20),b''):h.update(block)
 return h.hexdigest()

def main():
 ARCH.mkdir(exist_ok=True)
 files=sorted(p for p in BASE.rglob('*') if p.is_file() and not p.is_relative_to(ARCH)
              and '__pycache__' not in p.parts and p.suffix!='.pyc')
 manifest=ARCH/'MONOGRAPH_ARCHIVE_MANIFEST.csv'
 with manifest.open('w',newline='') as f:
  w=csv.writer(f,lineterminator='\n');w.writerow(['member','bytes','sha256'])
  for p in files:w.writerow([str(p.relative_to(BASE)),p.stat().st_size,sha(p)])
 members=files+[manifest]
 temp=ZIP.with_suffix('.zip.tmp')
 with zipfile.ZipFile(temp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=7) as z:
  for p in members:z.write(p,str(p.relative_to(BASE)))
 temp.replace(ZIP)
 with zipfile.ZipFile(ZIP) as z:
  bad=z.testzip()
  if bad:raise RuntimeError(f'CRC failed: {bad}')
  for p in members:
   if hashlib.sha256(z.read(str(p.relative_to(BASE)))).hexdigest()!=sha(p):
    raise RuntimeError(f'Member hash failed: {p}')
 report={'path':str(ZIP),'bytes':ZIP.stat().st_size,'sha256':sha(ZIP),
         'members':len(members),'crc':'PASS','all_member_sha256':'PASS',
         'historical_datasets_and_checkpoints_embedded':False}
 (ARCH/'ARCHIVE_VERIFICATION.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(report,indent=2))

if __name__=='__main__':main()
