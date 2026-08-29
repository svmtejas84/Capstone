# Test Execution Guide

Run commands from the repository root:

```bash
cd /home/tejas/Downloads/Capstone
```

## Full Test Suite

```bash
python -m pytest -q
```

This discovers tests under:

- `gnn/tests/`
- `ingestion/tests/`
- `matcher/tests/`
- `router/tests/`

## Focused Backend Verification

Use this when validating route recommendations, dosimetry, and Gale-Shapley mitigation:

```bash
python -m pytest \
  router/tests/test_routes.py \
  router/tests/test_edge_cost.py \
  matcher/tests/test_commuter_model.py \
  matcher/tests/test_gale_shapley.py \
  -q
```

## Neural Explanation Smoke Check

Route responses always include deterministic route-score explanations under
`candidates[].explanation.route_score`.

ST-PIGNN neural Integrated Gradients explanations are opt-in because they load the checkpoint
and run `captum.attr.IntegratedGradients` over route-local subgraphs:

```bash
TOXICITY_INCLUDE_NEURAL_EXPLANATION=1 python -m pytest router/tests/test_routes.py -q
```

The neural explanation appears at:

```text
candidates[].explanation.neural_model
```

## Useful Single-Test Runs

```bash
python -m pytest router/tests/test_routes.py::test_route_can_allocate_corridor_different_from_raw_rank_one -q
python -m pytest gnn/tests/test_plume_physics.py -q
python -m pytest matcher/tests/test_gale_shapley.py -q
```

## Notes

- `router/inhalation_rates.py` is deprecated and retained only for old imports.
- Active route dosimetry uses `shared.physics_config.get_respiratory_minute_volume`.
- Full route API tests load the local Bangalore road graph, so they are slower
  than pure unit tests.
