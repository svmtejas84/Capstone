# Station Gapfill Derived Layer Build

Run ID: gapfill_20260415_003809

## Inputs

- Raw station files were read-only.
- Gapfill policy from evaluator was applied per pollutant.

## Output Counts

- Derived rows (including observed + imputed + unresolved): 1073807
- Missing unresolved rows: 0
- Materialized rows (value not null): 1073807
- Imputed rows: 777350

## Method Mix

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

## Policy Snapshot

| Pollutant | Primary Method | Fallback Method | P90 Abs Error |
|---|---|---|---:|
| co | temporal_linear | station_median | 0.2051 |
| no2 | temporal_linear | hybrid_linear_idw | 2.4000 |
| pm10 | temporal_linear | temporal_climatology | 13.7294 |
| pm25 | temporal_linear | hybrid_linear_idw | 8.4725 |
| so2 | temporal_linear | temporal_climatology | 2.0339 |