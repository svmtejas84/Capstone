# Checkpoint coverage

| Family | Available compatible cells | Used by v2n IG | Verdict |
|---|---:|---:|---|
| v2m cutoff-safe station MLP | 25/25 | 9 (seed 11 across five horizons plus other four seeds at h=6) | COMPATIBLE for station IG |
| v2m cutoff-safe station TCN | 25/25 | 9 (same design) | COMPATIBLE for station IG |
| corrected v2j ST-PIGNN original | 0 verified saved weights | 0 | UNVERIFIABLE |
| corrected v2j λ=0 | 0 verified saved weights | 0 | UNVERIFIABLE |
| corrected v2j Laplacian | 0 verified saved weights | 0 | UNVERIFIABLE |
| corrected W6 fold models | 0 verified saved weights | 0 | UNVERIFIABLE |
| legacy root citywide and older `results/checkpoints_v2*` | different/uncertain protocol | 0 | BLOCKED as corrected substitutes |

Saved corrected v2j predictions support outcome analysis, not gradient computation. The 18 used v2m weights were strict-loaded and checked against per-cell `COMPLETE.json` hashes and saved predictions; exact used checkpoint paths are determined by `run_captum_ig.py` and the `(model,horizon,seed)` keys in `convergence_diagnostics.csv`.
