# V4 verification

{
  "status": "PASS",
  "v3_source_hashes": 11,
  "complete_model_horizon_rows": 80,
  "frozen_wind_contrasts": 20,
  "graph_architecture_contrasts": 15,
  "v4_fit_cells": 30,
  "v4_prediction_files": 36,
  "v4_contrasts": 6,
  "gradient_replay_rows": 21,
  "figures": 5,
  "latex_tables": 4,
  "invalidated_shuffle_attempts": 4,
  "historical_v3_tracked_diff_files": []
}

Commands: `PYTHONPATH=. python final_blr_results/controlled_validation_v4_review_closure/scripts/verify_v4.py`; `PYTHONPATH=. pytest -q tests/test_physics_v2.py` (3 passed). The V3 source-hash manifest was checked independently before and after scoring (7/7 unchanged). The test period remains exposed; computation verification is not independent validation.
