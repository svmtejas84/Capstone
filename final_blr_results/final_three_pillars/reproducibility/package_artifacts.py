"""Build deterministic source manifests and a checksum-verifiable ZIP export."""
from pathlib import Path
import csv, hashlib, json, zipfile

ROOT = Path(__file__).resolve().parents[1]
REP = ROOT / "reproducibility"
ARCHIVE = ROOT / "archive" / "final_three_pillars_supplement.zip"
EXCLUDE_PARTS = {"__pycache__", ".mplconfig"}
EXCLUDE_FILES = {"artifact_manifest.json", "CHECKSUMS.csv", "ARCHIVE_VERIFICATION.json"}

def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def files_for_package():
    out = []
    for p in ROOT.rglob("*"):
        if not p.is_file() or p == ARCHIVE or any(part in EXCLUDE_PARTS for part in p.parts):
            continue
        if p.name in EXCLUDE_FILES or p.name.endswith(".pyc"):
            continue
        if "archive" in p.relative_to(ROOT).parts:
            continue
        out.append(p)
    return sorted(out)

files = files_for_package()
rows = [{"path": p.relative_to(ROOT).as_posix(), "size_bytes": p.stat().st_size, "sha256": digest(p)} for p in files]
(REP / "artifact_manifest.json").write_text(json.dumps({
    "package": "final_three_pillars",
    "created_utc_date": "2026-11-07",
    "source_commit_before_final_package": "52c119c320b014a285f399e8de9420d364d17614",
    "files": rows,
    "scope_note": "No data/checkpoint archives; v2c/v2r IG tensors are included as derived outputs. Manifest excludes itself and the ZIP to avoid recursive hashes."
}, indent=2) + "\n")
with (REP / "CHECKSUMS.csv").open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["path", "size_bytes", "sha256"])
    w.writeheader(); w.writerows(rows)

ARCHIVE.parent.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(ARCHIVE, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for p in files + [REP / "artifact_manifest.json", REP / "CHECKSUMS.csv"]:
        z.write(p, (Path("final_three_pillars") / p.relative_to(ROOT)).as_posix())

with zipfile.ZipFile(ARCHIVE) as z:
    bad = z.testzip()
    assert bad is None, f"ZIP CRC failed at {bad}"
    for row in rows:
        member = "final_three_pillars/" + row["path"]
        data = z.read(member)
        assert hashlib.sha256(data).hexdigest() == row["sha256"], member
        assert len(data) == row["size_bytes"], member
archive_hash = digest(ARCHIVE)
verification = {
    "archive_path": str(ARCHIVE.resolve()),
    "size_bytes": ARCHIVE.stat().st_size,
    "sha256": archive_hash,
    "verified_source_members": len(rows),
    "zip_crc": "PASS",
    "per_file_sha256": "PASS",
    "included_manifest_and_checksum_list": True,
    "archive_excludes": ["__pycache__", ".mplconfig", "model checkpoints", "raw data"]
}
(REP / "ARCHIVE_VERIFICATION.json").write_text(json.dumps(verification, indent=2) + "\n")
print(json.dumps(verification, indent=2))
