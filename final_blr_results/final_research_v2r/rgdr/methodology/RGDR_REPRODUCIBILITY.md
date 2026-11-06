# RGDR reproducibility

- Binary predecessor source: `src/stpignn/rgdr.py`; frozen v2p methodology/results remain under `final_blr_results/citywide_extension/v2p_rgdr/`.
- Continuous V2 implementation: `src/stpignn/rgdr_continuous.py`; archived source copy: `continuous_v2/rgdr_continuous_v2.py`.
- Focused tests: `tests/test_rgdr_continuous_v2r.py`, `tests/test_rgdr.py`, `tests/test_physics_v2.py`; v2r command `python -m pytest -q tests/test_rgdr.py tests/test_physics_v2.py tests/test_rgdr_continuous_v2r.py` (13 passed).
- Gate diagnostic entry point: `gate_diagnostics/run_gate_diagnostics.py`; configuration and row-level summary: `gate_diagnostics/gate_diagnostics_config.json`, `gate_diagnostics/gate_diagnostics_v2r.csv`.
- Frozen horizon: 6 hours; station graph: 15 nodes/60 directed edges; τ: 4 hours from training-only median positive eligible age; eligible lookback: 24 hours; λ: 0.06 and original warm-up; source array: `results/data_v2j_arrays.npz`.
- No neural model was fit. The train-only feasibility gate failed. Resource use was CPU-only; no GPU-hour or checkpoint applies.
- Prior-art status is not established; see `final_blr_results/citywide_extension/v2p_rgdr/RGDR_PRIOR_ART_REVIEW.md`.
