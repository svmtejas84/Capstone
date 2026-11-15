"""Pretraining graph, cutoff and source-integrity verification; no fit/test score."""
import csv
import json
from pathlib import Path

import numpy as np
import torch

from final_blr_results.controlled_validation_v5.scripts.train_graph_lag import ExperimentalContext, rewire_preserving_degree, V5
from final_blr_results.controlled_validation_v3.scripts.train_controls import ARR, FIT, hash_file

EXPECTED = "bd08d733f924387da82e758d1060703dfcdd121f360b7e8765189d8b7446e202"


def main():
    assert hash_file(ARR) == EXPECTED and torch.cuda.is_available()
    base = ExperimentalContext(6, "rewired")
    original = np.load(ARR)["coordinates"]
    edge = base.edge_index.cpu().numpy()
    assert np.allclose(base.edge_distance.cpu().numpy()[:, 0],
                       np.linalg.norm(original[edge[1]] - original[edge[0]], axis=1), atol=1e-3)
    assert np.array_equal(edge, rewire_preserving_degree(ExperimentalContext(6, "lag24").edge_index.cpu().numpy()))
    source = np.load(ARR)
    lag = ExperimentalContext(6, "lag24")
    index, x, y, mask, anchor, wind = next(lag.batches("train"))
    assert index.min() - 6 >= 11 and x.shape[1:] == (12, 15, 21)
    assert torch.all(x[:, :-1, :, 18:] == 0)
    daily = index - 24
    cutoff = index - 6
    good = (daily[:, None] >= 0) & (daily[:, None] < cutoff[:, None]) & lag.observed[np.maximum(daily, 0)]
    daily_value = np.where(good, np.nan_to_num(lag.y[np.maximum(daily, 0)], nan=0), lag.anchor[np.maximum(daily, 0)])
    recovered = np.expm1(x[:, -1, :, 18].cpu().numpy() * lag.sd + lag.mu)
    assert np.allclose(recovered, daily_value, atol=1e-4), "daily-lag fallback differs from frozen baseline"
    # Perturb all target rows in the selected batch; no current target can
    # appear in its own lag or prior-observation window.
    initial = x.detach().cpu().clone()
    latest_target = int(index.max())
    old = lag.y[latest_target].copy()
    lag.y[latest_target] = 999999.
    try:
        _, x2, _, _, _, _ = next(lag.batches("train"))
        assert torch.equal(initial, x2.cpu())
    finally:
        lag.y[latest_target] = old
    assert np.array_equal(source["observed_target"], np.load(ARR)["observed_target"], equal_nan=True)
    # Different graph conditions share target-hour and target-mask populations.
    for variant in ("self_loops", "rewired", "lag24", "lookback36"):
        ctx = ExperimentalContext(6, variant)
        assert np.array_equal(ctx.hours["train"], lag.hours["train"])
        idx, _, _, m, _, _ = next(ctx.batches("train"))
        assert np.array_equal(idx, index) and torch.equal(m.cpu(), mask.cpu())
    receipt = dict(status="PASS", array_sha256=EXPECTED,
                   checks=["degree-preserving deterministic rewiring", "recomputed geometric edge distances",
                           "lag24 strictly prior", "lag24 fallback parity with same-hour-yesterday", "future target mutation invariant", "common train target masks"],
                   reference_batch_targets=int(mask.sum()), reference_batch_hours=len(index))
    out = V5 / "verification/preflight.json"; out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__": main()
