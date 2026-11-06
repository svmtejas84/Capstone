from __future__ import annotations
import csv,hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/"final_blr_results/final_research_v2r"
def sha_bytes(b):return hashlib.sha256(b).hexdigest()
def sha_file(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for b in iter(lambda:f.read(4*1024*1024),b""):h.update(b)
 return h.hexdigest()
def main():
 v=json.loads((BASE/"archive/archive_verification.json").read_text())
 for key,item in v.items():
  p=ROOT/item["zip"]
  if p.stat().st_size!=item["bytes"] or sha_file(p)!=item["sha256"]:raise RuntimeError(f"archive digest mismatch: {p}")
  with zipfile.ZipFile(p) as z:
   if z.testzip() is not None:raise RuntimeError(f"CRC failure: {p}")
   with (ROOT/item["member_manifest"]).open(newline="") as f:
    for row in csv.DictReader(f):
     b=z.read(row["member"])
     if len(b)!=int(row["bytes"]) or sha_bytes(b)!=row["sha256"]:raise RuntimeError(f"member mismatch: {row['member']}")
 print("CITYWIDE_AND_RGDR_ARCHIVES: SHA256/CRC/PER-MEMBER SHA256 PASS")
 with (BASE/"reproducibility/artifact_checksums.csv").open(newline="") as f:
  for row in csv.DictReader(f):
   p=ROOT/row["path"]
   if p.stat().st_size!=int(row["bytes"]) or sha_file(p)!=row["sha256"]:raise RuntimeError(f"artifact mismatch: {row['path']}")
 print("V2R_ARTIFACT_CHECKSUMS: PASS")
if __name__=="__main__":main()
