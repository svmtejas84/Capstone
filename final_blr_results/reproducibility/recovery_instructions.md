# Recovery commands for a future approved baseline run

Do not execute until the supervisor approves the fixed baseline configuration. Use one run directory per approved experiment, for example `final_blr_results/baselines/runs/mlp_v2l`, and never reuse historical `results/` output paths. Check `ps aux | grep -E 'scripts\.|run_supervised' | grep -v grep` and supervisor `status` before launching. Verify `nvidia-smi` and script-level `torch.cuda.is_available()`; neural training must fail closed without GPU.

```sh
cd /home/jupyter-1nt23cb058/Capstone
EXPERIMENT_CONFIG=configs/benchmark_v2g.yaml EXPERIMENT_SEEDS=11,23,37,51,79 \
  scripts/run_supervised.sh launch final_blr_results/baselines/runs/mlp_v2l -- python -m scripts.APPROVED_FUTURE_RUNNER
scripts/run_supervised.sh status final_blr_results/baselines/runs/mlp_v2l
scripts/run_supervised.sh verify final_blr_results/baselines/runs/mlp_v2l
scripts/run_supervised.sh resume final_blr_results/baselines/runs/mlp_v2l
```

The runner name above is deliberately a placeholder, not an existing authorized training command. On recovery, inspect `execution_manifest.json`, `attempts.log`, latest attempt log, `COMPLETE`, per-seed outputs and their hashes. If `COMPLETE` exists, verify expected files before accepting it. If no process holds the lock and no completion marker exists, validate the checkpoint sidecar and use `resume` with the saved command; do not issue a second `launch`. A corrupt checkpoint must be preserved for diagnosis before manual repair. The script must skip only fully validated seed/fold cells and restart an interrupted seed from its start unless a complete optimizer/RNG/epoch checkpoint was explicitly implemented. `stop` sends TERM to that run's process group; do not use it on another active experiment. See `docs/EXPERIMENT_RECOVERY.md` for the wrapper contract.
