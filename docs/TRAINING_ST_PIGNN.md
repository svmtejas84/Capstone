# ST-PIGNN Training Playbook

This guide covers end-to-end training for the Spatio-Temporal Physics-Informed GNN implemented in `gnn/model.py`.

## Goal

Train a model that predicts next-step PM2.5 at graph nodes using:
- Spatial graph context (`GINEConv`) with `edge_attr`
- Temporal context (`GRU`) over a 12-hour window
- Supervised loss only at sensor nodes (`train_mask`)
- Physics penalty weighted by `PHYSICS_LOSS_LAMBDA`

## Required Artifacts

Generate/refresh these first:

```bash
python scripts/sync_on_entry.py
python scripts/finalize_gnn_assets.py
```

Expected files:
- `data/processed/model_input/model_input_node_hourly_features.parquet`
- `data/processed/graph/topology_graph_pyg_inference.pt`
- `data/processed/graph/topology_nodeid_to_index_map.parquet`

## Sanity Check Before Training

```bash
python - <<'PY'
import torch
import pandas as pd

df = pd.read_parquet('data/processed/model_input/model_input_node_hourly_features.parquet')
print('rows=', len(df), 'cols=', len(df.columns))

data = torch.load('data/processed/graph/topology_graph_pyg_inference.pt', weights_only=False)
data.validate(raise_on_error=True)
print('num_nodes=', data.num_nodes)
print('num_edges=', int(data.edge_index.shape[1]))
print('train_mask_true=', int(data.train_mask.sum().item()))
print('isolated=', data.has_isolated_nodes(), 'self_loops=', data.has_self_loops())
PY
```

## Tensor Shapes Used by ST-PIGNN

Input tensor for model forward:
- `x_seq`: `[B, T, N, F]`
- `edge_index`: `[2, E]`
- `edge_attr`: `[E, D]`

Output:
- `pred`: `[B, N]` (predicted PM2.5 for next step)

Loss:
- Data loss: masked MSE on `train_mask`
- Physics loss: upwind consistency penalty
- Total: `data + PHYSICS_LOSS_LAMBDA * physics`

## Suggested Feature Columns

Use stable columns already present in `model_input/model_input_node_hourly_features.parquet`:
- Station: `station_pm10`, `station_pm25`, `station_no2`, `station_so2`, `station_co`
- Weather: `weather_wind_speed_10m`, `weather_wind_direction_10m`, `weather_wind_gusts_10m`, `weather_temperature_2m`, `weather_relative_humidity_2m`, `weather_surface_pressure`
- City background: `city_nitrogen_dioxide`, `city_sulphur_dioxide`, `city_pm2_5`, `city_pm10`, `city_carbon_monoxide`

Target column:
- `station_pm25`

## Sliding Window Construction (12-hour)

1. Pivot by timestamp x node_id to build node-aligned matrices.
2. Build contiguous windows of length `T=12`.
3. For each window ending at hour `t`, predict target at hour `t+1`.

Example conventions:
- `X[k]`: features for hours `[h, h+11]`
- `y[k]`: PM2.5 for hour `h+12`

## Minimal Training Skeleton

```python
from __future__ import annotations

import torch
import pandas as pd
from torch.amp import GradScaler

from gnn.model import STPIGNN, train_step_amp

WINDOW = 12
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

def build_windows(df: pd.DataFrame, feature_cols: list[str], target_col: str):
    df = df.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Ensure deterministic node order and complete hourly alignment.
    nodes = sorted(df['node_id'].dropna().astype('int64').unique().tolist())
    times = sorted(df['timestamp'].dropna().unique().tolist())

    feat = (
        df.pivot_table(index='timestamp', columns='node_id', values=feature_cols)
        .sort_index()
        .reindex(columns=nodes, level=1)
    )
    targ = (
        df.pivot_table(index='timestamp', columns='node_id', values=target_col)
        .sort_index()
        .reindex(columns=nodes)
    )

    x_vals = feat.to_numpy(dtype='float32').reshape(len(feat.index), len(feature_cols), len(nodes))
    x_vals = x_vals.transpose(0, 2, 1)  # [time, node, feat]

    y_vals = targ.to_numpy(dtype='float32')  # [time, node]

    xs, ys = [], []
    for i in range(0, len(times) - WINDOW - 1):
        xs.append(x_vals[i : i + WINDOW])
        ys.append(y_vals[i + WINDOW])

    x_tensor = torch.tensor(xs, dtype=torch.float32)  # [B, T, N, F]
    y_tensor = torch.tensor(ys, dtype=torch.float32)  # [B, N]
    return x_tensor, y_tensor


def main() -> None:
    df = pd.read_parquet('data/processed/model_input/model_input_node_hourly_features.parquet')
    data = torch.load('data/processed/graph/topology_graph_pyg_inference.pt', weights_only=False)

    feature_cols = [
        'station_pm10', 'station_pm25', 'station_no2', 'station_so2', 'station_co',
        'weather_wind_speed_10m', 'weather_wind_direction_10m', 'weather_wind_gusts_10m',
        'weather_temperature_2m', 'weather_relative_humidity_2m', 'weather_surface_pressure',
        'city_nitrogen_dioxide', 'city_sulphur_dioxide', 'city_pm2_5', 'city_pm10', 'city_carbon_monoxide',
    ]

    x_seq, y = build_windows(df, feature_cols=feature_cols, target_col='station_pm25')

    model = STPIGNN(
        node_in_dim=len(feature_cols),
        edge_dim=int(data.edge_attr.shape[1]),
        spatial_hidden_dim=128,
        temporal_hidden_dim=128,
        gnn_layers=2,
        gru_layers=1,
        dropout=0.1,
    ).to(DEVICE)

    optimizer = torch.optim.AdamW(model.parameters(), lr=3e-4, weight_decay=1e-4)
    scaler = GradScaler(enabled=(DEVICE.type == 'cuda'))

    edge_index = data.edge_index
    edge_attr = data.edge_attr
    train_mask = data.train_mask

    # Placeholder: replace with physically derived upwind mask from wind + edge bearings.
    upwind_edge_mask = torch.zeros(edge_index.shape[1], dtype=torch.bool)

    batch_size = 2
    epochs = 5

    for epoch in range(1, epochs + 1):
        epoch_loss = 0.0
        steps = 0
        for i in range(0, x_seq.shape[0], batch_size):
            xb = x_seq[i : i + batch_size]
            yb = y[i : i + batch_size]

            metrics = train_step_amp(
                model=model,
                optimizer=optimizer,
                x_seq=xb,
                target=yb,
                edge_index=edge_index,
                edge_attr=edge_attr,
                train_mask=train_mask,
                upwind_edge_mask=upwind_edge_mask,
                device=DEVICE,
                scaler=scaler,
            )
            epoch_loss += metrics['loss_total']
            steps += 1

        print(f'epoch={epoch} loss_total={epoch_loss / max(1, steps):.6f}')

    torch.save(model.state_dict(), 'gnn/model_weights/st_pignn_v1.pt')
    print('Saved model -> gnn/model_weights/st_pignn_v1.pt')


if __name__ == '__main__':
    main()
``` 

## V100 Recommendations

- Use CUDA + AMP (`autocast` + `GradScaler`) to leverage Tensor Cores.
- Start with lower batch size (1-4 windows) and scale up if memory allows.
- If OOM occurs, reduce:
  - `spatial_hidden_dim`
  - `temporal_hidden_dim`
  - batch size

## Physics Penalty Guidance

- Current implementation supports `upwind_edge_mask`.
- For full physics behavior, compute edge-level upwind flags from:
  - wind direction at each timestep
  - edge bearings in graph metadata
- Penalty should be active only where plume transport implies directional ordering.

## Common Issues

1. `torch.load` fails on PyTorch 2.6 default
- Use `weights_only=False` for PyG `Data` artifact loading.

2. Empty masked loss
- Ensure `int(data.train_mask.sum()) > 0`.

3. Shape mismatch in training loop
- Confirm `x_seq` is `[B, T, N, F]` and `y` is `[B, N]`.

4. NaNs during training
- Check all selected feature columns are finite after temporal repair.

## Suggested Next Improvements

- Build a dedicated `scripts/train_st_pignn.py` from the skeleton.
- Add a physically grounded `upwind_edge_mask` generator.
- Add validation split and early stopping.
- Log metrics to TensorBoard/W&B.
