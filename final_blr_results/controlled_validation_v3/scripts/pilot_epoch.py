"""One training epoch for resource timing only; no test access or saved model."""
import json
from pathlib import Path
import torch
from scripts.benchmark_v2j import fit
from final_blr_results.controlled_validation_v3.scripts.smoke_gpu import CutoffContext, ARR, FIT, V3


def main():
    assert torch.cuda.is_available()
    cfg = dict(neural_batch_size=512, station_graph_neighbours=4, neural_hidden_dim=64,
               neural_weight_decay=.01, neural_max_epochs=1, neural_early_stopping_patience=5,
               lambda_original=.06)
    ctx = CutoffContext(6, cfg, ARR, FIT)
    result, _ = fit(ctx, "stpignn_lambda0", .001, 11, evaluate_test=False)
    out = {k: result[k] for k in ("horizon_hours", "seed", "lr", "best_epoch", "validation_mae", "epochs_run", "parameter_count", "train_seconds")}
    out["peak_gpu_bytes"] = torch.cuda.max_memory_allocated()
    p = V3 / "verification/pilot_epoch.json"; p.write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps(out,indent=2))


if __name__ == "__main__": main()
