# Station-isolated and spatial-decoder evaluation

Station-isolated evaluation uses 11 scored sites (four eligible stations had no test targets). Pooled observation-weighted MAE is ST-PIGNN 22.314 versus weather/static ridge 20.624 µg/m³; equal-site mean paired difference is +1.487 µg/m³ (station-bootstrap 95% CI -2.577 to +5.328; 11 sites). Five sites favor ST-PIGNN and six favor ridge. Site 3409385 is influential. Separate six-hour decoder evaluation has pooled MAE 27.360 versus forecast-IDW 20.154; pooled and equal-site differences are distinct estimands. Repeated timestamps are not independent spatial sites.

Source artifacts:
- `results/loso_per_station_v2j.csv` (SHA-256 `4d38078240e5cf5ea910538fcc7ca95a98c09f80582d271c1e8342189f8ac43b`)
- `final_blr_results/final_research_v2r/citywide/spatial_decoder/pooled_test_metrics.csv` (SHA-256 `4998f1328da203bc08ac8f36a828e64a1ee5df9f0cc84883093b5cbbf114fecf`)

Derived source data: `source_data/F05_W6_per_station.csv`.

Regenerate: `python final_blr_results/ieee_publication_assets_v2v/scripts/build_assets.py`.
