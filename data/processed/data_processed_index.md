# Processed Data Index

This is the canonical map for `data/processed`.

## Folder Layout

| Folder | What it contains | Why it exists |
|---|---|---|
| `audits/` | File timestamp audits and inventory snapshots | Verifies recency and traceability of processed artifacts |
| `airquality/` | Raw airquality parquet copies | Non-station raw dependency mirror for processed-only environments |
| `checkpoints/` | Ingestion and pull checkpoints | Preserves resume state and source metadata snapshots |
| `gapfill/` | Gapfill benchmarking, policy, and derived station-layer artifacts | Stores method evaluation outputs and full imputation lineage |
| `graph/` | Graph tensors and node/station mappings | Holds the topology graph, PyG graph, and lookup tables used by ST-PIGNN and PyG workflows |
| `logs/` | Pull logs, event tables, and run reports | Keeps operation logs close to the processed workspace |
| `model_input/` | Final model input tensor(s) | Main temporal feature table for training/inference |
| `stations/` | Station-layer files sourced from gapfill outputs (not from raw station files) | Provides V100-ready station data fully inside `data/processed` |
| `source_docs/` | Raw source README and notes | Preserves raw source context without using a mirror folder |
| `weather/` | Raw weather parquet copies | Non-station raw dependency mirror for processed-only environments |

## File Catalog

### `audits/`

| File | Format | Purpose |
|---|---|---|
| `processed_file_timestamps_2026-04-15.txt` | Text | Timestamp listing for all files under `data/processed` at audit time |

### `airquality/`

| File | Format | Purpose |
|---|---|---|
| `2022.parquet` | Parquet | Raw air-quality history for 2022 |
| `2023.parquet` | Parquet | Raw air-quality history for 2023 |
| `2024.parquet` | Parquet | Raw air-quality history for 2024 |
| `2025.parquet` | Parquet | Raw air-quality history for 2025 |
| `2026_partial.parquet` | Parquet | Partial raw air-quality continuation for 2026 |

### `checkpoints/`

| File | Format | Purpose |
|---|---|---|
| `.checkpoint_airquality.json` | JSON | Resume state for air-quality pull workflow |
| `.checkpoint_weather.json` | JSON | Resume state for weather pull workflow |
| `.checkpoint_stations.json` | JSON | Station inventory and sensor map snapshot |
| `.checkpoint_stations_targeted_missing.json` | JSON | Resume state for targeted station recovery |
| `.checkpoint_2023_remap_retry.json` | JSON | Resume state for 2023 remap retry recovery |

### `gapfill/`

| File | Format | Purpose |
|---|---|---|
| `gapfill_benchmark_method_scores.parquet` | Parquet | Per-method benchmark metrics across pollutants |
| `gapfill_selected_method_policy.parquet` | Parquet | Selected primary/fallback gapfill policy per pollutant |
| `gapfill_benchmark_report.md` | Markdown | Human-readable benchmark summary and recommendation |
| `station_timeseries_observed_imputed.parquet` | Parquet | Full derived station layer with observed and imputed values |
| `station_timeseries_unresolved_index.parquet` | Parquet | Residual unresolved station points after gapfill build |
| `station_timeseries_imputation_summary.parquet` | Parquet | Aggregated imputation counts by method/tier/pollutant |
| `station_timeseries_imputation_build_report.md` | Markdown | Build report for the derived station layer |

### `graph/`

| File | Format | Purpose |
|---|---|---|
| `station_to_topology_node_map.parquet` | Parquet | Maps stations to nearest topology nodes with snap distance |
| `topology_graph.pt` | PyTorch | Graph payload containing node features and edge structure |
| `topology_graph_pyg_inference.pt` | PyTorch Geometric | PyG-ready graph object with train mask and physics metadata |
| `topology_nodeid_to_index_map.parquet` | Parquet | Maps topology node IDs to contiguous model node indices |

### `logs/`

| File | Format | Purpose |
|---|---|---|
| `targeted_missing_pull.log` | Text | Targeted station recovery run log |
| `targeted_missing_pull_log.md` | Markdown | Targeted station recovery summary report |
| `targeted_missing_pull_events.parquet` | Parquet | Event table for targeted station recovery |
| `remap_2023_retry.log` | Text | 2023 remap retry run log |
| `remap_2023_retry_log.md` | Markdown | 2023 remap retry summary report |
| `remap_2023_retry_events.parquet` | Parquet | Event table for 2023 remap retry |

### `model_input/`

| File | Format | Purpose |
|---|---|---|
| `model_input_node_hourly_features.parquet` | Parquet | Final hourly node-level temporal tensor for model training and inference |

### `stations/`

| File | Format | Purpose |
|---|---|---|
| `2022.parquet` | Parquet | Year-split station dataset derived from the fixed gapfill layer |
| `2024.parquet` | Parquet | Year-split station dataset derived from the fixed gapfill layer |
| `2025.parquet` | Parquet | Year-split station dataset derived from the fixed gapfill layer |
| `2026_partial.parquet` | Parquet | Partial 2026 station continuation derived from the fixed gapfill layer |

2023 is intentionally absent here because the OpenAQ station source did not yield observed 2023 rows; do not assume a missing file indicates a broken build.

### `source_docs/`

| File | Format | Purpose |
|---|---|---|
| `README.md` | Markdown | Source data notes copied from `data/raw/README.md` |

### `weather/`

| File | Format | Purpose |
|---|---|---|
| `2022.parquet` | Parquet | Raw weather history for 2022 |
| `2023.parquet` | Parquet | Raw weather history for 2023 |
| `2024.parquet` | Parquet | Raw weather history for 2024 |
| `2025.parquet` | Parquet | Raw weather history for 2025 |
| `2026_partial.parquet` | Parquet | Partial raw weather continuation for 2026 |

## V100 Usage

- Load `model_input/model_input_node_hourly_features.parquet` for temporal inputs.
- Load `graph/topology_graph_pyg_inference.pt` for the ready-to-use PyG graph.
- Load the year files under `stations/` when you need the processed station layer.
- Use `graph/station_to_topology_node_map.parquet` and `graph/topology_nodeid_to_index_map.parquet` for ID conversion.
