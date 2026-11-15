# Forecast lead and information parity

The repaired V3 source array has 37,152 hourly rows and 15 stations. For target hour `T` and nominal forecast horizon `h`, issue hour `c=T−h`. A 12-hour input contains feature rows `c−11` through `c`; the pollutant value shown in feature row `c` came from source row `c−1`, strictly before the issue. The residual anchor is the latest genuinely observed pollutant value strictly before `c`, or a station training mean fallback. Weather assigned to `c` is the archive observation stamped `c−30 min`; wind mask also uses issue-index wind. The actual release/ingestion latency of these sources is unverified, so timestamp causality does not certify operational availability. [SOURCE: `final_blr_results/controlled_validation_v3/scripts/build_causal_array.py`; `final_blr_results/controlled_validation_v3/scripts/smoke_gpu.py`; `final_blr_results/controlled_validation_v4_review_closure/FORECAST_ORIGIN_AND_LEAD_TIME_AUDIT.md`.]

Concrete UTC target example: `T=2025-10-01 12:00`.

| Nominal h | Issue c | Feature rows | Latest possible pollutant source row | Pollutant age at issue | Archived weather stamp | Same-hour-yesterday eligibility |
|---:|---|---|---|---:|---|---|
| 1 h | 2025-10-01 11:00 | Oct 1 00:00–11:00 | Oct 1 10:00 | ≥1 h | Oct 1 10:30 | Sep 30 12:00, when actually observed |
| 6 h | 2025-10-01 06:00 | Sep 30 19:00–Oct 1 06:00 | Oct 1 05:00 | ≥1 h | Oct 1 05:30 | Sep 30 12:00, when actually observed |
| 12 h | 2025-10-01 00:00 | Sep 30 13:00–Oct 1 00:00 | Sep 30 23:00 | ≥1 h | Sep 30 23:30 | Sep 30 12:00, when actually observed |
| 24 h | 2025-09-30 12:00 | Sep 30 01:00–12:00 | Sep 30 11:00 | ≥1 h | Sep 30 11:30 | T−24 equals issue; observed issue-hour value is excluded; strict-prior anchor used |

For 24 h, persistence and same-hour-yesterday both use `anchor[c]`, so their saved exposed-test predictions agree exactly, MAE **14.972188 µg/m³** on **14,583** pairs. For 1–12 h, the same-hour-yesterday value is `observed_target[T−24]` when present; otherwise the saved baseline uses the strict-prior anchor at that previous-day index. Its 14.130312 µg/m³ is for those shorter horizons, not the 24-hour rule. [SOURCE: `final_blr_results/controlled_validation_v3/scripts/evaluate_baselines.py:34,52-55`; saved V3 predictions.]

All five V3 matched neural variants use the same feature-window endpoint and weather assignment. Their representations differ but their input information is the same saved causal array; deterministic baselines use only their declared subsets. A nominal h-hour forecast is still issued h hours before the target; pollutant observation age can exceed h+1 hours when the station is missing. These quantities are separate.
