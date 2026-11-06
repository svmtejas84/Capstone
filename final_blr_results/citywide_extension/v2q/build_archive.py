"""Create and verify the lightweight v2q supplemental archive locally."""
from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
OUT = BASE / "research_results_v2q.zip"
REPORT = BASE / "v2q_archive_verification.json"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    sources = [p for p in sorted(BASE.iterdir()) if p.is_file() and p.name not in {OUT.name, REPORT.name}]
    sources.append(ROOT / "tests/test_v2q_spatial_decoder.py")
    with zipfile.ZipFile(OUT, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for path in sources:
            archive.write(path, arcname=str(path.relative_to(ROOT)))
    members = []
    with zipfile.ZipFile(OUT) as archive:
        assert archive.testzip() is None
        for path in sources:
            name = str(path.relative_to(ROOT))
            actual = archive.read(name)
            assert digest(actual) == digest(path.read_bytes())
            members.append({"path": name, "bytes": len(actual), "sha256": digest(actual)})
    payload = {"archive": str(OUT.relative_to(ROOT)), "bytes": OUT.stat().st_size,
               "sha256": digest(OUT.read_bytes()), "members": members, "crc_ok": True}
    REPORT.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps({k: v for k, v in payload.items() if k != "members"}))


if __name__ == "__main__":
    main()
