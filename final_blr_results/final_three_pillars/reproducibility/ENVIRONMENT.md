# Environment and numerical execution

- OS/runtime: existing Jupyter environment, Python 3.9 (verified from interpreter-generated checkpoint/run metadata).
- Captum runs used PyTorch/Captum in CPU mode; GPU availability was not needed. No training occurred and GPU-hours used: 0.
- IG: 64 integration steps; wrapper parity against saved predictions checked per example. Numerical tolerances and observed maxima are reported in `captum/IG_METHODOLOGY.md` and `captum/CAPTUM_FINAL_VERDICT.md`.
- Conservation diagnostic: NumPy finite-volume synthetic cases; exact grid/time parameters, units, and tolerances are in `physics/CONSERVATION_FORMULATION.md` and `physics/NUMERICAL_TEST_RESULTS.json`.
- Routing diagnostics: Python toy graph; no full city rerun. Historical implementation/environment is described in `routing/ROUTING_IMPLEMENTATION.md`.
- Test command: `python -m pytest -q router/tests/test_edge_cost.py matcher/tests/test_gale_shapley.py matcher/tests/test_road_capacity.py gnn/tests/test_plume_physics.py`; the post-fix focused suite completed with all ten tests passing (see final log entry).

Exact package-lock snapshots for all historical artifacts were not recovered; this supplement reports environment elements verified during these runs and does not claim complete bitwise environment reproduction.
