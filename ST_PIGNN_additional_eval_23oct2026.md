# ST-PIGNN additional evaluation — 23 October 2026

## Exact file paths

Repository: `/home/jupyter-1nt23cb058/Capstone`

| Role | Path |
| --- | --- |
| Citywide road graph | `data/graphs/bangalore_utm.graphml` |
| PyG inference graph tensor | `data/processed/graph/topology_graph_pyg_inference.pt` |
| Station timeline and targets | `data/processed/graph/master_scaled_checkpoint.parquet` |
| Node index mapping | `data/processed/graph/topology_nodeid_to_index_map.parquet` |
| Projected station coordinates | `data/processed/graph/nodes_elevation_true.parquet` |
| Temporal inference features | `data/processed/model_input/model_input_node_hourly_features.parquet` |
| Existing checkpoint | `citywide_stpignn_best.pt` |
| Routing snapshot generator | `scripts/prepare_routing_snapshot.py` |
| Routing evaluator | `scripts/evaluate_routing_gs.py` |
| LSO-CV, IDW, kriging evaluator | `scripts/evaluate_station_lso.py` |
| Shared 15-station sample builder | `scripts/stpignn_ablation_dem.py` |
| Report generator | `scripts/write_additional_eval_report.py` |
| Routing snapshot with `predicted_pm25` | `data/processed/evaluations/routing_snapshot.graphml` |
| Trip-level routing log | `data/processed/evaluations/routing_trip_results.csv` |
| Routing summary | `data/processed/evaluations/routing_results.json` |
| Station prediction log | `data/processed/evaluations/station_lso_predictions.csv` |
| Station fold metrics | `data/processed/evaluations/station_lso_metrics.csv` |
| Station configuration and metrics | `data/processed/evaluations/station_lso_results.json` |

## Reproduction

```bash
cd /home/jupyter-1nt23cb058/Capstone
python scripts/prepare_routing_snapshot.py
python scripts/evaluate_routing_gs.py --graph data/processed/evaluations/routing_snapshot.graphml --trips 1000 --max-routes 3 --seed 42
python scripts/evaluate_station_lso.py --epochs 5 --train-windows 96 --validation-windows 96 --seed 42
python scripts/write_additional_eval_report.py
```

## Methods and interpretation

### Routing

1. OSMnx loads a directed road graph. The snapshot generator selects the largest strongly connected component within a 1.5 km radius of the median projected road-node coordinate. It evaluates the existing ST-PIGNN checkpoint on the latest available 12-hour feature window and sets each directed edge's `predicted_pm25` to the mean of its endpoint predictions, clipped to 0–120 µg/m³. This is one fixed predicted exposure snapshot, not measured exposure on 1,000 real commutes.
2. NetworkX A* minimizes edge `length` in metres. Its projected-coordinate Euclidean heuristic is multiplied by the minimum edge-length-to-straight-line ratio, making it an admissible lower bound by the triangle inequality. Parallel OSM edges are collapsed by retaining the shortest edge together with that edge's PM2.5 estimate.
3. Edge time is `length / 15000` hours. Edge dose is `predicted_pm25 × 3.5 m³/hour × time_hours`, in µg. Trip dose and time are sums over directed edges.
4. Each edge receives an integer quota `clip(floor(12 × median_edge_PM2.5 / max(edge_PM2.5, 0.01)), 1, 48)`. The median is computed from the prediction snapshot, so the capacity changes across its actual PM2.5 range. Higher PM2.5 means lower simultaneous commuter capacity. A fixed seed samples 1,000 origin–destination pairs from the strongly connected component.
5. Each commuter proposes routes in ascending dose order. Each edge tentatively retains applicants ranked by lower total route dose, shorter time, then commuter ID. Rejected commuters release all edge reservations and propose their next route. This is a Gale–Shapley-style deferred-acceptance heuristic for paths that consume multiple edges; path bundles do not generally satisfy the substitutability assumptions required for a formal global stability guarantee. Unmatched trips are counted, and both methods are compared on the same admitted trips.

### Leave-station-out validation

1. Select the 15 distinct physical PM2.5 station nodes in the processed graph timeline. `KFold(n_splits=5, shuffle=True, random_state=42)` assigns three whole stations to each validation fold.
2. Build the existing four-nearest-neighbour directed station graph from UTM coordinates (60 directed edges). For each fold, instantiate a fresh PyTorch Geometric ST-PIGNN. During training, create an induced graph of only the 12 known stations; the three held-out stations have no nodes, edges, features, targets, gradients, or message paths in an optimizer step. Training labels are physical observations in the 0–500 µg/m³ range only; imputed targets are excluded.
3. At validation, restore hidden nodes as query receivers. Retain known-to-known and known-to-hidden edges only, suppress all ten station-derived pollutant feature channels at hidden nodes for every history hour, and score only observed PM2.5 targets at those three nodes. Weather and geographic edge features remain available. This directed query construction prevents hidden-node messages from reaching known-node embeddings.
4. Use 96 chronological training windows (2022-01-03 00:00:00 to 2025-09-23 06:00:00) and 96 later validation windows (2025-09-23 07:00:00 to 2026-03-28 23:00:00), each with 12 hourly history steps and a next-hour target. Train five epochs per fold with 32-hidden-channel ST-PIGNN, AdamW, learning rate 3×10⁻⁴, and MSE loss. Predictions are converted from the project's normalized target by multiplying by 342.9356. This is a station-subset retraining experiment, not an evaluation of the pre-trained 154,902-node citywide checkpoint.
5. Score MAE = mean |prediction − observed|, RMSE = sqrt(mean squared error), and R² on eligible hidden-station observations. A validation case requires at least three physical known-station PM2.5 observations in the final history hour; the GNN and both baselines use identical hidden-station targets. Fold sample counts differ because observations are sparse.

### Spatial baselines

- IDW uses projected UTM metre distances and weights `1 / max(distance, 10⁻⁶)²` over observed physical known-station PM2.5 readings from the final input hour. It forecasts the held-out station's next-hour target, matching the GNN cutoff. Hidden-station readings and next-hour known-station targets are never supplied.
- Kriging uses those same observed final-input-hour known-station readings in a constant-mean Gaussian-process spatial interpolator with a fixed RBF covariance of 5 km length scale and white-noise nugget 0.05, implemented with scikit-learn `GaussianProcessRegressor`. Coordinates are centred and converted to km. Its hyperparameters are fixed before scoring; no held-out readings enter the fit. This is ordinary-kriging-style GP interpolation under an RBF variogram, not a fitted empirical-variogram geostatistical model.
- The baselines use known-station local PM2.5 observations at the forecast cutoff. The current station-subset GNN features contain scaled regional PM2.5 and weather channels, not the same local station readings; the results share targets and forecast timing but do not have identical input information.

## Results

### A* versus capacity-constrained deferred acceptance

| Metric | Distance A* | GS-style routing | Relative change |
| --- | ---: | ---: | ---: |
| Mean dose (µg) | 0.271498 | 0.271827 | -0.121% dose reduction |
| Mean time (min) | 3.536 | 3.541 | 0.146% longer |

Requested trips: **1000**; capacity-admitted trips: **444**; unmatched trips: **556**. Mean comparisons use the admitted set only.
Predicted edge PM2.5 spans **1.283–1.629 µg/m³** (median 1.307); quotas span **9–12** (median 12.0). The narrow predicted concentration range limits the observed route-dose difference. A negative dose-reduction percentage means GS-style routing increased dose. Check the checkpoint's PM2.5 calibration before using this simulation as an air-quality benefit claim.

### LSO-CV by fold

| Fold | Hidden node indices | Observed targets | GNN MAE | GNN RMSE | GNN R² | IDW MAE | IDW RMSE | Kriging MAE | Kriging RMSE |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 2125,73674,138162 | 46 | 26.976 | 33.977 | -1.372 | 23.336 | 31.334 | 25.465 | 33.283 |
| 2 | 43714,70231,143543 | 59 | 12.714 | 14.662 | -0.524 | 23.999 | 53.245 | 24.513 | 53.593 |
| 3 | 5183,7024,153451 | 28 | 16.613 | 22.878 | -0.489 | 12.977 | 16.255 | 15.672 | 18.570 |
| 4 | 36797,68289,121255 | 47 | 26.292 | 42.700 | -0.417 | 20.380 | 35.241 | 24.758 | 47.766 |
| 5 | 7199,67115,139516 | 76 | 51.180 | 87.373 | -0.110 | 47.944 | 88.201 | 48.784 | 89.287 |

### Pooled observed-station comparison

| Method | Predictions | MAE (µg/m³) | RMSE (µg/m³) | R² |
| --- | ---: | ---: | ---: | ---: |
| GNN | 256 | 29.616 | 53.994 | -0.102 |
| IDW | 256 | 29.118 | 58.277 | -0.284 |
| KRIGING | 256 | 30.968 | 60.699 | -0.393 |

All station values are in µg/m³. These measured station scores apply to the 15-node station-subset experiment. The routing comparison is a fixed model-predicted simulation and should not be described as measured clinical dose or as a formal stable matching proof.
