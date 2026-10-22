"""Execute only the canonical notebook setup and evaluation cells, without training.

This deliberately preserves the notebook's original global state and data path so
that an independent reproduction attempt can test its saved headline numbers.
"""
import contextlib
import datetime as dt
import json
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "notebooks/production/evaluated_wind_advection.ipynb"
OUT = ROOT / "results"
OUT.mkdir(exist_ok=True)


def main():
    book = json.loads(NOTEBOOK.read_text())
    scope = {"__name__": "__main__"}
    cells = [0, 2, 5, 7, 9, 11, 20, 24]
    began = time.perf_counter()
    with (OUT / "replay_canonical.log").open("w") as log, contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
        for number in cells:
            print(f"BEGIN CELL {number}", flush=True)
            code = "".join(book["cells"][number]["source"])
            exec(compile(code, f"{NOTEBOOK.name}:cell_{number}", "exec"), scope)
            print(f"END CELL {number}", flush=True)
        result = {
            "timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
            "source_git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
            "seed": 42,
            "checkpoint": "citywide_stpignn_best.pt",
            "hardware": scope["gpu_name"] if scope["device"].type == "cuda" else "CPU",
            "config": scope["GLOBAL_CFG"],
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
    (OUT / "replay_canonical.json").write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
