"""Inventory and ZIP the v2o extension, with per-file verification."""
import csv
import hashlib
import json
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
ARCH=OUT/"research_results_v2o.zip"
INPUTS=[ROOT/"final_blr_results/baselines/v2m/data/data_v2m_arrays.npz",
        ROOT/"data/graphs/bangalore_utm_nodes.parquet",
        ROOT/"data/processed/graph/nodes_elevation_true.parquet"]
EXCLUDE={"research_results_v2o.zip","v2o_artifact_manifest.json","v2o_checksums.csv","v2o_archive_verification.json"}

def digest(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(4*1024*1024),b""):h.update(b)
    return h.hexdigest()

def main():
    if ARCH.exists():raise FileExistsError("v2o archive already exists; preserve it")
    files=sorted(p for p in OUT.rglob("*") if p.is_file() and p.name not in EXCLUDE and "__pycache__" not in p.parts)
    rows=[dict(role="source",path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=digest(p)) for p in INPUTS]
    rows += [dict(role="v2o_output",path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=digest(p)) for p in files]
    with (OUT/"v2o_checksums.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator="\n");w.writeheader();w.writerows(rows)
    manifest=dict(protocol_commit="27ba8c7",method="retrospective IDW power 2",snapshots=3,
                  road_nodes=154902,output_rows=464706,source_commit_before_v2o="c50f58f8107ddd485b8f82a21df13c2f7c2436d8",
                  missing=["corrected ST-PIGNN road checkpoint","complete road pollutant histories","independent road observations","calibrated road uncertainty"],artifacts=rows)
    (OUT/"v2o_artifact_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    archive_files=files+[OUT/"v2o_checksums.csv",OUT/"v2o_artifact_manifest.json"]
    with zipfile.ZipFile(ARCH,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
        for p in archive_files:z.write(p,p.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(ARCH) as z:
        assert z.testzip() is None
        for p in archive_files:
            name=p.relative_to(ROOT).as_posix()
            assert hashlib.sha256(z.read(name)).hexdigest()==digest(p)
    verification=dict(path=ARCH.relative_to(ROOT).as_posix(),bytes=ARCH.stat().st_size,sha256=digest(ARCH),
                      members=len(archive_files),crc_and_member_sha256="PASS")
    (OUT/"v2o_archive_verification.json").write_text(json.dumps(verification,indent=2)+"\n")
    print(json.dumps(verification))

if __name__=="__main__":main()
