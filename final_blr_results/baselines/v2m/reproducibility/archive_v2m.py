"""Create and independently verify a local ZIP64 supplementary results archive."""
from __future__ import annotations

import csv
import datetime as dt
import hashlib
import json
import zipfile
from pathlib import Path

from src.stpignn.paths import REPO_ROOT

BASE=REPO_ROOT/"final_blr_results/baselines/v2m"
OUT=BASE/"reproducibility"
ZIP=OUT/"research_results_v2m.zip"
SIDE=OUT/"RESEARCH_RESULTS_v2m_SHA256.txt"
MANIFEST=OUT/"RESEARCH_RESULTS_v2m_MANIFEST.csv"


def sha(path):
    d=hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda:f.read(4*1024*1024),b""):d.update(block)
    return d.hexdigest()


def main():
    if ZIP.exists():raise FileExistsError("Supplementary ZIP already exists; never overwrite it")
    cells=[]
    for model in ("mlp","tcn"):
        for h in (1,3,6,12,24):
            for seed in (11,23,37,51,79):
                cell=BASE/model/f"h{h}"/f"seed{seed}"
                marker=json.loads((cell/"COMPLETE.json").read_text())
                for key in ("checkpoint","predictions","metrics"):
                    p=cell/marker[key]["path"]
                    if sha(p)!=marker[key]["sha256"]:raise RuntimeError(f"Invalid cell {p}")
                cells.append(dict(model=model,horizon_hours=h,seed=seed,marker=str((cell/"COMPLETE.json").relative_to(REPO_ROOT))))
    experiment={"round":"v2m","status":"50/50 cells complete; local archive pending external copy",
                "training_source_commits":["e695c6e","dfa84d1","07dd9e2"],
                "evaluation_source_commit":"b78b5f2", "dataset":str((BASE/"data/data_v2m_arrays.npz").relative_to(REPO_ROOT)),
                "dataset_sha256":sha(BASE/"data/data_v2m_arrays.npz"),
                "protocol":str((BASE/"EXPERIMENT_PROTOCOL.md").relative_to(REPO_ROOT)),
                "cells":cells,"supervisor":str((BASE/"runs/all_v2m").relative_to(REPO_ROOT)),
                "historical_baseline_protocol":"v2j centered weather; cross-protocol comparisons only",
                "created_utc":dt.datetime.now(dt.timezone.utc).isoformat()}
    (OUT/"experiment_manifest.json").write_text(json.dumps(experiment,indent=2)+"\n")
    additions=[REPO_ROOT/"src/stpignn/data_v2.py",REPO_ROOT/"scripts/benchmark_v2j.py",REPO_ROOT/"scripts/run_supervised.sh",
               REPO_ROOT/"configs/benchmark_v2g.yaml",REPO_ROOT/"configs/data_v2.yaml"]
    files=[p for p in BASE.rglob("*") if p.is_file() and p not in (ZIP,SIDE,MANIFEST)
           and not any(part in ("__pycache__",".ipynb_checkpoints") for part in p.parts)
           and not p.name.endswith((".tmp",".tmp.json",".tmp.parquet",".tmp.pt"))
           and not p.name in ("supervisor.lock","supervisor.pid","command.nul")]
    files=sorted(set(files+additions),key=lambda p:str(p.relative_to(REPO_ROOT)))
    rows=[]
    with zipfile.ZipFile(ZIP,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
        for p in files:
            rel=str(p.relative_to(REPO_ROOT))
            z.write(p,rel)
            rows.append(dict(source=rel,archive_member=rel,bytes=p.stat().st_size,sha256=sha(p)))
    with MANIFEST.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=["source","archive_member","bytes","sha256"]);w.writeheader();w.writerows(rows)
    with zipfile.ZipFile(ZIP) as z:
        if z.testzip() is not None:raise RuntimeError("ZIP CRC verification failed")
        if set(z.namelist())!={r["archive_member"] for r in rows}:raise RuntimeError("ZIP member mismatch")
        for row in rows:
            d=hashlib.sha256(z.read(row["archive_member"])).hexdigest()
            if d!=row["sha256"]:raise RuntimeError(f"ZIP member SHA mismatch: {row['archive_member']}")
    SIDE.write_text(f"{sha(ZIP)}  {ZIP.name}\n")
    print(json.dumps({"archive":str(ZIP),"bytes":ZIP.stat().st_size,"sha256":sha(ZIP),"members":len(rows),"verified":True}))


if __name__=="__main__":main()
