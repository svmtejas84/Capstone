# Candidate data eligibility

## Existing feasibility status

`results/research_audit_r1/gate_m0_london.md` (source checked 2026-11-05) marks London BLOCKED under the existing threshold of ≥30 eligible reference-grade hourly PM2.5 stations with ≥2 years during 2022–2025. Station count is unknown, not zero: no station-hour inventory/instrument crosswalk/quality flags were acquired. LAQN/AURN pages are candidate providers, not proof of coverage. Weather ERA5 mapping is conditional. LAEI 2022 annual emissions do not establish hourly source-rate Q. OSM/DEM licensing and coverage require versioned review.

Copenhagen was also BLOCKED; the known official central network has three stations and two report daily PM2.5. It is not automatically a stronger candidate. Neither city has passed eligibility.

## Required before selection

Acquire source metadata and timestamped hourly pollutant values; flag/reference instrument metadata; establish valid-hour counts and at least two operating years per site; map coordinates and geographic coverage; document UTC/DST/quality rules; weather station/grid provenance and issue-time availability; license/redistribution review; code/data hashes. Keep low-cost sensors separate unless an approved calibration design exists.


## Recovery sources

Full Gate M0 details: `results/research_audit_r1/gate_m0_london.md`, `results/research_audit_r1/gate_m0_copenhagen.md`; protocol readiness and historical deviations: `results/research_audit_r1/protocol_readiness.md`.
