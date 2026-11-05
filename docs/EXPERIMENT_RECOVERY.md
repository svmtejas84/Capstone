# Supervised experiment recovery (engineering R1)

Source commit examined for historical training/checkpoints: `dca4bcce690da6b7865702f91d15dd2e06b6ef75`. The wrapper was added later in the R1 audit. It does not launch experiments by itself.

Use `scripts/run_supervised.sh` from a persistent shared filesystem. `tmux` is absent on this JupyterHub; if later installed, it can monitor the log interactively but cannot be assumed to survive a server reboot. The wrapper uses `setsid`/`nohup` for terminal disconnects, `flock` for one active worker, a PID file, bounded automatic retries (default two restarts), per-attempt logs, and a JSON execution manifest. `flock` lifetime follows the process, never lock age. A full VM reboot stops the process; use `resume` after reboot.

```bash
EXPERIMENT_CONFIG=configs/example.yaml EXPERIMENT_SEEDS=11,23,37 \
  scripts/run_supervised.sh launch results/runs/example -- python -m scripts.authorized_experiment --resume
scripts/run_supervised.sh status results/runs/example
scripts/run_supervised.sh stop results/runs/example
scripts/run_supervised.sh verify results/runs/example
scripts/run_supervised.sh resume results/runs/example
```

Do not run that example until the experiment is authorized. `launch` refuses an existing command manifest; `resume` reuses the saved command. The job must atomically write `COMPLETE` only after all outputs are validated. For the wrapper's generic checkpoint contract, write a temporary state file and call `scripts/run_supervised.sh checkpoint RUN_DIR TEMP_FILE`; this installs `checkpoint.bin` plus SHA256 sidecar by rename. `verify` and `resume` reject a mismatched or incomplete checkpoint pair. The training command must itself read the last valid checkpoint and skip completed seed/fold rows. The wrapper cannot infer progress from arbitrary model artifacts. `MAX_RESTARTS` is controlled at initial launch by `SUPERVISED_MAX_RESTARTS`; any later manual resume is explicit. Failed attempt logs are retained. `stop` sends TERM to the supervised process group, not unrelated jobs. Status may briefly say STOPPED during startup before the PID is written; the lock still prevents a duplicate active worker.

The execution manifest stores commit, command, configuration path from `EXPERIMENT_CONFIG`, seeds from `EXPERIMENT_SEEDS`, Python executable/version, PyTorch/GPU, start time and output directory. Do not put credentials in command-line arguments or config metadata. This wrapper does not save or restore model training state unless the underlying script supports it.

Historical `scripts/train_gate_v2.py:240` checkpoint samples (`results/checkpoints_v2/`, `results/checkpoints_v2b/`) contain model `state_dict`, best epoch, LR/seed/config text and validation score. They do **not** contain optimizer, scheduler, AMP scaler state, Python/NumPy/PyTorch RNG states, batch position, dataset/split hashes or a configuration fingerprint. The `scaler` key is a target-scaling *string*, not an AMP GradScaler. Exact interrupted-epoch recovery is impossible from those checkpoints; restart an unfinished seed from the beginning, while preserving completed seed results. W7/DEM/group-DRO local prediction caches checkpoint completed cells but do not restore mid-seed training state. Future exact recovery requires atomic files containing all enumerated state and fingerprints, with a loader that validates them before resuming. A wrapper cannot provide that for existing code.
