# ST-PIGNN Ablation Results

- Run type: observed station subset
- Executed (UTC): 2026-10-16T17:28:33.130680+00:00
- Device: Tesla V100-PCIE-32GB
- Epochs per variant: 15
- MAE/RMSE: µg/m³. PVR: upwind edges with normalized difference > 0.05.
- Graph: 15 mapped sensor nodes, 60 directed four-neighbor edges.
- Train: 64 windows, 2022-01-03 00:00:00 to 2025-09-23 06:00:00.
- Validation: 24 windows, 2025-09-23 07:00:00 to 2026-03-28 23:00:00.
- Observed validation targets: 94.
- Validation uses observed PM2.5 targets only; targets outside 0–500 µg/m³ are excluded.
- This station subset uses a distance-based graph and is not the paper's 154,902-node citywide evaluation.

| Model variant | MAE | RMSE | PVR | Architectural change |
| --- | ---: | ---: | ---: | --- |
| no_GRU | 30.2760 | 49.9276 | 8.78% | GRU replaced by an nn.Linear projection of all 12 spatial time steps. |
| no_GINE | 39.3264 | 53.9542 | 0.00% | GINEConv replaced by GCNConv; edge features are unused by GCN. |
| no_Physics | 40.1323 | 52.1762 | 19.26% | Advection penalty weight lambda_t fixed at 0.0. |
| no_Imputation | 40.2373 | 53.8059 | 18.92% | Imputed node targets masked; batches with no observed targets omitted. |
