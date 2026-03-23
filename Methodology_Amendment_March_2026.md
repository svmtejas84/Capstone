# METHODOLOGY AMENDMENT

## A Cross-Scale Geospatial Logic for Real-Time Urban Toxicity Orchestration
### To Aid Healthy Navigation for Vulnerable Commuters

Tejas V K (1NT23CB058)
Major Project Phase 1
AY 2025-26
Amendment Date: March 2026

## 1. Overview of Proposed Changes

This amendment formalizes two methodological refinements to Module 1 (Live Environmental Component) of the approved project synopsis.

1. Atmospheric data source for high-frequency updates
2. Traffic-derived source spike injection logic

Both changes are motivated by Indian subcontinent constraints and improve computational efficiency without reducing physical fidelity.

| Component | Original Design (Synopsis) | Amended Design (March 2026) |
|---|---|---|
| High-frequency atmospheric driver | ERA5 reanalysis wind vectors (ECMWF via GEE) | INSAT-3D / INSAT-3DR geostationary data (ISRO Mosdac) |
| Traffic spike injection logic | Continuous real-time traffic density via TomTom API | Threshold-based injection when density exceeds 1.4-1.6x learned baseline |

## 2. Amendment A - Atmospheric Data Source

### 2.1 Original Design

The approved synopsis specifies ERA5 reanalysis data (ECMWF, accessed via GEE) for high-frequency atmospheric forcing.

### 2.2 Identified Limitation

ERA5T has around 2-3 hour lag, which conflicts with the system target of 5-15 minute re-advection cycles.

### 2.3 Proposed Replacement: INSAT-3D + INSAT-3DR

INSAT-3D and INSAT-3DR are Indian geostationary meteorological satellites maintained at 82E and 74E with near-real-time distribution through Mosdac.

Relevant products at 15-30 minute cadence:

- Atmospheric Motion Vectors (AMV) at multiple pressure levels
- Outgoing Longwave Radiation (OLR)
- Cloud Motion Winds (CMW)
- Surface temperature products useful for BLH inference

| Parameter | ERA5T (Original) | INSAT-3D/3DR (Amended) |
|---|---|---|
| Temporal cadence | 1-hourly (preliminary) | 15-30 minutes |
| Latency | 2-3 hours | Around 15 minutes |
| Spatial resolution | 0.25 deg (around 28 km) | 4 km (visible), 8 km (IR) |
| India coverage | Global source, indirect | Direct geostationary coverage |
| Access | GEE API | Mosdac FTP/API |
| Cost | Free | Free for registered users |

### 2.4 Integration Architecture

The amended pipeline keeps ERA5 as base climatological initialization (daily refresh) and uses INSAT-3D/3DR as intra-day advection driver for wind and BLH refresh every 15-30 minutes.

Meteosat-11 was evaluated and rejected because India lies near its extreme eastern limb, causing geometric distortion and reduced effective resolution over Bangalore.

## 3. Amendment B - Threshold-Based Traffic Spike Injection

### 3.1 Original Design

The approved synopsis uses continuous real-time traffic density as source spike input every timestep.

### 3.2 Identified Limitation

Continuous injection can:

- Trigger redundant recomputation for normal diurnal congestion
- Double-count emissions already represented in Sentinel-5P base field

### 3.3 Proposed Amendment: Threshold-Gated Injection

Define per-segment baseline traffic density B(l, t) from historical data using a rolling window of at least 30 days.

Inject only when observed density D(l, t) exceeds threshold:

D(l, t) > alpha * B(l, t)

Recommended alpha range: 1.4 to 1.6 (default 1.5).

### 3.4 Spike Magnitude

For cells overlapping segment l:

S(x, y, t) = k * (D(l, t) - B(l, t))

Where k maps anomalous vehicle density to NO2 concentration increment (ug/m3).

### 3.5 Operational Benefits

| Concern | Threshold Gating Benefit |
|---|---|
| Redundant GNN re-propagation | Re-run only on anomalies |
| Double-counting with Sentinel-5P base | Inject only excess over baseline |
| TomTom API rate limits | Lower query and processing pressure in non-spike periods |
| Peak-hour compute load | Trigger by anomaly, not by clock |

## 4. Impact on Functional Requirements

The amendment does not change FR1-FR4 functionality. It is an implementation-level refinement in Module 1.

| FR ID | Requirement | Amendment Impact |
|---|---|---|
| FR1 | Live 100m Physics Plane refreshed every 15 minutes in Redis | Data source updated to INSAT for intra-day updates; cadence unchanged |
| FR2 | PI-GNN computes dynamic Cedge values via Gaussian Plume + wind | No interface change |
| FR3 | A* routing with mode-specific W = sum(Cedge * te * IRmode) | No change |
| FR4 | Gale-Shapley distributes at least 10 commuters across at least 2 stable routes | No change |

## 5. Notation Addendum

Append to formal notation set:

- B(l, t): Baseline traffic density for segment l at time-of-day t (30-day rolling estimate)
- D(l, t): Observed real-time traffic density for segment l at time t
- alpha: Anomaly threshold multiplier (default 1.5)
- k: Emission factor coefficient mapping density excess to NO2 increment
- INSAT-AMV: INSAT-3D/3DR Atmospheric Motion Vector product used for intra-day wind updates

---

End of Amendment Document
Nitte Meenakshi Institute of Technology
Department of CS and BS
AY 2025-26
