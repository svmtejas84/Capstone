# V5 final verification record

## Training and pretest gate

`logs/graph`, `logs/lag`, `logs/cross` and `logs/fairness` each have supervisor `COMPLETE` markers. The four training-stage markers are also present. The graph supervisor's initial attempt failed **after** all 50 cells were complete because its shell script was edited while Bash was parsing it; a clean restart verified/skipped those cells and exited 0. The orchestrator's first two attempts hit an immediate status/PID-file race when launching cross and fairness; the independent workers continued, completed, and orchestrator attempt 2 exited 0. All attempts and exact process IDs are retained in `logs/` and `RESUME.md`. There was no duplicate completed fit or missing seed.

Before test scoring, `PYTHONPATH=. MPLCONFIGDIR=/tmp/mpl_v5 python final_blr_results/controlled_validation_v5/scripts/verify_and_score.py --stage verify` exited **0** and reported `new_cells=160`, `status=PASS`. It checked checkpoint SHA-256, finite state tensors, array SHA, seed, horizon, epoch bounds, stage completion and all 90 fairness-grid cells. Validation-only choices and the gate were committed and pushed as `b80aa597d8cd89382720b64924986b890362749d`. `metrics/NEW_TEST_SCORES.csv` did not exist at that gate. The test unlock receipt explicitly labels the period exposed and exploratory.

## Numerical verification

| Command / check | Actual outcome |
|---|---|
| Supervised `logs/test_score` scorer | Exit 0 at 2026-11-16T02:38:58Z; 240 rows, 192 new NPZ files, 14,583 target pairs per condition |
| `scripts/analyze_v5.py` | Exit 0; 10 graph, 10 temporal, two lag-matched graph and six selected-family contrasts; 140 seed rows |
| `scripts/analyze_daily_baseline.py` | Exit 0; five matched descriptive daily-lag comparisons |
| `scripts/diagnose_v5.py` | Exit 0; 40 common actual-wind diagnostic rows; 5,817 eligible six-hour arcs |
| `scripts/replay_missing_penalties.py` | Exit 0; ten historical shuffled/rotated first-train-batch replay rows, no optimizer updates |
| `scripts/replay_fairness_gradients.py` | Exit 0; 90 grid checkpoint-local first-train-batch gradient rows; no optimizer updates |
| `scripts/summarize_training.py` | Exit 0; 225 total selected-run records, 160 new fits, 4,599.384 recorded fit seconds, six reaching epoch 30 |
| `scripts/verify_v5.py` | PASS; frozen protocol/array and 11 V4 plus 17 V5 source hashes checked; all 160 cells, 192 NPZs, 240 score rows, 28 contrasts and 140 seed rows counted |
| `scripts/verify_release.py` | PASS; all 240 score metrics recomputed from saved predictions with maximum absolute discrepancy $7.11\times10^{-15}$; four PNG/PDF/SVG triplets opened; nine CSV/LaTeX table pairs and five daily-baseline rows checked |
| `PYTHONPATH=. pytest -q tests/test_physics_v2.py final_blr_results/baselines/v2m/tests/test_cutoff_data.py` | Six tests passed |
| `python -m py_compile final_blr_results/controlled_validation_v5/scripts/*.py` | Exit 0 |

The first combined `pytest` invocation omitted `PYTHONPATH=.` and failed during collection with `ModuleNotFoundError: src`; rerunning with the repository root on `PYTHONPATH` passed all six tests. The first table export used pandas `to_latex`, which failed because this environment's Jinja2 3.0.3 is below pandas' required 3.1.2. A local deterministic LaTeX formatter replaced only the table export; model, predictions, CSV values and statistics did not change. The six table pairs then regenerated successfully.

## Assets and source preservation

Four figure triplets were generated as PNG, vector PDF and SVG. The PNGs opened with Pillow, PDFs had valid headers/trailers, SVG parsed as XML, and all PNGs exceed 1,200 by 600 pixels. F1, F2, F3 and F4 were visually inspected; F1's legend was moved below the plotted trajectories and F4's count note given an opaque background for readability. No figure depicts independent validation. Nine numerical table CSVs and corresponding LaTeX exports include the full negative grid and seed-selection register.

`PROTOCOL_FREEZE.md` remains SHA-256 `64682686b29660ff336ed6893e257950ce25c3e03683f68de088f6a808825266`; repaired array remains `bd08d733f924387da82e758d1060703dfcdd121f360b7e8765189d8b7446e202`. `verify_v5.py` checked immutable V3/V4 source manifest entries, and `git diff` showed no V3/V4 tracked scientific-result change. Historical model checkpoints, raw data, previous archives and earlier publication assets were not overwritten. The V5 local archive has its own member checksums; an external USB backup is still unverified.

## Scientific limits of verification

These checks show numerical and source consistency. They do not make the repeatedly exposed Bengaluru test independent, verify weather publication latency, create roadside ground truth, establish atmospheric conservation, or prove that the original kNN station topology is generally necessary.
