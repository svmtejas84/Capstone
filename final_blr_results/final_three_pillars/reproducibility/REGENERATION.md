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
