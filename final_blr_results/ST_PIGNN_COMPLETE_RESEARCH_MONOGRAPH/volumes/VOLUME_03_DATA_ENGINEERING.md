# Volume 3 — Data acquisition, alignment and version genealogy

<a id="volume-03"></a>

## Editorial reconstruction and evidentiary boundary

The central data distinction is observation versus imputation versus model estimate. The old gapfill layer materialized 1,073,807 pollutant rows, 777,350 of them imputed; PM2.5 specifically included 55,307 observed rows, 9,609 temporal-linear imputations and 239,734 climatology imputations. That is historical derived-layer provenance, not the corrected observed-target population. The old filtering audit found full-timeline bidirectional interpolation and climatology fits, plus an undocumented saved `y_clean` rule; these operations cannot be assumed forecast-safe. Fifteen monitoring sites provide actual PM2.5 supervision in corrected forecasting. A road coordinate is not a PM2.5 sensor. Later feature sets retained missingness provenance and observed-target masks; target-derived features at a held-out station were excluded in spatial folds. The v2i/v2j timestamp audit identified local-weather-to-UTC alignment; v2j used corrected timestamp pairing, while v2m's forecast-cutoff weather aggregation further changed input availability. Thus model rows from those rounds are exploratory cross-protocol comparisons. The original notebook's synthetic northing-derived elevation is not measured terrain. The source exhibits below document what each stage actually stored; absent exact provider versions, licenses or raw-source completeness remain unresolved rather than inferred. [EVIDENCE: historical gapfill | data/processed/gapfill/station_timeseries_imputation_build_report.md; results/old_filtering_audit.md | snapshot 1c46a4b]

## Full round-specific source exhibits

The exhibits reproduce the cited local reports as source evidence. Their original round-specific conclusions may be narrower than later findings; read the editorial reconstruction and final synthesis before treating one exhibit as the final verdict.

## Source exhibit 1: `final_blr_results/ieee_paper_evidence/methodology/DATA_AND_PREPROCESSING.md`

[EVIDENCE: `final_blr_results/ieee_paper_evidence/methodology/DATA_AND_PREPROCESSING.md` | SHA-256 `613a303927979cce1e17a9610ee95e5cd8c7960fd66a0f6ae635f366a6e81af4` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Data and preprocessing evidence

Authoritative detail is version-specific. Corrected station forecasting uses a 15-station observed PM2.5 setting, 12-hour histories, observed targets, and versioned 18-channel inputs. v2j and v2m weather aggregation/alignment are not interchangeable: v2m's cutoff-safe MLP/TCN protocol differs from historical ST-PIGNN weather inputs. Retain the documented v2j/v2m distinction; historical weather investigations are not reopened here.

Do not substitute road nodes for monitors. Road-node PM2.5 is not observed. Original notebook features contained duplicated channels and target-hour leakage; those inputs are historical-only. Synthetic northing-derived elevation is not terrain. v2r decoder used verified SRTM elevation under its stated pipeline. Full provenance and source hashes are recorded in round-specific methodology and manifests, especially `final_blr_results/final_research_v2r/reproducibility/`.

Dataset provenance is incomplete for manuscript-level reproduction wherever source downloads/versions or full raw inputs are not retained; classify those fields as UNVERIFIABLE rather than inferring them.

## Source exhibit 2: `data/processed/gapfill/station_timeseries_imputation_build_report.md`

[EVIDENCE: `data/processed/gapfill/station_timeseries_imputation_build_report.md` | SHA-256 `0f614cb97265ac06068e9bde23ce6af26b9674290e9429f4476ec9e7fccdaba4` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Station Gapfill Derived Layer Build

Run ID: gapfill_20260415_003809

#### Inputs

- Raw station files were read-only.
- Gapfill policy from evaluator was applied per pollutant.

#### Output Counts

- Derived rows (including observed + imputed + unresolved): 1073807
- Missing unresolved rows: 0
- Materialized rows (value not null): 1073807
- Imputed rows: 777350

#### Method Mix

| Pollutant | Method | Tier | Is Imputed | Rows |
|---|---|---|---|---:|
| co | observed | A | False | 53280 |
| co | temporal_climatology | C | True | 101517 |
| co | temporal_linear | B | True | 9133 |
| no2 | observed | A | False | 55403 |
| no2 | temporal_climatology | C | True | 99647 |
| no2 | temporal_linear | B | True | 8724 |
| pm10 | observed | A | False | 76266 |
| pm10 | temporal_climatology | C | True | 186692 |
| pm10 | temporal_linear | B | True | 12030 |
| pm25 | observed | A | False | 55307 |
| pm25 | temporal_climatology | C | True | 239734 |
| pm25 | temporal_linear | B | True | 9609 |
| so2 | observed | A | False | 56201 |
| so2 | temporal_climatology | C | True | 98146 |
| so2 | temporal_linear | B | True | 12118 |

#### Policy Snapshot

| Pollutant | Primary Method | Fallback Method | P90 Abs Error |
|---|---|---|---:|
| co | temporal_linear | station_median | 0.2051 |
| no2 | temporal_linear | hybrid_linear_idw | 2.4000 |
| pm10 | temporal_linear | temporal_climatology | 13.7294 |
| pm25 | temporal_linear | hybrid_linear_idw | 8.4725 |
| so2 | temporal_linear | temporal_climatology | 2.0339 |

## Source exhibit 3: `results/old_filtering_audit.md`

[EVIDENCE: `results/old_filtering_audit.md` | SHA-256 `47359fb008bd2ea807035535eaa2ab48d59e972eb83517a26b0167b9eb2816c6` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Old filtering audit

Source: `scripts/audit_old_cleaning.py`, config `configs/data_v2.yaml`, seed 42, source commit `748472042a59e910aa8924185638fab2cc236894`, 2026-10-24T15:42:28.785193+00:00.

| Rule | File:line | Type | Parameters | Rows affected |
|---|---|---|---|---:|
| Non-null station ID, parameter, value; numeric conversion; hourly mean | `scripts/build_gapfill_derived_layer.py:73-100` | per-row/aggregation | no outlier ceiling | see joined counts below |
| Gap-fill linear interpolation | `scripts/build_gapfill_derived_layer.py:246-253` | fitted across full timeline | limit 24, both directions | see old report: PM2.5 temporal-linear 9,609 |
| Climatology and median gap fill | `scripts/build_gapfill_derived_layer.py:279-315` | fitted across full timeline | hour×day medians; station median | see old report: PM2.5 climatology 239,734 |
| PM2.5 graph-node feature sanitation | `scripts/build_graph_tensors.py:154-165,178-195` | per-row after data-dependent kg/m³ inference | clip to [0,500], nonfinite/zero replaced by full-data median | not applied to canonical station target; count in this join N/A |
| Humidity / temperature graph-node sanitation | `scripts/build_graph_tensors.py:183-185` | per-row | humidity [0,100]%, temperature [10,50]°C | not applied to canonical station target; count N/A |
| Station feature interpolation and global medians | `scripts/sync_on_entry.py:335-363` | fitted across full timeline | bidirectional interpolation, ffill/bfill, column median | count N/A: separate master writer |
| `y_clean` in saved master | source writer absent from permitted scripts | UNKNOWN | empirical range [0,250], transformation not inferable from these files | see `old_vs_raw_pm25.csv` |

#### Raw-to-master join by station and UTC hour

| Old status | Raw hourly pairs | Raw min | Raw max |
|---|---:|---:|---:|
| absent_from_master | 578 | -48.940000 | 260.370000 |
| imputed_tier | 566 | -24.070000 | 99999.010000 |
| observed_tier | 54084 | -49.980000 | 647952.972500 |

Among 212 raw train station-hours above 10,000 µg/m³, 208 remain old observed-tier rows, 4 are old imputed-tier rows, and 0 are absent. The old saved `y_clean` reaches 250.0 on these rows. This does not establish the undocumented `y_clean` rule.

## Source exhibit 4: `results/weather_timestamp_check_v2i.md`

[EVIDENCE: `results/weather_timestamp_check_v2i.md` | SHA-256 `588313103ca8dd39de49a6cb39730773a2e931a83308601659cbc4c2cf5738b4` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Weather timestamp check v2i — measurement only

Source commit examined: `84b7f88dea65ff1134372f72bad3bb46b628cc75`. Measured 2026-11-05 UTC. No source data, array, model, result or threshold was changed.

| Item | Measurement |
|---|---|
| Source and request | `scripts/pull_weather.py:26-36,72-95`: Open-Meteo archive at 12.9716°N, 77.5946°E; `timezone="Asia/Kolkata"`; hourly wind speed/direction/gust, 2 m temperature, relative humidity, surface pressure. No ERA5 file was ingested separately in `data/raw/weather/`. |
| Raw file | `data/raw/weather/2022.parquet`; first three index timestamps: `2022-01-01 00:00:00`, `01:00:00`, `02:00:00`. Index dtype `datetime64[us]`, timezone **naive**. No timezone column, UTC offset or timezone attribute in the Parquet schema/pandas metadata; the API response offset was not retained. `scripts/pull_weather.py:92-94,111-113` parses ISO strings with `pd.to_datetime`, sets them as index, then writes Parquet. |
| v2 parsing | `src/stpignn/data_v2.py:41-47`: `pd.DatetimeIndex(pd.to_datetime(values))`; if naive and `assume_naive_utc=True`, `tz_localize("UTC")`, then `tz_convert("UTC").floor("h")`. `:302-305` invokes this path for weather, groups by assumed UTC hour and reindexes the UTC model timeline. `:320-324` broadcasts the weather values to all 15 station nodes. |
| Full-period sample | Five raw Parquet files covering `2022-01-01 00:00:00` through `2026-03-28 23:00:00`, 37,152 unique hourly rows (1,548 per clock hour), all timezone naive. |
| Diurnal temperature | Mean 2 m temperature by the pipeline-assumed UTC hour reaches 28.591°C at 13:00 and **28.596°C at 14:00** (maximum); 15:00 is 28.169°C. The corresponding `results/data_v2_arrays.npz` reconstructed temperature channel also peaks at **14:00**. Temperature minimum is 19.099°C at 05:00. |
| Expected UTC comparison | The fixed reference peak window is 08:30–10:30 UTC (14:00–16:00 local). Observed pseudo-UTC peak 14:00 is +3.5 to +5.5 h later than that window, or +4.5 h from its 09:30 midpoint. The code path has an **exact +5.5 h timestamp-label offset** for Asia/Kolkata local time: a raw 14:00 local record is labelled 14:00 UTC instead of 08:30 UTC. Hourly binning and the broad 13:00–14:00 temperature plateau prevent estimating that exact offset from the temperature peak alone. |
| Radiation | `shortwave_radiation` is absent from all six raw weather columns and from the v2 feature registry. Nighttime zero-radiation hours are **unavailable**, so no radiation-based cross-check can be reported. |

The [Open-Meteo historical API documentation](https://open-meteo.com/en/docs/historical-weather-api) states that requested `timezone` determines the ISO timestamps and offset; the repository request uses Asia/Kolkata and discards the response offset. The timestamp-label result follows directly from that request and `data_v2.py`'s UTC localization. It is a measurement of stored data and code, not a model-performance correction.

**Stored arrays affected:** `results/data_v2_arrays.npz` (`features` weather channels 5–11 and `raw_wind_degrees`), derived `results/data_v2g_arrays.npz`, and fold-local rebuilds made by `src/stpignn/data_v2.build`. `results/data_v2_fit.json`, `feature_registry.json`, `input_fix_v2g.json`, selection tables and model checkpoints inherit the aligned weather inputs or its fitted statistics.

**Weather-dependent result families:** `results/baselines_v2_predictions.parquet`, `baselines_v2b_predictions.parquet`, `neural_predictions_v2.parquet`, `neural_predictions_v2b.parquet`, `neural_predictions_v2c.parquet`, `gate_v2b.csv`, `gate_v2c.csv`, `benchmark_v2g.csv`/`.md` and `benchmark_predictions_h*_v2g.parquet`, `lambda_sweep_v2g.csv` and `lambda_predictions_v2g/*.parquet`, `dem_study_v2h.csv` and local `dem_predictions_v2h.parquet`, `sensor_density_v2h.csv`, `loso_summary_v2*.csv`, `loso_decision_v2g.csv`, `loso_groupdro_v2h.csv`, `conformal_v2h.csv` and local `conformal_predictions_v2h/*.parquet`, and derivative `protocol_inflation_v2h.csv`. Weather-independent persistence and station-mean components inside those comparisons do not inherit the weather feature shift. `citywide_precheck_v2h.md` counts raw weather sources but has no trained metric. This is a source-dependency list, not evidence that each numerical result changes by a specified amount.

SHIFT CONFIRMED

## Source exhibit 5: `final_blr_results/baselines/v2m/methodology/weather_availability_audit.md`

[EVIDENCE: `final_blr_results/baselines/v2m/methodology/weather_availability_audit.md` | SHA-256 `18cde6e7078d8911d986eb5c20779899f0cd07e5282f3560002b65fcbd2800bf` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Corrected v2j weather availability at forecast origin

Read-only audit of `scripts/pull_weather.py`, `src/stpignn/data_v2.py`, `scripts/benchmark_v2j.py`, `results/data_v2j_fit.json`, five raw weather Parquets, and existing saved prediction keys. No model fitting or test-score selection. Source HEAD at audit start `b0c401b`.

`scripts/pull_weather.py` obtains six **historical** variables from `https://archive-api.open-meteo.com/v1/archive` with `timezone=Asia/Kolkata`; it stores naive hourly local labels and no forecast issue/release time. `data_v2.py` subtracts 5h30m, producing actual :30 UTC record timestamps, then constructs each UTC hour `c` from records at `c−00:30` and `c+00:30`. `benchmark_v2j.py` sets forecast cutoff `c=target_time−h` and includes the feature row at `c` as the **last** of its 12 input hours. Therefore that last row incorporates the historical weather record timestamped **30 minutes after the forecast origin** whenever both records exist.

Example: target `2025-09-23 00:00:00+00:00` at h=1 has cutoff `2025-09-22 23:00:00+00:00`; its weather feature averages `2025-09-22 22:30:00+00:00` and `2025-09-22 23:30:00+00:00`. The latter is future relative to issue time. The same weather channels are broadcast to the 15 station inputs. This is an availability problem for operational forecasting even though the target PM2.5 observation itself is withheld.

| Horizon h | Existing test pairs | After-cutoff record present | Future temperature in mean | All six future values in mean |
|---:|---:|---:|---:|---:|
| 1 | 14583 | 14563 | 14563 | 14563 |
| 3 | 14583 | 14571 | 14571 | 14571 |
| 6 | 14583 | 14583 | 14583 | 14583 |
| 12 | 14583 | 14583 | 14583 | 14583 |
| 24 | 14583 | 14583 | 14583 | 14583 |

Array-level check at a scored h=1 forecast cutoff `2025-09-23 02:00:00+00:00`: temperature records at `01:30` and `02:30` UTC are 20.7°C and 22.2°C. The stored standardized v2j temperature channel (index 7), decoded with train-fit mean/SD, is 21.45000°C, matching their 21.45°C mean. Thus the later observed value actually enters the model input, beyond a code-path inference.

All five horizons and all original target pairs were retained in this audit; no favorable subset was selected. The source is retrospective archive/reanalysis, not an archived operational weather forecast. The raw files lack issue times or release latencies, so even `c−00:30` cannot be certified operationally available; the `c+00:30` record is definitively after the origin by timestamp. The half-hour rule was deliberately fixed in v2j, and this audit does not alter it or historical predictions.

**Methodological stop condition:** the original v2m assignment says not to permit an unavailable future observation in a forecasting input and to stop for supervisor review if temporal leakage is identified. The supervised backup exception does not waive this safeguard. Do not freeze or train the approved MLP/TCN on the unchanged v2j arrays as an operational forecast benchmark until the supervisor determines a new valid forecast-origin weather protocol. Such a change would require an explicit protocol revision and would invalidate direct input-equivalent comparison with existing v2j neural predictions unless those baselines are rerun under the new information set; no rerun is authorized here.

## Source exhibit 6: `final_blr_results/city_scale/features/feature_provenance.md`

[EVIDENCE: `final_blr_results/city_scale/features/feature_provenance.md` | SHA-256 `cf1e95842cbb85b74082a80c95c60f0b94bee382b8a70b1cdcf53109965e41f8` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Feature provenance

The corrected 15-station model takes 12 hourly steps × 18 channels. `src/stpignn/data_v2.py` constructs 13 physical channels (five station pollutants, wind speed/gust, temperature, humidity, pressure, circular wind sine/cosine, SRTM elevation). `scripts/benchmark_v2j.py:Context` adds `lag_is_imputed` and four UTC calendar sine/cosine channels. Train-only causal fill and train-fitted scaling apply to physical channels; v2m explicitly transforms PM2.5/PM10 to standardized log1p space. The final output adds the standardized log1p residual anchor and reconstructs concentration by `expm1(z * target_sd + target_mean)`. The anchor is the latest observed PM2.5 at or before cutoff for each monitored station, falling back to a train-only station mean. These computations are station specific, not available as measured histories on unmonitored roads.

The historical v2j weather series subtracts 5 h 30 min from local-clock timestamps, then averages corrected c−30 and c+30 weather. v2m chooses the most recent corrected record at or before cutoff c (normally c−30) and therefore has a different information set. Neither protocol validates a spatially differentiated road weather field; one known raw request coordinate was found. The v2m data file `final_blr_results/baselines/v2m/data/data_v2m_arrays.npz` SHA-256 is `8dfe2a3eebdd7900c86d738c1225c1941ac716305282c2efc17a5da8c4bb84d5`. Its fit record is adjacent. The corrected v2j array and fit live under `results/` and remain unchanged.

The OSM graph has static 17-channel `x` and 16 road-edge channels (length plus 15 highway indicators). `data/processed/model_input/model_input_node_hourly_features.parquet` contains 1,932,700 node-hour rows over only 22 nodes and 87,850 hours. Its imputed pollutant fields are not road-node observations. Exactly 154,880 of 154,902 road nodes have no stored temporal rows. The 64 partitions have 16-channel dynamic arrays and omit boundary arcs. No road-node residual anchor or compatible train-fitted 18-channel feature tensor is archived. Sources: `final_blr_results/road_graph/road_graph_features.md`, `graph_measurements_v2k.json`, `scripts/build_graph_tensors.py` and `scripts/citywide_precheck_v2h.py`.

## Source exhibit 7: `final_blr_results/city_scale/features/feature_validation.md`

[EVIDENCE: `final_blr_results/city_scale/features/feature_validation.md` | SHA-256 `83f3965c2f767612e74d1f6aafeef1244703aded2c7d0271d318bcc1df540907` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Feature and checkpoint gate

| Required item | Verified state | Verdict |
|---|---|---|
| Station input, 12 × 18 and 15 monitored nodes | Corrected v2j/v2m arrays and builder document it | COMPATIBLE for their own station protocols |
| Road tensor x and edge attributes | Static 17 channels; 16 road length/category edge channels | BLOCKED for direct corrected station-model use |
| Complete cutoff-aligned road-node pollutant history | Stored at only 22 road nodes; 154,880 absent | BLOCKED |
| Residual PM2.5 anchor at unmonitored road nodes | No observed history or validated estimate | BLOCKED |
| Citywide differentiated weather with source grid provenance | One known raw source coordinate; no source-grid mapping | UNVERIFIABLE |
| Corrected v2j ST-PIGNN/λ0/Laplacian weights | Saved predictions exist, matching neural checkpoints not archived | UNVERIFIABLE for IG; BLOCKED for city inference |
| v2m MLP/TCN weights | 50 matching station-model checkpoints and cutoff-safe array | COMPATIBLE for station-only IG after wrapper check; BLOCKED for graph inference |
| Legacy root citywide and `results/checkpoints_v2*` weights | Different historical protocols and no demonstrated corrected feature/scaler equivalence | APPROXIMATE WITH ASSUMPTIONS as historical artifacts; BLOCKED as corrected substitutes |

**Overall corrected full-city compatibility: BLOCKED.** No small, medium or full road-subgraph predictive forward pass is admissible under the frozen gate. Numerical shape or V100 capacity cannot repair missing source features and checkpoint lineage. Existing road-node PM2.5 fields are legacy/imputed features, not 154,902 observed labels. The v2m station-only checkpoint path remains viable for descriptive IG of MLP/TCN, without implying any ST-PIGNN physics explanation.

## Source exhibit 8: `final_blr_results/road_graph/road_graph_features.md`

[EVIDENCE: `final_blr_results/road_graph/road_graph_features.md` | SHA-256 `ee2bf029891aa14c80c134829cc46a27c13ad586457a12f90a4f70e1f8d4414d` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Road-node feature coverage and weather fidelity

Sources: `scripts/build_graph_tensors.py`, `scripts/pull_weather.py`, `scripts/citywide_precheck_v2h.py`, `src/stpignn/data_v2.py`, `results/citywide_precheck_v2h.md`, `data/processed/model_input/model_input_node_hourly_features.parquet`, `results/data_v2j_fit.json`, and `graph_measurements_v2k.json`.

The serialized road graph has a static 17-channel node vector: five station pollutants, six weather variables, five city pollutants, and SRTM elevation. Its 16 edge channels are length plus 15 highway category indicators. Elevation and road topology exist citywide, but these static tensors do not constitute a corrected hourly forecast input. The node-hour parquet has 1,932,700 rows across **22 nodes and 87,850 hours**, leaving **154,880 road nodes without stored temporal rows**. PM2.5 is non-null in these rows, but the legacy feature field includes imputation and must not be treated as 1.93 million independent observed targets. Temperature is non-null in 1,493,450 rows. The 23 station-to-road mappings cannot turn the remaining nodes into observed ground truth.

Corrected v2j uses 15 stations and 18 dynamic input channels: 13 train-fitted base data features, `lag_is_imputed`, and four time-calendar features over a 12-hour history. Weather raw timestamps are shifted from Asia/Kolkata local labels by exactly 5h30m and averaged around each UTC hour. Station observations are UTC. Input pollutant and target transformations are train-only, with PM2.5 lag and target in the same standardized log1p space. The citywide static vector has different dimensions, content, temporal alignment, normalization provenance and road edge representation. Legacy citywide weather and pollutant values were built before the corrected weather rule. Raw weather degrees are circular and require consistent handling in wind advection.

W8 found one raw Open-Meteo request at 12.9716°N, 77.5946°E. Broadcasting that single source would make every city's node weather series identical; it is a projected behavior, not a measured completed citywide mapper. Five of the 22 stored node-hour series duplicate one another. The repository contains no archived source-grid metadata or coordinate-to-grid-cell mapping proving how many distinct meteorological cells cover Bengaluru. This audit therefore cannot distinguish coarse source resolution from lost variation in an unarchived feature builder. Valid differentiated meteorology may be obtainable from a documented multi-grid source, but availability has not been verified. No invented high-resolution interpolation or concentration pseudo-labels are used here.

## Source exhibit 9: `final_blr_results/citywide_extension/v2o/ROAD_NODE_FEATURE_PROVENANCE.md`

[EVIDENCE: `final_blr_results/citywide_extension/v2o/ROAD_NODE_FEATURE_PROVENANCE.md` | SHA-256 `1c9b43e910d090aaf822cfc3e239f13f29e3e92bd370dadf1a96d474e33f8b07` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Road-node input provenance

The v2o bridge needs road geometry and contemporaneous monitor observations, not the incompatible 17-channel legacy road tensor. Raw OSM node coordinates come from `data/graphs/bangalore_utm_nodes.parquet` in EPSG:32643; `osmid` and the original row index are preserved. SRTM-derived elevation is joined by the same ordered `osmid` and UTM coordinate from `data/processed/graph/nodes_elevation_true.parquet`, with all 154,902 values present. Elevation is recorded but not used to tune or fit IDW. This table is distinct from earlier synthetic northing-derived terrain controls.

Cleaned observed monitor PM2.5 comes from `final_blr_results/baselines/v2m/data/data_v2m_arrays.npz`, whose observed target and mask match v2j. The 0–500 µg/m³ cleaning, station IDs, UTC timeline and source hash are preserved. At each snapshot, only monitors with a real observation at that hour enter IDW. Their values are *not* road-node labels. The output has explicit `method`, `observed_road_label=False`, support count, nearest-monitor distance, hull and poor-support flags. The nearest station is a support source, not a ground truth value for nearby roads.

The only archived raw weather request identified earlier is one Bengaluru coordinate; no spatially differentiated road weather source or grid mapping has been verified. Wind, pollutant lags, emissions, traffic and complete road-node temporal model features are unavailable and are not filled with constants or copied station values. This bridge is a same-time retrospective surface and is not eligible as an h-step-ahead forecast input. `ROAD_NODE_FEATURE_REGISTRY.csv` records units, provenance, time eligibility and missingness for each output/input.
