# ST-PIGNN DEM mapping and ablation study: methods and results

**Run date:** 16 October 2026 (UTC). **Hardware:** NVIDIA Tesla V100-PCIE-32GB. **Status:** DEM mapped to the complete 154,902-node graph; ablation metrics measured on a smaller, chronologically held-out 15-station graph. This is a station-subset study, not the paper's full citywide evaluation.

The executable implementation is [stpignn_ablation_dem.py](../../scripts/stpignn_ablation_dem.py). The compact, automatically generated results table is [ST_PIGNN_Ablation_Results_Nov2026.md](../../ST_PIGNN_Ablation_Results_Nov2026.md). The architectural and metric conventions were taken from [evaluated_wind_advection.ipynb](evaluated_wind_advection.ipynb), the production notebook identified as the paper model.

## 1. Digital elevation model and node mapping

The DEM covers **77.45°E–77.80°E, 12.80°N–13.15°N**. The script requests the SRTM1 one-arc-second product, commonly described as approximately 30 m elevation data. The installed `elevation` package could not use its usual clipping path because `gdal_translate` and `gdalbuildvrt` were absent. The downloader therefore fetched the same public Skadi SRTM1 source listed by [elevation's datasource code](https://github.com/bopen/elevation/blob/main/elevation/datasource.py): tiles `N12E077.hgt.gz` and `N13E077.hgt.gz`. It decompressed the tiles, merged and clipped them with `rasterio`, and wrote [bangalore_srtm1.tif](../../data/dem/bangalore_srtm1.tif). The output is a 1,260 × 1,260 pixel GeoTIFF in EPSG:4326 with a `-32768` NoData value. Its raster pixel values span 717–993 m within the clipped box.

The actual [Bangalore graph node table](../../data/graphs/bangalore_utm_nodes.parquet) has 154,902 rows, with UTM Zone 43N coordinates stored as `x` and `y`. The mapping function renames those fields to `utm_x` and `utm_y`, transforms their coordinates from EPSG:32643 into the raster CRS with `pyproj` using `always_xy=True`, and computes all raster row and column indices in vectorized NumPy operations. It samples the nearest raster pixel through one masked raster read, preserves the original row order, and writes a new `elevation_true` column. Invalid, out-of-bounds, or NoData locations would remain `NaN`; none occurred for these nodes. The mapped table is [nodes_elevation_true.parquet](../../data/processed/graph/nodes_elevation_true.parquet).

| Elevation mapping check | Result |
| --- | ---: |
| Graph nodes | 154,902 |
| Nodes with valid SRTM elevation | 154,902 (100%) |
| Minimum / median / mean / maximum node elevation | 767 / 897 / 891.88 / 957 m |

`elevation_true` is a sampled DEM value in metres, rather than an independently surveyed elevation. In this study it contributes the elevation difference in station-graph edge attributes. The production notebook's citywide node feature matrix was **not** rebuilt with this column, so the citywide deployed model does not yet consume the new DEM value.

## 2. Real-data sample construction

The real ablation reads [master_scaled_checkpoint.parquet](../../data/processed/graph/master_scaled_checkpoint.parquet), keeps its `parameter == "pm25"` rows, and sorts them by timestamp and graph node index. There are 15 mapped PM2.5 station nodes in this table. Each input consists of **12 consecutive hourly steps before the target hour**, with the notebook's 11 scaled base features plus its five duplicated channels, giving 16 channels per node. This shift keeps the target hour out of the input window.

For the subset graph, each of the 15 stations connects to its four nearest other stations by UTM distance, yielding **60 directed edges**. The 16-dimensional edge tensor stores distance, UTM displacement, and the DEM elevation difference in its first four channels; the other channels are zero. Edge bearings come from the UTM displacement. The wind cone uses the median **unscaled** wind direction in degrees across station rows at the target time, and selects edges within 37.5° of the reverse edge bearing. This graph is deliberately smaller and has different topology and edge attributes from the notebook's 64 citywide partitions.

Candidate windows require an unbroken 12-hour history followed by a target hour with at least one valid observed PM2.5 value. Target values outside **0–500 µg/m³** or without finite values are masked at the node level. Eligible timestamps are divided chronologically at 80% of the PM2.5 timeline. The script then chooses evenly spaced windows from each side: 64 for training and 24 for validation. The training sample range is **2022-01-03 00:00:00 through 2025-09-23 06:00:00**; validation is **2025-09-23 07:00:00 through 2026-03-28 23:00:00**. These are selected windows across each period, not every intervening hour.

The 64 training windows contain **955 valid node targets**: 160 observed and 795 flagged as imputed. The first three variants may use all 955. `no_Imputation` masks the 795 imputed targets before computing supervised loss; its 64 windows still contain 160 observed targets. Validation uses the same 24 windows for every variant, scores **94 observed targets** only, and makes **296 upwind-edge comparisons**. Imputed validation targets never contribute to MAE or RMSE.

## 3. Model changes and training

Each variant starts from a fresh `gnn.model.STPIGNN` with seed 42, 16 input channels, 96 spatial and temporal hidden units, two graph convolution layers, and the notebook's 12-step window. All variants train for **15 epochs** with batch size 1, `AdamW` at learning rate `3e-6` and weight decay `1e-2`, gradient clipping at norm `0.3`, and CUDA float16 autocast plus `torch.amp.GradScaler("cuda")`. Validation runs with gradients disabled. No trained variant checkpoint was saved; the generated report stores aggregate metrics.

| Variant | Exact change |
| --- | --- |
| `no_GRU` | Replaces the GRU with one `nn.Linear` projection of the flattened spatial encodings from **all 12** time steps. The temporal history remains available, but there is no recurrent state. |
| `no_GINE` | Replaces each `GINEConv` with `GCNConv`; the GCN layers use graph connectivity but do not consume the 16 edge attributes. The GRU remains. |
| `no_Physics` | Fixes the advection-loss weight `lambda_t` to exactly `0.0` for every epoch, so the advection penalty is not computed. |
| `no_Imputation` | Masks node targets whose `is_imputed` flag is true in the training loader; a window with no remaining observed target would be skipped. The architecture and physics term remain. |

For the other three variants, `lambda_t = 0.060 × min(1, epoch / 25)`, matching the notebook's ramp. Over this 15-epoch run it rises from **0.0024** to **0.036** and does not reach the 0.060 cap. The advection term is the mean squared positive predicted destination-minus-source difference on selected upwind edges, after multiplying by the notebook-style sigmoid resistance based on edge attributes divided by 1,000. The target is normalized by the notebook's fixed scale **342.9356** for training.

MAE and RMSE pool all observed validation-node errors and convert them back to **µg/m³**. PVR is the fraction of selected upwind edges for which the predicted normalized destination-minus-source concentration exceeds **0.05**; it is reported as a percentage. The physics training penalty starts at a zero difference, while the evaluation PVR threshold is 0.05, as in the notebook's evaluation convention.

## 4. Measured results

| Variant | MAE (µg/m³) ↓ | RMSE (µg/m³) ↓ | PVR ↓ | Violations / comparisons |
| --- | ---: | ---: | ---: | ---: |
| `no_GRU` | **30.2760** | **49.9276** | 8.78% | 26 / 296 |
| `no_GINE` | 39.3264 | 53.9542 | **0.00%** | 0 / 296 |
| `no_Physics` | 40.1323 | 52.1762 | 19.26% | 57 / 296 |
| `no_Imputation` | 40.2373 | 53.8059 | 18.92% | 56 / 296 |

Within this single station-subset run, `no_GRU` has the lowest MAE and RMSE, and `no_GINE` has the lowest PVR. These are descriptive comparisons across four different trained models. They do **not** establish that removing a component improves the full ST-PIGNN: this run has no unablated reference row, only 15 stations, 94 observed validation targets, and one random seed. The zero PVR for `no_GINE` means none of its 296 evaluated edge comparisons crossed the chosen threshold; it is not proof of general physical compliance. The `no_Imputation` comparison also changes the amount of supervised training data from 955 to 160 targets.

## 5. Verification, reproducibility, and limits

The Python script passed `py_compile`. A synthetic raster check sampled **154,902 UTM points** and recovered the expected elevation for every point. The real DEM was checked for its CRS, extent, dimensions, NoData value, and elevation range, and the real node mapping was checked for 154,902 non-null elevations. A two-window real-data smoke run completed for all four variants before the 15-epoch V100 run. The corrected `no_GRU` version was then used for the final result table above.

The recorded environment was Python **3.9.7**, PyTorch **2.8.0+cu128**, PyTorch Geometric **2.6.1**, pandas **2.3.3**, NumPy **2.0.2**, rasterio **1.4.3**, pyproj **3.6.1**, and pyarrow **21.0.0**. The project's `pyproject.toml` declares Python `>=3.11`; the measured run nevertheless used the existing Python 3.9 virtual environment. CUDA was detected as a Tesla V100-PCIE-32GB. No repeated-seed uncertainty interval or full citywide training run was performed.

From the Capstone root, the same workflow can be run with:

```bash
./.venv/bin/python scripts/stpignn_ablation_dem.py \
  --download-dem \
  --nodes-parquet data/graphs/bangalore_utm_nodes.parquet \
  --real-ablation --epochs 15 \
  --train-windows 64 --validation-windows 24
```

The command reuses the DEM if it already exists, rewrites the mapped-node Parquet file, and replaces the compact Markdown results file. For a paper-scale claim, the next experiment needs the complete citywide partition graph, the same DEM feature in its node pipeline, an unablated reference model, and repeated-seed evaluation on a fixed held-out split.
