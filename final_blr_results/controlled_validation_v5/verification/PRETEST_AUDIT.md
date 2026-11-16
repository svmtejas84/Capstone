# V5 pretest audit and frozen gates

The primary V5 protocol was committed/pushed as `0ce92700e264da6e2788225bef5f0a4f327035dc`, SHA-256 `64682686b29660ff336ed6893e257950ce25c3e03683f68de088f6a808825266`, before any V5 fit. Amendment 01 (`6f1f2e1`) added ten six-hour lag-matched graph cells before any V5 test scoring. Amendment 02 (`77d2e66`) corrected the L1 missing-daily-lag fallback to match the saved simple baseline before any lag fit or V5 test score. The original protocol file and hash remain unchanged. `SOURCE_HASHES.csv` and both amendment hash manifests record the source versions. No V3/V4 source or result artifact was edited.

Read-only input verification: **7/7 V3** `data_manifests/source_checksums.csv` and **11/11 V4** `SOURCE_HASHES.csv` entries existed and matched SHA-256. The repaired causal array matches `bd08d733f924387da82e758d1060703dfcdd121f360b7e8765189d8b7446e202`. `scripts/preflight.py` passed deterministic directed-degree-preserving rewiring, recomputed UTM edge distance, strict-prior L1 source, exact L1 fallback parity on a frozen training batch, future-target mutation invariance and common train target masks. Four V100 one-batch forward/backward smoke tests yielded finite gradients and recorded input shapes/parameter counts. `scripts/verify_cutoff_all_horizons.py` passed index-only cutoff checks for all five horizons and 14,583 scored pairs each. These tests establish timestamp ordering, not operational publication latency.

Saved same-hour-yesterday predictions were independently recomputed: h=1,3,6,12 MAE **14.130312 µg/m³** each; h=24 MAE **14.972188 µg/m³**. At h=24 its saved prediction array is byte-for-byte value-equal to persistence; the other four horizons differ. This follows the frozen T−24 eligibility rule and does not depend on the V5 neural fits.

Test commands that ran successfully:

```text
PYTHONPATH=. MPLCONFIGDIR=/tmp/mpl_v5 python final_blr_results/controlled_validation_v5/scripts/train_graph_lag.py --stage smoke
PYTHONPATH=. MPLCONFIGDIR=/tmp/mpl_v5 python final_blr_results/controlled_validation_v5/scripts/train_fairness.py --stage smoke
PYTHONPATH=. MPLCONFIGDIR=/tmp/mpl_v5 python final_blr_results/controlled_validation_v5/scripts/preflight.py
PYTHONPATH=. python final_blr_results/controlled_validation_v5/scripts/verify_cutoff_all_horizons.py
PYTHONPATH=. pytest -q tests/test_physics_v2.py   # 3 passed
PYTHONPATH=. pytest -q final_blr_results/baselines/v2m/tests/test_cutoff_data.py   # 3 passed
```

The first preflight attempt had a test assertion using `np.array_equal` on arrays containing NaNs; it failed because NaNs are not equal by default. The assertion was repaired with `equal_nan=True`, with no change to data or training code. The graph supervisor's initial finalizer exited code 2 after all 50 fits because `run_stage.sh` was edited while the active Bash process still had it open. The supervisor's next attempt verified and skipped all complete cells and exited 0. Both attempts and their exact logs are preserved. This was a process-wrapper read race, not a model fit failure. The graph stage used 1,074.044 recorded V100 fit seconds; the lag stage follows sequentially. No new-model exposed-test score existed at this pretest audit.

Additional reuse check: V5 `scripts/verify_reused_predictions.py` confirmed all 13 reused V3/V4 zero/regularizer ensemble NPZs equal the arithmetic mean of their five saved seed predictions exactly (maximum absolute difference 0.0). Receipt: `verification/REUSED_PREDICTION_VERIFICATION.json`. This check used saved predictions only; it did not unlock V5 test scoring or influence V5 training.
