# Historical benchmark versus controlled V3 — input lineage

## Directly verified

The historical five-seed `stpignn_original` benchmark prediction files `results/benchmark_predictions_h{1,3,6,12,24}_stpignn_original_seed*_v2j.parquet` use the historical `results/data_v2j_arrays.npz` protocol (SHA-256 `649519c9d11e02c535b960642fbc35a7f79ab1916df418cbea276f3960eaa3f8`). The repaired V3 array is `data_manifests/data_v3_causal_arrays.npz` in the V3 directory, SHA-256 `bd08d733f924387da82e758d1060703dfcdd121f360b7e8765189d8b7446e202`. The old and repaired arrays have identical 37,152 hourly rows, 15 station IDs, observed PM2.5 targets and masks. An explicit join of the historical one-hour seed-11 predictions with the V3 one-hour ensemble matched all 14,583 target-time/station pairs and all target values exactly. Thus the old-versus-V3 MAE difference is not explained by a changed scored population for that comparison.

| Horizon (h) | Historical retrospective MAE | Repaired V3 true-wind MAE | V3 − historical (µg/m³) |
|---:|---:|---:|---:|
| 1 | 8.026 | 11.161 | +3.135 |
| 3 | 12.342 | 13.624 | +1.282 |
| 6 | 14.706 | 15.366 | +0.660 |
| 12 | 15.509 | 15.422 | −0.087 |
| 24 | 13.902 | 14.597 | +0.695 |

Historical numbers: `final_blr_results/ieee_paper_evidence/results/RECOMPUTED_V2J_BENCHMARK.csv`; V3 numbers: `COMPLETE_MODEL_AND_BASELINE_REGISTER.csv`, independently checked against per-pair NPZs.

The historical v2j weather builder in `src/stpignn/data_v2.py:weather_utc_half_hours,build` uses the average of records at feature hour c−30 minutes and **c+30 minutes**. The latter is after issue c, so the historical array contains future weather information under a forecast-issued-at-c interpretation. `scripts/build_data_v2j.py` saves that result. The V3 weather source instead selects the most recent archived record at or before c, usually c−30; its actual publication time is not recorded. `PROTOCOL_AMENDMENT_02.md` documents a second defect: raw station records were floored to their hour, so a c+30 PM2.5 reading could enter the feature labeled c. A full future-mutation test changed 15 PM2.5 feature cells at the issue hour. V3 shifts pollutant channels 0–4 and their observed/imputed provenance to row c−1; its residual anchor is the latest genuinely observed value strictly before c, with train-only station-mean fallback. The full mutation test passed the repaired array (`verification/full_future_mutation.json`).

Across all array cells, 77.89% of PM2.5 feature entries and all five weather-channel entries numerically differ between historical v2j and repaired V3; this descriptive array difference does not quantify the isolated effect of leakage. The architecture, optimization and selection implementations may also differ. Therefore **the historical benchmark is superseded for forecast-origin-safe performance claims**, while its results remain valid historical retrospective computations. The V3 candidate run set of 20 LR-selection and 54 final fits on an unshifted array was separately quarantined *before test scoring* and is not the old published v2j benchmark. No causal decomposition attributes the MAE gap solely to leakage. V3 itself is timestamp-causal retrospective prediction, not certified operational forecasting, because station-ingestion and archive-weather release times are unknown.
