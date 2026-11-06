"""Create separate checksum-verified v2p method-development archive."""
import csv
import hashlib
import json
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
ARCH=OUT/"research_results_v2p_rgdr.zip"
EXCLUDE={"research_results_v2p_rgdr.zip","v2p_manifest.json","v2p_checksums.csv","v2p_archive_verification.json"}
SOURCES=[ROOT/"src/stpignn/rgdr.py",ROOT/"src/stpignn/physics_v2.py",ROOT/"tests/test_rgdr.py",
         ROOT/"configs/data_v2.yaml",ROOT/"final_blr_results/baselines/v2m/data/data_v2m_arrays.npz"]

def digest(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(4*1024*1024),b""):h.update(b)
    return h.hexdigest()

def main():
    if ARCH.exists():raise FileExistsError("preserve existing v2p archive")
    files=sorted(p for p in OUT.rglob("*") if p.is_file() and p.name not in EXCLUDE and "__pycache__" not in p.parts)
    rows=[dict(role="source",path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=digest(p)) for p in SOURCES]
    rows += [dict(role="v2p_output",path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=digest(p)) for p in files]
    with (OUT/"v2p_checksums.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator="\n");w.writeheader();w.writerows(rows)
    manifest=dict(stage="method implementation and train/validation mask diagnostics only",source_branch="research/bengaluru-v2o-v2p",
                  dataset_sha256=rows[-len(files)-1]["sha256"],training_runs=0,validation_forecast_metrics=None,
                  test_access=False,novelty="NOT ESTABLISHED",artifacts=rows)
    (OUT/"v2p_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    included=[p for p in files if p.name!="build_v2p_archive.py"]+[OUT/"build_v2p_archive.py",OUT/"v2p_checksums.csv",OUT/"v2p_manifest.json"]
    included += SOURCES[:4]  # small code/config; data array is identified by SHA only
    with zipfile.ZipFile(ARCH,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in included:z.write(p,p.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(ARCH) as z:
        assert z.testzip() is None
        for p in included:assert hashlib.sha256(z.read(p.relative_to(ROOT).as_posix())).hexdigest()==digest(p)
    v=dict(path=ARCH.relative_to(ROOT).as_posix(),bytes=ARCH.stat().st_size,sha256=digest(ARCH),
           members=len(included),crc_and_member_sha256="PASS")
    (OUT/"v2p_archive_verification.json").write_text(json.dumps(v,indent=2)+"\n")
    print(json.dumps(v))

if __name__=="__main__":main()
