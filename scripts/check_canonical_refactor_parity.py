"""Fixed-batch parity against unexecuted function/class definitions in notebook."""
import ast
import datetime as dt
import json
import subprocess
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import torch
import torch.nn.functional as F

ROOT = Path(__file__).resolve().parents[1]
from src.stpignn import (TierAwareClusterDatasetV3, compute_dynamic_upwind_mask_vectorized,
                         compute_wind_advection_penalty, masked_mae_rmse_vectorized)

book = json.loads((ROOT / "results/legacy_canonical_notebook.ipynb").read_text())


def original(cell, name, globals_):
    tree = ast.parse("".join(book["cells"][cell]["source"]))
    definition = next(node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name == name)
    ns = dict(globals_)
    exec(compile(ast.Module(body=[definition], type_ignores=[]), f"cell_{cell}", "exec"), ns)
    return ns[name]


def main():
    torch.manual_seed(42)
    bearings = torch.tensor([0., 30., 180., 220., 350.])
    part = SimpleNamespace(edge_bearings=bearings)
    old_mask = original(7, "compute_dynamic_upwind_mask_vectorized", {"torch": torch, "device": torch.device("cpu")})
    assert torch.equal(old_mask(part, 30.), compute_dynamic_upwind_mask_vectorized(bearings, 30.))
    edge_index = torch.tensor([[0, 1, 2, 1, 0], [1, 2, 0, 0, 2]])
    edge_attr = torch.randn(5, 16)
    pred = torch.randn(3)
    old_penalty = original(13, "compute_wind_advection_penalty", {"torch": torch, "F": F})
    assert torch.equal(old_penalty(pred, edge_index, old_mask(part, 30.), edge_attr),
                       compute_wind_advection_penalty(pred, edge_index, old_mask(part, 30.), edge_attr))
    target = torch.tensor([0., 1., -1.])
    scored = torch.tensor([False, True, True])
    old_metrics = original(13, "masked_mae_rmse_vectorized", {"torch": torch})
    assert all(torch.equal(a, b) for a, b in zip(old_metrics(pred, target, scored),
                                                 masked_mae_rmse_vectorized(pred, target, scored)))
    registry = {i: torch.randn(30, 16) for i in range(3)}
    clusters = [SimpleNamespace(n_id=torch.tensor([0, 1, 2]), train_mask=torch.tensor([False, True, False]),
                                global_feature_registry=registry)]
    time_count = 30
    time_breaks = np.arange(31, dtype=np.int32)
    raw_node_indices = np.ones(30, dtype=np.int64)
    raw_targets = np.arange(30, dtype=np.float32) / 10
    old_dataset = original(9, "TierAwareClusterDatasetV3", {
        "Dataset": torch.utils.data.Dataset, "np": np, "torch": torch, "T_total": time_count,
        "time_breaks": time_breaks, "raw_node_indices": raw_node_indices, "raw_targets": raw_targets})
    a = old_dataset(clusters, 0, 20, window=12, stride=4)
    b = TierAwareClusterDatasetV3(clusters, 0, 20, time_count, time_breaks, raw_node_indices,
                                  raw_targets, window=12, stride=4)
    assert a.samples == b.samples
    for i in range(len(a)):
        old, new = a[i], b[i]
        assert all(torch.equal(x, y) if isinstance(x, torch.Tensor) else x == y for x, y in zip(old, new))
    result = {"timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
              "source_git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
              "seed": 42, "config": {"window": 12, "stride": 4, "toy_nodes": 3},
              "fixed_batch_samples": len(a), "mask_equal": True,
              "penalty_equal": True, "metrics_equal": True, "dataset_equal": True}
    (ROOT / "results/refactor_parity.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
