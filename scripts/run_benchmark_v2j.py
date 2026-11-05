"""Sequential, resumable v2j horizon benchmark under run_supervised.sh."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from src.stpignn.paths import REPO_ROOT


def main():
    run_dir = REPO_ROOT / "results/codex_log/runs/benchmark_gpu_v2j"
    for horizon in (1, 3, 6, 12, 24):
        subprocess.run([sys.executable, "-m", "scripts.benchmark_v2j", "--horizon", str(horizon)],
                       cwd=REPO_ROOT, check=True)
    (run_dir / "COMPLETE").write_text("all five horizons complete\n")


if __name__ == "__main__":
    main()
