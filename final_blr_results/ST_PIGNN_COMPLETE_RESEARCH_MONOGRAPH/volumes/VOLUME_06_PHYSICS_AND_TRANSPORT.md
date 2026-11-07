# Volume 6 — Directional penalties, attribution and conservation

<a id="volume-06"></a>

## Editorial reconstruction and evidentiary boundary

The implemented upwind-inspired term penalizes a selected directed difference with a squared hinge after bearing/wind masking and geometric scaling. It encourages a local monotonic order under that mask; it does not close a control-volume mass balance, represent the full advection–diffusion PDE or supply a dimensioned emissions source Q. The v2l matched five-seed ensemble shows negative physics-minus-λ0 MAE at 3, 6 and 12 hours, but a positive point difference at 24 hours; Laplacian comparisons do not establish physical specificity. A later standalone finite-volume diagnostic passed synthetic conservation cases, which validates its numerical discretization only. It does not change historical checkpoint physics. [EVIDENCE: v2l verdict | final_blr_results/physics_audit/FINAL_PHYSICS_VERDICT.md | snapshot 1c46a4b]

## Full round-specific source exhibits

The exhibits reproduce the cited local reports as source evidence. Their original round-specific conclusions may be narrower than later findings; read the editorial reconstruction and final synthesis before treating one exhibit as the final verdict.

## Source exhibit 1: `final_blr_results/physics_audit/methodology/PHYSICS_ATTRIBUTION_METHODOLOGY.md`

[EVIDENCE: `final_blr_results/physics_audit/methodology/PHYSICS_ATTRIBUTION_METHODOLOGY.md` | SHA-256 `f0646f6f9130954e09bcb649c07636ee03f89b507c7ab0a26e82a2a65f9a3449` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Physics attribution methodology — post-hoc v2l audit

This is a diagnostic reanalysis of an exposed Bengaluru test set, recorded before computation in `results/codex_log/DECISIONS.md` at commit `2b2ab47`. It is neither preregistered confirmation nor external validation. No training was performed. The primary question is whether the selected weak upwind-inspired penalty improves prediction over the same ST-PIGNN backbone with λ=0 across seeds and time. The secondary question is whether that benefit exceeds generic Laplacian regularization and corresponds to transport-related behavior.

#### Data and experimental provenance

- Source: raw UTC station observations (`data/raw/stations/*.parquet`), raw Asia/Kolkata-labelled weather (`data/raw/weather/*.parquet`), station metadata, station-to-road mapping and SRTM elevation. The corrected dataset is `results/data_v2j_arrays.npz`, SHA-256 `649519c9d11e02c535b960642fbc35a7f79ab1916df418cbea276f3960eaa3f8`; fit/provenance is `results/data_v2j_fit.json`, generated at source commit `27dd8ce04a7522279ee38a53609cf7cf4fd3ea4e`. The fit file confirms `weather_half_hour_rule=true` and temperature peak at 08:00 UTC. Raw weather local timestamps are shifted by exactly 5h30m and the UTC hour is the mean of the two adjacent :30 records. The weather builder's edge-hour handling is documented in the fit file and `results/codex_log/ACTIONS.md`.
- PM2.5 targets are observed-only values filtered to 0–500 µg/m³. Fifteen stations have model inputs; eleven contribute test targets. The common test mask has 14,583 station-hour pairs on 177 observed UTC days. `provenance/prediction_integrity.csv` verifies identical keys, target bytes, counts and finite values across all 75 model/seed/horizon files; no population intersection or exclusion was used. The fact that another node has an imputed input never makes its target observed.
- Temporal split (`configs/data_v2.yaml`): train 2022-01-01 to 2025-06-29; validation 2025-07-01 to 2025-09-21; test 2025-09-23 to 2026-03-28, UTC, with gaps. Inputs use a 12-hour history ending at target time minus horizon. They contain 13 train-fitted data channels, `lag_is_imputed`, and four calendar channels. Missing pollutant inputs use the documented causal/train-only fitting; target and lag use standardized log1p in the same space. Forecast output is a residual above the last observed-at-or-before-cutoff anchor. The station graph is directed four-nearest-neighbor on projected station coordinates, with meter distances on edges.
- The benchmark run used `scripts/benchmark_v2j.py` and `src/stpignn/models_v2.py` at training source commit `9a299f1bf01787f26750515cad8dff370e9c9aa0`; run log `results/codex_log/runs/benchmark_gpu_v2j/attempt_0_20261105T130158Z.log` reports commit `a736005077104f01d0ab1006ba7dc12daae0d403` at each horizon completion. The intervening commit changed no benchmark/model/physics/config source (`git diff 9a299f1 a736005` on those paths was empty). Source configuration is `configs/benchmark_v2g.yaml`; seed set is 11,23,37,51,79. Supervisor manifest reports Python 3.9.7, PyTorch 2.8.0+cu128, Tesla V100-PCIE-32GB, start 2026-11-05T13:01:57Z. Manifest config/seeds fields were null; YAML and run rows supply them. v2k paired source is commit `931bf09975dd17bfdca4f26259ede91046974f07`.

#### Models and selection

All three variants call the same `gnn.model.STPIGNN` through `src/stpignn/models_v2.py`, with 43,393 parameters, 18 inputs, 64 hidden width, two GINE layers and GRU, the same graph/edge input and residual output. `stpignn_lambda0` minimizes standardized-log1p target MSE. `stpignn_original` adds a wind-cone, rectified downwind-increase penalty; `stpignn_laplacian` adds a mean squared directed-edge concentration difference. Both penalties scale predictions by the train target standard deviation and use coefficient `0.06×min(1,epoch/25)`. No measured traffic/emissions Q enters this loss. The positive coefficient is deliberately weak early in training.

Each model/horizon searches the same four learning rates `[0.0001,0.0003,0.001,0.003]` **using seed 11 only** and picks minimum validation MAE, then trains all five fixed seeds at that selected LR. Optimizer AdamW has weight decay 0.01, batch 512, at most 30 epochs, patience 5, gradient clip 0.3. Best validation epoch is restored before test scoring. `results/benchmark_selection_v2j.csv`, `benchmark_runs_v2j.csv` and `selection_audit/selected_configurations.csv` record opportunities and choices. Search budget and information set are equal, but chosen LRs differ by variant at h=1,6,12,24; therefore the observed outcome compares validation-selected *procedures*, not an isolated penalty at a common LR. No source code path selects a checkpoint using test MAE. Trained v2j checkpoints were not saved, so weight-level diagnostics and exact retraining replay are unavailable.

#### Statistical definitions

For observed pair i, truth yᵢ and prediction pᵢ, `MAE(p)=Σᵢ|pᵢ−yᵢ|/N`. A paired difference for first model A against B is `Δ=Σᵢ(|pᴬᵢ−yᵢ|−|pᴮᵢ−yᵢ|)/N`; negative favors A. `RMSE=sqrt(Σᵢ(pᵢ−yᵢ)²/N)` and `R²=1−Σᵢ(pᵢ−yᵢ)²/Σᵢ(yᵢ−ȳ)²` when reported. Relative Δ is `100Δ/MAE(B)`.

Let n_d be the number of station pairs and D_d their sum of paired absolute-error differences on UTC day d. The original 2,000-replicate paired UTC-day bootstrap samples days with replacement and calculates `Δ*=Σ_d D_{d*}/Σ_d n_{d*}`. Percentile 2.5/97.5 quantiles form a nominal 95% CI. Days are resampled as units, keeping all same-day station pairs together. Because n_d varies, the statistic is **observation-weighted MAE**, not equal-day mean MAE. v2k uses seed `4303+100h+row_index`; v2l per-seed CIs use a separately declared deterministic seed in `run_physics_audit.py`. The original v2k physics rows were independently regenerated to rounding precision using their exact seed and 2,000 draws.

For the v2k sign-flip test, each UTC-day sum D_d receives one random ± sign; `T*=Σ_d s_d D_d/Σ_d n_d`, with two-sided Monte Carlo p=`(1+#(|T*|≥|Δ|))/(2001)`. The script draws signs after its bootstrap samples from the same seeded generator. Grouping station observations by day is correct for within-day dependence. Symmetry/exchangeability of day effects remains an assumption and is doubtful under serial dependence, seasonality and heteroskedastic pollution episodes; p values are sensitivity measures. Monte Carlo resolution is 1/2001. The v2k original Holm adjustment sorts all 35 p values and uses step-down `max_{j≤rank}(m−j+1)p_(j)` capped at 1. v2l additionally applies the same formula to the fixed five physics-versus-λ=0 horizons only, labelled retrospective. Nominal intervals and historical fixed criterion remain unchanged.

For seed s, compute `Δ_s` on its own matched predictions; summarize five values by arithmetic mean, median, sample standard deviation (denominator 4), min/max and sign counts. Five seeds are training repeats on **one test set**, not five independent datasets. The ensemble at pair i is `p̄ᵢ=(1/5)Σ_s p_{s,i}`. Mean individual MAE is `(1/5)Σ_s MAE(p_s)`; ensemble MAE is `MAE(p̄)`; gain is their difference. Physics-specific gain difference is `gain_physics−gain_lambda0`. The ensemble Δ equals mean-individual Δ minus that gain difference; report both.

Monthly effects recompute Δ within each UTC calendar month with all available pairs; no month is dropped. The seven-consecutive-calendar-day moving-block bootstrap samples overlapping length-7 blocks with replacement, concatenates `ceil(D/7)` blocks, truncates to the original number of calendar days, and computes the same ratio of D sums to n sums, with 2,000 replicates. Missing calendar days enter as n=D=0, preserving calendar spacing. This is a dependence sensitivity, not a better-estimator selection rule. It assumes approximate stationarity over the test interval and cannot eliminate long-range dependence or test exposure.

#### Physical-proxy definitions

The directed edge `u→v` has UTM bearing `atan2(x_v−x_u,y_v−y_u)` clockwise from north. Raw meteorological wind is a **FROM** direction in degrees; transport points toward `(wind_from+180) mod 360`. An edge is active if circular angular distance to transport is ≤37.5° at the forecast cutoff time `target_time−h`. The feature data's corrected `raw_wind_degrees` is used, never the shifted-weather series. Only edges whose source and destination both have observed test targets and corresponding predictions are diagnosed. This is a sparse station subset, not the full graph.

For an active edge, `g=p_v−p_u` in µg/m³. PVR at normalized threshold τ is `100×mean[ g / train_target_SD > τ ]`, τ∈{0,.01,.05,.1}. Violation magnitude is `mean(max(g,0))`; the scaled hinge proxy is `mean(max(g×sigmoid(length_km),0)² / train_target_SD²)`. Absolute edge difference `mean|g|` and gradient `mean(|g|/length_km)` are reported for active edges, with non-wind edge differences as a descriptive comparator. At each hour with at least two observed stations, spatial SD is computed over available predictions; near-constant frequency is the proportion with SD<1 µg/m³, and an edge-collapse proxy is the proportion of active pairs with |g|<1. Per-station temporal SD is averaged across stations. Identical observed-station edge/time masks supply observed gradient and spatial-SD references. These metrics are proxies, not conservation laws. The upwind hinge penalizes downwind increases without measured Q and does not enforce mass balance. Low PVR can result from excessive smoothing or constant predictions.

#### Limitations and regeneration

The Bengaluru test set was repeatedly examined, with six prior post-hoc methodological deviations catalogued in `results/research_audit_r1/protocol_readiness.md`: residual/lag repair, LR-grid expansion, seasonal baseline addition, LOSO anchor modification, lambda sweep, and later Laplacian-separated W7 criterion. The five horizons share observations and are dependent. Only 15 stations are modeled, 11 have test targets, and the test spans parts of seven months/one season cycle. UTC-day sign exchangeability and seven-day block stationarity are uncertain. No measured emissions Q, verified citywide corrected inputs, full-road checkpoint or street-level ground truth exists. Prediction-only diagnostics cannot establish causal mechanism or physical validity. Required local caches have no verified independent durable backup.

From repository root, regenerate statistics with `python final_blr_results/physics_audit/reproducibility/run_physics_audit.py` and physical proxies with `python -m final_blr_results.physics_audit.physical_diagnostics.compute_physical_diagnostics`. Both read existing predictions only; `reproducibility/artifact_checksums.csv` lists inputs and hashes. These commands do not train or overwrite historical artifacts.

## Source exhibit 2: `final_blr_results/physics_audit/FINAL_PHYSICS_VERDICT.md`

[EVIDENCE: `final_blr_results/physics_audit/FINAL_PHYSICS_VERDICT.md` | SHA-256 `7bddfc1776c8d23123c6ad0400cc1c0c98434db6c2e7bc4017565506d0f724fe` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Final physics attribution verdict — v2l

**Scope:** post-hoc reanalysis of existing corrected v2j Bengaluru predictions. Source training commit `9a299f1bf01787f26750515cad8dff370e9c9aa0`; v2k comparison commit `931bf09975dd17bfdca4f26259ede91046974f07`; v2l decision commit `2b2ab47`. No training, test-time selection, manuscript edit or citywide inference occurred. Complete methods: `methodology/PHYSICS_ATTRIBUTION_METHODOLOGY.md`.

#### 1. Predictive contribution and multiplicity

The table uses matched five-seed mean predictions on the same 14,583 observed station-hour targets (177 UTC days) at every horizon. Negative Δ favors physics. The original 35-test Holm results are preserved; the five-horizon family is a separately labelled retrospective sensitivity analysis.

| h | Physics−λ0 ensemble ΔMAE (µg/m³) | Nominal 95% UTC-day CI | Original 35-test Holm p | Retrospective five-test Holm p |
|---:|---:|---:|---:|---:|
| 1 | −0.026 | [−0.050,−0.001] | 0.4453 | 0.0840 |
| 3 | −0.130 | [−0.210,−0.055] | 0.0175 | 0.0025 |
| 6 | −0.410 | [−0.550,−0.274] | 0.0175 | 0.0025 |
| 12 | −0.262 | [−0.381,−0.139] | 0.0175 | 0.0025 |
| 24 | +0.145 | [−0.013,+0.314] | 0.6357 | 0.0840 |

There is exploratory evidence of better ensemble prediction at h=3,6,12 under both adjusted families. The h=1 nominal interval excludes zero, as did the separate fixed h=1 lambda check, but its 35-test Holm result does not; the h=24 ensemble is worse by point estimate. No historical success criterion is revised.

#### 2. Seed stability and ensemble dependence

| h | Seeds favoring physics | Mean individual-seed ΔMAE | Ensemble ΔMAE | Extra physics ensemble gain |
|---:|---:|---:|---:|---:|
| 1 | 1/5 | +0.009 | −0.026 | +0.036 |
| 3 | 3/5 | −0.005 | −0.130 | +0.125 |
| 6 | 5/5 | −0.566 | −0.410 | −0.156 |
| 12 | 4/5 | −0.254 | −0.262 | +0.008 |
| 24 | 3/5 | +0.155 | +0.145 | +0.011 |

At h=1 the ensemble gain reverses the average individual-model direction; at h=3 it accounts for nearly all the benefit. At h=6/12 individual models also improve, although h=12 is not universal across seeds. Seed counts are descriptive training variability on one test population, not independent replications. Full per-seed intervals and spread are in `seed_analysis/`.

#### 3. Model-selection validity

The three models share the exact 43,393-parameter backbone, corrected input arrays, graph/edge features, target transformation and observed test mask. Their source loss branches differ by upwind hinge, zero penalty or Laplacian gradient penalty. Each had four LR trials with seed-11 validation MAE, the same 30-epoch/patience-five budget, and five complete final seeds. No test-based selection is visible. Selected LRs differ at h=1,6,12,24, and best epochs differ, so this is a fair **validation-selected procedural ablation** but not a common-LR/common-epoch causal estimate of the penalty alone. No corrected v2j checkpoint exists for weight-level audit. Details: `selection_audit/model_selection_review.md`.

#### 4. Statistical and temporal robustness

The original 2,000-replicate UTC-day bootstrap and sign-flip values reproduce to rounding. Resampling is paired by day and observation-weighted; day-level sign symmetry and independence remain assumptions. Seven-consecutive-calendar-day moving-block CIs are [−0.068,+0.015], [−0.252,−0.042], [−0.632,−0.209], [−0.451,−0.076], [−0.064,+0.342] for h=1,3,6,12,24. Thus h=3/6/12 remain negative in this dependence sensitivity, h=1 does not. Months favor physics in 4/7, 6/7, 6/7, 6/7 and 1/7 respectively; unfavorable months were retained. The five largest absolute day sums account for 13–20% of absolute day effect depending on horizon. See `statistical_robustness/`.

#### 5. Physics versus Laplacian and physical behavior

Physics−Laplacian ensemble ΔMAE is −0.073, +0.178, −0.130, +0.003 and −0.103 µg/m³ across h=1,3,6,12,24. In the original 35-test family, physics has adjusted favorable evidence at h=1 and h=6; Laplacian is better at h=3; h=12 is indistinguishable and h=24 only nominally favors physics. The wind-cone PVR>0 of physics is lower than λ0 at h=1/12 but **higher** at h=3/6/24. Spatial gradients, variance and near-constant output rates do not show a unique transport-consistency signature. The same sparse observed station edges provide a descriptive reference, not street-level truth. The upwind hinge has no measured emissions Q and does not enforce mass conservation. Lower PVR or hinge magnitude cannot prove atmospheric validity. Details: `physical_diagnostics/`.

#### 6. Historical reconciliation and limits

Shifted-weather W7 found a weak λ=0.06 benefit only at h=6 among five horizons and generally harmful larger λ. Corrected v2j shifted h=1 into a small favorable fixed-check cell and retained no h=24 benefit. v2k's broader benchmark additionally found h=3/6/12 ensemble contrasts, but different weather, selection and aggregation prevent pooling old and new experiments as independent replication. Earlier physics-null findings and negative Laplacian/λ cells remain in `reconciliation/historical_physics_evidence.md`. The Bengaluru test set has been repeatedly exposed, horizons share observations, only 11 stations provide test targets, and no compatible citywide checkpoint or validated street-level ground truth exists.

#### Separate classifications

| Question | Classification | Reason |
|---|---|---|
| Predictive effect | **MIXED** | Exploratory adjusted benefit at h=3/6/12; h=1 fragile and h=24 absent. |
| Seed robustness | **MIXED** | Stronger at h=6/12, weak/inconsistent at h=1/3/24. |
| Ensemble dependence | **PRESENT** | Dominant at h=1/3; not the principal source at h=6/12. |
| Physics specificity | **UNSUPPORTED** | Laplacian and transport-proxy comparisons are inconsistent; no conservation/Q evidence. |
| Independent confirmation | **NOT AVAILABLE** | Same repeatedly examined Bengaluru test set; no external holdout. |

These classifications separate statistical predictive association from causal architectural attribution. A physical mechanism cannot be established from these saved outputs alone. Required local prediction caches have no verified independent durable backup; `reproducibility/` lists paths, checksums and the no-training regeneration command.

## Source exhibit 3: `final_blr_results/final_three_pillars/physics/ORIGINAL_LOSS_AUDIT.md`

[EVIDENCE: `final_blr_results/final_three_pillars/physics/ORIGINAL_LOSS_AUDIT.md` | SHA-256 `192ac32053e35e6a81ead376a41af8863e1e02b2986afd98fbda0496569d86a0` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Original directional loss audit

#### Exact computational operation

The original notebook's cell 7 computes projected edge bearings as `atan2(dy, dx)` in mathematical degrees (east is 0°), then delegates a mask to `compute_dynamic_upwind_mask_vectorized`. That helper adds 180° to each edge bearing and compares the result to `current_wind_dir_deg` with a ±37.5° cone. Cell 13 sets that value from `xb[0,0,0,6]`: first batch, first time, first node, channel 6. The notebook does not demonstrate that this transformed feature value is unscaled meteorological degrees or spatially/time representative. Cell 20 reuses the same mask and calls positive downwind differences a “physical violation,” with a threshold of 0.05 in normalized/model-output units.

For active directed edge `u→v`, `src=u`, `dst=v`, the preserved legacy helper computes:

`d_uv = p_v - p_u`;

`w_uv = sigmoid(sum_k(edge_attr[u,v,k] / 1000))` when the edge-attribute length agrees with E, else `w_uv=1`;

`L_hinge = mean_active( max(0, w_uv d_uv)^2 )`.

The training loop adds `lambda(epoch) * L_hinge`, with `lambda(epoch)=lambda_max*min(1, epoch/25)`. The reported v2l corrected study is a distinct implementation: its wind-FROM direction is converted to transport-to, bearing is compass clockwise from north, and only its corrected length feature supplies the geometric sigmoid. Do not conflate those versions.

The hinge penalizes positive prediction differences in the selected direction. It has no time derivative, control-volume integral, face-normal flux, source/sink, boundary accounting, or cell volume. Penalty values inherit the model output's normalized target scale; the original notebook does not convert it to a dimensionally consistent physical mass rate. Summation over edge attributes inside a sigmoid is also not a calibrated transport coefficient. Its gradient pushes paired endpoint predictions toward a chosen monotonic ordering. That is a graph regularizer, not a conservation law.

#### Relation to Gaussian plume formulation

The repository has a separate analytic `gnn/plume_physics.py::gaussian_plume(q,x,y,u,sigma_y,sigma_z,...)`. It needs emission rate `q` in µg/s, wind speed in m/s, dispersion widths in m and release height in m; the returned idealized concentration is µg/m³. The original directional hinge does not evaluate this equation, does not use its Q term, and does not solve the plume equation. The presence of plume utilities or a notebook visualization does not make the loss plume-informed or mass-conserving.

#### Orientation caution

The intended corrected v2l convention is clear: meteorological wind is FROM; transport is `(wind_from+180) mod 360`; selected graph edges are aligned source-to-destination with transport; positive `p_dst-p_src` is the penalized increase. In the legacy notebook, the channel-6 scaling/meaning and bearing convention are not validated. Even if the mask selected exactly the intended downwind edges, requiring nonincreasing concentration downwind is only a heuristic and is not generally implied by a source-driven plume.

Source code: notebook cells 7, 13, 20; `src/stpignn/legacy_canonical.py`; corrected comparator `src/stpignn/physics_v2.py`; v2l full derivation `final_blr_results/physics_audit/methodology/PHYSICS_ATTRIBUTION_METHODOLOGY.md`.

## Source exhibit 4: `final_blr_results/final_three_pillars/physics/CONSERVATION_FORMULATION.md`

[EVIDENCE: `final_blr_results/final_three_pillars/physics/CONSERVATION_FORMULATION.md` | SHA-256 `3a486e1fed537adeab82c4b13d4375d7f2f7de22872f58b77bb02f6dab686b6c` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Conservation-aware formulation and data gate

A physically dimensioned passive-tracer balance over a control volume Ω is:

`∂C/∂t + ∇·(u C) = ∇·(K ∇C) + S - k C`,

where C is µg/m³, velocity u is m/s, diffusivity tensor K is m²/s, volumetric source S is µg/(m³ s), and first-order removal k is s⁻¹. Integrating over cell Ωᵢ of volume Vᵢ gives:

`d/dt ∫Ωᵢ C dV = - Σ_f A_f [(u C - K∇C)·n]_f + ∫Ωᵢ S dV - ∫Ωᵢ k C dV`.

For finite volume, each internal face must use one shared flux with opposite signs in its two adjacent cell balances. Closed-domain global mass conservation follows by cancellation of internal fluxes and zero net boundary flux, and only if source/removal terms are also accounted.

#### Required inputs and current status

| Term | Required data | Bengaluru availability / status |
|---|---|---|
| Cell geometry | Non-overlapping 2-D/3-D cells, face areas, normals, volumes, valid CRS and mesh-to-observation mapping | Road graph has nodes/links, not atmospheric cells/faces; no justified road-to-air control-volume construction. **Unavailable**. |
| Initial and evolving concentration | Time-resolved cell concentration field with calibrated observation operator | Station observations are sparse; road-node outputs are estimates, not independent concentration observations. **Insufficient**. |
| Advection | Spatially/temporally resolved wind vector at modeled height, forecast-causal alignment | Station meteorology is sparse and does not resolve street-level flow. **Incomplete/estimated**. |
| Diffusion | Turbulent diffusivity tensor or a calibrated closure varying in space/time | No validated citywide K field or calibration. **Missing**. |
| Source | Emission rate/location/speciation, preferably time-resolved traffic/inventory, units µg/s | No validated Q field. Synthetic northing is not terrain; no emissions values may be invented. **Missing**. |
| Boundary flux | Inflow/outflow and boundary concentration or a justified boundary condition | Not established for a city-air domain. **Missing**. |
| Removal | Deposition/chemistry/settling terms with coefficients and units | No validated removal field. **Missing**. |
| Time integration | Observation interval, forecast dt, stable discretization and measurement alignment | Station series exists but cannot repair absent grid/flux terms. |

Road links are transportation geometry, not atmospheric cell faces. A road-edge graph must not be used as a finite-volume mesh without a separate physical construction and validation. The right path is a separately reviewed domain/mesh and data proposal; no new neural training is needed to verify the numerical scheme.

The implemented synthetic 1-D diagnostic uses conservative upwind advection, centered diffusive face flux, explicit Euler, periodic boundaries for analytic convergence, and an explicitly accounted nonperiodic boundary-flux identity. It tests algebra and numerical behavior only. It is not a Bengaluru atmospheric solver and does not retroactively alter any ST-PIGNN result.

## Source exhibit 5: `final_blr_results/final_three_pillars/physics/NUMERICAL_TEST_RESULTS.md`

[EVIDENCE: `final_blr_results/final_three_pillars/physics/NUMERICAL_TEST_RESULTS.md` | SHA-256 `3cba2c3b3562e248f780419ca2b2a1b41d79b120c5f206a56c0e5b822e9d8453` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Numerical conservation diagnostic results

Command: `python final_blr_results/final_three_pillars/physics/conservation_diagnostic.py`. Machine-readable output: `NUMERICAL_TEST_RESULTS.json`.

| Test | Result | Tolerance |
|---|---:|---:|
| Constant concentration, periodic domain RHS | 0 µg m⁻³ s⁻¹ | exact zero |
| Closed periodic advective-diffusive mass relative error | 0 | < 1e−12 |
| 1-D advection L1 error, n=64 / 128 / 256 | 2.7716e−3 / 1.2115e−3 / 5.5894e−4 µg/m³ | strictly decreasing |
| Diffusion Fourier-mode L1 error, n=64 / 128 / 256 | 2.8974e−4 / 7.2317e−5 / 1.8072e−5 µg/m³ | strictly decreasing |
| Uniform source/removal equilibrium residual | 0 µg m⁻³ s⁻¹ | < 1e−14 |
| Nonperiodic net boundary mass identity error | 2.14e−15 µg | < 1e−12 |

The discretization accounts for source/sink dimensions and boundary flux. The periodic test is a synthetic closed-domain case. The solver uses NumPy and is not differentiable; autograd checks are not applicable. CFL/diffusion stability limits are respected by selected explicit time steps in the test harness. No real weather, emissions, diffusivity, concentration grid, or road geometry enters.

**Interpretation:** the conservative finite-volume arithmetic is verified for these synthetic cases. Empirical atmospheric mass conservation is **not evaluated**. The historical ST-PIGNN loss remains a directional prediction regularizer.

## Source exhibit 6: `final_blr_results/final_three_pillars/physics/PHYSICS_FINAL_VERDICT.md`

[EVIDENCE: `final_blr_results/final_three_pillars/physics/PHYSICS_FINAL_VERDICT.md` | SHA-256 `17241b6d919518e854c306b0a2edbd6f9d8cdfcb7f583b839e0b558323764cd3` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Physics final verdict

**Classification: PHYSICALLY ASSUMPTION-BOUND.** A separate 1-D finite-volume balance passed synthetic numerical checks. This does not demonstrate that Bengaluru ST-PIGNN is conservative or that any road-level concentration field obeys atmospheric mass balance.

The original loss is a wind-selected squared positive endpoint-difference penalty with a sigmoid edge factor and scheduled λ. The corrected v2l study preserves the broad directional hinge concept while fixing wind convention and using a specified distance factor. Neither includes ∂C/∂t, face flux conservation, validated source Q, diffusion closure, boundary flux, deposition, or real control-volume geometry. Historical outcomes remain the v2l mixed horizon findings; the h=24 point effect is unfavorable, and physical specificity was unsupported relative to generic smoothing.

Allowed: “we evaluated a directional monotonicity regularizer and independently verified a synthetic 1-D conservative finite-volume diagnostic.” Not allowed: mass-conserving ST-PIGNN, solved advection-diffusion dynamics, validated Gaussian plume, or measured atmospheric conservation. Any integrated physical loss requires a reviewed mesh/data protocol and source/meteorology/diffusivity/boundary evidence; no training or new loss integration was performed.
