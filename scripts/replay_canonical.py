"""Execute only the canonical notebook setup and evaluation cells, without training.

This deliberately preserves the notebook's original global state and data path so
that an independent reproduction attempt can test its saved headline numbers.
"""
import contextlib
import argparse
import datetime as dt
import json
import os
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "notebooks/production/evaluated_wind_advection.ipynb"
OUT = ROOT / "results"
OUT.mkdir(exist_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--deterministic-fp32", action="store_true")
    args = parser.parse_args()
    if args.deterministic_fp32:
        os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"
    book = json.loads(NOTEBOOK.read_text())
    scope = {"__name__": "__main__"}
    cells = [0, 2, 5, 7, 9, 11, 20, 24]
    began = time.perf_counter()
    stem = "replay_rewired_fp32" if args.deterministic_fp32 else "replay_rewired_amp"
    with (OUT / f"{stem}.log").open("w") as log, contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
        for number in cells:
            print(f"BEGIN CELL {number}", flush=True)
            code = "".join(book["cells"][number]["source"])
            exec(compile(code, f"{NOTEBOOK.name}:cell_{number}", "exec"), scope)
            if args.deterministic_fp32 and number == 0:
                scope["torch"].use_deterministic_algorithms(True)
            if args.deterministic_fp32 and number == 11:
                scope["amp_enabled"] = False
            print(f"END CELL {number}", flush=True)
        result = {
            "timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
            "source_git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
            "seed": 42,
            "checkpoint": "citywide_stpignn_best.pt",
            "hardware": scope["gpu_name"] if scope["device"].type == "cuda" else "CPU",
            "config": scope["GLOBAL_CFG"],
            "deterministic_fp32": args.deterministic_fp32,
            "cells": cells,
            "runtime_seconds": time.perf_counter() - began,
            "mae": scope.get("global_mae"),
            "rmse": scope.get("global_rmse"),
            "median_ae": scope.get("global_median_err"),
            "scored_pairs": len(scope.get("final_preds", [])),
            "violations": scope.get("total_physical_violations"),
            "active_edges": scope.get("total_evaluated_edges"),
            "pvr_percent": scope.get("global_pvr"),
            "predicted_mean": float(scope["final_preds"].mean()),
            "predicted_std": float(scope["final_preds"].std()),
            "predicted_min": float(scope["final_preds"].min()),
            "predicted_max": float(scope["final_preds"].max()),
            "observed_mean": float(scope["final_targets"].mean()),
            "observed_std": float(scope["final_targets"].std()),
            "observed_min": float(scope["final_targets"].min()),
            "observed_max": float(scope["final_targets"].max()),
        }
        import numpy as np
        result["correlation"] = float(np.corrcoef(scope["final_preds"], scope["final_targets"])[0, 1])
        print(json.dumps(result, indent=2), flush=True)
    (OUT / f"{stem}.json").write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
