# Citywide precheck v2h

Source `scripts/citywide_precheck_v2h.py`, `scripts/pull_weather.py`, no training, no seed, commit `dd947370ebdd83a323ac843f1061f85bce860951`, 2026-11-04T15:27:07.404625+00:00.

Nodes: 154902.
Distinct weather source points: 1 (12.9716 N, 77.5946 E).
Nodes with stored hourly model-input rows: 22/154902; nodes with no stored temporal model-input data: 154880.
Unique weather series among stored nodes: 18.
Stored nodes whose weather series exactly duplicates another stored node's: 5/22 (22.727273%).
If the single raw weather series were broadcast to all topology nodes, duplicate fraction would be 100.000000%.
Weather hours with all six fields finite: 37152/37152.
Nodes with SRTM elevation: 154902/154902; missing: 0.
Nodes mapped to a station: 23/154902; without a station: 154879.
Nodes with no weather or SRTM data after broadcast: 0.
BLOCKED: a single weather source would give more than 50% identical citywide node series.
