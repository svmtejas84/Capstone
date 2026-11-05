"""Preserve the interrupted CPU outputs before a clean GPU-only rerun."""
from __future__ import annotations

import json

from src.stpignn.paths import REPO_ROOT


def main():
    out = REPO_ROOT / "results"
    archive = out / "codex_log/runs/benchmark_cpu_v2j"
    archive.mkdir(parents=True, exist_ok=True)
    paths = [out / "benchmark_runs_v2j.csv", out / "benchmark_selection_v2j.csv"]
    paths.extend(sorted(out.glob("benchmark_predictions_h*_v2j.parquet")))
    moved = []
    for path in paths:
        if not path.exists():
            continue
        destination = archive / path.name
        if destination.exists():
            raise FileExistsError(destination)
        path.rename(destination)
        moved.append(path.name)
    (archive / "cpu_partial_manifest_v2j.json").write_text(json.dumps({
        "reason": "CPU sandbox had no GPU access; user required a GPU-only rerun",
        "files": moved,
    }, indent=2) + "\n")
    print(f"Archived {len(moved)} CPU partial artifacts")


if __name__ == "__main__":
    main()
