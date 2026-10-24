# Old filtering audit

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

## Raw-to-master join by station and UTC hour

| Old status | Raw hourly pairs | Raw min | Raw max |
|---|---:|---:|---:|
| absent_from_master | 578 | -48.940000 | 260.370000 |
| imputed_tier | 566 | -24.070000 | 99999.010000 |
| observed_tier | 54084 | -49.980000 | 647952.972500 |

Among 212 raw train station-hours above 10,000 µg/m³, 208 remain old observed-tier rows, 4 are old imputed-tier rows, and 0 are absent. The old saved `y_clean` reaches 250.0 on these rows. This does not establish the undocumented `y_clean` rule.
