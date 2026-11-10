# Publication figure captions — corrected evidence package

These captions describe the evidence shown by the v2v assets. Reader-facing captions avoid internal run labels. Internal experiment IDs remain in source filenames and provenance manifests. The wording is evidence documentation, not manuscript prose.

## Figure 1 — Evaluated architecture and downstream extensions

**Caption.** The upper lane reconstructs the historical partitioned road-network GINEConv–GRU implementation: 154,902 road nodes, 64 geographic partitions, a 12-hour input window, 16 node channels, 16 edge attributes, and 96 hidden units. Its input construction had target-hour information risk and must be distinguished from the corrected station benchmark. The middle lane shows corrected station forecasting on a separate 15-node, 60-directed-edge k-nearest-neighbor graph using a 12-hour window and 18 input channels. In the retrospective centered-weather protocol, each hourly weather value could include the record timestamped 30 minutes after the forecast origin; a separate MLP/TCN evaluation used a forecast-cutoff-safe protocol. The directional hinge is a training-only loss computed from predictions. Zero regularization and Laplacian smoothing are separate ablation conditions. The hinge does not enforce atmospheric mass conservation. Dashed arrows denote later neural-assisted station-to-road estimates and a routing prototype; road-node values are estimates, not observations.

**Sources:** `citywide_extension/v2q/ORIGINAL_MODEL_ARCHITECTURE.md`; `src/stpignn/data_v2.py`; `scripts/benchmark_v2j.py`; v2r handoff. **Limitations:** the middle lane is station-graph forecasting; it does not depict road-network message passing as part of the corrected benchmark.

## Figure 2 — Road graph, partitions, and monitoring stations

**Caption.** The panels show the stored Bengaluru road topology (154,902 nodes; 393,089 raw directed edge rows; 424,550 processed message arcs), the original 64-way geographic partition membership (with 7,134 cross-partition arcs omitted by the historical partition representation), and fifteen station locations. The corrected forecasting graph is a distinct 15-station graph with 60 directed k-nearest-neighbor arcs. Road nodes indicate network geometry and are not monitoring stations or pollutant observations.

**Sources:** canonical OSM-derived graph Parquets, stored 64-partition tensor, `results/stations_v2.csv`. **Limitations:** partition boundaries are historical; no equivalence to full-graph message passing is implied.

## Figure 3 — Multi-horizon station forecasting

**Caption.** Panel A reports retrospective centered-weather station evaluation results for selected conventional, neural, and regularization controls over 1-, 3-, 6-, 12-, and 24-hour horizons. Each horizon uses 14,583 observed station-time pairs from eleven scored stations; negative (R^2) values are retained in the source table. Panel B separately reports MLP and TCN results under a forecast-cutoff-safe weather protocol. The two panels use different weather information sets and are not identical-input architecture ablations. Figure 3b contains all seventeen archived variants from the retrospective protocol. Results are exploratory after repeated Bengaluru test-period examination.

**Sources:** recomputed saved prediction benchmark and baseline ensemble metrics. **Limitations:** the complete table preserves all MAE, RMSE, (R^2), pair counts, and seed coverage; protocols must not be pooled.

## Figure 4 — Directional regularization and ablation analysis

**Caption.** Panel A gives five-seed ensemble MAE differences between directional regularization and zero regularization; panel B compares directional regularization with generic Laplacian smoothing and includes 95% seven-day moving-block bootstrap intervals from aligned saved ensemble predictions; panel C displays individual-seed directional-minus-zero-regularization differences. Negative differences favor the directional model. At six hours, all five individual seeds favor the directional model over zero regularization; the two-sided exact sign-test value is (p=0.0625). The existing 35-contrast Holm values near 0.0175 arise from Monte Carlo sign-flip (p)-value resolution (2,000 draws; minimum (1/2001)) followed by Holm adjustment. This is evidence about an exploratory regularization heuristic, not mass conservation or a discretized advection–diffusion law.

**Sources:** saved per-seed and ensemble predictions; corrected physics analysis methods. **Limitations:** the test period was repeatedly examined; day-level resampling assumptions remain imperfect; individual seed repetitions share one test period.

## Figure 5 — Station-isolated evaluation

**Caption.** Panel A shows per-station MAE for genuine leave-one-station-out evaluation on eleven scored sites; four mapped sites had no test observations. Pooled observation-weighted MAE is 22.314 µg/m³ for ST-PIGNN and 20.624 µg/m³ for weather/static ridge, while five sites favor ST-PIGNN and six favor ridge. The equal-site mean paired difference (ST-PIGNN minus ridge) is +1.487 µg/m³ (station-bootstrap 95% CI −2.577 to +5.328; eleven independent sites); a nested station/seven-day-block sensitivity interval is −2.545 to +6.602 µg/m³. Panel B is a separate forecast-origin-safe decoder task: pooled MAE is 27.360 µg/m³ for the decoder, 20.154 for forecast-IDW, and 20.634 for the station mean. Decoder minus forecast-IDW is +7.206 µg/m³ pooled and +5.101 µg/m³ equal-site (station-bootstrap 95% CI +1.815 to +8.301). These are distinct estimands and protocols; timestamps are not independent spatial sites.

**Sources:** saved W6 station metrics and prediction rows; v2r pooled and station-bootstrap results. **Limitations:** the W6 neural output uses a train-mean residual anchor while the ridge output uses its baseline reconstruction, so this is not a fully matched output-anchor ablation. Station 3409385 is influential; station 6974 has only eight targets.

## Figure 6 — Spatio-temporal feature attribution

**Caption.** Panels show Captum Integrated Gradients for a one-hour ST-PIGNN variant and a separate six-hour station-isolated ST-PIGNN variant. Each analysis uses a training-mean baseline and twelve historical input steps. Feature-level absolute attribution, signed attribution, temporal attribution, and feature-by-lag attribution are computed from saved tensors over station nodes and examples. The one-hour analysis has 45 primary records from 54 total records; the six-hour analysis has 9 primary records from 18 total records. In the six-hour variant, mean summed absolute attribution is approximately (5.43\times10^{-6}) for lagged PM2.5, 2.647 for temperature, 2.406 for surface pressure, 0.989 for wind speed, 0.998 for hour sine, and 0.578 / 0.319 for wind-direction sine/cosine. The one-hour lagged-PM2.5 value is 4.918. The variants differ in feature schema, checkpoint selection, and evaluation population; magnitudes should not be compared as a controlled horizon effect. Attributions are baseline-relative prediction sensitivities, not causal effects or evidence of physical transport.

**Sources:** raw IG tensors and per-record verification outputs. **Limitations:** these analyses do not explain every corrected forecasting checkpoint; completeness and wrapper errors are reported by variant, and feature scale differences matter.

## Figure 7 — Experimental neural-assisted road-node estimates

**Caption.** Panel A maps the saved six-hour decoder estimates for the prespecified earliest frozen snapshot, 2025-10-08 07:00 UTC, across 154,902 road nodes. A corrected station forecaster operates on the 15-station graph; a separate 1,249-parameter decoder produces the road-node values. Panel B shows nearest-monitor distance and convex-hull/support indicators. The decoder underperformed forecast-IDW and the station-mean control at held-out stations. These are experimental neural-assisted road-node estimates, not independently validated roadside concentrations.

**Sources:** saved road-node Parquet and station coordinates. **Limitations:** no road-level ground truth; 19.45% of nodes are more than 5 km from a monitor and 60.58% lie outside the station convex hull.

## Figure 8 — Routing capacity and modeled-dose trade-offs

**Caption.** Panel A summarizes assignment coverage and observed shared-edge feasibility for nine low-load demand batches under the original concentration field; all compared methods assigned the submitted 252 trips and had zero recorded capacity violations. Maximum edge utilization for this field was 4.5918% (seed 37, demand 48). Panel B reports corrected-allocator paired differences against shortest-distance, fastest-time, and unconstrained minimum-dose routes on common admitted trips. Against shortest-distance routing, modeled dose changed by −0.001207% and travel time by +0.001324%. These differences are extremely small. Across all four saved concentration fields, maximum utilization was 5.4054% in the spatial-sine perturbation (seed 11, demand 48). The perturbation set comprises the original field plus three alternatives (uniform scaling, spatial sine, and support-distance). Dose values are model outputs under unvalidated concentration scenarios; they are not measured exposure reductions. The allocator has no established classical Gale–Shapley stability guarantee.

**Sources:** v2t routing comparisons, paired comparisons, capacity metrics, and sensitivity records. **Limitations:** low demand and synthetic scenario capacities; no validated traffic flow, human exposure, or equilibrium evaluation.
