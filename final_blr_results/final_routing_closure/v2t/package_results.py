"""Build and verify the local v2t routing supplement without touching older runs."""

from __future__ import annotations

import csv
import hashlib
import json
import platform
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
REPRO = BASE / "reproducibility"
ARCHIVE = BASE / "archive" / "routing_v2t.zip"
SOURCE = [
    ROOT / "matcher/edge_capacity_da.py",
    ROOT / "router/api/routes.py",
    ROOT / "tests/test_edge_capacity_da_v2t.py",
    ROOT / "final_blr_results/ieee_paper_evidence/ROUTING_VALIDATION_SUPPLEMENT.md",
    ROOT / "data/processed/evaluations/routing_snapshot.graphml",
    ROOT / "results/stations_v2.csv",
]


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def build() -> None:
    REPRO.mkdir(exist_ok=True)
    ARCHIVE.parent.mkdir(exist_ok=True)
    (REPRO / "environment.md").write_text(
        "# v2t environment\n\n"
        f"Python {platform.python_version()} ({platform.platform()}); CPU-only routing. "
        "Git source/protocol identity is in the manifest and final handoff. "
        "Exact installed package versions can be inspected with `python -m pip freeze`; "
        "the active environment is not vendored.\n"
    )
    files = sorted(
        p for p in BASE.rglob("*")
        if p.is_file()
        and not p.is_relative_to(ARCHIVE.parent)
        and p.name not in {"artifact_manifest.json", "checksums.csv", "archive_verification.json"}
        and "__pycache__" not in p.parts
        and not p.name.endswith(".pyc")
    )
    rows = []
    for p in files + SOURCE:
        if not p.exists():
            raise FileNotFoundError(p)
        rows.append({"path": str(p.relative_to(ROOT)), "bytes": p.stat().st_size, "sha256": digest(p),
                     "archive_member": p in files or p in SOURCE[:4]})
    (REPRO / "artifact_manifest.json").write_text(json.dumps({
        "protocol_commit": "d85e81c9055f95fa5b900c29e50124d1c985c963",
        "records": rows,
        "note": "Graph and stations are hashed but omitted from the portable ZIP; historical source data must be supplied separately.",
    }, indent=2) + "\n")
    with (REPRO / "checksums.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["path", "bytes", "sha256", "archive_member"], lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    members = sorted(set(files + SOURCE[:4] + [REPRO / "artifact_manifest.json", REPRO / "checksums.csv", REPRO / "environment.md"]))
    temp = ARCHIVE.with_suffix(".zip.tmp")
    with zipfile.ZipFile(temp, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for p in members:
            z.write(p, str(p.relative_to(ROOT)))
    temp.replace(ARCHIVE)
    with zipfile.ZipFile(ARCHIVE) as z:
        bad = z.testzip()
        if bad:
            raise RuntimeError(f"ZIP CRC failure: {bad}")
        for p in members:
            member = str(p.relative_to(ROOT))
            if hashlib.sha256(z.read(member)).hexdigest() != digest(p):
                raise RuntimeError(f"ZIP member mismatch: {member}")
    report = {"archive": str(ARCHIVE), "bytes": ARCHIVE.stat().st_size,
              "sha256": digest(ARCHIVE), "members": len(members), "crc": "PASS", "member_sha256": "PASS"}
    (REPRO / "archive_verification.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    build()
