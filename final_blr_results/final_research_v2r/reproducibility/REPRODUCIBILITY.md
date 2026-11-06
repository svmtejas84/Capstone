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
