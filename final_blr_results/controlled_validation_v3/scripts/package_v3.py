"""Create a checksum-verified local v3 export with selected checkpoints."""
import csv
import hashlib
import json
import subprocess
import zipfile
from pathlib import Path
from final_blr_results.controlled_validation_v3.scripts.train_controls import V3,ARR,hash_file

ARCHIVE="ST_PIGNN_CONTROLLED_VALIDATION_V3.zip"


def write_csv(path,rows,fields):
    path.parent.mkdir(exist_ok=True)
    with path.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)


def main():
    assert (V3/"FINAL_SCIENTIFIC_VERDICT.md").exists()
    assert (V3/"metrics/matched_controls.csv").exists()
    assert (V3/"metrics/baselines.csv").exists()
    assert (V3/"statistical_analysis/primary_contrasts.csv").exists()
    dst=V3/"archives"/ARCHIVE;dst.parent.mkdir(exist_ok=True)
    repro=V3/"verification";repro.mkdir(exist_ok=True)
    skip={"verification/CHECKSUMS.csv","verification/ARTIFACT_MANIFEST.json",
          "verification/local_checkpoint_manifest.csv"}
    checkpoint=[];included=[]
    for p in sorted(V3.rglob("*")):
        if not p.is_file():continue
        rel=p.relative_to(V3).as_posix()
        if rel.startswith("archives/") or rel in skip or "__pycache__" in p.parts or p.suffix==".pyc":continue
        if p.name=="partial.pt":
            checkpoint.append(dict(path=str(p.resolve()),size_bytes=p.stat().st_size,sha256=hash_file(p)))
            continue
        included.append(dict(path=rel,size_bytes=p.stat().st_size,sha256=hash_file(p)))
    write_csv(repro/"local_checkpoint_manifest.csv",checkpoint,["path","size_bytes","sha256"])
    write_csv(repro/"CHECKSUMS.csv",included,["path","size_bytes","sha256"])
    commit=subprocess.check_output(["git","rev-parse","HEAD"],text=True,cwd=V3.parents[1]).strip()
    manifest=dict(source_commit=commit,branch="research/controlled-validation-v3",
                  protocol_sha256=hash_file(V3/"PROTOCOL_FREEZE.md"),
                  repaired_array_sha256=hash_file(ARR),
                  included_file_count=len(included)+3,
                  excluded_partial_checkpoint_count=len(checkpoint),
                  excluded_partial_checkpoint_bytes=sum(x["size_bytes"] for x in checkpoint),
                  checkpoint_policy="best.pt selected checkpoints included; restart-only partial.pt tensors excluded with verified local paths and hashes",
                  exposed_historical_test=True,independent_temporal_validation=False)
    (repro/"ARTIFACT_MANIFEST.json").write_text(json.dumps(manifest,indent=2)+"\n")
    members=included+[
        dict(path="verification/local_checkpoint_manifest.csv"),
        dict(path="verification/CHECKSUMS.csv"),
        dict(path="verification/ARTIFACT_MANIFEST.json")]
    tmp=dst.with_suffix(".zip.tmp")
    with zipfile.ZipFile(tmp,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for row in members:
            z.write(V3/row["path"],arcname=row["path"])
    with zipfile.ZipFile(tmp) as z:
        assert z.testzip() is None
        assert set(z.namelist())=={r["path"] for r in members}
        for row in included:
            assert hashlib.sha256(z.read(row["path"])).hexdigest()==row["sha256"]
    tmp.replace(dst)
    report=dict(path=str(dst.resolve()),size_bytes=dst.stat().st_size,sha256=hash_file(dst),
                member_count=len(members),excluded_partial_checkpoint_count=len(checkpoint),
                crc_and_member_sha256="PASS")
    (dst.parent/"ARCHIVE_VERIFICATION.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))


if __name__=="__main__":main()
