# V4 reproduction and recovery

Repository: `/home/jupyter-1nt23cb058/Capstone`, branch `research/controlled-validation-v4-review-closure`. Frozen initial protocol SHA-256 `649f6af1f43dc510816efafd0e033a2118b5b7758fc41a1a4572089c740e44f0`; commit `5241eae` was pushed before any new fit. Correction amendment commit `be2e65f` was pushed before the invalidated full-shuffle cells were rerun. Pretest audit/scorer commits `839a8f5` and `afd9c48` were pushed before test scoring. The repaired V3 array SHA-256 is `bd08d733f924387da82e758d1060703dfcdd121f360b7e8765189d8b7446e202`. `SOURCE_HASHES.csv` records 11 input/source hashes; V3's original seven-source manifest remained unchanged.

From repo root, read-only regeneration of V3-saved evidence into V4:

```bash
MPLCONFIGDIR=/tmp/mpl_v4 PYTHONPATH=. python final_blr_results/controlled_validation_v4_review_closure/scripts/audit_saved.py
```

The 30-cell V4 training run used the V100 and `scripts/run_supervised.sh`. Its exact command, attempts, PID history, host environment and completion marker are in `logs/sensitivity/`; per-cell `COMPLETE.json`, `epochs.json`, `best.pt` and `partial.pt` remain under `training/final/`. Do not rerun completed training or one-time test scoring merely to reproduce published numbers. The scorer is guarded against overwriting its final metrics CSV. The initial stopped attempt is under `training/invalidated_pre_amendment/` and `logs/sensitivity/attempt_0_20261115T145427Z.log`.

To check existing results without training:

```bash
PYTHONPATH=. python final_blr_results/controlled_validation_v4_review_closure/scripts/verify_and_score.py --stage verify
MPLCONFIGDIR=/tmp/mpl_v4 PYTHONPATH=. python final_blr_results/controlled_validation_v4_review_closure/scripts/analyze_sensitivity.py
PYTHONPATH=. python final_blr_results/controlled_validation_v4_review_closure/scripts/summarize_training.py
PYTHONPATH=. python final_blr_results/controlled_validation_v4_review_closure/scripts/build_tables.py
MPLCONFIGDIR=/tmp/mpl_v4 PYTHONPATH=. python final_blr_results/controlled_validation_v4_review_closure/scripts/plot_audits.py
MPLCONFIGDIR=/tmp/mpl_v4 PYTHONPATH=. python final_blr_results/controlled_validation_v4_review_closure/scripts/verify_v4.py
PYTHONPATH=. pytest -q tests/test_physics_v2.py
```

`analyze_sensitivity.py` rereads saved exposed-test predictions and recomputes the six frozen V4 paired contrasts, seed differences and common wind-cone diagnostics. `plot_audits.py` regenerates five numerical figures from saved CSVs. `scripts/replay_penalty_gradients.py` requires CUDA and replays one frozen training batch through selected saved checkpoints without any optimizer step; its completed supervised run is `logs/gradient_replay/`, and numerical output is `PENALTY_GRADIENT_REPLAY.csv`. The first replay attempt failed because cuDNN GRU backward requires training mode; the later attempt succeeded without weight updates. Do not mistake module training mode for model training.

The final archive can be recreated with `MPLCONFIGDIR=/tmp/mpl_v4 PYTHONPATH=. python final_blr_results/controlled_validation_v4_review_closure/scripts/package_v4.py`; its external receipt is `verification/ZIP_VERIFICATION.json`. Repackaging after any documentation edit changes the archive SHA-256 and requires a new receipt.

The score-producing command was launched once with `SUPERVISED_MAX_RESTARTS=0` after all 30 checkpoints passed validation-only verification; details are in `logs/test_score/` and `verification/test_unlock.json`. It must not be rerun to select a favorable model. The 14,583 scored station-hour pairs at each horizon are from an exposed test period. Weather archive release times and sensor ingestion latencies remain unknown. No new independent spatial fold or road-level evaluation was performed.

Selected V4 checkpoint and prediction hashes are in `verification/CHECKPOINT_MANIFEST.csv` and `verification/PREDICTION_MANIFEST.csv`. Archive member hashes and the ZIP SHA-256 are generated in the final packaging step. The source archive is a research record, not an independent backup of V3 raw data. External USB backup remains unverified.
