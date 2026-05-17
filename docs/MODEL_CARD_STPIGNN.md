# ST-PIGNN Model Card

## Artifact

- Current checkpoint: `citywide_stpignn_best.pt`
- Archived checkpoint: `notebooks/models/phase_11_1_final/stpignn_mesh_resolution_E11_20260429_1205.pt`
- Notebook source: `notebooks/cluster_working.ipynb`
- Best epoch: 11
- Notebook validation total: 0.018886
- Notebook validation MAE/RMSE: 0.057592 / 0.061224 scaled target units
- Target scale used in notebook: 342.9356

## Model Scope

The checkpoint is a concentration/toxicity-field model. It predicts next-step PM2.5-style node values from temporal pollutant/weather features and graph structure.

The checkpoint does not learn user biology or route-level dosimetry. Inhaled dose should be computed after model inference in the routing cost layer:

```text
dose = concentration * respiratory_minute_volume(mode) * travel_time_hours
```

## Architecture

- `STPIGNN` from `gnn/model.py`
- Node input dimension: 16
- Edge attribute dimension: 16
- Spatial hidden dimension: 96
- Temporal hidden dimension: 96
- GNN layers: 2
- Temporal layer: GRU
- Saved tensor count: 26

## Training Inputs

Feature columns used by `cluster_working.ipynb`:

- `station_pm10`
- `station_pm25`
- `station_no2`
- `station_so2`
- `station_co`
- `weather_wind_speed_10m`
- `weather_wind_direction_10m`
- `weather_wind_gusts_10m`
- `weather_temperature_2m`
- `weather_relative_humidity_2m`
- `weather_surface_pressure`
- `city_nitrogen_dioxide`
- `city_sulphur_dioxide`
- `city_pm2_5`
- `city_pm10`
- `city_carbon_monoxide`

Training used station-supervised samples plus physics-only samples. The physics term is an upwind consistency penalty weighted by Gaussian plume severity.

## Validation And Handoff Checks

Run:

```bash
python scripts/evaluate_stpignn_holdout.py --max-samples 64 --horizons 1,3,6,12 --out docs/stpignn_holdout_report.json
```

The report compares:

- ST-PIGNN checkpoint predictions
- Persistence baseline
- Station-mean baseline

Use the holdout report before claiming the model generalizes beyond the notebook validation window.

Current small-sample holdout status:

- The checkpoint loads and runs.
- On the latest smoke report, ST-PIGNN beats the station-mean baseline.
- Persistence remains much stronger at 1-6 hour horizons on the sampled late slice.
- Treat the model as trained and integrated, but not yet externally validated against strong temporal baselines.

## Routing Policy

Routing is persistence-first until the learned model beats persistence on a larger holdout/backtest.

- Default route concentration source: `TOXICITY_ROUTE_MODEL=persistence`
- Opt into trained checkpoint route inference: `TOXICITY_ROUTE_MODEL=stpignn`
- Use live stream toxicity only: `TOXICITY_ROUTE_MODEL=stream`

This keeps dose-aware routing scientifically conservative while preserving the ST-PIGNN integration for experiments and demos.

## Route Recommendations And Explanations

The `/route` API returns all candidate corridors under `candidates[]`. Each
candidate includes route geometry, graph `node_ids`, distance, travel time,
mean concentration, inhaled dose, preference rank, and whether it was selected
by the stable matching layer.

Explanations are returned under `candidates[].explanation`:

- `route_score`: deterministic additive attributions for the route preference
  score. The terms decompose the same dose/distance score used by commuter
  preference ranking.
- `neural_model`: optional ST-PIGNN neural SHAP explanation. Enable with
  `TOXICITY_INCLUDE_NEURAL_EXPLANATION=1`. This uses `shap.GradientExplainer`
  against a route-local ST-PIGNN wrapper and explains the mean route prediction
  by input feature. It is opt-in because it loads the checkpoint and performs
  extra gradient passes.

Gale-Shapley mitigation is active in the route API: individual route preferences
are computed from dose and distance, segment capacities are derived from route
dose, segments rank commuters by vulnerability, and `batch_match()` selects the
stable corridor. This can intentionally return a corridor whose raw individual
rank is not 1 when that avoids over-allocating the same corridor.

## Known Limitations

- Only 23 sensor nodes are supervised by station targets.
- Physics-only samples regularize directional consistency; they are not ground-truth labels.
- Biology and dosimetry are not part of the checkpoint.
- The route API defaults to persistence because the current checkpoint has not beaten persistence on smoke holdout checks.
- `TOXICITY_ROUTE_MODEL=stpignn` enables route-local checkpoint inference for candidate route dose scoring.
- Neural ST-PIGNN SHAP explains the model prediction, while `route_score`
  explains the final recommendation score; these are related but not identical
  quantities.
- The notebook contains machine-specific paths and should be treated as provenance, not the production training entry point.
