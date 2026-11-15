# V5 data and target eligibility

V5 uses the **same frozen repaired causal array** as V3/V4, SHA-256 `bd08d733f924387da82e758d1060703dfcdd121f360b7e8765189d8b7446e202`, with 37,152 hourly rows, 15 station IDs, 13 base channels expanded to 18 model channels, observed target values/masks, source-observation indicators and strict-prior residual anchors. V5 preflight verified this hash, deterministic graph rewiring/geometry, lag-24 strict-prior indices, invariance to a modified future target, and identical train target-hour/mask populations across all new conditions. Four one-batch V100 forward/backward smoke tests produced finite gradients. [SOURCE: V3 `DATA_ELIGIBILITY.md`, V5 `verification/preflight.json`, V5 `scripts/train_graph_lag.py`.]

| Split | UTC interval | Role |
|---|---|---|
| Train | 2022-01-01 00:00 through 2025-06-29 23:00 | Optimization; train-only target transform/imputation parameters |
| Validation | 2025-07-01 00:00 through 2025-09-21 23:00 | Checkpoint and family-strength selection |
| Exposed test | 2025-09-23 00:00 through 2026-03-28 23:00 | One-time new-model exploratory scoring after training verification |

The V3/V4 repair delayed station pollutant source rows so feature row c uses only source pollutant observations from row c−1 or earlier. The 12-hour model window is c−11 through c, with issue c=T−h. L1's daily-lag source must be strictly earlier than c; if not observed or h=24, the strict-prior anchor at T−24 is used (equal to issue at h=24), with explicit indicator and age. L2 extends only the lookback length, with left padding at the start to retain target masks. Graph controls change edges and recomputed edge geometry, not data or target labels. Full-period and within-month wind-mask shuffles use calendar rows only, not target values or target-availability masks.

This is a **timestamp-causal historical-observation** evaluation. Archive weather release delay and station sensor ingestion latency were not recorded. No issued weather forecasts are present. The test period has been repeatedly inspected in previous Bengaluru work; V5 findings cannot be independent temporal confirmation. No new geographic holdout or roadside labels are part of this assignment. Historical station-isolated results remain separate. [SOURCE: `configs/data_v2.yaml`; V3 `PROTOCOL_AMENDMENT_02.md`, `DATA_ELIGIBILITY.md`; V5 `FORECAST_LEAD_AND_INFORMATION_PARITY.md`.]
