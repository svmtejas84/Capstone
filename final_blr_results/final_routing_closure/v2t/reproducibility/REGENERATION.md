# v2t regeneration and integrity

Run from the repository root. The original graph and station coordinate CSV must be present at the exact paths and hashes in `artifact_manifest.json`. No model training is involved.

1. `python -m pytest -q tests/test_edge_capacity_da_v2t.py matcher/tests/test_gale_shapley.py router/tests/test_edge_cost.py`
2. `PYTHONPATH=. MPLCONFIGDIR=/tmp/stpignn-v2t-mpl python final_blr_results/final_routing_closure/v2t/run_benchmark.py`
3. `python final_blr_results/final_routing_closure/v2t/analyze_results.py`
4. `PYTHONPATH=. python final_blr_results/final_routing_closure/v2t/verify_outputs.py`
5. `python final_blr_results/final_routing_closure/v2t/package_results.py`

The benchmark saves one atomic parquet per frozen cell in `batches/`; the supervised run record is in `runs/benchmark_fixed/`. Existing saved cells are reused by the benchmark script. Check `OUTPUT_INTEGRITY.json`, `archive_verification.json`, and SHA-256 values before interpreting the results. The ZIP embeds all v2t outputs and new code but omits the historical graph/station source inputs, which are separately hashed. It is a local supplement, not a self-contained environment or independent exposure validation.
