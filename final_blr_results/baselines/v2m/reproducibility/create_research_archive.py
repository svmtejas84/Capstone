"""Build and verify the v2m pre-training ZIP64 export from the frozen backup list.

The original research files are read only. The ZIP is a local download artifact,
not an independent durable backup until the owner transfers and verifies it.
"""
from __future__ import annotations

import csv
import datetime as dt
import hashlib
import re
import shutil
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "final_blr_results/baselines/v2m"
EXPORT = ROOT / "final_blr_results/research_backup_exports"
ARCHIVE = EXPORT / "research_backup_pretrain_v2m.zip"
MANIFEST = EXPORT / "RESEARCH_BACKUP_MANIFEST.csv"
INSTRUCTIONS = EXPORT / "RESEARCH_BACKUP_INSTRUCTIONS.md"
SHA_FILE = EXPORT / "RESEARCH_BACKUP_SHA256.txt"
SENSITIVE = re.compile(r"(?i)(^|/)(\.aws|\.ssh|\.env|id_rsa|id_ed25519|credentials?|secrets?|tokens?|private[_-]?keys?)(/|\.|$)|\.(pem|key|p12|pfx)$")
TEXT_SECRET = re.compile(rb"(?i)(--(?:api[-_]?key|password|secret|token)(?:=|\x00)|AWS_SECRET_ACCESS_KEY|BEGIN (?:RSA |OPENSSH )?PRIVATE KEY)")


def hash_file(path: Path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main():
    EXPORT.mkdir(parents=True, exist_ok=True)
    partial = ARCHIVE.with_suffix(".partial.zip")
    for output in (ARCHIVE, partial, MANIFEST, INSTRUCTIONS, SHA_FILE):
        if output.exists():
            raise FileExistsError(f"Refusing to overwrite existing export: {output}")
    with (BASE / "backup_manifest.csv").open(newline="") as stream:
        original = [row for row in csv.DictReader(stream) if row["status"] == "LOCAL COPY ONLY"]
    if len(original) != 1110:
        raise AssertionError(f"Expected all 1110 snapshot paths, found {len(original)}")
    free = shutil.disk_usage(EXPORT).free
    total = sum(int(row["source_size_bytes"]) for row in original)
    if free < total * 2 + 2 * 1024**3:
        raise RuntimeError(f"Insufficient free space: {free} for {total} source bytes and ZIP safety margin")
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    rows = []
    for entry in original:
        rel = entry["source_path"]
        path = ROOT / rel
        if not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(ROOT):
            raise RuntimeError(f"Missing, symlinked or escaping source: {rel}")
        if SENSITIVE.search(rel):
            raise RuntimeError(f"Sensitive-path candidate in backup list; review before export: {rel}")
        if path.name in ("supervisor.lock", "supervisor.pid") or path.name.endswith((".tmp", ".part", ".swp", "~")):
            status, reason = "EXCLUDED_TRANSIENT", "stale supervisor lock/PID or temporary file"
        else:
            status, reason = "INCLUDED", ""
        if path.name == "command.nul" and TEXT_SECRET.search(path.read_bytes()):
            raise RuntimeError(f"Potential credential in command metadata; review before export: {rel}")
        current = hash_file(path)
        snapshot_match = int(entry["source_size_bytes"]) == path.stat().st_size and current == entry["source_sha256"]
        rows.append(dict(source_path=rel, source_size_bytes=path.stat().st_size,
                         source_sha256=current, prior_manifest_sha256=entry["source_sha256"],
                         snapshot_match=snapshot_match,
                         archive_member=rel if status == "INCLUDED" else "", archive_status=status,
                         exclusion_reason=reason, source_verified_utc=now))
    included = [row for row in rows if row["archive_status"] == "INCLUDED"]
    drift = [row["source_path"] for row in rows if not row["snapshot_match"]]
    with MANIFEST.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    manifest_bytes = MANIFEST.read_bytes()
    with zipfile.ZipFile(partial, "w", compression=zipfile.ZIP_DEFLATED,
                         compresslevel=1, allowZip64=True, strict_timestamps=False) as archive:
        for index, row in enumerate(included, 1):
            archive.write(ROOT / row["source_path"], arcname=row["archive_member"])
            if index % 100 == 0 or index == len(included):
                print(f"archived {index}/{len(included)}", flush=True)
        archive.writestr("RESEARCH_BACKUP_MANIFEST.csv", manifest_bytes)
    with zipfile.ZipFile(partial, "r", allowZip64=True) as archive:
        expected = {row["archive_member"] for row in included} | {"RESEARCH_BACKUP_MANIFEST.csv"}
        names = archive.namelist()
        if len(names) != len(expected) or set(names) != expected:
            raise AssertionError("ZIP member population differs from manifest")
        if archive.read("RESEARCH_BACKUP_MANIFEST.csv") != manifest_bytes:
            raise AssertionError("Embedded manifest differs from sidecar")
        for index, row in enumerate(included, 1):
            digest = hashlib.sha256()
            with archive.open(row["archive_member"], "r") as stream:
                for block in iter(lambda: stream.read(4 * 1024 * 1024), b""):
                    digest.update(block)
            if digest.hexdigest() != row["source_sha256"]:
                raise AssertionError(f"ZIP SHA-256 mismatch: {row['source_path']}")
            if index % 100 == 0 or index == len(included):
                print(f"verified {index}/{len(included)}", flush=True)
        if archive.testzip() is not None:
            raise AssertionError("ZIP CRC integrity failure")
    partial.replace(ARCHIVE)
    digest = hash_file(ARCHIVE)
    SHA_FILE.write_text(f"{digest}  {ARCHIVE.name}\n")
    excluded = [row["source_path"] for row in rows if row["archive_status"] != "INCLUDED"]
    INSTRUCTIONS.write_text(f"""# Research backup export — local ZIP verified, external copy pending

Created/verified UTC: {dt.datetime.now(dt.timezone.utc).isoformat()}.

- Archive: `{ARCHIVE}`
- Size: {ARCHIVE.stat().st_size:,} bytes.
- SHA-256: `{digest}`.
- Source list: `{BASE / 'backup_manifest.csv'}`; export manifest: `{MANIFEST}` (also embedded in the ZIP).
- Included: {len(included)} of the 1,110 previously local-only files, including all 305 corrected v2j benchmark prediction files. All included members had CRC and SHA-256 verified against the **current** source manifest. {len(drift)} source paths changed since the earlier backup-gate snapshot; both old and current hashes are in the export manifest: {', '.join(drift) if drift else 'none'}. Excluded transient controls: {len(excluded)} files, listed with reasons in the manifest: {', '.join(excluded)}.
- Git-backed research reports, code, methodology, configurations and existing tracked data are independently recoverable from GitHub branch `audit/canonical-notebook-20261023` at commit `a0d87aa7d16ba7d202f2b6e833d57f489741ab7d` (later v2m documentation commits add this report). The three historical classes in `backup_verification.md` remain MISSING AT SOURCE.

## Download and external transfer

In JupyterLab's file browser, navigate to `Capstone/final_blr_results/research_backup_exports/` and download `{ARCHIVE.name}`, `RESEARCH_BACKUP_MANIFEST.csv`, this instruction file and `RESEARCH_BACKUP_SHA256.txt`. Save all four to a persistent external drive. On the destination computer, verify the ZIP hash using `sha256sum -c RESEARCH_BACKUP_SHA256.txt` from the directory containing the ZIP, then run `unzip -t {ARCHIVE.name}`. To restore, extract into an empty directory, preserving member relative paths. Compare extracted SHA-256s with `source_sha256` for rows marked INCLUDED in the manifest. Obtain Git-backed files from the cited commit separately. Do not overwrite an active workspace during restore.

**Status: LOCAL ARCHIVE VERIFIED — EXTERNAL COPY PENDING.** The ZIP currently shares the JupyterHub filesystem with the source; it is not a verified pen-drive/off-host backup. JupyterHub loss before the owner downloads and verifies the archive could destroy local-only artifacts. Do not delete local sources or this archive before external verification.
""")
    print(f"archive={ARCHIVE} bytes={ARCHIVE.stat().st_size} sha256={digest} included={len(included)} excluded={len(excluded)} changed_since_snapshot={len(drift)}", flush=True)


if __name__ == "__main__":
    main()
