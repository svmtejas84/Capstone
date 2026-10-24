"""Check refactored notebook replay against retained Phase A output."""
import datetime as dt
import json
import subprocess
from pathlib import Path

from src.stpignn.paths import REPO_ROOT


def main():
    base = json.loads((REPO_ROOT / "results/replay_canonical.json").read_text())
    first = json.loads((REPO_ROOT / "results/replay_rewired_fp32_run1.json").read_text())
    second = json.loads((REPO_ROOT / "results/replay_rewired_fp32.json").read_text())
    tolerance = {"mae": 0.01, "rmse": 0.03, "pvr_percent": 0.002}
    checks = {name: abs(first[name] - base[name]) <= limit for name, limit in tolerance.items()}
    checks["scored_pairs"] = first["scored_pairs"] == base["scored_pairs"]
    checks["active_edges"] = first["active_edges"] == base["active_edges"]
    checks["fp32_repeat_identical"] = all(first[k] == second[k] for k in
                                           ("mae", "rmse", "violations", "active_edges", "pvr_percent"))
    report = {"timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
              "script": "scripts/check_full_replay_parity.py", "seed": 42,
              "source_git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True).strip(),
              "baseline": {k: base[k] for k in ("mae", "rmse", "pvr_percent", "violations", "active_edges", "scored_pairs")},
              "rewired_fp32": {k: first[k] for k in ("mae", "rmse", "pvr_percent", "violations", "active_edges", "scored_pairs")},
              "tolerance": tolerance, "checks": checks, "pass": all(checks.values())}
    (REPO_ROOT / "results/full_replay_parity.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    if not report["pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
