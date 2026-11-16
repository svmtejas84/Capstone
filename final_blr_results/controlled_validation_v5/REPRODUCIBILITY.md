# V5 reproduction and recovery

Run from `/home/jupyter-1nt23cb058/Capstone`. Verify branch `research/controlled-validation-v5`, source hashes and V100 availability. V3/V4 checkpoint and prediction directories are required local dependencies and must remain read-only. The source array is `final_blr_results/controlled_validation_v3/data_manifests/data_v3_causal_arrays.npz`.

```bash
sha256sum final_blr_results/controlled_validation_v5/PROTOCOL_FREEZE.md
sha256sum final_blr_results/controlled_validation_v3/data_manifests/data_v3_causal_arrays.npz
PYTHONPATH=. MPLCONFIGDIR=/tmp/mpl_v5 python final_blr_results/controlled_validation_v5/scripts/audit_saved.py
PYTHONPATH=. MPLCONFIGDIR=/tmp/mpl_v5 python final_blr_results/controlled_validation_v5/scripts/preflight.py
PYTHONPATH=. python final_blr_results/controlled_validation_v5/scripts/verify_cutoff_all_horizons.py
bash scripts/run_supervised.sh status final_blr_results/controlled_validation_v5/logs/graph
```

The frozen stage order is `graph`, `lag`, `cross`, `fairness`. Only start a stage when its predecessor has a verified supervisor `COMPLETE` marker. The supervisor's elevated process namespace is required for correct PID/GPU status; sandbox-only `ps` may fail to see a live elevated worker. The following is a recovery example for a **not-yet-launched** stage; do not relaunch a completed stage or duplicate an active worker:

```bash
bash scripts/run_supervised.sh launch final_blr_results/controlled_validation_v5/logs/lag -- bash final_blr_results/controlled_validation_v5/scripts/run_stage.sh lag final_blr_results/controlled_validation_v5/logs/lag
bash scripts/run_supervised.sh status final_blr_results/controlled_validation_v5/logs/lag
bash scripts/run_supervised.sh resume final_blr_results/controlled_validation_v5/logs/lag
```

Each new fit writes atomic `partial.pt` per epoch, selected `best.pt`, `epochs.json` and `COMPLETE.json`. The stage writes `training/<stage>_COMPLETE` and the supervised wrapper writes `logs/<stage>/COMPLETE`; completed cells are validated and skipped on a restart. Do not delete failed attempts. The V100 training runner never reads test labels. The scorer is guarded against a second creation of `metrics/NEW_TEST_SCORES.csv`.

After all **160** new cells complete, run these in order. The `score` step unlocks the previously exposed test once, after validation-only selection and checkpoint verification:

```bash
PYTHONPATH=. MPLCONFIGDIR=/tmp/mpl_v5 python final_blr_results/controlled_validation_v5/scripts/verify_and_score.py --stage verify
PYTHONPATH=. MPLCONFIGDIR=/tmp/mpl_v5 python final_blr_results/controlled_validation_v5/scripts/replay_missing_penalties.py
PYTHONPATH=. MPLCONFIGDIR=/tmp/mpl_v5 python final_blr_results/controlled_validation_v5/scripts/replay_fairness_gradients.py
PYTHONPATH=. MPLCONFIGDIR=/tmp/mpl_v5 python final_blr_results/controlled_validation_v5/scripts/summarize_training.py
PYTHONPATH=. MPLCONFIGDIR=/tmp/mpl_v5 python final_blr_results/controlled_validation_v5/scripts/verify_and_score.py --stage score
PYTHONPATH=. MPLCONFIGDIR=/tmp/mpl_v5 python final_blr_results/controlled_validation_v5/scripts/analyze_v5.py
PYTHONPATH=. MPLCONFIGDIR=/tmp/mpl_v5 python final_blr_results/controlled_validation_v5/scripts/diagnose_v5.py
PYTHONPATH=. MPLCONFIGDIR=/tmp/mpl_v5 python final_blr_results/controlled_validation_v5/scripts/build_results.py
PYTHONPATH=. MPLCONFIGDIR=/tmp/mpl_v5 python final_blr_results/controlled_validation_v5/scripts/plot_v5.py
PYTHONPATH=. MPLCONFIGDIR=/tmp/mpl_v5 python final_blr_results/controlled_validation_v5/scripts/verify_v5.py
PYTHONPATH=. MPLCONFIGDIR=/tmp/mpl_v5 python final_blr_results/controlled_validation_v5/scripts/package_v5.py
```

Statistics use the V3 frozen `block_analysis`: 2,000 seven-day moving-block bootstrap draws for a 95% interval and 100,000 seven-day block sign flips for p-values, with deterministic seeds fixed in `scripts/analyze_v5.py`. New graph and temporal families have separate Holm adjustments; later regularizer-family selection contrasts are exploratory. The old V3 20-member and V4 six-member families are not retrospectively combined. Seed signs are descriptive. Historical test exposure forbids independent-confirmation language.

The archive includes selected checkpoints and saved evaluation predictions when available; restart-only partials and historical raw datasets are intentionally excluded. `archives/ZIP_VERIFICATION.json` records the final ZIP hash and member verification. External USB backup remains unverified.
