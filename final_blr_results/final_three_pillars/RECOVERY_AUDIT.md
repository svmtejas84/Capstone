# Final three-pillar recovery audit

Date: 2026-11-07. Starting branch `research/bengaluru-v2r-final`, commit `52c119c320b014a285f399e8de9420d364d17614`. No research jobs were active at startup. Existing untracked v2r outputs and v2j run-control files were preserved.

## Source recovery

| Pillar | Recovered implementation/evidence | What was measured | Limitation / unsupported claim |
|---|---|---|---|
| Original city model | `notebooks/production/evaluated_wind_advection.ipynb` (SHA-256 `242d0cf3d2f95c78a011841ed2aec2e100cc8c326e6211c918a8bd70504b8161`); no notebook cells executed. `src/stpignn/legacy_canonical.py`; `gnn/model.py`; root legacy weights and artifacts inventoried in v2q. | v2q static inspection: 26 code cells, no saved outputs; 16-channel historical GINE–GRU, 64 partitions of a 154,902-node road graph, sparse snapped supervision. | Input timeline copies pollutant observations to unsensed nodes and includes a target-hour input; not a valid future road forecast. Historical checkpoint does not validate corrected v2j.
| Physics | Exact notebook penalty and `src/stpignn/legacy_canonical.py`; corrected station-graph masks/loss in `src/stpignn/physics_v2.py`; full v2l statistical audit. New standalone synthetic FV diagnostic in this directory. | v2l matched prediction/physics controls, diagnostics and statistical robustness; new synthetic FV consistency and convergence tests. | Neither historical hinge nor corrected loss is a mass balance. No validated source, diffusivity field, cell geometry, or atmospheric boundary data supports real-city conservation.
| Routing | `router/api/routes.py`, `router/edge_cost.py`, `matcher/gale_shapley.py`, `matcher/road_capacity.py`, `scripts/evaluate_routing_gs.py`, and historical snapshot preparation. | Saved seed-42 scenario: 1,000 requested trips; 444 admitted; admitted-only dose and time summaries. New toy-graph algorithm checks. | Static route field not validated on roads. API matcher only sees route capacities; the offline script has a separate shared-edge quota allocator. No independent exposure benefit or operational capacity result.
| Captum | Notebook cell 14, `src/stpignn/explain.py`, `gnn/stpignn_explain.py`; v2n Captum reports. Five v2c corrected h=1 checkpoints and three v2r corrected h=6 outer-LOSO checkpoints were recovered and strict per-example wrapper parity checked. | v2n previously completed 228 MLP/TCN IG records (85 flagged); this round completed 54 v2c ST-PIGNN and 18 v2r ST-PIGNN IG records; both new sets have zero flagged/nonfinite records. | Final corrected v2j ST-PIGNN/λ0/Laplacian checkpoint weights were not saved. Earlier 13-channel v2c and v2r fold weights are not substitutes for final v2j. No IG establishes causality or physical validity.

## Existing quantitative findings preserved

- v2l corrected station-graph penalty versus λ=0: exploratory horizon-dependent prediction effects; physics specificity and conservation unsupported. See `../physics_audit/FINAL_PHYSICS_VERDICT.md`.
- Routing: `final_blr_results/ieee_paper_evidence/methodology/ROUTING_AND_EXPOSURE.md`; 1000 OD requests under seed 42, 444 assigned. Admitted-only modeled dose increased 0.1211%; travel time increased 0.1463%. This is not a measured exposure effect.
- v2n: 228 v2m MLP/TCN IG rows, wrapper error 2.67e-5 µg/m³, zero nonfinite records, but 85 completeness flags. It is not ST-PIGNN attribution.
- This round: v2c h=1 has 54 records across five checkpoints/nine examples; wrapper max error 4.58e-5 µg/m³, max absolute completeness delta 2.15e-5 µg/m³, 0 flags. v2r h=6 outer-LOSO has 18 records across three stations; wrapper max error 7.63e-6 µg/m³, max absolute completeness delta 7.81e-6 µg/m³, 0 flags. These are distinct, exposed-data protocols and are not pooled for scientific comparisons.
- v2r: 154,902-node × three snapshots are experimental neural-assisted road estimates; the compact decoder lost to spatial controls on held-out sites.

No historical result or IEEE evidence-package artifact was overwritten. The complete final interpretation is in `FINAL_THREE_PILLARS_HANDOFF.md`.
