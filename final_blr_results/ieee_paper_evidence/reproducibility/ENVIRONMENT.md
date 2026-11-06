# Environment and provenance

Evidence assembly ran in the existing JupyterHub container on 2026-11-06 (Asia/Kolkata), Python available as `python`, pandas 2.3.3, Matplotlib 3.9.4. v2m models were originally trained on NVIDIA V100 per `final_blr_results/baselines/v2m/FINAL_BASELINE_VERDICT.md`; v2r source fold fits used V100, while complete city expansion used CPU. No training was run during this evidence assembly. The repository is at the package-start commit `a5b396da3f41c2d626ba072e8cec1a0ee15d383d` before evidence commits; each subsequent commit is recorded in Git.

Exact system package lock/export was unavailable at assembly; do not infer full environment reproducibility. Per-round environment and CUDA records take precedence.
