# V5 controlled validation — startup

Started 2026-11-15 on `research/controlled-validation-v5`, branching from V4 commit `bb0d06fa73c25e8420c32d09e5da5372c1328d99`. Historical V3/V4 results and checkpoints are read-only. The tracked tree was clean at startup; numerous pre-existing untracked research archives, checkpoints and logs are preserved. NVIDIA Tesla V100-PCIE-32GB has 32,488 MiB free (elevated `nvidia-smi` check). Host storage has 95 GiB free. No V5 jobs are active.

Current stage: inspect authoritative saved evidence, then perform saved-prediction audits. **No V5 training or new-model test scoring has started.** Freeze and commit `PROTOCOL_FREEZE.md` before either. Bengaluru test labels are previously exposed; all V5 inferences are exploratory. No manuscript or London work.

Recovery: `cd /home/jupyter-1nt23cb058/Capstone`; `git branch --show-current`; `git status --short`; `cat final_blr_results/controlled_validation_v5/RESUME.md`; `nvidia-smi`; inspect V3/V4 `REPRODUCIBILITY.md` before using their saved predictions. Historical source array: `final_blr_results/controlled_validation_v3/data_manifests/data_v3_causal_arrays.npz` (SHA-256 `bd08d733f924387da82e758d1060703dfcdd121f360b7e8765189d8b7446e202`).

## Saved-data audit and protocol freeze

Saved-prediction audit ran successfully: 602 method/horizon/anchor rows, 20 V3 contrasts, six V4 contrasts, 130 seed rows, 31 common-mask diagnostic rows. The V3 source array hash matched. Protocol SHA-256 `64682686b29660ff336ed6893e257950ce25c3e03683f68de088f6a808825266`; training remains NOT STARTED. Next: commit/push protocol, implement and smoke-test graph/lag/fairness runners, then launch bounded V100 work.
