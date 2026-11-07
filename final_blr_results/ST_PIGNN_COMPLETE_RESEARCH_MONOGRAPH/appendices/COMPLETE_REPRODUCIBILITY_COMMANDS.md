# Complete Reproducibility Commands

This register reproduces the cited source records below, retaining their original protocol and status. Later source exhibits can supersede earlier conclusions; no incompatible populations are pooled.

## Source 1: `final_blr_results/ieee_paper_evidence/reproducibility/REGENERATION.md`

[EVIDENCE: `final_blr_results/ieee_paper_evidence/reproducibility/REGENERATION.md` | SHA-256 `feeddba103b3bf71b2d06533868b32ae42cdf52292cbc4d5cbd8d1110f822f89` | snapshot `1c46a4b`]

# Regeneration instructions

This is an evidence-only consolidation. It runs no model fitting. It recomputes metrics solely from previously saved prediction parquets in preserved archives and saved v2r output.

From repository root, with pandas, pyarrow, Matplotlib and pyproj available, run the bounded evidence-only rebuild:

```sh
python final_blr_results/ieee_paper_evidence/reproducibility/rebuild_package.py
```

The orchestrator runs the individual extraction, metric verification, table, figure, and checksum scripts in order. It reads saved prediction files and writes only to the evidence package. It does not access new targets or fit models.

For original studies, use round-specific procedures only when specifically authorized: v2l `final_blr_results/physics_audit/reproducibility/regenerate_v2l.sh`, v2m `final_blr_results/baselines/v2m/reproducibility/regeneration_instructions.md`, v2r `final_blr_results/final_research_v2r/reproducibility/REPRODUCIBILITY.md`.

The original rejected manuscript and six review reports are missing. The full original bibliography therefore cannot be audited. v2l frozen p-values and intervals are cited from source artifacts and are not recalculated under a new family.

## Source 2: `final_blr_results/final_research_v2r/reproducibility/REPRODUCIBILITY.md`

[EVIDENCE: `final_blr_results/final_research_v2r/reproducibility/REPRODUCIBILITY.md` | SHA-256 `2bae3a811e0bcf15461a11f1fb07793ba137de1301c3bb0d655f9036627d7516` | snapshot `1c46a4b`]

# v2r reproducibility and provenance

## Source and environment

Protocol commit `1e2a3c3` and its prefit amendments `1416661`, `6c2ef7c` were pushed before fitting. The final source/results commit is recorded in the root handoff and `results/codex_log/RESUME.md`. The original notebook hash is `242d0cf3d2f95c78a011841ed2aec2e100cc8c326e6211c918a8bd70504b8161`. Relevant data: `results/data_v2j_arrays.npz`, `data/graphs/bangalore_utm_nodes.parquet`, `data/processed/graph/nodes_elevation_true.parquet`, `configs/data_v2.yaml`, `configs/loso_v2.yaml`. The separate station graph has 15 nodes and 60 directed edges; the road geometry has 154,902 nodes. These graphs are not interchangeable.

Execution host: Python 3.9.7, PyTorch 2.8.0+cu128, PyG 2.6.1, NumPy 1.26.4, pandas 2.3.3, SciPy 1.13.1, scikit-learn 1.6.1, PyArrow 21.0.0, NVIDIA Tesla V100-PCIE-32GB. The station folds ran under `scripts/run_supervised.sh` with durable attempt logs, per-fold checkpoints and COMPLETE markers. Peak measured fold CUDA allocation was 1,830,575,616 bytes. Road inference and decoder used deterministic CPU execution; peak RSS across city run was 1,494,616 KiB, GPU VRAM for road expansion 0. The remaining 2.9 GiB GPU allocation observed after completion belonged to a pre-existing Jupyter kernel PID 3626528, not a v2r process; no v2r worker remained active.

## Commands

```sh
python -m pytest -q tests/test_rgdr.py tests/test_physics_v2.py tests/test_rgdr_continuous_v2r.py  # 13 passed
bash scripts/run_supervised.sh status final_blr_results/final_research_v2r/citywide/station_forecasts/runs/loso_full
python final_blr_results/final_research_v2r/citywide/spatial_decoder/summarize_decoder_loso.py
bash scripts/run_supervised.sh status final_blr_results/final_research_v2r/citywide/spatial_validation/runs/decoder_loso
bash scripts/run_supervised.sh status final_blr_results/final_research_v2r/citywide/road_predictions/runs/full_city
python final_blr_results/final_research_v2r/citywide/verify_citywide_repeat.py
```

The full station campaign command, run directory and all fold configs/logs are retained in `citywide/station_forecasts/runs/loso_full/` and `citywide/station_forecasts/folds/`. Decoder source and outputs: `citywide/spatial_decoder/`. City run command is `python final_blr_results/final_research_v2r/citywide/run_citywide_supervised.py`, supervised directory `citywide/road_predictions/runs/full_city/`. Continuous RGDR test command and gate diagnostic sources are listed in `rgdr/methodology/RGDR_REPRODUCIBILITY.md`.

## Outputs, checks and gaps

Full-city outputs: three `road_predictions_*.parquet`, maps under `citywide/figures/`, `citywide_manifest.json`, `citywide_benchmarks.csv`, final decoder checkpoint and training curve. Repeat inference exactly reproduced all three decoder arrays with 0.0 maximum absolute error. Per-fold and per-file checksums are indexed in `artifact_checksums.csv` and both supplemental archives have independent ZIP CRC and member SHA-256 verification.

No independent roadside observations, calibrated uncertainty targets, independent Bengaluru dataset, external-city validation, or RGDR pilot checkpoints exist. v2r supports no claim of street-level accuracy or RGDR predictive improvement. Historical results remain unchanged. Large input datasets are not duplicated in v2r archives; regenerate only with the exact source files above and verify their manifest hashes.

## Source 3: `final_blr_results/final_three_pillars/reproducibility/REGENERATION.md`

[EVIDENCE: `final_blr_results/final_three_pillars/reproducibility/REGENERATION.md` | SHA-256 `3eecce942ef671fbbf16ab6ad10d0ef81d2db16823a42ab0ad8e9ffde3b73a63` | snapshot `1c46a4b`]

# Regeneration and verification

Repository root: `/home/jupyter-1nt23cb058/Capstone`. The original notebook was inspected statically only; no historical notebook cell was executed.

## Captum

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

## Physics and routing

```sh
python final_blr_results/final_three_pillars/physics/conservation_diagnostic.py
python final_blr_results/final_three_pillars/routing/route_correctness_diagnostics.py
python -m pytest -q router/tests/test_edge_cost.py matcher/tests/test_gale_shapley.py matcher/tests/test_road_capacity.py gnn/tests/test_plume_physics.py
```

The first two commands regenerate synthetic numerical diagnostics only. Routing benchmark metrics are historical saved results; do not regenerate using unverified road concentration fields and describe it as validation.

## Inventory and integrity

`reproducibility/build_checkpoint_manifest.py` creates the checkpoint inventory and SHA-256 list. The archived checksum manifest covers every archived file. Verify with:

```sh
python final_blr_results/final_three_pillars/reproducibility/verify_archive.py
sha256sum -c final_blr_results/final_three_pillars/reproducibility/CHECKSUMS.csv
```

No data or model checkpoint is included in the supplement archive. Current source artifacts remain at the paths listed by `captum/CHECKPOINT_MANIFEST.csv` and existing v2r reports.

## Source 4: `final_blr_results/final_routing_closure/v2t/reproducibility/REGENERATION.md`

[EVIDENCE: `final_blr_results/final_routing_closure/v2t/reproducibility/REGENERATION.md` | SHA-256 `c9074fbeda4c25899e428bed704192e1a918e43155688963956520a0c0fa2304` | snapshot `1c46a4b`]

# v2t regeneration and integrity

Run from the repository root. The original graph and station coordinate CSV must be present at the exact paths and hashes in `artifact_manifest.json`. No model training is involved.

1. `python -m pytest -q tests/test_edge_capacity_da_v2t.py matcher/tests/test_gale_shapley.py router/tests/test_edge_cost.py`
2. `PYTHONPATH=. MPLCONFIGDIR=/tmp/stpignn-v2t-mpl python final_blr_results/final_routing_closure/v2t/run_benchmark.py`
3. `python final_blr_results/final_routing_closure/v2t/analyze_results.py`
4. `PYTHONPATH=. python final_blr_results/final_routing_closure/v2t/verify_outputs.py`
5. `python final_blr_results/final_routing_closure/v2t/package_results.py`

The benchmark saves one atomic parquet per frozen cell in `batches/`; the supervised run record is in `runs/benchmark_fixed/`. Existing saved cells are reused by the benchmark script. Check `OUTPUT_INTEGRITY.json`, `archive_verification.json`, and SHA-256 values before interpreting the results. The ZIP embeds all v2t outputs and new code but omits the historical graph/station source inputs, which are separately hashed. It is a local supplement, not a self-contained environment or independent exposure validation.
