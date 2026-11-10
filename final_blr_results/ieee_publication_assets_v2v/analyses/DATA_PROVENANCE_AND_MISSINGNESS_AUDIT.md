# Data provenance, observed coverage, missingness, and temporal shift audit

This evidence note reads saved corrected arrays and source-building code. It does not alter historical data or prediction artifacts.

## Source-role verification

| Source | Verified role in completed work | Boundary |
|---|---|---|
| OpenAQ API / CPCB monitor records | Raw station Parquets identify Bengaluru CPCB locations; `scripts/pull_stations.py` and targeted pull scripts use OpenAQ v3. PM2.5 observations are the scored station target after documented cleaning. | Station measurements only; not road-node labels. Raw source fields and station identifiers are retained. |
| Open-Meteo archive | `scripts/pull_weather.py` requests historical weather at a Bengaluru reference coordinate and stores six hourly variables with Asia/Kolkata labels. | One reference series is broadcast across stations; archived historical values have no forecast issue/release times. The corrected v2j centered half-hour aggregation uses a record 30 minutes after its UTC hour label; a separate baseline protocol uses cutoff-safe availability. |
| OpenStreetMap-derived road graph | Stored canonical node/edge Parquets underpin road topology and projected coordinates. | Structural geometry only; no traffic, emissions, or observed PM2.5 at each road node. |
| SRTM | `nodes_elevation_true.parquet` is the verified raster-sampled elevation artifact used by corrected feature pipelines and v2r static covariates. | Remote-sensing elevation estimate, not ground survey. It is distinct from the old synthetic northing-derived proxy. |
| CAMS | No CAMS raw dataset or independently verifiable temporal CAMS inputs are part of the corrected v2j station arrays or v2r decoder data flow. CAMS-like urban pollutant channels appear in historical graph-building code/artifact pathways. | Do not describe CAMS as an input to the corrected station benchmark or v2r citywide decoder without additional source artifacts. |
| ERA5 | No separately ingested ERA5 file was found in the corrected raw-weather directory or corrected v2j data-builder source. | Do not attribute corrected model weather inputs to ERA5. |

## Evaluation coverage

The corrected station test set contains **14,583 observed station-hour target pairs** over **177 UTC days with at least one scored observation**, at eleven of fifteen modelled stations. The stated denominator is (11\times177\times24=46{,}728) possible scored-station hours, giving **31.2083% observed target coverage**. Four mapped stations have no scored test observations. The 177-day observed span is not the same as all possible station-hours in the calendar envelope. Exact calculation: `analyses/coverage_calculation.json`.

## PM2.5 distribution shift

| Split | Observed pairs | Mean | Median | SD | Q1–Q3 |
|---|---:|---:|---:|---:|---:|
| Training | 32,638 | 34.136 | 31.000 | 22.994 | 21.000–42.693 |
| Validation | 7,203 | 24.970 | 25.818 | 12.811 | 15.000–33.120 |
| Test | 14,583 | 44.426 | 36.340 | 37.072 | 24.335–53.704 |

Concentrations are µg/m³. Test mean exceeds validation mean by 19.456 µg/m³; test median exceeds validation median by 10.523 µg/m³. This makes validation-to-test transport uncertain and helps explain why held-out test metrics should not be framed as a stable future operating distribution. Raw summary: `source_data/DATA_validation_test_pm25_distribution.csv`.

## Input missingness and fill

Using the v2j forecast window construction at a six-hour horizon, the history contains 15 station nodes × 12 input hours. The fraction of those station-hour pollutant slots without an observed PM2.5 reading was:

| Split | Forecast origins | Missing observed PM2.5 slots |
|---|---:|---:|
| Training | 14,214 | 85.391% |
| Validation | 1,961 | 75.788% |
| Test | 4,063 | 76.686% |

The model receives an imputed PM2.5 lag channel plus `lag_is_imputed`; filled values are not observed measurements. For PM10, NO2, SO2, and CO, pre-fill raw missingness is very high and split-specific; the per-feature counts/fractions are in `source_data/DATA_per_feature_missingness.csv`. Weather inputs have a small set of missing raw observations near the end of the test interval; the pipeline applies bounded forward-fill and training medians. The main PM2.5 imputation uses a training-fitted PM2.5:PM10 ratio, same-timestamp spatial IDW over available monitor values, training-only hour/day climatology, then training station/global medians. This same-timestamp spatial borrowing does not use later timestamps, but it also means an imputed lag is not an independent observation.

`src/stpignn/data_v2.py:_fit_imputed_pm25` and `_causal_fill` show no backward temporal fill. The former uses same-time observations across stations, train-fitted ratios/climatology, and station/global training medians; the latter uses bounded forward-fill and training medians. These are forecast-time causal with respect to temporal ordering, subject to the separate v2j centered-weather look-ahead described above. Feature-level raw missingness and processing notes: `source_data/DATA_per_feature_missingness.csv`.

## Corrected weather protocol distinction

The retrospective centered-weather path reinterprets Open-Meteo local labels as half-hour UTC records and builds hour (c) from (c-30) min and (c+30) min values. Since a forecast window ends at (c=\text{target}-h), the (c+30) value can be unavailable at issue time. The separate forecast-cutoff-safe path uses the past half-hour value only. The publication figure separates these protocols; it does not call the historical ST-PIGNN results cutoff-safe.

## Reproduction

From the repository root:

```bash
python final_blr_results/ieee_publication_assets_v2v/scripts/analyze_saved_evidence.py
python final_blr_results/ieee_publication_assets_v2v/scripts/audit_feature_missingness.py
```

Both commands read saved arrays and code and write only under `ieee_publication_assets_v2v/`.
