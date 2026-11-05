# Synthetic recovery test — R1

Source commit examined for old checkpoints: `dca4bcce690da6b7865702f91d15dd2e06b6ef75`. Wrapper/test files belong to the R1 audit commit. Test date: 2026-11-05 UTC. No ST-PIGNN training was launched.

`bash -n scripts/run_supervised.sh` passed. `scripts/supervised_dummy_v2h.py` is CPU-only and writes a progress checkpoint plus COMPLETE marker. In `/tmp/capstone_r1_dummy`, the first attempt exited 23 deliberately, the supervisor retained its log, restarted once, completed attempt 1 with code 0, and `verify` returned `CHECKPOINT_VALID`. A concurrent `resume` while PID 3505933 was live returned `RUNNING`, demonstrating duplicate prevention. The recorded attempt log and manifest remain in that temporary directory.

In `/tmp/capstone_r1_interrupt`, the dummy's attempt 1 was interrupted via the wrapper `stop` after a valid checkpoint; `status` returned STOPPED and `verify` returned CHECKPOINT_VALID. Manual `resume` started a new supervisor PID 3506105, read the saved checkpoint, and completed with code 0. This is interrupted-process recovery for a cooperating synthetic command, not proof of exact recovery for existing training scripts.

In `/tmp/capstone_r1_integrity`, a checkpoint installed with the wrapper verified successfully; modifying its bytes afterward made `verify` return `CHECKPOINT_INVALID`, so automatic resume will refuse it.

The wrapper relies on the filesystem and process namespace surviving terminal loss. A JupyterHub server reboot kills `setsid` and `tmux` processes; a later `resume` is required. Historic model checkpoints lack optimizer/RNG/batch state, so a stopped training seed must restart unless its runner saved a completed prediction row.
