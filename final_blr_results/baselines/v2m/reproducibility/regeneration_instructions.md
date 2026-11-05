# v2m recovery and regeneration

Repository root: `/home/jupyter-1nt23cb058/Capstone`; branch `audit/canonical-notebook-20261023`. Set `PYTHONPATH=.` and use the V100 for any training. The saved results need no retraining to regenerate comparisons.

```bash
cd /home/jupyter-1nt23cb058/Capstone
git status --short
PYTHONPATH=. python final_blr_results/baselines/v2m/tests/test_cutoff_data.py
PYTHONPATH=. python final_blr_results/baselines/v2m/tests/test_models.py
PYTHONPATH=. python final_blr_results/baselines/v2m/reproducibility/evaluate_v2m.py
MPLCONFIGDIR=/tmp/mpl-v2m python final_blr_results/baselines/v2m/reproducibility/make_figures.py
```

To check the already completed supervised run:

```bash
bash scripts/run_supervised.sh status final_blr_results/baselines/v2m/runs/all_v2m
bash scripts/run_supervised.sh verify final_blr_results/baselines/v2m/runs/all_v2m
tail -n 30 final_blr_results/baselines/v2m/runs/all_v2m/attempt_*.log
```

The run is complete. If a future copy is interrupted and the run lacks `COMPLETE`, resume only after confirming no active process:

```bash
PYTHONPATH=. bash scripts/run_supervised.sh resume final_blr_results/baselines/v2m/runs/all_v2m
```

To train a *specified authorized* model/horizon group in a fresh location, use `MODEL=mlp` or `tcn`, `H=1,3,6,12,24`, then:

```bash
PYTHONPATH=. bash scripts/run_supervised.sh launch final_blr_results/baselines/v2m/runs/${MODEL}_h${H} -- python final_blr_results/baselines/v2m/reproducibility/train_v2m.py --model "$MODEL" --horizon "$H"
```

The current assignment authorizes no further Bengaluru model training. These commands document recovery, not approval to rerun completed experiments. Each completed seed has `COMPLETE.json` with checkpoint, prediction and metrics checksums. The runner refuses a corrupt completed cell, skips an intact one, and reruns an incomplete seed from its start. It does not resume mid-epoch. Use `bash scripts/run_supervised.sh stop RUN_DIR` for a safe stop; it sends TERM to the process group. Check `scripts/run_supervised.sh status RUN_DIR` and the attempt log before resuming.

`evaluate_v2m.py` regenerates individual, ensemble, primary and secondary CSVs and the checksum table from saved prediction Parquets. `make_figures.py` regenerates the descriptive MAE plot. The final Markdown verdict is a human-readable synthesis of those tables. The pre-training source ZIP is `final_blr_results/research_backup_exports/research_backup_pretrain_v2m.zip`, with sidecar `RESEARCH_BACKUP_SHA256.txt`. The v2m supplementary ZIP has its own SHA-256 sidecar in this directory. Both are local verified archives awaiting external download. Download both without altering filenames, verify `sha256sum -c` against each sidecar on the destination, then retain a second copy outside JupyterHub. A local ZIP is not a durable independent backup.
