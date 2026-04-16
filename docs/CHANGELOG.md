# Changelog

This log records the main architecture, pipeline, model, and documentation changes in dated groups from the recent git history.

## 2026-04-01

- Hardened `scripts/build_graph_tensors.py` with physical sanitization, UTM KDTree joins, case-insensitive highway encoding, and stronger data-quality checks.
- Regenerated the canonical graph artifacts and training tensor outputs, including `data/processed/graph/topology_graph_pyg_inference.pt` and `data/processed/model_input/model_input_node_hourly_features.parquet`.
- Finalized the ST-PIGNN pipeline and phase-7 training refinements, including the resumable engine work reflected in the recent training commits.
- Updated the architecture and data docs to describe the new graph preprocessing and artifact outputs.

## 2026-03-31

- Added `scripts/finalize_gnn_assets.py` to perform temporal repair, sensor masking, PyG serialization, and validation in one pass.
- Added `gnn/model.py` with `GINEConv + GRU`, masked MSE, a physics penalty, and AMP-ready training.
- Hardened `scripts/sync_on_entry.py` to persist ratio caches, validate helper maps, emit explicit merge logging, and preserve idempotent checkpoint skips.
- Added `PHYSICS_LOSS_LAMBDA` to `shared/physics_config.py` and documented the new training flow in the docs.

## 2026-03-30

- Centralized physics configuration in `shared/physics_config.py` with Pasquill stability classes, RMV constants, canyon settings, and the city registry.
- Refactored `gnn/plume_physics.py`, `gnn/angular_diffusion.py`, and `router/edge_cost.py` to use the shared physics model.
- Added the data automation pipeline: `scripts/finalize_data_layer.py`, `scripts/build_graph_tensors.py`, `scripts/sync_on_entry.py`, and `data/check_data.py`.
- Added the main architecture and physics documentation set across `docs/ARCHITECTURE.md`, `docs/PHYSICS.md`, `README.md`, `data/README.md`, `gnn/README.md`, `router/README.md`, and `INTEGRATION_GUIDE.md`.
- Added graph parquet exports and checkpoint artifacts under `data/raw/`.

## 2026-03-29

- Expanded matcher and routing behavior with capacity-aware preferences, fallback allocation logic, and stable corridor selection.
- Added or expanded tests across ingestion and matcher components.
- Added the quickstart script and migration/checklist documentation used during the March rollout.
