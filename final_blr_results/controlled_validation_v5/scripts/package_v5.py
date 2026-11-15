"""Create and verify a checksum-indexed V5 archive; omit restart-only partials."""
import csv
import hashlib
import json
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
V5=ROOT/"final_blr_results/controlled_validation_v5"
ZIP=V5/"archives/ST_PIGNN_CONTROLLED_VALIDATION_V5.zip"


def digest(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(4*1024*1024),b""):h.update(b)
    return h.hexdigest()


def main():
    assert (V5/"FINAL_SCIENTIFIC_VERDICT.md").exists()
    assert (V5/"verification/FINAL_VERIFICATION.md").exists()
    assert (V5/"metrics/NEW_TEST_SCORES.csv").exists()
    files=[]
    for p in V5.rglob("*"):
        if not p.is_file() or "archives" in p.relative_to(V5).parts or p.name=="partial.pt" or "__pycache__" in p.parts:
            continue
        if p.name in ("CHECKSUMS.csv", "ZIP_VERIFICATION.json"):
            continue
        files.append(p)
    files.sort()
    manifest=V5/"verification/CHECKSUMS.csv"
    manifest.parent.mkdir(exist_ok=True)
    with manifest.open("w",newline="") as f:
        w=csv.writer(f);w.writerow(("relative_path","bytes","sha256"))
        for p in files:w.writerow((str(p.relative_to(V5)),p.stat().st_size,digest(p)))
    ZIP.parent.mkdir(exist_ok=True)
    tmp=ZIP.with_suffix(".tmp")
    with zipfile.ZipFile(tmp,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
        for p in files+[manifest]:z.write(p,arcname=str(p.relative_to(V5)))
    tmp.replace(ZIP)
    expected={r["relative_path"]:r["sha256"] for r in csv.DictReader(manifest.open())}
    with zipfile.ZipFile(ZIP) as z:
        assert z.testzip() is None
        assert set(z.namelist())==set(expected)|{"verification/CHECKSUMS.csv"}
        for name,h in expected.items():assert hashlib.sha256(z.read(name)).hexdigest()==h,name
    receipt=dict(archive_absolute_path=str(ZIP),bytes=ZIP.stat().st_size,sha256=digest(ZIP),
                 members=len(expected)+1,member_hashes_verified=len(expected),crc="PASS",
                 excluded="restart-only partial.pt, archive itself and Python caches; historical V3/V4 datasets/checkpoints remain external source dependencies")
    (V5/"archives/ZIP_VERIFICATION.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(json.dumps(receipt,indent=2))


if __name__=="__main__":main()
