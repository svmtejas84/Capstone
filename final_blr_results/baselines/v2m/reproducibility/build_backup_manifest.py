"""Read-only inventory and Git-remote verification for the v2m backup gate.

No copying, uploading, training, or mutation of historical research artifacts.
"""
from __future__ import annotations

import csv
import datetime as dt
import hashlib
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "final_blr_results/baselines/v2m"
BRANCH = "refs/heads/audit/canonical-notebook-20261023"


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def sha_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def committed_blobs(index):
    oids = list(dict.fromkeys(index.values()))
    proc = subprocess.Popen(["git", "cat-file", "--batch"], cwd=ROOT,
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    proc.stdin.write(b"".join(oid.encode() + b"\n" for oid in oids))
    proc.stdin.close()
    blobs = {}
    for requested in oids:
        header = proc.stdout.readline().decode().strip().split()
        if len(header) != 3 or header[0] != requested or header[1] != "blob":
            raise RuntimeError(f"Unexpected Git object header for {requested}: {header}")
        length = int(header[2]); digest = hashlib.sha256(); remaining = length
        while remaining:
            chunk = proc.stdout.read(min(4 * 1024 * 1024, remaining))
            if not chunk: raise EOFError(requested)
            digest.update(chunk); remaining -= len(chunk)
        if proc.stdout.read(1) != b"\n": raise RuntimeError("Missing Git batch separator")
        blobs[requested] = (length, digest.hexdigest())
    if proc.wait() != 0: raise RuntimeError(proc.stderr.read().decode())
    return blobs


def main():
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    head = git("rev-parse", "HEAD").decode().strip()
    remote = git("ls-remote", "origin", BRANCH).decode().split()[0]
    remote_matches = head == remote
    entries = git("ls-files", "--stage", "-z").split(b"\0")
    index = {}
    for item in entries:
        if item:
            prefix, path = item.split(b"\t", 1)
            index[path.decode()] = prefix.decode().split()[1]
    blobs = committed_blobs(index)
    old = ROOT / "final_blr_results/archive/archive_integrity.csv"
    with old.open(newline="") as stream:
        known = {row["path"] for row in csv.DictReader(stream)}
    known.update(index)
    known.update(p.relative_to(ROOT).as_posix() for p in (ROOT / "final_blr_results").rglob("*")
                 if p.is_file() and not p.is_relative_to(OUT))
    # Compiled Python caches are regenerable execution debris, not research source or output.
    paths = sorted(rel for rel in known if not rel.endswith(".pyc") and "__pycache__/" not in rel)
    rows = []
    for rel in paths:
        path = ROOT / rel
        if not path.is_file():
            rows.append(dict(source_path=rel, source_exists=False, source_sha256="", source_size_bytes="",
                             destination="", destination_exists=False, destination_sha256="", destination_size_bytes="",
                             verification_timestamp_utc=now, status="SOURCE FILE MISSING", note="Listed in prior inventory but absent now"))
            continue
        size = path.stat().st_size
        digest = sha_file(path)
        oid = index.get(rel)
        committed = oid is not None and blobs[oid] == (size, digest)
        verified = bool(committed and remote_matches)
        rows.append(dict(source_path=rel, source_exists=True, source_sha256=digest, source_size_bytes=size,
                         destination=f"git:origin@{remote}:{rel}" if verified else "",
                         destination_exists=verified, destination_sha256=blobs[oid][1] if verified else "",
                         destination_size_bytes=blobs[oid][0] if verified else "",
                         verification_timestamp_utc=now,
                         status="VERIFIED INDEPENDENT BACKUP" if verified else "LOCAL COPY ONLY",
                         note="Remote Git commit matches and committed blob SHA-256 equals worktree" if verified else
                              "No verified independent copy of current bytes; Git is not used for large ignored caches"))
    for logical, note in (("not_saved:v2j_corrected_neural_checkpoints", "v2j benchmark saved predictions, not model checkpoints"),
                          ("not_saved:legacy_p0_paired_baseline_predictions", "legacy paired baseline artifacts unavailable"),
                          ("not_saved:w4_sensor_density_pair_predictions", "W4 per-pair predictions unavailable")):
        rows.append(dict(source_path=logical, source_exists=False, source_sha256="", source_size_bytes="",
                         destination="", destination_exists=False, destination_sha256="", destination_size_bytes="",
                         verification_timestamp_utc=now, status="SOURCE FILE MISSING", note=note))
    rows.append(dict(source_path="scope:complete_existing_research_archive", source_exists=False, source_sha256="", source_size_bytes="",
                     destination="", destination_exists=False, destination_sha256="", destination_size_bytes="",
                     verification_timestamp_utc=now, status="BACKUP BLOCKED",
                     note="No already-authorized independent destination for ignored/local-only research artifacts"))
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "backup_manifest.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    count = {status: sum(r["status"] == status for r in rows) for status in
             ("VERIFIED INDEPENDENT BACKUP", "LOCAL COPY ONLY", "SOURCE FILE MISSING", "BACKUP BLOCKED")}
    print({"head": head, "remote_matches": remote_matches, "files": len(paths), "status_counts": count,
           "local_only_bytes": sum(int(r["source_size_bytes"]) for r in rows if r["status"] == "LOCAL COPY ONLY")})


if __name__ == "__main__":
    main()
