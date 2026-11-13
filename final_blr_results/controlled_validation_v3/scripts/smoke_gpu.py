"""One-batch GPU correctness and resource pilot; no optimizer step or test labels."""
import json
import time
from pathlib import Path
import torch

from scripts.benchmark_v2j import Context, seed_all

ROOT = Path(__file__).resolve().parents[3]
V3 = ROOT / "final_blr_results/controlled_validation_v3"
ARR = ROOT / "final_blr_results/baselines/v2m/data/data_v2m_arrays.npz"
FIT = ROOT / "final_blr_results/baselines/v2m/data/data_v2m_fit.json"


class CutoffContext(Context):
    def _old_feature_mean(self, j):
        return json.loads(FIT.read_text())["fit"]["feature_means"][j]

    def _old_feature_sd(self, j):
        return json.loads(FIT.read_text())["fit"]["feature_stds"][j]


def main():
    assert torch.cuda.is_available(), "CUDA gate failed"
    cfg = dict(neural_batch_size=512, station_graph_neighbours=4, neural_hidden_dim=64,
               neural_weight_decay=.01, neural_max_epochs=30, neural_early_stopping_patience=5,
               lambda_original=.06)
    seed_all(11)
    c = CutoffContext(6, cfg, ARR, FIT)
    index, x, y, mask, anchor, wind = next(c.batches("train"))
    assert x.shape[1:] == (12, 15, 18) and bool(mask.any())
    assert (index - 6 >= 11).all()
    model = c.make("stpignn_original")
    torch.cuda.reset_peak_memory_stats()
    t0 = time.perf_counter()
    z = c.forward(model, "stpignn_original", x, anchor, wind)
    target = (torch.log1p(y.clamp_min(0)) - c.mu) / c.sd
    loss = ((z-target).square()*mask).sum()/mask.sum()
    assert bool(torch.isfinite(loss))
    loss.backward()
    assert all(p.grad is None or bool(torch.isfinite(p.grad).all()) for p in model.parameters())
    torch.cuda.synchronize()
    out = dict(gpu=torch.cuda.get_device_name(0), batch_shape=list(x.shape),
               observed_targets=int(mask.sum()), parameter_count=sum(p.numel() for p in model.parameters()),
               loss=float(loss.detach()), seconds=time.perf_counter()-t0,
               peak_allocated_bytes=torch.cuda.max_memory_allocated(),
               all_input_indices_at_or_before_issue=True, finite_gradients=True)
    p = V3 / "verification/smoke_gpu.json"; p.parent.mkdir(exist_ok=True)
    p.write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps(out,indent=2))


if __name__ == "__main__": main()
