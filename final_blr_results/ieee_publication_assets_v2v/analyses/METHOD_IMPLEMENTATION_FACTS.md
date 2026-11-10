# Implementation facts recovered from code and saved configurations

This sheet records actual implementation details used in figure and table captions. It is not a paper method section.

| Fact | Verified value | Source | Confidence / limitation |
|---|---|---|---|
| Corrected forecasting graph | 15 station nodes; directed four-nearest-neighbor graph; 60 directed arcs | `scripts/benchmark_v2j.py`, `src/stpignn/station_graph.py` | Direct code and graph artifact |
| Corrected input tensor | 12 historical hours × 15 stations × 18 channels | `scripts/benchmark_v2j.py`; `configs/benchmark_v2g.yaml` | 13 physical channels + imputation indicator + 4 calendar channels |
| Hidden width / message passing | 64 hidden units; two GINE layers in corrected ST-PIGNN; GRU temporal processing | `configs/benchmark_v2g.yaml`; `src/stpignn/models_v2.py` | Corrected model differs from notebook's historical 96-unit architecture |
| Historical road implementation | 12 h; 16 node channels; 16 edge attributes; 96 hidden units; 2 GINE blocks + GRU; 64 road partitions | `citywide_extension/v2q/ORIGINAL_MODEL_ARCHITECTURE.md` | Genuine road-partition implementation; legacy input/target protocol has target-hour risk and is not corrected station-benchmark evidence |
| Wind source and location | Open-Meteo historical archive request at Bengaluru reference coordinate 12.9716°N, 77.5946°E; one citywide series broadcast across station nodes | `scripts/pull_weather.py`; data engineering monograph | Stored archive lacks issue/release timestamp; no spatially varying street winds |
| Wind direction convention | Meteorological FROM direction; transport-to = (wind-from + 180°) mod 360° | `src/stpignn/physics_v2.py` | Code test explicitly states west wind transports east |
| Edge orientation | Bearing from source to destination, clockwise from true north: atan2(Δx, Δy) | `src/stpignn/physics_v2.py` | Directed station arcs; not road-link atmospheric fluxes |
| Direction cone | Circular angular difference ≤37.5° | `src/stpignn/physics_v2.py`; `configs/benchmark_v2g.yaml` | Corrected cone; original notebook's wider/ambiguous convention is historical only |
| Wind mask timestamp | Saved training batch indexes the wind mask at target index minus horizon (forecast cutoff) | `scripts/benchmark_v2j.py` | However the v2j weather value at that hour averages records at ±30 min, including the +30 min record after cutoff. Thus the *hour label* is cutoff but the centered weather input is not fully issue-time available |
| Calm-wind handling | No explicit low-speed calm threshold in the corrected directional mask; finite direction determines cone membership | `src/stpignn/physics_v2.py` | Direction can remain finite at calm speed; no calm exclusion is coded |
| Directional eligible-edge count | Across 4,063 test forecast hours, 60 directed arcs, 5,752 active wind-edge/time pairs at h=1; horizon-specific totals vary | `physics_audit/physical_diagnostics/physical_metrics.csv` | Requires both observed endpoint targets for evaluation proxy; not full-graph diagnostics |
| Directional geometric factor | `sigmoid(edge_length_m / 1000)` applied to prediction difference | `src/stpignn/physics_v2.py:batched_penalty` | Length is converted to km; no atmospheric diffusivity or source term |
| Directional hinge | Mean of `mask × ReLU((p_v−p_u) × sigmoid(length_km))²`, divided by active-mask mass | `src/stpignn/physics_v2.py:batched_penalty` | Predictions are physical concentration divided by training target SD; heuristic monotonicity penalty, not a conservation equation |
| Laplacian control | Mean squared directed edge concentration difference over all graph arcs, no wind mask | `src/stpignn/physics_v2.py:batched_penalty` | Generic graph smoothing comparator |
| Data loss | Masked mean squared error in standardized log1p target space, with residual forecast anchor | `scripts/benchmark_v2j.py` | Corrected station evaluation; distinct from original direct scaled target |
| Regularization coefficient | λ=0.06 × min(1, epoch/25) | `scripts/benchmark_v2j.py`; benchmark config | Fixed warm-up schedule |
| Did λ reach maximum? | No. Across directional selected best checkpoints, best epochs ranged 1–12 (λ up to 0.0288, 48% of 0.06). Training stop epochs ranged 6–17 (λ at most 0.0408, 68%). | `physics_audit/selection_audit/selected_configurations.csv` | Maximum warm-up was never reached before stopping; report both selected-checkpoint and last-trained exposure |
| Batch / optimizer | Batch 512; AdamW; weight decay 0.01; gradient clip 0.3; max 30 epochs; early stopping patience 5 | `configs/benchmark_v2g.yaml`; `scripts/benchmark_v2j.py` | LR candidates [1e-4,3e-4,1e-3,3e-3], selected with seed 11 validation MAE per model/horizon |
| Physics comparison conditions | Directional, λ=0, and Laplacian are separate fits | `scripts/benchmark_v2j.py` | Not simultaneous penalties; saved prediction family covers 5 horizons × 5 seeds |
| Wind-cone diagnostic availability | Corrected station-space post-hoc PVR and edge-gradient proxies are available for 15 stations and 11 scored test sites | `physics_audit/physical_diagnostics/physical_metrics.csv`, `spatial_behavior.csv` | Not a road-network violation map; not an empirical conservation metric; centered-weather issue-time limitation applies |

## Interpretation boundary

Historical v2j directional results include a look-ahead component in meteorology: hourly values are averaged from neighboring half-hour records and the latter record can be 30 minutes after the forecast origin. The direction cone and PVR are therefore mathematical diagnostics on the saved station predictions and selected wind series, not a prospective operational wind-validity claim. No reported proxy demonstrates mass conservation, a Gaussian-plume law, or physical causality.
