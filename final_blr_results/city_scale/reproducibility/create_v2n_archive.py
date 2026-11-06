"""Create and verify a supplemental local v2n ZIP; never replace older ZIPs."""
from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CITY = ROOT / "final_blr_results/city_scale"
OUT = CITY / "reproducibility"
ARCHIVE = OUT / "research_results_v2n.zip"
VERIFY = OUT / "V2N_ARCHIVE_VERIFICATION.json"


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(4 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    if ARCHIVE.exists():
        raise FileExistsError("Preserve existing v2n archive; inspect before rebuilding")
    files = sorted(p for p in CITY.rglob("*") if p.is_file() and p not in (ARCHIVE, VERIFY)
                   and "__pycache__" not in p.parts)
    source = {p.relative_to(ROOT).as_posix(): digest(p) for p in files}
    tmp = OUT / "research_results_v2n.tmp.zip"
    with zipfile.ZipFile(tmp, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6, allowZip64=True) as z:
        for p in files:
            z.write(p, p.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(tmp) as z:
        assert z.testzip() is None
        assert set(z.namelist()) == set(source)
        for name, expected in source.items():
            assert hashlib.sha256(z.read(name)).hexdigest() == expected, name
    tmp.replace(ARCHIVE)
    payload = dict(path=ARCHIVE.relative_to(ROOT).as_posix(), bytes=ARCHIVE.stat().st_size,
                   sha256=digest(ARCHIVE), member_count=len(files), member_sha256=source,
                   verification="ZIP CRC and every member SHA-256 matched local source")
    VERIFY.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps({k: payload[k] for k in ("path", "bytes", "sha256", "member_count", "verification")}))


if __name__ == "__main__":
    main()
