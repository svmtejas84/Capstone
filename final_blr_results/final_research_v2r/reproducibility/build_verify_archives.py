from __future__ import annotations
import csv,hashlib,json,zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/"final_blr_results/final_research_v2r"
ARCH=BASE/"archive";ARCH.mkdir(parents=True,exist_ok=True)
REPRO=BASE/"reproducibility"

def digest(path):
 h=hashlib.sha256()
 with path.open("rb") as f:
  for b in iter(lambda:f.read(4*1024*1024),b""):h.update(b)
 return h.hexdigest()

def members_for(kind):
 roots=[BASE/"EXPERIMENT_PROTOCOL.md",BASE/"FINAL_RESEARCH_HANDOFF.md",BASE/kind]
 if kind=="citywide":roots.append(REPRO/"REPRODUCIBILITY.md")
 files=[]
 for p in roots:
  if p.is_file():files.append(p)
  else:
   for f in p.rglob("*"):
    if not f.is_file() or "__pycache__" in f.parts or f.suffix==".pyc":continue
    if f.name.endswith(".tmp") or f.name in {"supervisor.lock","supervisor.pid"}:continue
    files.append(f)
 return sorted(set(files))

def build(kind):
 path=ARCH/f"{kind}_v2r.zip"; files=members_for(kind)
 with zipfile.ZipFile(path,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for f in files:z.write(f,f.relative_to(ROOT).as_posix())
 with zipfile.ZipFile(path) as z:
  bad=z.testzip()
  if bad:raise RuntimeError(f"CRC failed {path}: {bad}")
  rows=[]
  for name in z.namelist():
   raw=z.read(name);rows.append({"member":name,"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest()})
   src=ROOT/name
   if src.read_bytes()!=raw:raise RuntimeError(f"member differs from source {name}")
 csvpath=ARCH/f"{kind}_v2r_members.csv"
 with csvpath.open("w",newline="") as f:
  w=csv.DictWriter(f,fieldnames=["member","bytes","sha256"]);w.writeheader();w.writerows(rows)
 return {"zip":path.relative_to(ROOT).as_posix(),"bytes":path.stat().st_size,"sha256":digest(path),"members":len(rows),"member_manifest":csvpath.relative_to(ROOT).as_posix(),"crc":"PASS","per_member_sha256":"PASS"}

def main():
 result={"citywide":build("citywide"),"rgdr":build("rgdr")}
 (ARCH/"archive_verification.json").write_text(json.dumps(result,indent=2)+"\n")
 # Hash all v2r files, excluding checksum/index files themselves to avoid a
 # recursive digest. Include both zip archives and their per-member manifests.
 rows=[]
 for p in sorted(BASE.rglob("*")):
  if not p.is_file() or "__pycache__" in p.parts or p.suffix==".pyc" or p.name in {"supervisor.lock","supervisor.pid"} or p.name.endswith(".tmp"):continue
  if p.name in {"artifact_checksums.csv","artifact_manifest.json"}:continue
  rows.append({"path":p.relative_to(ROOT).as_posix(),"bytes":p.stat().st_size,"sha256":digest(p)})
 with (REPRO/"artifact_checksums.csv").open("w",newline="") as f:
  w=csv.DictWriter(f,fieldnames=["path","bytes","sha256"]);w.writeheader();w.writerows(rows)
 import subprocess
 try:
  commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
  branch=subprocess.check_output(["git","branch","--show-current"],cwd=ROOT,text=True).strip()
 except Exception:commit="UNKNOWN";branch="UNKNOWN"
 source_paths=["results/data_v2j_arrays.npz","data/graphs/bangalore_utm_nodes.parquet","data/processed/graph/nodes_elevation_true.parquet","notebooks/production/evaluated_wind_advection.ipynb","configs/data_v2.yaml","configs/loso_v2.yaml","src/stpignn/data_v2.py","src/stpignn/models_v2.py","src/stpignn/physics_v2.py","src/stpignn/station_graph.py","src/stpignn/rgdr.py","src/stpignn/rgdr_continuous.py","tests/test_rgdr_continuous_v2r.py"]
 source_inputs=[]
 for rel in source_paths:
  p=ROOT/rel
  source_inputs.append({"path":rel,"available":p.is_file(),"bytes":p.stat().st_size if p.is_file() else None,"sha256":digest(p) if p.is_file() else None})
 manifest={"round":"Bengaluru v2r","branch":branch,"source_commit_before_archive_manifest":commit,"artifacts_indexed":len(rows),"checksums_csv":"final_blr_results/final_research_v2r/reproducibility/artifact_checksums.csv","self_hashes_excluded":["artifact_manifest.json","artifact_checksums.csv"],"source_inputs":source_inputs,"archives":result,"citywide":{"nodes":154902,"target_timestamps":3,"status":"experimental neural-assisted estimates; no independent roadside accuracy"},"rgdr":{"implementation":"continuous V2 passed focused tests","training":"not run; frozen feasibility gate failed","status":"predictive effect not evaluated"}}
 (REPRO/"artifact_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
 print(json.dumps({"archives":result,"checksummed_files":len(rows)},indent=2))

if __name__=="__main__":main()
