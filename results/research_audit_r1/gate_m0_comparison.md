# Gate M0 comparison — engineering feasibility only

Source commit examined: `dca4bcce690da6b7865702f91d15dd2e06b6ef75`; checked 2026-11-05 UTC. The original fixed screen requires ≥30 reference-grade stations with ≥2 years of hourly PM2.5 in 2022–2025. No model accuracy or city-specific experiment informed this decision.

| Dimension | London | Copenhagen |
|---|---|---|
| Monitoring coverage | BLOCKED: LAQN/AURN station-hour count and spatial distribution unverified | BLOCKED: official page lists only three central stations, two with daily PM2.5 |
| Instrument consistency | BLOCKED: per-site methods not inventoried | BLOCKED: comparable hourly instruments not established |
| Meteorology | CONDITIONAL: ERA5 available; actual grid mapping needed | CONDITIONAL: ERA5 available; likely coarse relative to city graph, mapping needed |
| Q feasibility | BLOCKED: LAEI 2022 PM2.5 emissions are spatial but annual; hourly Q needs approved profile/units | BLOCKED: SPREAD 1-km emissions available in concept, dataset access and hourly Q unresolved |
| Geospatial inputs | CONDITIONAL: OSM and DEM available subject to sampling/licence | CONDITIONAL: OSM and DEM available subject to sampling/licence |
| Licensing | CONDITIONAL: OGL/CC-BY/ODbL sources identifiable; combined redistribution review needed | BLOCKED: DCE/EEA/SPREAD use and redistribution terms unresolved |
| Reproducibility | BLOCKED: no station-hour manifest or versioned downloads | BLOCKED: no station-hour manifest or versioned downloads |
| Overall | **BLOCKED** | **BLOCKED** |

London is the more promising *data-audit candidate* solely because LAQN/AURN provide hourly PM2.5 access and LAEI provides versioned pollutant emissions ([LAQN API](https://londonair.org.uk/LondonAir/API/), [LAEI 2022](https://data.london.gov.uk/dataset/london-atmospheric-emissions-inventory-laei-2022-2lg5g)); no assertion that it passes 30 eligible stations is made. Copenhagen's official [station descriptions](https://envs.au.dk/en/research-areas/air-pollution-emissions-and-effects/the-monitoring-program/measuring-stations/measurements-at-the-stations/copenhagen) directly conflict with the 30-hourly-station screen. Both remain blocked; no city training is authorized. The precise next data-only command is to obtain station metadata and 2022–2025 hour/flag extracts from the named provider APIs, then populate the manifest without altering the threshold.
