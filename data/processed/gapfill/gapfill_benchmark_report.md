# Gapfill Options Evaluation

This report evaluates candidate gapfilling methods on observed data by masking known points.

## Benchmark Setup

- Sample points per pollutant: 400
- Random seed: 42
- Inputs: station files for 2022, 2024, 2025, 2026_partial (read-only)
- Methods: temporal_linear, temporal_climatology, spatial_idw, hybrid_linear_idw, station_median

## Best Method Per Pollutant

| Pollutant | Best Method | Coverage | MAE | RMSE | MAPE % | sMAPE % | P90 Abs Error |
|---|---|---:|---:|---:|---:|---:|---:|
| co | temporal_linear | 1.000 | 7.1076 | 38.5001 | 16.23 | 13.59 | 0.2051 |
| no2 | temporal_linear | 1.000 | 0.9934 | 1.9966 | 2184380.23 | 6.09 | 2.4000 |
| pm10 | temporal_linear | 1.000 | 1076.0855 | 14195.5687 | 21.75 | 9.50 | 13.7294 |
| pm25 | temporal_linear | 1.000 | 6.3701 | 31.6073 | 16.52 | 12.05 | 8.4725 |
| so2 | temporal_linear | 1.000 | 1.5454 | 12.9057 | 2509779.73 | 14.73 | 2.0339 |

## Overall Ranking

| Method | Pollutants | Avg Composite | Avg Coverage | Avg Normalized MAE | Avg sMAPE % |
|---|---:|---:|---:|---:|---:|
| temporal_linear | 5 | 5.9633 | 1.000 | 5.8962 | 11.19 |
| hybrid_linear_idw | 5 | 15.7805 | 1.000 | 15.5817 | 33.13 |
| station_median | 5 | 17.1711 | 1.000 | 16.9467 | 37.40 |
| temporal_climatology | 5 | 17.6549 | 1.000 | 17.4404 | 35.74 |
| spatial_idw | 5 | 35.5332 | 0.934 | 35.1491 | 61.27 |

## Recommendation

- Primary default: `temporal_linear`
- Policy: keep raw observations immutable and store imputed values in a separate derived layer.
- For production: attach confidence tiers (observed, high-confidence-imputed, low-confidence-inferred).

## Full Scores

| Pollutant | Method | Coverage | MAE | RMSE | MAPE % | sMAPE % | Normalized MAE | P90 Abs Error |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| co | temporal_linear | 1.000 | 7.1076 | 38.5001 | 16.23 | 13.59 | 12.3075 | 0.2051 |
| co | station_median | 1.000 | 21.8906 | 90.9852 | 555000074.68 | 39.94 | 37.9058 | 10.0000 |
| co | temporal_climatology | 1.000 | 23.3519 | 90.3559 | 541250067.33 | 37.56 | 40.4362 | 2.0064 |
| co | hybrid_linear_idw | 1.000 | 25.4276 | 87.2197 | 280484385.34 | 36.54 | 44.0305 | 80.5995 |
| co | spatial_idw | 0.990 | 60.1357 | 208.6553 | 708293888.82 | 67.45 | 104.1310 | 138.6868 |
| no2 | temporal_linear | 1.000 | 0.9934 | 1.9966 | 2184380.23 | 6.09 | 0.0547 | 2.4000 |
| no2 | hybrid_linear_idw | 1.000 | 4.5257 | 6.3226 | 10258995.02 | 24.84 | 0.2494 | 9.6430 |
| no2 | temporal_climatology | 1.000 | 6.3386 | 10.4517 | 26891812.49 | 30.95 | 0.3493 | 14.4825 |
| no2 | station_median | 1.000 | 6.6893 | 10.7102 | 25975669.44 | 33.32 | 0.3686 | 15.1260 |
| no2 | spatial_idw | 0.938 | 11.4121 | 15.1928 | 23862316.06 | 52.80 | 0.6289 | 23.6515 |
| pm10 | temporal_linear | 1.000 | 1076.0855 | 14195.5687 | 21.75 | 9.50 | 16.6545 | 13.7294 |
| pm10 | temporal_climatology | 1.000 | 1471.6965 | 17995.7567 | 65195062.56 | 39.31 | 22.7773 | 56.6407 |
| pm10 | station_median | 1.000 | 1472.9827 | 17995.6418 | 55905063.19 | 40.90 | 22.7973 | 60.0620 |
| pm10 | hybrid_linear_idw | 1.000 | 1485.4093 | 15153.5349 | 23779778.19 | 43.63 | 22.9896 | 1204.3851 |
| pm10 | spatial_idw | 0.902 | 2611.0802 | 19431.1728 | 65871932.14 | 72.33 | 40.4115 | 3067.5648 |
| pm25 | temporal_linear | 1.000 | 6.3701 | 31.6073 | 16.52 | 12.05 | 0.1930 | 8.4725 |
| pm25 | hybrid_linear_idw | 1.000 | 335.8809 | 3474.0506 | 1176680.34 | 26.01 | 10.1782 | 18.1723 |
| pm25 | temporal_climatology | 1.000 | 767.0642 | 8658.1537 | 9168797.17 | 38.26 | 23.2444 | 31.0000 |
| pm25 | station_median | 1.000 | 767.7596 | 8658.1255 | 8577550.26 | 40.00 | 23.2654 | 32.4105 |
| pm25 | spatial_idw | 0.853 | 980.7338 | 9406.8464 | 3450653.79 | 52.84 | 29.7192 | 41.2713 |
| so2 | temporal_linear | 1.000 | 1.5454 | 12.9057 | 2509779.73 | 14.73 | 0.2711 | 2.0339 |
| so2 | temporal_climatology | 1.000 | 2.2507 | 4.8077 | 16664103.72 | 32.64 | 0.3949 | 5.2615 |
| so2 | station_median | 1.000 | 2.2589 | 4.7803 | 16976290.68 | 32.83 | 0.3963 | 5.4500 |
| so2 | hybrid_linear_idw | 1.000 | 2.6270 | 8.3493 | 12680331.84 | 34.60 | 0.4609 | 5.1470 |
| so2 | spatial_idw | 0.988 | 4.8726 | 7.0524 | 28289790.43 | 60.92 | 0.8548 | 11.2789 |