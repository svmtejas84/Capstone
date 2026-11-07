# Volume 16 — Original vision, realized system and future gates

<a id="volume-16"></a>

## Editorial reconstruction and evidentiary boundary

The original vision joined sparse-monitor prediction, physics-guided urban concentration fields and safer route allocation. The completed system is narrower: exploratory corrected station forecasting; structurally valid road data; neural-assisted city maps with unfavorable station holdout evidence; numerical but nonempirical conservation diagnostics; version-specific descriptive IG; software-feasible directed-edge allocation; and an RGDR hypothesis stopped by sparse training exposure. The defensible contributions are engineering reconstruction, explicit leakage/protocol correction, unusually complete negative controls and bounded computational demonstrations. Independent roadside sensing, a genuinely new city, calibrated weather/emissions/traffic inputs and prospective validation would be needed for broader physical or public-health claims. These are future gates, not completed experiments. [EVIDENCE: v2r and v2t final handoffs | final_blr_results/final_research_v2r/FINAL_RESEARCH_HANDOFF.md; final_blr_results/final_routing_closure/v2t/FINAL_V2T_HANDOFF.md | snapshot 1c46a4b]

## Full round-specific source exhibits

The exhibits reproduce the cited local reports as source evidence. Their original round-specific conclusions may be narrower than later findings; read the editorial reconstruction and final synthesis before treating one exhibit as the final verdict.

## Source exhibit 1: `final_blr_results/ieee_paper_evidence/FINAL_PAPER_EVIDENCE_HANDOFF.md`

[EVIDENCE: `final_blr_results/ieee_paper_evidence/FINAL_PAPER_EVIDENCE_HANDOFF.md` | SHA-256 `23ba2c5484d26e28aa99f65d8c4080d7dd0094639e07a86b22259a7a539c8a45` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Final paper evidence handoff (not a manuscript)

#### Research record

The evidence package consolidates Bengaluru results from the historical production notebook through v2r. The original ten-page IEEE BigData manuscript PDF and four BigData/two DELCON full review texts were not found in the repository. They are explicitly pending transfer; exact quotations, reviewer assignment, original page/figure mapping and complete bibliography audit remain unavailable. This handoff does not draft any paper section.

#### What was implemented

The historical production notebook implements a 16-channel GINE–GRU over road partitions with a legacy directional hinge and a surviving old checkpoint. It does not provide a scientifically defensible corrected road forecast: target-hour pollutant input, copied station histories, timeline wrap risk, sparse supervision and omitted partition boundaries were documented. The corrected experiment instead forecasts on a separate 15-station, 60-directed-edge kNN graph using 18 channels and a 12-hour history. It predicts observed monitoring-station targets, not road labels.

#### Dataset and authoritative evidence

Bengaluru station forecasting uses a small 15-monitor dataset with sparse labels. v2j historical ST-PIGNN weather information differs from v2m's cutoff-safe MLP/TCN weather input. v2l reused saved v2j predictions for physical-penalty attribution; v2m completed 50 MLP/TCN cells and ten frozen comparisons. v2n–v2r consolidated road graph, attribution, spatial estimation, recovery, decoder validation, and RGDR feasibility. The 20-row machine-readable experiment register is `source_registry/EXPERIMENT_SOURCE_REGISTER.csv`; methodological source paths and chronology are linked there.

#### Strongest positive findings

- The station-level system produces exploratory multi-horizon forecasts on the stated monitoring population.
- In the fixed v2m comparison family, ST-PIGNN had lower MAE than MLP at h=6 (−0.8066 µg/m³, Holm p=.0049975) and h=12 (−0.5171, Holm p=.0089955), but the input weather protocols differ. No ST-PIGNN–TCN contrast survived Holm.
- Directional regularization had comparatively favorable h=6 evidence; results vary by horizon and seed.
- The 154,902-node road network passed structural topology checks, and v2r generated finite estimates for every road node at three frozen h=6 targets.
- v2r issue-time-safe station source forecasts were fit across spatial folds; exact pipeline and checkpoints are inventoried in its methodology/archive.

#### Strongest negative findings

- Corrected W6 LOSO loses to weather/static ridge: MAE 22.314 versus 20.624 µg/m³ on 11 scored spatial sites; four stations have no test targets.
- The v2r decoder loses to train-only mean and forecast-IDW (27.360 versus 20.634 and 20.154 MAE), with decoder worse at 9/11 sites. v2j benchmark metrics were independently recomputed for 85 model-horizon rows; all v2m 50 individual cells, 10 five-seed ensembles, and 10 frozen paired deltas were also checked against archived predictions. v2r pooled and per-site LOSO summaries were recalculated from paired outputs. The road maps are experimental neural-assisted estimates, not validated road concentrations.
- v2l penalty gains are horizon-dependent; h=24 is unfavorable, and physics did not establish conservation, PDE fidelity, or specificity beyond generic smoothing.
- RGDR binary and continuous gates retain too little train directional mass; v2r stopped before predictive model fitting. Prediction gain is NOT EVALUATED and novelty NOT ESTABLISHED.
- Captum is available for v2m MLP/TCN only; 85/228 completeness records were flagged. Corrected ST-PIGNN IG is unavailable.
- No roadside accuracy, calibrated road uncertainty, or independent replication is established. Routing code and an offline simulator exist, but one saved 1,000-trip run admitted only 444 trips; admitted-only dose increased 0.121% and mean travel time increased 0.146%. Its static PM2.5 field is unvalidated, and no route/exposure effectiveness is established.

#### Reviewer reconciliation

Conference-specific matrices include every issue category supplied in the task and the actual available counter-evidence. They do not fabricate exact review wording or reviewer assignment. Source reviews must be transferred to resolve pending points. Valid criticisms that remain should be acknowledged; claim withdrawal is an acceptable resolution.

#### Claim boundaries

Supportable: exploratory station forecasting on the defined observed monitor population; limited protocol-labeled neural comparison; mixed regularization effect; graph structural integrity; computational generation of road estimates; software-level RGDR math/tests; descriptive v2m IG with numerical flags.

Must be withdrawn or explicitly not established: broad superiority to neural baselines, physical conservation/advection-diffusion, causal transport, accurate citywide/roadside concentrations, validated exposure-aware routing, RGDR novelty or predictive superiority, and independent replication. Full list: `claims/`.

#### Tables and figures

There are 15 CSV result tables under `results/`, 21 table/export entries in `tables/table_manifest.csv` (including recomputation checks and the figure manifest), and 14 publication-style diagnostic figures (PNG and PDF) catalogued in `figures/figure_manifest.csv`. Figures include horizon benchmarks, physics effects/seed stability/Laplacian comparisons, spatial pooled/per-site/coverage, road support and station locations, city execution, RGDR exposure, and Captum completeness. They use saved outputs and are descriptive, not new experiments.

#### Missing artifacts and reproducibility

Missing: original PDF, six full review reports, original bibliography source, and corrected ST-PIGNN Captum weights. Saved v2m prediction parquet members were read directly from the existing ZIP archive for metric verification; the package does not duplicate those inputs. Some other historical source inputs/checkpoints are local-only or contained in prior verified archives. Follow `reproducibility/REGENERATION.md`; hashes and environment records are in that directory. No ZIP or checkpoint artifact is committed here.

#### Second-city handover

`final_blr_results/second_city_handover/` is a separate independent-replication handoff. London and Copenhagen data gates remain blocked; neither has eligibility evidence or training approval. The next session should perform eligibility and protocol review only unless separately authorized.

## Source exhibit 2: `final_blr_results/final_research_v2r/FINAL_RESEARCH_HANDOFF.md`

[EVIDENCE: `final_blr_results/final_research_v2r/FINAL_RESEARCH_HANDOFF.md` | SHA-256 `caafc9c9842e5871c1e9bae8115acb12c883dda38c8e3a63457120b504d6d549` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Bengaluru v2r final research handoff

#### Research status

v2r is complete with a negative spatial-decoder result and an RGDR feasibility stop. All evidence is exploratory: the Bengaluru dataset and test period have been exposed in previous rounds. No paper, other-city training, new architecture search or test-tuned selection was performed. Historical v2j–v2q results were preserved.

#### Citywide forecasting

- **Source forecasts:** A corrected station-level GINE–GRU was fit in 15 outer station-isolated folds plus 15 time-block crossfit folds (30 total, seed 11). It uses the existing corrected architecture, 18 feature channels and 12 historical hours for h=6. Forecast input windows end at target−6h; target-hour features are excluded. No held-out station pollutant history, target, preprocessing or anchor data was used in its own fold. Per-fold models, manifests and forecast outputs are under `citywide/station_forecasts/`.
- **Decoder:** The existing frozen 1,249-parameter v2q compact decoder was trained from cross-fitted forecasts; validation selected epoch 3. Genuine LOSO validation scored 11 stations / 14,583 pairs; four stations had no eligible test observations. Pooled MAE: train-only spatial mean 20.634, forecast-IDW 20.154, decoder 27.360 µg/m³. Decoder-minus-IDW equal-site MAE difference was +5.101 (station-bootstrap 95% CI +1.815,+8.302). Decoder lost to each control at 9/11 scored sites. It does not improve the controls.
- **Full-city execution:** Completed for 154,902 road nodes at three frozen h=6 targets: 2025-10-08 13:00, 2026-02-10 07:00 and 2026-03-28 23:00 UTC. Road outputs are a combination of corrected GINE–GRU station forecasts and compact neural spatial decoder; IDW is retained as a comparator. They are **experimental neural-assisted estimates**, not observations or validated road-level predictions. All node outputs are finite and aligned; deterministic repeat inference matched exactly. The run took 56.44 seconds including decoder fit and maps; complete-node expansion was 1.12–1.30 seconds per timestamp, peak RSS 1.49 GB, GPU VRAM 0 for spatial expansion. Source GINE–GRU folds used up to 1.831 GB GPU memory per model.
- **Support:** Median nearest-station distance 3.315 km; 19.45% of road nodes exceed 5 km; 60.58% are outside the 15-station convex hull. These are support diagnostics, not calibrated prediction intervals. No independent road-side measurement exists, and held-out decoder results are unfavorable. Do not claim accurate citywide concentration or exposure mapping.

#### RGDR

- `RGDR_BINARY_V1` is preserved unchanged, with prior 2.3% train edge-retention finding.
- `RGDR_CONTINUOUS_V2` is implemented as `q_i=exp(-age/4h)` for eligible observed pollutant values aged 0–24 hours; edge weight is `q_src q_dst`. It preserves the original directional mask, length factor, normalization, λ and warm-up. Age uses past observed values only.
- Existing physics tests plus continuous RGDR tests passed 13/13. The train-only h=6 diagnostic retained 2.48% directional edge mass and had 74.75% zero-penalty hours, failing frozen thresholds of ≥10% and <50%. The pilot stopped before model fitting. RGDR predictive effect is **NOT EVALUATED**, not zero. No claim of forecasting gain or physical conservation is supported. Prior-art review concluded novelty is not established.

#### Claim assessment

| Claim | Status | Permitted conclusion |
|---|---|---|
| Issue-time-safe station h=6 forecasts can be generated | SUPPORTED as engineering | Corrected forecast code produced finite, cutoff-checked station predictions; Bengaluru results remain exploratory. |
| Learned decoder improves spatial generalization over controls | UNSUPPORTED | It performed worse than forecast-IDW and training-only mean on the 11 scored sites. |
| Full road network can be populated computationally | SUPPORTED as computational execution | Three 154,902-node arrays were generated and reproduced; this is not accuracy evidence. |
| Road-node concentration accuracy | NOT EVALUATED | No independent roadside targets exist. |
| RGDR implementation and mathematical checks | SUPPORTED as software correctness | Formula and tests pass; optimization feasibility fails. |
| RGDR predictive advantage, novelty or physical validity | NOT EVALUATED / NOT ESTABLISHED | No matched pilot ran; prior art is close and no conservation law is implemented. |
| Citywide exposure/routing benefit | NOT EVALUATED | No validated road concentration or route comparison is available. |

Earlier evidence remains binding context: v2m completed all 50 MLP/TCN cells; no ST-PIGNN-versus-TCN contrast survived reported Holm correction; v2l/v2p did not demonstrate physics specificity or mass conservation; previous LOSO favored weather/static ridge over ST-PIGNN (22.314 vs 20.624 µg/m³ on 11 sites); original notebook full-road input construction was historically target-leaking. The new v2r full-city demonstration does not overturn these limitations.

#### Required next evidence

Further RGDR work requires a revised frozen reliability rule that passes training exposure without test-based tuning, then a matched controlled pilot and an independent dataset. A publishable citywide accuracy claim requires independent roadside PM2.5 measurements, calibrated uncertainty and spatial validation at genuinely independent locations. Any new large training campaign requires supervisor review. No further Bengaluru engineering is authorized after v2r without that review.

#### Recovery and artifacts

See `EXPERIMENT_PROTOCOL.md`, `citywide/{methodology/CITYWIDE_METHODOLOGY.md,CITYWIDE_FINAL_VERDICT.md}`, `citywide/spatial_validation/SPATIAL_VALIDATION_VERDICT.md`, `rgdr/RGDR_FINAL_VERDICT.md`, `reproducibility/REPRODUCIBILITY.md`, `reproducibility/artifact_manifest.json`, and the v2r archive verification files. `results/codex_log/RESUME.md` records exact Git/push status and recovery commands.

Separate supplemental bundles are `archive/citywide_v2r.zip` and `archive/rgdr_v2r.zip`; their byte sizes, SHA-256 values, CRC results, and per-member hashes are recorded in `archive/archive_verification.json` and the two `archive/*_members.csv` files. The archive builder/verifier are `reproducibility/build_verify_archives.py` and `reproducibility/verify_archives.py`. Large data and checkpoint artifacts remain outside Git and are included in the citywide bundle; their source inputs are identified by hash in `reproducibility/artifact_manifest.json`.

## Source exhibit 3: `final_blr_results/final_three_pillars/FINAL_THREE_PILLARS_HANDOFF.md`

[EVIDENCE: `final_blr_results/final_three_pillars/FINAL_THREE_PILLARS_HANDOFF.md` | SHA-256 `c5e10d783b02214144f65c4b94d827d5a1a10f813be5881c25679070f33b806d` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Final three-pillars handoff

Date: 2026-11-07. Starting HEAD: `52c119c320b014a285f399e8de9420d364d17614`; branch: `research/bengaluru-v2r-final`. Work is limited to physics diagnostics, routing recovery/toy validation, and bounded Captum attribution. No model training, new forecasting, or test-guided tuning was performed.

#### Physical conservation

The legacy production notebook applies a direction-masked endpoint hinge on concentration differences, weighted by an edge attribute. It has no time derivative, finite-volume mass, flux divergence, emissions source, removal, or complete boundary accounting. It does **not** conserve mass. The v2l corrected directional regularizer is also a monotonicity heuristic rather than a conservation equation.

A standalone finite-volume diagnostic was implemented and run on synthetic periodic and bounded domains. It verified constant-field balance, one-dimensional advection/diffusion convergence, source/sink balance, boundary-flux accounting, and closed-domain mass to the tolerances recorded in `physics/NUMERICAL_TEST_RESULTS.md`. Classification: **CONSERVATION FORMULATION VALIDATED NUMERICALLY** for the synthetic discretization, but **PHYSICALLY ASSUMPTION-BOUND** for real Bengaluru air. Empirical atmospheric conservation is not evaluated because measured cell geometry, emissions, diffusivity, meteorological fields, vertical structure, and defensible atmospheric boundary conditions are unavailable. Historical checkpoints are unaffected and must not be described as mass-conserving.

#### Routing and exposure

Recovered implementation paths are documented in `routing/ROUTING_IMPLEMENTATION.md`. Deterministic toy graphs verify shortest/fastest/min-dose behavior, disconnected paths, and a shared-edge capacity counterexample. The API Gale–Shapley path representation cannot enforce overlapping edge capacity; the offline bundle allocator represents shared links but is a heuristic quota process and does not establish classical stable matching or welfare optimality.

The available seed-42 historical simulation admitted 444 of 1,000 requests (44.4%). Among admitted requests, modeled dose rose 0.1211% and travel time rose 0.1463% relative to its recorded comparison. The underlying static concentration snapshot is not a validated forecast. A new full-network route benchmark was not run because input concentration/capacity provenance does not support a valid extension. Independent real-world exposure reduction, travel-time benefit, and capacity guarantees are **UNSUPPORTED**.

#### Captum

IG completed on v2c h=1 (54 baseline/example records across five checkpoints and nine fixed examples) and v2r outer-LOSO h=6 (18 records across three held-out stations and two baselines). Wrapper errors and completeness deltas are small; no nonfinite or flagged records were found. Full tensors, row-level records, summaries, selection metadata, figures, scripts and run markers are retained under `captum/`. Results explain only model sensitivity relative to selected baselines. They are not causal or physical evidence.

The final corrected v2j checkpoints and matched λ=0 checkpoints are missing; no compatible historical artifacts were found for those comparisons. v2c/v2r models are not substitutes for v2j weights. No regeneration training was authorized or performed.

#### Claims and recovery

The machine-readable status table is `CLAIM_EVIDENCE_MATRIX.csv`. The updated IEEE package reference is `IEEE_EVIDENCE_SUPPLEMENT.md`. Full checksums and regeneration commands are under `reproducibility/`; the verified ZIP path and SHA-256 are recorded in `reproducibility/ARCHIVE_VERIFICATION.json`.

The working branch and source notebook are identified in `RECOVERY_AUDIT.md`. Read `captum/CAPTUM_FINAL_VERDICT.md`, `physics/PHYSICS_FINAL_VERDICT.md`, and `routing/ROUTING_FINAL_VERDICT.md` before reusing any pillar claim. Final Git/remote status is recorded in `results/codex_log/RESUME.md` after push verification.

## Source exhibit 4: `final_blr_results/final_routing_closure/v2t/FINAL_V2T_HANDOFF.md`

[EVIDENCE: `final_blr_results/final_routing_closure/v2t/FINAL_V2T_HANDOFF.md` | SHA-256 `17b274687a631fac69150b9187495e04c786ea8fb1fd5d6ee6c63967e538394b` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Final v2t routing handoff

The protocol was frozen and pushed before code or benchmark execution. The original `matcher.gale_shapley.batch_match` remains available with `TOXICITY_ROUTE_ALLOCATOR=original`; the serving API defaults to the new `matcher.edge_capacity_da.allocate_shared_edges`. The historical offline `scripts.evaluate_routing_gs.deferred_acceptance` is unchanged. The corrected path enforces supplied route/directed-edge quotas and gives `UNASSIGNED` when no feasible route exists. It has no proven classical stability or welfare guarantee.

Focused correctness tests passed 20/20 after recording and repairing a test-fixture priority mismatch and a disconnected candidate `NodeNotFound` defect. The 36-cell supervised benchmark completed, with 1,008 scenario-request instances and 6,048 saved method-request rows. An independent route/occupancy scan found 0 invalid paths and 0 shared-edge quota violations. All requests were assigned in all methods/scenarios; max edge utilization was only 5.405%. Original and corrected serving allocations were identical in all 1,008 instances. Thus the city benchmark did not stress capacity; toy cases demonstrate the correction.

Original-field corrected versus shortest mean batch-level paired modeled-dose change: −0.001207%; time overhead +0.001324%. All-request, admitted and common-admitted sets are identical here. Uniform +25% concentration preserved routes; spatial sine changed 11.11% of corrected paths; support-distance perturbation changed 1.59%, with no assignment changes. Four-scenario batch work totaled about 104 s; original-field batch runtime averaged 1.236/2.738/4.734 s at 12/24/48 requests. No independent exposure claim follows.

Source, frozen protocol, tests, per-request parquet, comparison/capacity/sensitivity CSVs, statistical methodology, claim decision, artifact hashes and supervised logs are in this directory. The additive IEEE supplement is `final_blr_results/ieee_paper_evidence/ROUTING_VALIDATION_SUPPLEMENT.md`. The verified local ZIP and final Git state are recorded in `results/codex_log/RESUME.md`. Previous Bengaluru outputs and archives remain preserved.

## Source exhibit 5: `final_blr_results/second_city_handover/BENGALURU_LESSONS_AND_FAILURES.md`

[EVIDENCE: `final_blr_results/second_city_handover/BENGALURU_LESSONS_AND_FAILURES.md` | SHA-256 `acc79a17d1b499f74c2b06644c79137d8ef6306233f3cfb18e352b402c93d23b` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Second-city research handover — independent replication candidate

This is a data/protocol handover only. London is a candidate, not approved. No second-city data eligibility gate is passed and no training is authorized. Bengaluru has repeatedly exposed test data, so independent replication is needed to determine whether forecasting/physics findings transfer beyond the development city. Do not select a city or protocol from expected scores.

#### Lessons

1. Keep station and road graphs separate; topology does not provide road labels.
2. Enforce forecast-cutoff provenance for every feature; original notebook included target-hour pollutant input and copied station histories to roads.
3. Record v2j/v2m weather protocols separately; comparisons are cross-protocol.
4. Use independent spatial sites as inferential units; repeated timestamps do not create more sites. Four LOSO stations remained unscored.
5. Strong baselines matter; ridge, station mean and forecast-IDW were competitive or better.
6. A lower hinge violation score does not establish physical validity, source terms or conservation.
7. RGDR age gate did not solve sparse regularization exposure; do not relax post hoc.
8. No independent road truth or route effectiveness result exists.

Historical test exposure means Bengaluru is exploratory for any future design.

## Source exhibit 6: `final_blr_results/second_city_handover/SECOND_CITY_RESEARCH_GATES.md`

[EVIDENCE: `final_blr_results/second_city_handover/SECOND_CITY_RESEARCH_GATES.md` | SHA-256 `6971b49ab625d9cc2448965ff2b121d89cc2b5616d9c0b3cfbcf4e1cf2d18e8e` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Research gates

**Gate 0: eligibility.** Source-level hourly inventory, instrument comparability, station count, operating duration, spatial coverage, license, weather alignment. Fail => no training.

**Gate 1: protocol.** Supervisor approves frozen forecast-time information set, spatial and temporal split, baselines, physical quantities, statistical family, and resource limits.

**Gate 2: reproducibility.** Pin hashes, environment, transforms, code and backup; dry-run data audit without test-score access.

**Gate 3: bounded pilot.** Only after explicit training authorization; measure runtime and VRAM, validation-only debugging, restart-safe checkpoints.

**Gate 4: locked evaluation.** One untouched external-city test; independent-site analysis and multiplicity plan; preserve negative outcomes.

**Gate 5: claims.** Predictive performance, physics validity, spatial transfer, road estimates, and routing each require separate evidence. No gate implies another.
