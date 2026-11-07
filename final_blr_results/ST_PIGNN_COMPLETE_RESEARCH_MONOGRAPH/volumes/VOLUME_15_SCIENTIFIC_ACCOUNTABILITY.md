# Volume 15 — Claim boundaries, negative results and novelty

<a id="volume-15"></a>

## Editorial reconstruction and evidentiary boundary

The final claims must separate implemented code, verified numerical behavior and empirical validity. Multi-horizon station prediction and road-graph structural integrity are supported within their stated populations. Directional regularization is mixed and lacks physical specificity. Spatial decoder improvement, road-node accuracy, measured exposure benefit, mass conservation and RGDR predictive advantage are unsupported or unevaluated. The final v2t correction supports declared-capacity software feasibility only. Negative results are not ancillary: they determine what future paper claims must be withdrawn or narrowed. The bibliography and reviewer-specific claims remain source-limited until the missing PDF/review texts are supplied. [EVIDENCE: claims register | final_blr_results/ieee_paper_evidence/claims/CLAIM_CLASSIFICATIONS.csv | snapshot 1c46a4b]

## Full round-specific source exhibits

The exhibits reproduce the cited local reports as source evidence. Their original round-specific conclusions may be narrower than later findings; read the editorial reconstruction and final synthesis before treating one exhibit as the final verdict.

## Source exhibit 1: `final_blr_results/ieee_paper_evidence/claims/SUPPORTED_CLAIMS.md`

[EVIDENCE: `final_blr_results/ieee_paper_evidence/claims/SUPPORTED_CLAIMS.md` | SHA-256 `799f04a5de45566e399cea29931260b2c91b9becaaba15b224d82646e90b5dff` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Supportable claims

- The corrected station forecasting system was evaluated on the 15-monitor graph using the documented horizons and splits; results are exploratory because Bengaluru test exposure is repeated.
- v2m completed all 50 MLP/TCN cells; within the frozen cross-protocol comparison, ST-PIGNN beat MLP at h=6 and h=12 after the reported Holm correction, while no ST-PIGNN–TCN contrast survived it.
- Weak directional regularization showed mixed, horizon-dependent effects; h=6 was comparatively favorable, h=24 unfavorable; physics specificity was not established.
- Road graph structure and full-node output generation were computationally demonstrated; neither establishes road-level accuracy.
- v2r decoder did not outperform frozen spatial controls on eleven scored held-out stations.
- Captum IG was numerically computed for compatible v2m MLP/TCN models with substantial completeness flags; corrected ST-PIGNN IG is unavailable.

## Source exhibit 2: `final_blr_results/ieee_paper_evidence/claims/UNSUPPORTED_CLAIMS.md`

[EVIDENCE: `final_blr_results/ieee_paper_evidence/claims/UNSUPPORTED_CLAIMS.md` | SHA-256 `018c48ed616a8a7e5c9892bd6d2bd9b6795dd221101d9c6f8f9b9c7caa9ebfa0` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Claims unsupported or not evaluated

Do not claim atmospheric mass conservation, full advection–diffusion fidelity, a validated source term Q, causal physical dependence, independently validated roadside concentrations, accurate citywide exposure surfaces, validated route exposure reductions, travel-time/welfare/capacity guarantees, ST-PIGNN direct message passing over the full 154,902-node graph, successful RGDR prediction gains, RGDR novelty, independent replication, or generalization beyond the monitored network.

## Source exhibit 3: `final_blr_results/ieee_paper_evidence/claims/NOVELTY_BOUNDARIES.md`

[EVIDENCE: `final_blr_results/ieee_paper_evidence/claims/NOVELTY_BOUNDARIES.md` | SHA-256 `005e029d047aacbca09bdce4d5a23e964d1ad997e15bde424f336a8993ba0ff5` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Novelty boundaries

GINE/GRU spatiotemporal forecasting, graph-based sensor prediction, wind-aware air-quality forecasting, physics-informed penalties, missingness-aware modeling, and station-to-road estimation each have prior art. The repository's directional hinge is an engineering regularizer, not a demonstrated conservation law. RGDR adds provenance/age-based weighting to that heuristic, but available review found close ideas in missingness-aware models and adaptive physics-loss weighting; novelty is NOT ESTABLISHED. Do not claim a new general architecture or new physical mechanism without a separate rigorous literature review and independent evidence.

## Source exhibit 4: `final_blr_results/ieee_paper_evidence/claims/LIMITATIONS.md`

[EVIDENCE: `final_blr_results/ieee_paper_evidence/claims/LIMITATIONS.md` | SHA-256 `d5818b48f5d6de4be54139660ea6b6b7c5b33ecbd9c9ec8ebda8ebcb6999a6b2` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Limitations

Bengaluru test exposure; weather protocol mismatch across model generations; only 11 spatially scored stations and four unscored; negative LOSO results; sparse support and no road truth; no calibrated road uncertainty; original notebook target-hour leakage and omitted partition boundaries; no corrected ST-PIGNN checkpoints for IG; many Captum completeness flags; no physics mass conservation/source term; no RGDR comparative training; no validated routing/exposure evaluation; missing original manuscript PDF and review texts; ; source data/checkpoint redistribution and exact versions vary by round.


The full classification table is `CLAIM_CLASSIFICATIONS.csv`; evidence paths are exact repository-relative sources.

## Source exhibit 5: `final_blr_results/city_scale/final_evidence/KNOWN_LIMITATIONS.md`

[EVIDENCE: `final_blr_results/city_scale/final_evidence/KNOWN_LIMITATIONS.md` | SHA-256 `1be0e1e2307b9bf9091148c3955b67b1517ebc4550cb3ea5d51765eb4f15007d` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Known limitations at Bengaluru freeze

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

## Source exhibit 6: `final_blr_results/city_scale/final_evidence/FINAL_BENGALURU_RESEARCH_VERDICT.md`

[EVIDENCE: `final_blr_results/city_scale/final_evidence/FINAL_BENGALURU_RESEARCH_VERDICT.md` | SHA-256 `dcac722ad234628ab86fbb040f46cec09e31d7b3811499d74aeed98ea6af77e5` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Final Bengaluru v2n research verdict

**BENGALURU v2n COMPLETE — EXPERIMENTAL RESEARCH FROZEN.** All workstreams reached a terminal outcome, including explicit blocks and unverifiable comparisons. No new training, citywide concentration map, road-node pseudo-label, routing validation or manuscript edit was performed.

The corrected 15-station model has exploratory multi-horizon monitoring-station forecasting evidence and intermediate-horizon advantages over selected historical neural controls. The v2m 50-cell MLP/TCN comparison finds historical ST-PIGNN below MLP at h6/h12 after exploratory Holm, but no ST-PIGNN versus TCN contrast survives. Historical ST-PIGNN and new models use different weather aggregation, so this is not an isolated architecture win. Weak upwind regularization has mixed horizon-dependent predictive associations; physical specificity, conservation and causal atmospheric mechanism were not demonstrated.

Corrected W6 LOSO does not establish spatial-transfer superiority: the original ST-PIGNN loses to weather/static ridge on eleven scored station sites (MAE 22.314 versus 20.624 µg/m³; paired Δ +1.690, CI +1.116 to +2.275). The OSM graph has 154,902 nodes, 393,089 raw directed edge rows and 424,550 processed message arcs with valid topology. Structural validity does not provide PM2.5 truth. The corrected full-city inference pathway is **BLOCKED** by absent compatible ST-PIGNN weights and incomplete road-node dynamic features/anchors; no road node was inferred and compute feasibility remains unmeasured.

Captum IG completed for compatible v2m MLP/TCN station models: 228 baseline-relative records from 18 checkpoint cells with wrapper match ≤2.67e−5 µg/m³ and zero nonfinite values. Eighty-five records breach the frozen numerical completeness flag; corrected ST-PIGNN physics IG is UNVERIFIABLE. This supports only limited descriptive input sensitivity, not physical or road-level claims. Routing effectiveness and independent external replication remain unsupported/not evaluated, respectively.

The twelve independent classifications, exact source paths, statistical evidence, allowed wording and prohibited wording are in `CLAIM_EVIDENCE_MATRIX.csv`. `REVIEWER_ISSUE_MATRIX.md`, `BENGALURU_EXPERIMENT_REGISTER.md` and `KNOWN_LIMITATIONS.md` complete the review trail. The local backup archive is supplemental only; external USB verification remains pending. The existing historical v2j/v2k/v2l/v2m artifacts are preserved unchanged. No further Bengaluru test-set exploration is authorized by this freeze.

## Source exhibit 7: `final_blr_results/final_routing_closure/v2t/IEEE_ROUTING_CLAIM_DECISION.md`

[EVIDENCE: `final_blr_results/final_routing_closure/v2t/IEEE_ROUTING_CLAIM_DECISION.md` | SHA-256 `464cf320ed30e33ce0c04075f2f60895352fde6f0d90fcd4b615ef11655b00e7` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### IEEE routing claim decision

**Appropriate contribution:** A preference-based deferred-acceptance implementation with explicit directed-edge capacity bookkeeping, deterministic tests, and a bounded computational scenario comparison. Describe the original route-only matcher, its fallback/shared-edge defects, and the corrected capacity-feasible implementation with exact assumptions. The 1,428-node/36-batch benchmark is suitable only as a software feasibility and sensitivity result.

**Modelled-dose result:** On the original field the corrected method's average paired change versus shortest was −0.001207% across nine batches, with a range reaching zero and no capacity binding. Report the negative/near-zero practical finding. State that all 252 requests per scenario were admitted and original/corrected outputs coincided.

**Claims to withhold:** proven classical stable matching for overlapping route bundles; network equilibrium; social-welfare optimum; real traffic-capacity satisfaction; clinically or personally measured exposure reduction; safety for vulnerable commuters; validated street-level concentrations; operational citywide latency. The scenario field is a historical model estimate and the graph covers only a central 1,428-node subnetwork. Route dose is modeled inhaled mass under fixed RMV/speed assumptions.

See `final_blr_results/ieee_paper_evidence/ROUTING_VALIDATION_SUPPLEMENT.md` for an additive evidence-package pointer. No manuscript section was drafted or modified.
