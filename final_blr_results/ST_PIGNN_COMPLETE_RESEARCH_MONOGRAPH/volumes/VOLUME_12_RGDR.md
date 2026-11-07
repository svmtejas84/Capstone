# Volume 12 — Binary and continuous reliability-gated regularization

<a id="volume-12"></a>

## Editorial reconstruction and evidentiary boundary

RGDR was a falsifiable attempt to weight the directional penalty by input reliability after mixed physics effects. Binary V1 used imputation flags and retained only about 2.3% of train directional edges. Continuous V2 used past-observation age, q=exp(−age/4h) for eligible ages 0–24h and r=q_source q_target, but still retained 2.48% of directional edge mass and had 74.75% zero-penalty hours. It failed prespecified exposure gates; no comparative forecast pilot ran. Unit tests support implementation properties, not predictive advantage, calibrated reliability, novelty or conservation. The prior-art review finds close quality-aware and adaptive-weighting ideas, leaving originality unsettled. [EVIDENCE: v2r handoff | final_blr_results/final_research_v2r/FINAL_RESEARCH_HANDOFF.md | snapshot 1c46a4b]

## Full round-specific source exhibits

The exhibits reproduce the cited local reports as source evidence. Their original round-specific conclusions may be narrower than later findings; read the editorial reconstruction and final synthesis before treating one exhibit as the final verdict.

## Source exhibit 1: `final_blr_results/citywide_extension/v2p_rgdr/RGDR_RESEARCH_HYPOTHESIS.md`

[EVIDENCE: `final_blr_results/citywide_extension/v2p_rgdr/RGDR_RESEARCH_HYPOTHESIS.md` | SHA-256 `68e0ecbf446e6cfdf0a27dc6e1a48c1259097222dbf54ac9e77cd36c66bd7a4a` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### RGDR falsifiable hypothesis

The corrected station model uses a global coefficient on a wind-cone directional monotonicity penalty. Earlier v2l analysis found mixed horizon/seed effects, a more stable h6 association, no conservation, and no reliable advantage over generic Laplacian smoothing. Larger historical penalty strengths sometimes degraded accuracy. These are motivation, not evidence for the proposed change.

**Hypothesis:** restricting the directional penalty to edges whose two cutoff PM2.5 lags are genuinely observed, using only input-provenance indicators known by forecast cutoff, may improve training/validation robustness relative to a fixed penalty. **Alternative:** reliability gating has no benefit or worsens forecasting, potentially because it removes useful edge constraints or makes the effective penalty sparse. The method is a testable variant, not a physical law or established new contribution.

Development is limited to synthetic tests and training/validation diagnostics on Bengaluru. The repeatedly examined Bengaluru test period is excluded from RGDR configuration selection. No external dataset is ready for a confirmatory claim; a future multi-seed controlled comparison requires the frozen plan and supervisor review in `RGDR_FROZEN_EVALUATION_PROTOCOL.md`.

## Source exhibit 2: `final_blr_results/citywide_extension/v2p_rgdr/RGDR_MATHEMATICAL_SPECIFICATION.md`

[EVIDENCE: `final_blr_results/citywide_extension/v2p_rgdr/RGDR_MATHEMATICAL_SPECIFICATION.md` | SHA-256 `d96147f56b61821d01b13d6b37d6c4f173c6143c03802e50bb538e85a3549096` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Exact RGDR mathematical specification

The existing `src/stpignn/physics_v2.py:batched_penalty(..., variant="corrected_mask")` uses directed edge `(src,dst)` and `diff = pred_norm[:,dst] − pred_norm[:,src]`. The mask selects an edge whose bearing aligns with wind *transport-to* (raw wind-from +180°, half angle 37.5°). For west-from wind (270°), eastbound edges are selected. The original hinge penalizes a **higher predicted downwind value**. Its geometric factor is `g_e = sigmoid(edge_length_m/1000)`; the penalty is `mean_{M=1} ReLU(g_e·diff)^2`, with `pred_norm = predicted physical PM2.5 / cleaned training target SD`. This is a monotonicity heuristic, not a conservation balance.

Let `m_{b,i,c}` be the existing binary `lag_is_imputed` input indicator for station i at forecast cutoff c, where 0 means the immediate PM2.5 lag was observed. Define observation reliability `o=1−m`, clipped to {0,1} after validation, and edge gate `r_{b,e}=o_{b,src,c}o_{b,dst,c}`. No target value, future observation, test outcome or learned weight enters r. The proposed penalty is

`P_RGDR = Σ_{b,e} M_{b,e} r_{b,e} [ReLU(g_e (ŷ_norm[b,dst]−ŷ_norm[b,src]))]^2 / max(Σ_{b,e} M_{b,e} r_{b,e}, 1)`.

`L_total = L_data + λ P_RGDR`, using the same global λ and warm-up as the matched fixed-directional model. When `r≡1`, RGDR equals the existing corrected masked penalty to floating-point tolerance. With zero eligible reliable edges, it returns differentiable zero. The denominator matches the original masked-mean definition at constant reliability; it does not silently rescale by all graph edges.

Controls: (1) λ=0; (2) original fixed directional `M` with r≡1; (3) reliability-weighted **generic symmetric smoothing** over all directed station edges, `Σ r (g_e diff)^2 / max(Σ r,1)`, which has the same reliability signal and geometric factor but no wind mask or rectified sign; (4) RGDR. The generic penalty need not have the same raw magnitude. A future matched experiment must report each train-only penalty magnitude and gradient norm and prespecify any training-only scale calibration for the generic control before validation/test. Do not claim a directional mechanism if RGDR merely changes effective regularization strength.

## Source exhibit 3: `final_blr_results/citywide_extension/v2p_rgdr/RGDR_RELIABILITY_PROVENANCE.md`

[EVIDENCE: `final_blr_results/citywide_extension/v2p_rgdr/RGDR_RELIABILITY_PROVENANCE.md` | SHA-256 `8e84be44ae5f88238b5b4e59c8b4d5fc4df920fb5d47ea6eb253e591ce4add5f` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Reliability provenance and separation

The first implemented gate uses only the existing `lag_is_imputed` channel at the forecast cutoff, constructed by `scripts/benchmark_v2j.py:Context` from the station observed mask. An indicator of zero means the immediate station PM2.5 reading is observed; one means the causal lag/anchor is imputed or carried. Edge reliability is one only if **both** endpoint readings at cutoff are observed. This binary definition avoids an invented fractional confidence coefficient. It is observation-provenance reliability, not calibrated concentration uncertainty.

The wind mask remains the existing corrected directional mask from the archived raw wind direction. It is not multiplied by a claimed wind-quality score: the archive has one known weather source coordinate and no independent local wind uncertainty flags. Spatial support is also distinct; v2o's road IDW support diagnostic is not imported into a 15-station loss. Missingness duration and observed-data age may be useful future variables, but they are not present as a validated fitted reliability model and are not implemented in this first hypothesis. No held-out station's label may be reintroduced through the gate during a spatial holdout. Validation-only diagnostics must derive m from cutoff inputs only.

## Source exhibit 4: `final_blr_results/citywide_extension/v2p_rgdr/RGDR_PRIOR_ART_REVIEW.md`

[EVIDENCE: `final_blr_results/citywide_extension/v2p_rgdr/RGDR_PRIOR_ART_REVIEW.md` | SHA-256 `ad41dbcfbfc82d95872d4dae7f206f3f22e0da9a623605a8fb8ac1bc8fe9c154` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### RGDR prior-art review (primary sources, checked 2026-11-06)

| Work | Relevant established idea | Difference and remaining uncertainty |
|---|---|---|
| [Che et al., GRU-D, *Scientific Reports* 2018](https://www.nature.com/articles/s41598-018-24271-9) | Missingness masks and time intervals can be informative model inputs. | RGDR would use a cutoff missingness indicator to weight a loss term, not change recurrent imputation. Missingness-aware modeling is established. |
| [Cini et al., GRIN, ICLR 2022](https://openreview.net/pdf?id=kOu3-S3wJ7) | Graph message passing can reconstruct missing multivariate sensor time series. | RGDR is not a new graph imputer. It reweights an existing directional penalty. |
| [McClenny & Braga-Neto, SA-PINNs](https://arxiv.org/abs/2009.04544) | Pointwise adaptive physics-loss weights are established. | RGDR uses nonlearned provenance-based edge weights; adaptive physics weighting itself is not novel. |
| [Xiang et al., loss-balanced PINNs, *Neurocomputing* 2022](https://www.sciencedirect.com/science/article/pii/S092523122200546X) | Physics/data loss balancing can be uncertainty-based and adaptive. | RGDR leaves the global λ fixed and modulates eligible graph edges only. |
| [Hettige et al., AirPhyNet, ICLR 2024](https://openreview.net/pdf?id=JW3jTjaaAB) | Air-quality graph forecasting with explicit advection/diffusion-guided modeling is established. | RGDR does not add a governing PDE or validated transport operator; its hinge remains heuristic. |
| [GraPhy, *ACM TOSN* 2026](https://doi.org/10.1145/3734869) | Sparse-monitor air-quality imputation uses coarse wind and graph convection features. | This is close environmental context; no claim that RGDR invents wind-aware sparse-monitor learning. |
| [TransNet, *npj Clean Air* 2026](https://www.nature.com/articles/s44407-026-00052-x) | Directional transport and Laplacian-type graph operators for PM2.5 forecasting have been explored. | RGDR does not inherit its mass-conserving formulation; a simple directionally weighted hinge is narrower. |

**Novelty status: NOT ESTABLISHED.** This search found missingness-aware temporal models, adaptive per-point physics weights, and wind-aware sparse-sensor graph methods. A binary provenance gate on the repository's particular directional hinge may be an implementation-specific experimental variant, but we cannot claim a new general mechanism from this review. A publishable contribution would need a more exhaustive literature search and independent matched-control evidence. No cited paper is used to assert that RGDR will improve Bengaluru accuracy.

## Source exhibit 5: `final_blr_results/citywide_extension/v2p_rgdr/RGDR_VALIDATION_ONLY_RESULTS.md`

[EVIDENCE: `final_blr_results/citywide_extension/v2p_rgdr/RGDR_VALIDATION_ONLY_RESULTS.md` | SHA-256 `69c6d7a16fa7e6adad06bee1eaf71665a8e4844c18a803f09d21f7c757bc5a21` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Training/validation-only RGDR gate diagnostic

`gate_diagnostics.py` reads the existing station observed mask and raw wind direction at forecast cutoffs for all five fixed horizons, restricted to training and validation target hours. It does **not** inspect test targets, train a model, choose λ, or score PM2.5 predictions. The 15-station four-neighbor graph has 60 directed edges. Full per-horizon/split counts are in `gate_diagnostics.csv`.

| Horizon | Train retained directional edge instances | Train hours with zero gated edges | Validation retained edge instances | Validation hours with zero gated edges |
|---:|---:|---:|---:|---:|
| 1 h | 2.36% | 11,251/14,210 (79.2%) | 6.70% | 591/1,961 (30.1%) |
| 3 h | 2.34% | 11,276/14,209 (79.4%) | 6.68% | 597/1,961 (30.4%) |
| 6 h | 2.32% | 11,292/14,206 (79.5%) | 6.66% | 602/1,961 (30.7%) |
| 12 h | 2.31% | 11,320/14,200 (79.7%) | 6.69% | 592/1,961 (30.2%) |
| 24 h | 2.27% | 11,351/14,190 (80.0%) | 6.75% | 586/1,961 (29.9%) |

At h=6, the fixed wind mask has 197,297 training edge instances, but only 4,583 also have two immediately observed endpoint lags. Validation has 29,942 fixed-mask instances and 1,994 gated instances. The binary gate therefore removes most regularization exposure, especially in training. This is a **negative feasibility diagnostic** for the first gate definition. It is not a predictive-loss result, and there is no basis to relax the gate or choose fractional weights from Bengaluru test outcomes. Future work may investigate formally defined observed-data age or reliability categories using train/validation only, but such a change would be a new prespecified variant and needs separate approval before test evaluation.

No validation MAE/RMSE/R² for RGDR exists. The previous v2l physics MAE advantages cannot be assigned to this untrained variant. CUDA access in this sandbox was false; the training authorization remains limited and no CPU neural fit was substituted.

## Source exhibit 6: `final_blr_results/final_research_v2r/rgdr/continuous_v2/RGDR_CONTINUOUS_V2_SPEC.md`

[EVIDENCE: `final_blr_results/final_research_v2r/rgdr/continuous_v2/RGDR_CONTINUOUS_V2_SPEC.md` | SHA-256 `20be4515f9c29e5d4183abf53f5a0edbbabb43f675908c29a5bdb1a6c0708bac` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### RGDR_CONTINUOUS_V2 specification

Preserved binary predecessor: `src/stpignn/rgdr.py`, label **RGDR_BINARY_V1**, and unchanged v2p diagnostics. Continuous implementation: `src/stpignn/rgdr_continuous.py`.

At forecast cutoff c, `Δ_i(c)` is the elapsed number of continuous hourly UTC steps since the latest finite observed PM2.5 reading at station i at or before c. The helper accepts only the observed mask and cutoff indices, not targets or future values. Reliability is `q_i=exp(-Δ_i/τ)` for `0 ≤ Δ_i ≤ 24 h`; no prior observation, age >24 h, or missing age gives q=0; age zero gives q=1. τ is the median positive eligible age across the frozen training cutoff sample, excluding zero, missing, and >24 h values. Here τ=4 h. No free parameter was added.

For directed edge e=(src,dst), `r_e=q_src q_dst`. The original corrected wind mask, source/destination convention, length geometry `g_e=sigmoid(length_m/1000)`, rectified term `h_e=ReLU(g_e(ŷ_dst−ŷ_src))`, normalization by `max(Σ M_e r_e,1)`, λ=0.06 and warm-up are unchanged:

`P_RGDR = Σ M_e r_e h_e² / max(Σ M_e r_e,1)`; `L = L_data + λ_epoch P_RGDR`.

For positive denominator, gradient for node k is `2 Σ_e M_e r_e g_e h_e 1[h_e>0] (1[k=dst]−1[k=src]) / Σ M r`, with λ multiplier in total loss. Reliability is detached data provenance. If all q=1, the penalty equals fixed directional corrected penalty. If every reliability is zero, the returned differentiable penalty and its prediction gradient are zero. `q` describes elapsed-time weighting only; it is not calibrated uncertainty or a statement about physical validity. Generic smoothing comparator uses the same r and g with squared signed edge differences and no wind mask or directional rectification.

Tests: `tests/test_rgdr_continuous_v2r.py` plus unchanged `tests/test_rgdr.py` and `tests/test_physics_v2.py`. Thirteen passed. Constant fractional reliability equivalence is asserted when the existing denominator is above its floor; with very small aggregate reliability, the preserved clamp-at-one can scale the loss down. The age test alters observations strictly after a cutoff and verifies identical age. No test or diagnostic reads Bengaluru test targets to choose τ.

## Source exhibit 7: `final_blr_results/final_research_v2r/rgdr/gate_diagnostics/RGDR_GATE_DIAGNOSTICS.md`

[EVIDENCE: `final_blr_results/final_research_v2r/rgdr/gate_diagnostics/RGDR_GATE_DIAGNOSTICS.md` | SHA-256 `b5e8d13c04b3b41926a000d62ed7bb9a257f1fb1c7411e8c1abd4548af0eb4af` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### RGDR gate feasibility — h=6, training and validation only

Source: `run_gate_diagnostics.py`; input `results/data_v2j_arrays.npz`; 15-node/60-directed-edge corrected station graph; fixed wind-from mask and 24-hour max age. τ=4 hours was fitted once as median positive eligible age from train cutoffs. No test target, neural fit or validation-based gate selection was used. Observation-age distribution and full metrics are in `gate_diagnostics_v2r.csv`.

| Split | Fixed directional edge instances | Binary gate mass / retention | Continuous gate mass / retention | Hours with zero continuous penalty | Continuous effective edge sample size | Median positive age |
|---|---:|---:|---:|---:|---:|---:|
| Train | 196,762 | 4,472 / 2.27% | 4,873.2 / 2.48% | 10,621/14,206 (74.75%) | 5,048 | 4 h |
| Validation | 29,910 | 1,985 / 6.64% | 2,190.6 / 7.32% | 265/1,961 (13.51%) | 2,276 | 5 h |

The continuous gate modestly raises training edge mass relative to binary and reduces zero-gate hours by 4.9 percentage points, but remains far below the frozen minimum 10% mass and exceeds the 50% zero-hour limit. It therefore **fails the predeclared optimization exposure gate**. In a fixed first-64-cutoff proxy calculation, all penalties and gradients were finite; train fixed/binary/continuous/generic values were respectively 0.09375/0.01348/0.04074/1.02033, with prediction gradient norms 0.0271/0.0589/0.0542/0.3196. These are deterministic proxy inputs from cutoff observations, not trained model predictions or evidence of predictive benefit. Generic smoothing has a much larger raw scale; no validation-selected rescaling was attempted.

**Decision: stop RGDR model fitting under frozen rule.** Do not tune τ, lookback, gate thresholds, λ or scaling in response. The gate is mathematically implemented and tested, while its feasible optimization signal remains inadequate. This does not test predictive performance and cannot support a positive or negative accuracy effect. Novelty remains NOT ESTABLISHED per `final_blr_results/citywide_extension/v2p_rgdr/RGDR_PRIOR_ART_REVIEW.md`.

## Source exhibit 8: `final_blr_results/final_research_v2r/rgdr/RGDR_FINAL_VERDICT.md`

[EVIDENCE: `final_blr_results/final_research_v2r/rgdr/RGDR_FINAL_VERDICT.md` | SHA-256 `541511f0e6e625e7276c6613f8506af6cdd9a51f7f78f857a455a8d1720067fa` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### RGDR final verdict — v2r

**Decision: UNSUPPORTED under the frozen feasibility rule; predictive effect NOT EVALUATED.**

`RGDR_BINARY_V1` is preserved as an unchanged copy of `src/stpignn/rgdr.py` and its v2p outcome remains: about 2.3% train directional-edge retention, roughly 79–80% zero-gate train hours. `RGDR_CONTINUOUS_V2` is implemented in `src/stpignn/rgdr_continuous.py` and preserved under this deliverable. It uses observation age with `τ=4 h`, the training-only median positive eligible age, 24-hour maximum lookback, and edge reliability `q_src q_dst`.

All 13 focused tests passed: the continuous-v2 tests plus existing binary RGDR and corrected-physics tests. They cover fixed-loss equivalence at constant-one reliability and at constant fractional reliability when the unchanged normalization denominator is above its floor, wind-mask direction, bounds, missing/zero-weight behavior, finite gradients, differentiability, future-observation exclusion, train-only τ, batch/reproducibility behavior and existing physics behavior.

The frozen h=6 diagnostic retained 4,873.2/196,762 fixed directional edge mass (2.48%) in training; 10,621/14,206 hours (74.75%) had zero continuous penalty. Validation retention was 7.32%, with 13.51% zero hours. The gate therefore fails both preregistered exposure checks (≥10% mass and <50% zero train hours). A finite proxy gradient does not establish a useful learned optimization signal. The proxy comparison's raw continuous gradient norm was 0.0542 versus fixed 0.0271, binary 0.0589, and generic smoothing 0.3196; these are not trained-model gradients.

Per the frozen stop rule, no RGDR GPU training, validation metric comparison, or 12-cell pilot was run. λ=0 and the three regularized training controls were therefore not compared predictively. Do not claim RGDR improves forecasting, solves sparsity, is novel, establishes physical specificity, conserves mass, or generalizes. Prior-art status remains **NOT ESTABLISHED** in `final_blr_results/citywide_extension/v2p_rgdr/RGDR_PRIOR_ART_REVIEW.md`. A new independent dataset and a revised, supervisor-approved reliability definition/protocol would be needed for further training.
