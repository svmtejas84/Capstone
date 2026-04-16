# Raw Station Data Audit (2022-2026)

This file documents year-purity cleanup and coverage gaps for station raw files.

## Post-Run Update (2026-04-15)

Two audited recovery passes were completed:

- Targeted missing pull (`scripts/pull_stations_missing_targeted.py`) completed with 628 tasks: 139 success, 489 confirmed missing, 0 failed.
- 2023 remap retry (`scripts/pull_stations_2023_remap_retry.py`) completed with 89 tasks: 0 success, 89 confirmed missing, 0 failed.

Current effective yearly coverage after these runs:

| File | Rows | Stations Present | Stations Missing | Missing Days |
|---|---:|---:|---:|---:|
| 2022.parquet | 60752 | 10 | 13 | 173 |
| 2023.parquet | 0 | 0 | 23 | 365 |
| 2024.parquet | 13417 | 1 | 22 | 65 |
| 2025.parquet | 594974 | 15 | 8 | 27 |
| 2026_partial.parquet | 186985 | 13 | 10 | 8 |

Artifacts produced by the remap retry pass:

- `data/raw/remap_2023_retry.log`
- `data/raw/remap_2023_retry_log.md`
- `data/raw/remap_2023_retry_events.parquet`

Conclusion from remap retry: 2023 remains source-empty for all targeted station/parameter windows in OpenAQ under current API visibility.

## Files Normalized

- data/raw/stations/2022.parquet (kept only rows where timestamp year == 2022)
- data/raw/stations/2023.parquet (kept only rows where timestamp year == 2023)
- data/raw/stations/2024.parquet (kept only rows where timestamp year == 2024)
- data/raw/stations/2025.parquet (kept only rows where timestamp year == 2025)
- data/raw/stations/2026_partial.parquet (kept only rows where timestamp year == 2026)

## Coverage Summary

| File | Audit Year | Rows | Start | End | Stations Present | Stations Missing | Missing Days |
|---|---:|---:|---|---|---:|---:|---:|
| 2022.parquet | 2022 | 6226 | 2022-01-01 00:00:00+05:30 | 2022-10-31 07:00:00+05:30 | 2 | 21 | 173 |
| 2023.parquet | 2023 | 0 | None | None | 0 | 23 | 365 |
| 2024.parquet | 2024 | 13417 | 2024-03-01 21:30:00+05:30 | 2024-12-31 23:30:00+05:30 | 1 | 22 | 65 |
| 2025.parquet | 2025 | 562671 | 2025-01-01 00:30:00+05:30 | 2025-12-31 23:30:00+05:30 | 15 | 8 | 38 |
| 2026_partial.parquet | 2026 | 1415 | 2026-01-01 00:30:00+05:30 | 2026-03-30 03:30:00+05:30 | 2 | 21 | 300 |

## Missing Stations by File

### 2022.parquet (2022)
- 412: Peenya, Bengaluru - KSPCB
- 594: BTM Layout, Bengaluru - KSPCB
- 797: City Railway Station - KSPCB
- 2589: SaneguravaHalli - KSPCB
- 2592: BWSSB Kadabesanahalli, Bengaluru - KSPCB
- 5547: BWSSB Kadabesanahalli, Bengaluru - CPCB
- 5574: City Railway Station, Bengaluru - KSPCB
- 5644: Sanegurava Halli, Bengaluru - KSPCB
- 6973: Jayanagar 5th Block, Bengaluru - KSPCB
- 6974: Bapuji Nagar, Bengaluru - KSPCB
- 6975: Silk Board, Bengaluru - KSPCB
- 6983: Hombegowda Nagar, Bengaluru - KSPCB
- 6984: Hebbal, Bengaluru - KSPCB
- 229473: blore_India_07_14_official
- 2498781: SiriJaya
- 3409385: RVCE-Mailasandra, Bengaluru - KSPCB
- 3409388: Kasturi Nagar, Bengaluru - KSPCB
- 3409393: Shivapura_Peenya, Bengaluru - KSPCB
- 6119271: Kumaraswamy Layout
- 6146655: Bellandur
- 6206921: Koramangala

### 2023.parquet (2023)
- 412: Peenya, Bengaluru - KSPCB
- 594: BTM Layout, Bengaluru - KSPCB
- 797: City Railway Station - KSPCB
- 2589: SaneguravaHalli - KSPCB
- 2592: BWSSB Kadabesanahalli, Bengaluru - KSPCB
- 5547: BWSSB Kadabesanahalli, Bengaluru - CPCB
- 5548: BTM Layout, Bengaluru - CPCB
- 5574: City Railway Station, Bengaluru - KSPCB
- 5607: Peenya, Bengaluru - CPCB
- 5644: Sanegurava Halli, Bengaluru - KSPCB
- 6973: Jayanagar 5th Block, Bengaluru - KSPCB
- 6974: Bapuji Nagar, Bengaluru - KSPCB
- 6975: Silk Board, Bengaluru - KSPCB
- 6983: Hombegowda Nagar, Bengaluru - KSPCB
- 6984: Hebbal, Bengaluru - KSPCB
- 229473: blore_India_07_14_official
- 2498781: SiriJaya
- 3409385: RVCE-Mailasandra, Bengaluru - KSPCB
- 3409388: Kasturi Nagar, Bengaluru - KSPCB
- 3409393: Shivapura_Peenya, Bengaluru - KSPCB
- 6119271: Kumaraswamy Layout
- 6146655: Bellandur
- 6206921: Koramangala

### 2024.parquet (2024)
- 412: Peenya, Bengaluru - KSPCB
- 594: BTM Layout, Bengaluru - KSPCB
- 797: City Railway Station - KSPCB
- 2589: SaneguravaHalli - KSPCB
- 2592: BWSSB Kadabesanahalli, Bengaluru - KSPCB
- 5547: BWSSB Kadabesanahalli, Bengaluru - CPCB
- 5548: BTM Layout, Bengaluru - CPCB
- 5574: City Railway Station, Bengaluru - KSPCB
- 5607: Peenya, Bengaluru - CPCB
- 5644: Sanegurava Halli, Bengaluru - KSPCB
- 6973: Jayanagar 5th Block, Bengaluru - KSPCB
- 6974: Bapuji Nagar, Bengaluru - KSPCB
- 6975: Silk Board, Bengaluru - KSPCB
- 6983: Hombegowda Nagar, Bengaluru - KSPCB
- 6984: Hebbal, Bengaluru - KSPCB
- 229473: blore_India_07_14_official
- 3409385: RVCE-Mailasandra, Bengaluru - KSPCB
- 3409388: Kasturi Nagar, Bengaluru - KSPCB
- 3409393: Shivapura_Peenya, Bengaluru - KSPCB
- 6119271: Kumaraswamy Layout
- 6146655: Bellandur
- 6206921: Koramangala

### 2025.parquet (2025)
- 412: Peenya, Bengaluru - KSPCB
- 594: BTM Layout, Bengaluru - KSPCB
- 797: City Railway Station - KSPCB
- 2589: SaneguravaHalli - KSPCB
- 2592: BWSSB Kadabesanahalli, Bengaluru - KSPCB
- 5547: BWSSB Kadabesanahalli, Bengaluru - CPCB
- 229473: blore_India_07_14_official
- 6206921: Koramangala

### 2026_partial.parquet (2026)
- 412: Peenya, Bengaluru - KSPCB
- 594: BTM Layout, Bengaluru - KSPCB
- 797: City Railway Station - KSPCB
- 2589: SaneguravaHalli - KSPCB
- 2592: BWSSB Kadabesanahalli, Bengaluru - KSPCB
- 5547: BWSSB Kadabesanahalli, Bengaluru - CPCB
- 5548: BTM Layout, Bengaluru - CPCB
- 5574: City Railway Station, Bengaluru - KSPCB
- 5607: Peenya, Bengaluru - CPCB
- 5644: Sanegurava Halli, Bengaluru - KSPCB
- 6973: Jayanagar 5th Block, Bengaluru - KSPCB
- 6974: Bapuji Nagar, Bengaluru - KSPCB
- 6975: Silk Board, Bengaluru - KSPCB
- 6983: Hombegowda Nagar, Bengaluru - KSPCB
- 6984: Hebbal, Bengaluru - KSPCB
- 229473: blore_India_07_14_official
- 2498781: SiriJaya
- 3409385: RVCE-Mailasandra, Bengaluru - KSPCB
- 3409388: Kasturi Nagar, Bengaluru - KSPCB
- 3409393: Shivapura_Peenya, Bengaluru - KSPCB
- 6146655: Bellandur

## Missing Date Ranges by File

### 2022.parquet (2022)
- 2022-01-27
- 2022-02-07 to 2022-03-24
- 2022-06-23 to 2022-07-03
- 2022-08-04 to 2022-09-12
- 2022-10-17 to 2022-10-30
- 2022-11-01 to 2022-12-31

### 2023.parquet (2023)
- 2023-01-01 to 2023-12-31

### 2024.parquet (2024)
- 2024-01-01 to 2024-02-29
- 2024-03-12 to 2024-03-13
- 2024-03-17 to 2024-03-19

### 2025.parquet (2025)
- 2025-01-15 to 2025-02-10
- 2025-12-16 to 2025-12-25
- 2025-12-29

### 2026_partial.parquet (2026)
- 2026-01-07 to 2026-01-18
- 2026-02-20 to 2026-02-23
- 2026-02-28
- 2026-03-10 to 2026-03-16
- 2026-03-31 to 2026-12-31
