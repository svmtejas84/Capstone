# Spatial holdout forecasting: W6 and v2r

W6 pooled MAE: ST-PIGNN 22.314 versus ridge 20.624 µg/m³; 11 scored stations, four without test observations. v2r is a separate forecast population: decoder 27.360, forecast-IDW 20.154, station mean 20.634 µg/m³. Timestamps are not independent spatial sites.

Source artifacts:
- `results/loso_per_station_v2j.csv` (SHA-256 `4d38078240e5cf5ea910538fcc7ca95a98c09f80582d271c1e8342189f8ac43b`)
- `final_blr_results/final_research_v2r/citywide/spatial_decoder/pooled_test_metrics.csv` (SHA-256 `4998f1328da203bc08ac8f36a828e64a1ee5df9f0cc84883093b5cbbf114fecf`)

Derived source data: `source_data/F05_W6_per_station.csv`.

Regenerate: `python final_blr_results/ieee_publication_assets/scripts/build_assets.py`.
