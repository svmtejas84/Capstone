# Complete Failure And Correction Log

This register reproduces the cited source records below, retaining their original protocol and status. Later source exhibits can supersede earlier conclusions; no incompatible populations are pooled.

## Source 1: `final_blr_results/city_scale/final_evidence/KNOWN_LIMITATIONS.md`

[EVIDENCE: `final_blr_results/city_scale/final_evidence/KNOWN_LIMITATIONS.md` | SHA-256 `1be0e1e2307b9bf9091148c3955b67b1517ebc4550cb3ea5d51765eb4f15007d` | snapshot `1c46a4b`]

# Known limitations at Bengaluru freeze

1. The test set was repeatedly inspected during six historical post-hoc deviations. Bootstrap/Holm analyses describe this exposed population; they are not independent confirmation. Five horizons share days and labels, and seeds share the same training/test population.
2. Historical v2j ST-PIGNN inputs average corrected weather at c−30 and c+30, while v2m MLP/TCN use the latest record at or before cutoff. Their matched-target comparisons cannot isolate architecture. Retrospective reanalysis weather may also differ from an issue-time operational forecast source.
3. Fifteen stations train the forecast graph; only eleven have observed test targets in corrected W6 LOSO. Four folds are unscored. Stations are geographically sparse/nonrandom and cannot represent all road microenvironments. Timestamp count is not spatial site count.
4. Corrected v2j ST-PIGNN, λ=0, Laplacian and LOSO fold neural checkpoints plus optimizer/RNG state were not archived. Their saved predictions cannot provide gradients or exact training restart. The legacy root checkpoint and older `results/checkpoints_v2*` have different or uncertain protocol lineage.
5. Road graph topology is sound but its 17 static channels and 16 edge channels differ from the station forecast schema. Only 22 road nodes have stored node-hour rows; 154,880 do not. Unmonitored nodes have no observed PM2.5 lag/anchor or independent concentration truth. The known raw weather source is one coordinate, with no verified city grid mapping.
6. Stored road partitions omit 7,134 cross-boundary arcs and have no demonstrated two-hop halo equivalence. Full-city runtime, CPU RAM, GPU VRAM and throughput were not measured because the scientific compatibility gate failed first. The sandbox also did not expose the host NVIDIA driver.
7. The upwind-inspired hinge uses no measured emissions Q and does not implement a conservative atmospheric balance or full advection–diffusion. Laplacian and wind/PVR controls do not demonstrate physical specificity.
8. v2n IG applies to the compatible v2m station MLP/TCN only. The strict 64-step Captum completeness rule flags 85/228 records; baseline choice changes total absolute attribution substantially. Fine rankings and physical interpretations are limited. No graph-edge or neighbor attribution was available for these station-independent models.
9. Legacy routing field scaling and paired-comparison gaps remain. No validated road-node exposure surface, route-level dose/time gain, or capacity guarantee was established.
10. The two local ZIPs have verified hashes; independent external USB copies remain pending. Some historical source artifacts are missing, so complete bitwise replay of all Bengaluru runs is not possible. No independent external-city replication exists.

## Source 2: `final_blr_results/final_research_v2r/FINAL_RESEARCH_HANDOFF.md`

[EVIDENCE: `final_blr_results/final_research_v2r/FINAL_RESEARCH_HANDOFF.md` | SHA-256 `caafc9c9842e5871c1e9bae8115acb12c883dda38c8e3a63457120b504d6d549` | snapshot `1c46a4b`]

# Bengaluru v2r final research handoff

## Research status

v2r is complete with a negative spatial-decoder result and an RGDR feasibility stop. All evidence is exploratory: the Bengaluru dataset and test period have been exposed in previous rounds. No paper, other-city training, new architecture search or test-tuned selection was performed. Historical v2j–v2q results were preserved.

## Citywide forecasting

- **Source forecasts:** A corrected station-level GINE–GRU was fit in 15 outer station-isolated folds plus 15 time-block crossfit folds (30 total, seed 11). It uses the existing corrected architecture, 18 feature channels and 12 historical hours for h=6. Forecast input windows end at target−6h; target-hour features are excluded. No held-out station pollutant history, target, preprocessing or anchor data was used in its own fold. Per-fold models, manifests and forecast outputs are under `citywide/station_forecasts/`.
- **Decoder:** The existing frozen 1,249-parameter v2q compact decoder was trained from cross-fitted forecasts; validation selected epoch 3. Genuine LOSO validation scored 11 stations / 14,583 pairs; four stations had no eligible test observations. Pooled MAE: train-only spatial mean 20.634, forecast-IDW 20.154, decoder 27.360 µg/m³. Decoder-minus-IDW equal-site MAE difference was +5.101 (station-bootstrap 95% CI +1.815,+8.302). Decoder lost to each control at 9/11 scored sites. It does not improve the controls.
- **Full-city execution:** Completed for 154,902 road nodes at three frozen h=6 targets: 2025-10-08 13:00, 2026-02-10 07:00 and 2026-03-28 23:00 UTC. Road outputs are a combination of corrected GINE–GRU station forecasts and compact neural spatial decoder; IDW is retained as a comparator. They are **experimental neural-assisted estimates**, not observations or validated road-level predictions. All node outputs are finite and aligned; deterministic repeat inference matched exactly. The run took 56.44 seconds including decoder fit and maps; complete-node expansion was 1.12–1.30 seconds per timestamp, peak RSS 1.49 GB, GPU VRAM 0 for spatial expansion. Source GINE–GRU folds used up to 1.831 GB GPU memory per model.
- **Support:** Median nearest-station distance 3.315 km; 19.45% of road nodes exceed 5 km; 60.58% are outside the 15-station convex hull. These are support diagnostics, not calibrated prediction intervals. No independent road-side measurement exists, and held-out decoder results are unfavorable. Do not claim accurate citywide concentration or exposure mapping.

## RGDR

- `RGDR_BINARY_V1` is preserved unchanged, with prior 2.3% train edge-retention finding.
- `RGDR_CONTINUOUS_V2` is implemented as `q_i=exp(-age/4h)` for eligible observed pollutant values aged 0–24 hours; edge weight is `q_src q_dst`. It preserves the original directional mask, length factor, normalization, λ and warm-up. Age uses past observed values only.
- Existing physics tests plus continuous RGDR tests passed 13/13. The train-only h=6 diagnostic retained 2.48% directional edge mass and had 74.75% zero-penalty hours, failing frozen thresholds of ≥10% and <50%. The pilot stopped before model fitting. RGDR predictive effect is **NOT EVALUATED**, not zero. No claim of forecasting gain or physical conservation is supported. Prior-art review concluded novelty is not established.

## Claim assessment

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

## Required next evidence

Further RGDR work requires a revised frozen reliability rule that passes training exposure without test-based tuning, then a matched controlled pilot and an independent dataset. A publishable citywide accuracy claim requires independent roadside PM2.5 measurements, calibrated uncertainty and spatial validation at genuinely independent locations. Any new large training campaign requires supervisor review. No further Bengaluru engineering is authorized after v2r without that review.

## Recovery and artifacts

See `EXPERIMENT_PROTOCOL.md`, `citywide/{methodology/CITYWIDE_METHODOLOGY.md,CITYWIDE_FINAL_VERDICT.md}`, `citywide/spatial_validation/SPATIAL_VALIDATION_VERDICT.md`, `rgdr/RGDR_FINAL_VERDICT.md`, `reproducibility/REPRODUCIBILITY.md`, `reproducibility/artifact_manifest.json`, and the v2r archive verification files. `results/codex_log/RESUME.md` records exact Git/push status and recovery commands.

Separate supplemental bundles are `archive/citywide_v2r.zip` and `archive/rgdr_v2r.zip`; their byte sizes, SHA-256 values, CRC results, and per-member hashes are recorded in `archive/archive_verification.json` and the two `archive/*_members.csv` files. The archive builder/verifier are `reproducibility/build_verify_archives.py` and `reproducibility/verify_archives.py`. Large data and checkpoint artifacts remain outside Git and are included in the citywide bundle; their source inputs are identified by hash in `reproducibility/artifact_manifest.json`.

## Source 3: `final_blr_results/final_routing_closure/original_gale_shapley_audit/ORIGINAL_ROUTING_VERDICT.md`

[EVIDENCE: `final_blr_results/final_routing_closure/original_gale_shapley_audit/ORIGINAL_ROUTING_VERDICT.md` | SHA-256 `5472c1825a97d5451de4dce295b20369c02b28c166d53778a3359ac90395e754` | snapshot `1c46a4b`]

# Original routing verdict

## Decision: D — Contains an identifiable correctness defect

The serving `matcher.gale_shapley.batch_match` is a recognizable commuter-proposing, route-capacitated deferred-acceptance procedure in its main proposal/displacement loop. Under fixed route quotas and complete strict preferences, with responsive route choices and **without** its post-loop fallback, ordinary many-to-one deferred acceptance has the standard termination, feasibility and stability guarantees. A bounded toy case agrees with an independent exhaustive stable-assignment enumeration.

The shipped function does not preserve those conditions for all inputs. Its fallback assigns any remaining commuter to nearest/least-loaded route without checking capacity or acceptability. A two-commuter, one-route/quota-one example returns two assigned commuters. It also lacks shared-edge resource data; two different routes sharing a bottleneck can independently fill their quotas beyond that edge's limit. These are concrete allocation-feasibility defects in the serving matcher. No production correction is made in this audit.

`matcher/README.md` describes fallback as complete assignment “under capacity constraints” and says equilibrium is validated; the implementation and tests contradict the capacity assertion when supply is exceeded, and no runtime stability check is called by `batch_match`. Treat those README statements as documentation claims, not verified properties.

Separately, the offline evaluator does account for shared directed-edge quotas and asserts ex-post feasibility for its allocation. This narrow mechanism is real and was exercised by the prior 1,000-trip simulation. However, it is not the API matcher and does not establish formal stability for multi-edge route bundles, validated traffic capacities, dose reduction, or operational performance.

## Classification by component

- **API route-based deferred acceptance:** D (identifiable fallback capacity/acceptability defect; shared-edge capacities unmodeled).
- **Offline route-bundle allocation:** B (edge-feasible under its supplied directed-edge quotas and finite listed options, subject to heuristic quota assumptions; formal stability/welfare unproved).
- **Historical quantitative exposure/routing claim:** C (an implementation and one saved simulation exist, but quantitative evidence is exploratory, admission-conditioned and based on invalid/unvalidated road concentration inputs; effectiveness not supported).
- **Notebook-contained routing:** E as a notebook claim (no routing/matching implementation in the named production notebook); repository-level routing code remains recoverable from modules and scripts.

## Minimum future work (approval required before implementation/large runs)

1. Decide whether the serving contract should allow unassigned demand. Remove or redesign capacity-bypassing fallback only after supervisor approval; report unmatched requests rather than silently exceeding quota.
2. For physical shared-edge enforcement, pass route edge bundles and shared directed-edge capacities to allocation or solve a specified constrained assignment problem; use measured/justified capacity data. Keep stability and feasibility as separate properties.
3. Add independent tests for all path/capacity edge cases, preference acceptability and the no-blocking-pair condition for the exact restricted API model.
4. Before an effectiveness benchmark, use validated forecast-time concentrations and OD demand, freeze capacity definitions and comparator population, retain paths/edge occupancies, record runtime, and report unallocated demand. This audit did not run that benchmark.

Primary report set: this directory. Prior routing evidence remains in `final_blr_results/final_three_pillars/routing/` and the IEEE evidence package, without alteration.

## Source 4: `final_blr_results/final_routing_closure/v2t/ROUTING_FINAL_VERDICT.md`

[EVIDENCE: `final_blr_results/final_routing_closure/v2t/ROUTING_FINAL_VERDICT.md` | SHA-256 `384b88ea1b58ebca57c9c725d309e2bea40101c2257cd99e1fc39883c307966b` | snapshot `1c46a4b`]

# v2t final routing verdict

**Software correction: SUPPORTED within the declared model. Exposure effectiveness: UNSUPPORTED as an empirical claim.** The corrected additive allocator preserves the serving system's commuter and route preference builders, enforces route and shared directed-edge quotas, atomically releases displaced routes, and returns `UNASSIGNED` when no feasible route remains. The historical matcher and offline bundle evaluator remain callable. The critical focused suite passed 20/20, and an independent scan of saved outputs found zero invalid routes and zero declared-capacity violations.

The frozen scenario used a 1,428-node central Bengaluru graph and four static concentration scenarios. There were 252 requests per scenario (1,008 scenario-request instances). All methods assigned all requests; original and corrected serving allocators returned the **same path in all 1,008 cases**. Maximum edge utilization was 5.405%, with no saturated edge. Thus the city scenario does not demonstrate a capacity-driven improvement; the defect correction is supported by explicit stress tests on deterministic toy graphs.

For the original field, the corrected allocator's mean across nine batch-level paired dose differences versus shortest/fastest was **−0.001207%**, with batch range −0.006322% to 0; mean travel-time overhead was **+0.001324%**. Versus unconstrained minimum dose, its mean dose was +0.000413%. These differences are numerically tiny and should not be described as meaningful exposure benefit. The original and corrected allocators were identical here. The offline bundle control had different path preferences and matched the unconstrained minimum-dose route in this unstressed scenario.

Uniform +25% concentration preserved all route choices and assignments. Spatial sine perturbation preserved corrected assignments but changed 11.11% of its route paths; support-distance perturbation changed 1.59%. All corrected scenario outputs remained feasible and fully assigned. These are synthetic sensitivity probes, not calibrated uncertainty intervals.

The new algorithm does **not** establish classical preference stability or global welfare optimality for overlapping path bundles. The road concentration field comes from an historically invalid/unvalidated city model, and traffic capacities, OD demands, speed and RMV are assumptions. No measured human exposure, operational congestion, actual edge capacity, full 154,902-node network routing latency, or roadside accuracy was evaluated.
