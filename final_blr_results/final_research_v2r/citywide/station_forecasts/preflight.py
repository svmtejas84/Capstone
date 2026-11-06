"""One-batch resource preflight for the frozen corrected 18-channel station model.

No target scoring or optimizer step. Writes a bounded JSON resource record.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

import numpy as np
import torch

from src.stpignn.models_v2 import make_model
from src.stpignn.station_graph import directed_knn_graph

OUT = Path(__file__).resolve().parent


def main() -> None:
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA unavailable; preserve preflight blocker")
    z = np.load(ROOT / "results/data_v2j_arrays.npz")
    xy = z["coordinates"].astype(np.float32)
    edge, length = directed_knn_graph(xy, 4)
    edge, length = edge.cuda(), length.cuda()
    # 13 stored channels + observed-lag flag + four calendar channels = 18.
    # Batch is shape/resource-only and has no target values or model fitting.
    torch.manual_seed(11)
    x = torch.zeros((512, 12, len(xy), 18), device="cuda")
    model = make_model("stpignn_corrected", 18, 96, 1).cuda()
    model.train()
    torch.cuda.reset_peak_memory_stats()
    started = time.perf_counter()
    y = model(x, edge, length)
    (y.square().mean()).backward()
    torch.cuda.synchronize()
    elapsed = time.perf_counter() - started
    batches = 28  # 14,206 eligible train hours / 512, rounded up.
    # Minimum is 15 outer models plus 15*14 support-excluding inner models.
    minimum_models = 15 + 15 * 14
    projected_min_hours = elapsed * batches * 20 * minimum_models / 3600
    result = {"batch_size": 512, "hours_per_fit_upper_epochs": 20,
              "measured_forward_backward_seconds": elapsed,
              "peak_gpu_bytes": torch.cuda.max_memory_allocated(),
              "parameter_count": sum(p.numel() for p in model.parameters()),
              "minimum_fold_models": minimum_models,
              "projected_20_epoch_gpu_hours_lower_bound": projected_min_hours,
              "source_arrays": "results/data_v2j_arrays.npz",
              "note": "shape-only, no optimizer or data preprocessing; projection excludes fold building, validation, cross-fitting time blocks and I/O"}
    (OUT / "preflight.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
