"""Evaluate corrected and legacy-mask PVR on the common test hours.

Q rows are deliberately absent until a measured traffic index exists.
"""
from __future__ import annotations

import datetime as dt
import json
import subprocess

import numpy as np
import pandas as pd
import torch

from scripts.train_gate_v2 import Context, inverse_y, model_inputs, scaler_params
from src.stpignn.models_v2 import make_model
from src.stpignn.paths import REPO_ROOT


def main():
    ctx = Context()
    final = pd.read_csv(REPO_ROOT / "results/neural_final_v2.csv")
    scale = float(ctx.fit["target_standard_std"])
    thresholds = (0.0, 0.01, 0.05, 0.1)
    rows = []
    for record in final.itertuples(index=False):
        path = REPO_ROOT / record.checkpoint
        payload = torch.load(path, map_location=ctx.device, weights_only=False)
        model = make_model(record.model, ctx.features.shape[-1],
                           int(ctx.cfg["neural_hidden_dim"]), ctx.edge_attr.shape[1]).to(ctx.device)
        model.load_state_dict(payload["state_dict"])
        model.eval()
        mean, std = scaler_params(ctx.fit, record.scaler)
        counts = {mask_name: np.zeros(4, dtype=np.int64) for mask_name in ("legacy", "corrected")}
        active = {mask_name: 0 for mask_name in counts}
        positive = {mask_name: [] for mask_name in counts}
        total_edges = 0
        src, dst = ctx.edge_index
        with torch.no_grad():
            for _, x, _, _, _, corrected_mask, legacy_mask in ctx.batches("test", int(ctx.cfg["neural_batch_size"])):
                y = inverse_y(model(model_inputs(x, record.model), ctx.edge_index, ctx.edge_attr),
                              record.scaler, mean, std)
                diff = ((y[:, dst] - y[:, src]) / scale).cpu().numpy()
                total_edges += diff.size
                for mask_name, mask_tensor in (("legacy", legacy_mask), ("corrected", corrected_mask)):
                    mask = mask_tensor.cpu().numpy()
                    selected = diff[mask]
                    active[mask_name] += selected.size
                    positive[mask_name].append(np.maximum(selected, 0))
                    for index, threshold in enumerate(thresholds):
                        counts[mask_name][index] += int(np.count_nonzero(selected > threshold))
        for mask_name in counts:
            excess = np.concatenate(positive[mask_name])
            for index, threshold in enumerate(thresholds):
                rows.append({"model": record.model, "seed": int(record.seed), "mask": mask_name,
                             "with_q": False, "threshold_normalized": threshold,
                             "threshold_ug_m3": threshold * scale,
                             "active_edges": active[mask_name], "total_edges": total_edges,
                             "mask_fraction": active[mask_name] / total_edges,
                             "violations": int(counts[mask_name][index]),
                             "pvr_percent": 100 * counts[mask_name][index] / active[mask_name],
                             "mean_relu_excess_ug_m3": float(excess.mean() * scale),
                             "p95_relu_excess_ug_m3": float(np.percentile(excess, 95) * scale)})
    pd.DataFrame(rows).to_csv(REPO_ROOT / "results/pvr_gate_v2.csv", index=False)
    metadata = {"script": "scripts/evaluate_pvr_gate_v2.py", "config": "configs/gate_v2.yaml",
                "data_config": "configs/data_v2.yaml", "timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
                "source_git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True).strip(),
                "seeds": sorted(final.seed.unique().astype(int).tolist()),
                "target_scale_ug_m3": scale,
                "q_status": "BLOCKED: measured traffic index absent; with-Q PVR cannot be evaluated"}
    (REPO_ROOT / "results/pvr_gate_v2_run.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(pd.DataFrame(rows).query('threshold_normalized == 0.0 and mask == "corrected"').groupby("model").pvr_percent.agg(["mean", "std"]).to_string())


if __name__ == "__main__":
    main()
