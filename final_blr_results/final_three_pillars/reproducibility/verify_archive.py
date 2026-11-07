"""Verify ZIP CRC, per-file SHA-256, and archive checksum metadata."""
from pathlib import Path
import csv, hashlib, json, zipfile

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "archive" / "final_three_pillars_supplement.zip"
REP = ROOT / "reproducibility"

def sha(data):
    return hashlib.sha256(data).hexdigest()

with (REP / "CHECKSUMS.csv").open(newline="") as f:
    rows = list(csv.DictReader(f))
with zipfile.ZipFile(ARCHIVE) as z:
    assert z.testzip() is None
    names = set(z.namelist())
    for row in rows:
        member = "final_three_pillars/" + row["path"]
        assert member in names, member
        data = z.read(member)
        assert len(data) == int(row["size_bytes"]), member
        assert sha(data) == row["sha256"], member
archive_hash = sha(ARCHIVE.read_bytes())
metadata = json.loads((REP / "ARCHIVE_VERIFICATION.json").read_text())
assert metadata["sha256"] == archive_hash
assert metadata["size_bytes"] == ARCHIVE.stat().st_size
assert metadata["verified_source_members"] == len(rows)
print(f"PASS: {len(rows)} file hashes, ZIP CRC, archive size/hash")
