# v2t routing methodology and reproduction

Protocol frozen and pushed at `d85e81c9055f95fa5b900c29e50124d1c985c963` before code modification or benchmark. The complete frozen definitions are in `ROUTING_PROTOCOL.md`; this document records their execution. The original serving matcher, historical offline allocator and corrected allocator have separate entry points.

## Sources and inputs

- Graph/concentration: `data/processed/evaluations/routing_snapshot.graphml`, SHA-256 `38e2a46792e9209af57e9c71fb17f6768e0117016e978ebc280ba96241647810`; 1,428 nodes, 3,459 raw directed arcs, EPSG:32643. `scripts.evaluate_routing_gs.load_graph` collapses parallel arcs to the shortest selected arc with matching PM. The field was built from the legacy city model and has no roadside accuracy validation.
- Station coordinates for the support stress factor: `results/stations_v2.csv`, transformed from WGS84 to EPSG:32643. Distance is a diagnostic, not uncertainty calibration.
- Demand: sorted largest strongly connected component, NumPy PCG64 seeds 11/23/37, 12/24/48 requests per batch, two distinct nodes per request; same OD list across all four concentration scenarios and methods. Total 36 batches, 1,008 scenario-request instances, 6,048 method-request rows.
- Candidate limit three; fixed cycling speed 15 km/h, RMV 3.5 m³/h. Edge dose (C\,[\mu g/m^3]\times3.5\,[m^3/h]\times L\,[m]/15000\,[m/h]) in µg. API preference uses cycling α=.60 and 8,000 m tolerance; receiver ranking uses cyclist vulnerability and `id_min=2.4`. This constant-mode design isolates path/allocation behavior.
- Route and directed-edge capacities from existing `matcher.road_capacity.route_capacity` with OSM road class/lane tags and 900-s window; one commuter consumes one unit on each traversed directed edge. Capacities stay fixed from the original field across perturbations.

## Execution and verification

`run_benchmark.py` writes one atomic parquet per frozen batch/scenario, then the aggregate parquet and three required CSVs. The supervised runner logs are under `runs/benchmark_fixed/`; the initial `runs/benchmark/` failed before output because Python could not import the repository package. The repaired run completed all 36 cells. Its first attempt returned code 0 but wrote the completion marker in the result directory rather than the supervisor run directory; two restart attempts re-read all saved cells without redoing route generation. After verifying complete outputs, the supervisor completion marker was copied into its run directory. `run_supervised.sh status` reports COMPLETE. The failed attempts and recovery are retained.

Reproduction, subject to the historical local inputs: `PYTHONPATH=. MPLCONFIGDIR=/tmp/stpignn-v2t-mpl python final_blr_results/final_routing_closure/v2t/run_benchmark.py`; then `python final_blr_results/final_routing_closure/v2t/analyze_results.py`; then `PYTHONPATH=. python final_blr_results/final_routing_closure/v2t/verify_outputs.py`. Existing batch parquet files make reruns idempotent; remove none without a new authorized protocol. `python -m pytest -q tests/test_edge_capacity_da_v2t.py matcher/tests/test_gale_shapley.py router/tests/test_edge_cost.py` passed 20/20. No GPU or neural fit was used.

## Comparisons and uncertainty

`ROUTING_PER_REQUEST_RESULTS.parquet` retains every submitted request and all six method outcomes. Every method assigned every request, so all submitted, admitted-only and common-admitted populations coincide in this bounded scenario. `PAIRED_COMPARISONS.csv` contains matched request differences by batch; `SENSITIVITY_STABILITY.csv` compares the same IDs with the original concentration scenario. Reported uncertainty is a range/2.5–97.5 percentile of nine batch-level values, not a confidence claim over independent commuters. No post-hoc subset was selected.

Runtime is measured for an entire batch including graph scenario construction, candidate generation and all six methods; it must not be assigned to a single method. Peak RAM was not recorded; GPU memory is 0 because CPU execution was used. The static concentration field, assumed RMV/speed, heuristic traffic quotas, small central area and synthetic OD demand limit external interpretation.
