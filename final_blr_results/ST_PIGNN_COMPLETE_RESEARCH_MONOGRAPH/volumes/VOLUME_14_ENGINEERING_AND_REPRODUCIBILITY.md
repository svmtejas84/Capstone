# Volume 14 — Execution, artifacts, backup and recovery

<a id="volume-14"></a>

## Editorial reconstruction and evidentiary boundary

The repository uses versioned data arrays and Parquet/CSV predictions, checkpoint state dictionaries, per-round manifests, frozen protocols, SHA-256 inventories and a supervised shell runner with locks, attempt logs and completion markers. Long-running jobs were recoverable only when their own outputs and markers survived; a Codex or JupyterHub session alone was not a process supervisor. Some older optimizer/RNG states and final v2j weights were never archived. Prior local ZIPs were checksum-verified, but an independent USB copy is unverified. Reproducibility must be stated per artifact: a saved prediction summary can be independently recomputed without implying full model retraining is possible. [EVIDENCE: v2k handoff | final_blr_results/FINAL_HANDOFF.md | snapshot 1c46a4b]

## Full round-specific source exhibits

The exhibits reproduce the cited local reports as source evidence. Their original round-specific conclusions may be narrower than later findings; read the editorial reconstruction and final synthesis before treating one exhibit as the final verdict.

## Source exhibit 1: `final_blr_results/archive/reproducibility_status.md`

[EVIDENCE: `final_blr_results/archive/reproducibility_status.md` | SHA-256 `81d560d50ab5b965caeeee92024db842afacd6d6d9b9473cb87d597d29167639` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Archive integrity and recovery classification

`build_archive_v2k.py` hashed 2,141 available files into `archive_integrity.csv`; `experiment_manifest.json` groups them by research question, status, source/config where known, dataset, split, seeds, checkpoint/prediction/metric/log paths, defects, and recovery class. Missing source commits/timestamps/config fingerprints are `null` or explicitly unrecorded, not inferred from current HEAD. The 318 catchall result files prevent a false claim that all family provenance is resolved. Re-run the builder after any later output changes; compare hashes before and after transfer.

Classes: v2j benchmark, W2/W7, W3, P1–P3, conformal and Group-DRO are numerically recomputable where paired predictions survive. Some legacy model weights permit an inference replay but cannot restore optimizer/RNG/epoch state. W4 saved aggregate scores need retraining for paired verification; P0's historical claimed gain is unrecoverable from available paired predictions. W8 is a data-only precheck. The manifest records per-family paths and classifications, but a status such as VERIFIED refers to checked arithmetic or structure, not a valid confirmatory claim.

**Durability:** GitHub branch HEAD was verified equal to the local source commit before this round; tracked lightweight files have a remote Git copy. The April 2026 `Capstone.tar.gz` is readable but on the same filesystem, old, and not an independent durable backup. No verified off-host backup of local prediction caches, checkpoints or datasets was found. JupyterHub home persistence after server recreation is unknown. Thus zero historical experiment families have a verified complete independent durable backup. A manifest or checksum list is not a backup.

Safe backup procedure after the supervisor supplies an institution-approved persistent destination: (1) freeze new jobs and record source commit; (2) create a path list from `archive_integrity.csv`, excluding credentials and secrets; (3) transfer the required local prediction/checkpoint/raw data files to the destination with encryption and access controls; (4) generate a destination-side SHA-256 listing or download a sample and compare every required file against this register; (5) record remote object/version IDs, retention policy, verification time and responsible owner; (6) only then mark the corresponding experiment verified durable. Do not push large datasets, sensitive data or prediction caches to GitHub without explicit approval. No backup transfer was attempted in v2k.

## Source exhibit 2: `final_blr_results/reproducibility/execution_readiness.md`

[EVIDENCE: `final_blr_results/reproducibility/execution_readiness.md` | SHA-256 `1e1c240736704a0789db2bbabac0cfa107e4d9f459759e0f9e969805b2067def` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Supervised execution readiness

Inspected `scripts/run_supervised.sh`, `docs/EXPERIMENT_RECOVERY.md`, historical execution manifests and `results/research_audit_r1/persistence_test.md`. No model training or new supervisor job was started. At phase-0 host inspection no `scripts.*` or supervisor process was active.

The wrapper uses `flock` for a single worker per run directory, `setsid`/`nohup` for terminal disconnect, per-attempt logs, a PID file, saved command, bounded automatic restarts (default two), `COMPLETE` marker, and optional atomic `checkpoint.bin` with SHA-256 sidecar. `verify` and `resume` reject a bad checkpoint pair. The manifest captures Git commit, command, Python, PyTorch/GPU, start time and run directory. Config and seeds are populated only if `EXPERIMENT_CONFIG` and `EXPERIMENT_SEEDS` are set; several historical manifests omitted these fields. The wrapper does not itself enforce CUDA, output isolation, metric validity or checkpoint state coverage; the experiment script must do so. The v2j neural benchmark explicitly requires CUDA in its source. A stale PID can mislead `status`, but the process lock is authoritative. Full host reboot stops jobs; explicit `resume` is required.

**Verdict: wrapper ready for supervised GPU runs, conditional on a future baseline script satisfying the contracts.** New outputs must be isolated under `final_blr_results/` and each approved job must set config/seeds, record source/data/split hashes, refuse CPU neural training, atomically write per-seed predictions and checkpoint metadata, skip completed cells on resume, and write `COMPLETE` only after validating all expected files. Existing v2j per-seed Parquet files permit recovery between completed seeds/horizons; they contain no optimizer/RNG state, so interrupted epoch recovery is unavailable. Older point checkpoints contain model weights and best-epoch metadata but no full training state; exact epoch resumption is unavailable. No redesign or synthetic re-test was necessary for this audit; the R1 persistence test provides existing synthetic coverage.

## Source exhibit 3: `final_blr_results/city_scale/reproducibility/regeneration_instructions.md`

[EVIDENCE: `final_blr_results/city_scale/reproducibility/regeneration_instructions.md` | SHA-256 `3a418d9dbb6d76aef4f3f397143a01e0de1a02abaa9e97acf6a900e9c87cbae5` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### v2n regeneration and limits

From `/home/jupyter-1nt23cb058/Capstone`, inspect `final_blr_results/city_scale/protocol/CITY_SCALE_PROTOCOL.md` before any replay. No new training is part of v2n. Reproducing historical v2j/v2m training bitwise is not possible from the available archive: corrected v2j neural checkpoint/optimizer/RNG state and some source provenance are missing. The saved-result tables and v2m IG described below can be regenerated if their listed inputs remain available. Do not run the historical v2m trainer.

1. Check source checksums: `sha256sum -c final_blr_results/city_scale/reproducibility/artifact_checksums.sha256` after rebuilding the sidecar if paths differ. The CSV manifest records each role/path/hash and missing classes.
2. Recreate the saved-result per-station table: `python final_blr_results/city_scale/spatial_validation/build_spatial_table.py`. It reads `results/loso_per_station_v2j.csv` and writes only the v2n table.
3. Recreate compatible station-model IG, if desired, using the recoverable supervisor command: `bash scripts/run_supervised.sh launch final_blr_results/city_scale/explainability/runs/ig_v2n_replay -- env PYTHONPATH=. python final_blr_results/city_scale/explainability/run_captum_ig.py`. The runner currently writes its v2n output files and a marker at the canonical `runs/ig_v2n` path, so for a clean comparison use a separate checkout/copy of the v2n directory or preserve the existing files and compare hashes afterwards. The source selection is deterministic and in `sample_selection.json`; it uses 18 v2m checkpoint cells, 64-step Gauss-Legendre Captum IG and two frozen baselines. Run `python final_blr_results/city_scale/explainability/plot_captum_ig.py` to regenerate the three figures from saved tensors. This is station MLP/TCN IG, not corrected ST-PIGNN IG.
4. Regenerate the inventory after all reports/figures are final: `python final_blr_results/city_scale/reproducibility/build_manifest.py`. This writes `artifact_manifest.json`, `artifact_checksums.csv` and `artifact_checksums.sha256` without modifying historical inputs. The manifest excludes itself, the checksum sidecars and the v2n archive to avoid self-reference. Re-run after any v2n code/report edit.
5. The supplemental ZIP is built with `python final_blr_results/city_scale/reproducibility/create_v2n_archive.py`, which excludes its own ZIP and records CRC/member SHA-256 checks. Its final outer SHA-256 and byte size are in the final RESUME and archive verification file.

Evaluation definitions: MAE is mean absolute error, RMSE the root mean squared error, and R² the observed-target coefficient of determination. v2j W6 LOSO tables preserve the original 11 scored station sites, four unscored folds, fixed anchor/bias strata and original paired UTC-day bootstrap. v2m paired comparisons use matched station/time targets, 2,000 UTC-day bootstrap draws and a ten-test exploratory Holm family, but historical ST-PIGNN weather differs. Captum sums signed and absolute IG separately. Wrapper tolerance is 1e−4 µg/m³; convergence flags are absolute delta >0.05 µg/m³ or relative delta >1%; nonfinite values abort. The city gate blocks road inference, so no road prediction table can be regenerated.

## Source exhibit 4: `final_blr_results/baselines/v2m/reproducibility/regeneration_instructions.md`

[EVIDENCE: `final_blr_results/baselines/v2m/reproducibility/regeneration_instructions.md` | SHA-256 `50ae9adede740c1ff1cd895ceb5657b42b53b8bb19147b98847e8ea15f6d9bf0` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### v2m recovery and regeneration

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

## Source exhibit 5: `final_blr_results/final_research_v2r/reproducibility/REPRODUCIBILITY.md`

[EVIDENCE: `final_blr_results/final_research_v2r/reproducibility/REPRODUCIBILITY.md` | SHA-256 `2bae3a811e0bcf15461a11f1fb07793ba137de1301c3bb0d655f9036627d7516` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### v2r reproducibility and provenance

#### Source and environment

Protocol commit `1e2a3c3` and its prefit amendments `1416661`, `6c2ef7c` were pushed before fitting. The final source/results commit is recorded in the root handoff and `results/codex_log/RESUME.md`. The original notebook hash is `242d0cf3d2f95c78a011841ed2aec2e100cc8c326e6211c918a8bd70504b8161`. Relevant data: `results/data_v2j_arrays.npz`, `data/graphs/bangalore_utm_nodes.parquet`, `data/processed/graph/nodes_elevation_true.parquet`, `configs/data_v2.yaml`, `configs/loso_v2.yaml`. The separate station graph has 15 nodes and 60 directed edges; the road geometry has 154,902 nodes. These graphs are not interchangeable.

Execution host: Python 3.9.7, PyTorch 2.8.0+cu128, PyG 2.6.1, NumPy 1.26.4, pandas 2.3.3, SciPy 1.13.1, scikit-learn 1.6.1, PyArrow 21.0.0, NVIDIA Tesla V100-PCIE-32GB. The station folds ran under `scripts/run_supervised.sh` with durable attempt logs, per-fold checkpoints and COMPLETE markers. Peak measured fold CUDA allocation was 1,830,575,616 bytes. Road inference and decoder used deterministic CPU execution; peak RSS across city run was 1,494,616 KiB, GPU VRAM for road expansion 0. The remaining 2.9 GiB GPU allocation observed after completion belonged to a pre-existing Jupyter kernel PID 3626528, not a v2r process; no v2r worker remained active.

#### Commands

```sh
python -m pytest -q tests/test_rgdr.py tests/test_physics_v2.py tests/test_rgdr_continuous_v2r.py  # 13 passed
bash scripts/run_supervised.sh status final_blr_results/final_research_v2r/citywide/station_forecasts/runs/loso_full
python final_blr_results/final_research_v2r/citywide/spatial_decoder/summarize_decoder_loso.py
bash scripts/run_supervised.sh status final_blr_results/final_research_v2r/citywide/spatial_validation/runs/decoder_loso
bash scripts/run_supervised.sh status final_blr_results/final_research_v2r/citywide/road_predictions/runs/full_city
python final_blr_results/final_research_v2r/citywide/verify_citywide_repeat.py
```

The full station campaign command, run directory and all fold configs/logs are retained in `citywide/station_forecasts/runs/loso_full/` and `citywide/station_forecasts/folds/`. Decoder source and outputs: `citywide/spatial_decoder/`. City run command is `python final_blr_results/final_research_v2r/citywide/run_citywide_supervised.py`, supervised directory `citywide/road_predictions/runs/full_city/`. Continuous RGDR test command and gate diagnostic sources are listed in `rgdr/methodology/RGDR_REPRODUCIBILITY.md`.

#### Outputs, checks and gaps

Full-city outputs: three `road_predictions_*.parquet`, maps under `citywide/figures/`, `citywide_manifest.json`, `citywide_benchmarks.csv`, final decoder checkpoint and training curve. Repeat inference exactly reproduced all three decoder arrays with 0.0 maximum absolute error. Per-fold and per-file checksums are indexed in `artifact_checksums.csv` and both supplemental archives have independent ZIP CRC and member SHA-256 verification.

No independent roadside observations, calibrated uncertainty targets, independent Bengaluru dataset, external-city validation, or RGDR pilot checkpoints exist. v2r supports no claim of street-level accuracy or RGDR predictive improvement. Historical results remain unchanged. Large input datasets are not duplicated in v2r archives; regenerate only with the exact source files above and verify their manifest hashes.

## Source exhibit 6: `final_blr_results/final_three_pillars/reproducibility/REGENERATION.md`

[EVIDENCE: `final_blr_results/final_three_pillars/reproducibility/REGENERATION.md` | SHA-256 `3eecce942ef671fbbf16ab6ad10d0ef81d2db16823a42ab0ad8e9ffde3b73a63` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Regeneration and verification

Repository root: `/home/jupyter-1nt23cb058/Capstone`. The original notebook was inspected statically only; no historical notebook cell was executed.

#### Captum

The v2c and v2r IG runs have durable supervisor records and completion markers:

```sh
bash scripts/run_supervised.sh status final_blr_results/final_three_pillars/captum/runs/ig_v2c
bash scripts/run_supervised.sh status final_blr_results/final_three_pillars/captum/v2r_heldout_h6/runs/ig_v2r
```

Do not rerun unless needed: the selected examples and model artifacts are already saved. To rebuild the combined row table from retained version-specific sources, first restore v2c rows from `IG_RESULTS_v2c.csv` as the root input (the combination script writes root output), then run:

```sh
python final_blr_results/final_three_pillars/captum/combine_ig_results.py
```

Runner entry points: `captum/run_v2c_ig.py`, `captum/run_v2r_heldout_ig.py`. Each uses a fixed sample selection, explicit baseline(s), wrapper comparison, 64 integration steps and record-level persistence. The v2r run status is also in `captum/v2r_heldout_h6/COMPLETE`.

#### Physics and routing

```sh
python final_blr_results/final_three_pillars/physics/conservation_diagnostic.py
python final_blr_results/final_three_pillars/routing/route_correctness_diagnostics.py
python -m pytest -q router/tests/test_edge_cost.py matcher/tests/test_gale_shapley.py matcher/tests/test_road_capacity.py gnn/tests/test_plume_physics.py
```

The first two commands regenerate synthetic numerical diagnostics only. Routing benchmark metrics are historical saved results; do not regenerate using unverified road concentration fields and describe it as validation.

#### Inventory and integrity

`reproducibility/build_checkpoint_manifest.py` creates the checkpoint inventory and SHA-256 list. The archived checksum manifest covers every archived file. Verify with:

```sh
python final_blr_results/final_three_pillars/reproducibility/verify_archive.py
sha256sum -c final_blr_results/final_three_pillars/reproducibility/CHECKSUMS.csv
```

No data or model checkpoint is included in the supplement archive. Current source artifacts remain at the paths listed by `captum/CHECKPOINT_MANIFEST.csv` and existing v2r reports.

## Source exhibit 7: `final_blr_results/final_routing_closure/v2t/reproducibility/REGENERATION.md`

[EVIDENCE: `final_blr_results/final_routing_closure/v2t/reproducibility/REGENERATION.md` | SHA-256 `c9074fbeda4c25899e428bed704192e1a918e43155688963956520a0c0fa2304` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### v2t regeneration and integrity

Run from the repository root. The original graph and station coordinate CSV must be present at the exact paths and hashes in `artifact_manifest.json`. No model training is involved.

1. `python -m pytest -q tests/test_edge_capacity_da_v2t.py matcher/tests/test_gale_shapley.py router/tests/test_edge_cost.py`
2. `PYTHONPATH=. MPLCONFIGDIR=/tmp/stpignn-v2t-mpl python final_blr_results/final_routing_closure/v2t/run_benchmark.py`
3. `python final_blr_results/final_routing_closure/v2t/analyze_results.py`
4. `PYTHONPATH=. python final_blr_results/final_routing_closure/v2t/verify_outputs.py`
5. `python final_blr_results/final_routing_closure/v2t/package_results.py`

The benchmark saves one atomic parquet per frozen cell in `batches/`; the supervised run record is in `runs/benchmark_fixed/`. Existing saved cells are reused by the benchmark script. Check `OUTPUT_INTEGRITY.json`, `archive_verification.json`, and SHA-256 values before interpreting the results. The ZIP embeds all v2t outputs and new code but omits the historical graph/station source inputs, which are separately hashed. It is a local supplement, not a self-contained environment or independent exposure validation.

## Source exhibit 8: `final_blr_results/ieee_paper_evidence/reproducibility/REGENERATION.md`

[EVIDENCE: `final_blr_results/ieee_paper_evidence/reproducibility/REGENERATION.md` | SHA-256 `feeddba103b3bf71b2d06533868b32ae42cdf52292cbc4d5cbd8d1110f822f89` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Regeneration instructions

This is an evidence-only consolidation. It runs no model fitting. It recomputes metrics solely from previously saved prediction parquets in preserved archives and saved v2r output.

From repository root, with pandas, pyarrow, Matplotlib and pyproj available, run the bounded evidence-only rebuild:

```sh
python final_blr_results/ieee_paper_evidence/reproducibility/rebuild_package.py
```

The orchestrator runs the individual extraction, metric verification, table, figure, and checksum scripts in order. It reads saved prediction files and writes only to the evidence package. It does not access new targets or fit models.

For original studies, use round-specific procedures only when specifically authorized: v2l `final_blr_results/physics_audit/reproducibility/regenerate_v2l.sh`, v2m `final_blr_results/baselines/v2m/reproducibility/regeneration_instructions.md`, v2r `final_blr_results/final_research_v2r/reproducibility/REPRODUCIBILITY.md`.

The original rejected manuscript and six review reports are missing. The full original bibliography therefore cannot be audited. v2l frozen p-values and intervals are cited from source artifacts and are not recalculated under a new family.
