# Complete Unresolved Issues

This register reproduces the cited source records below, retaining their original protocol and status. Later source exhibits can supersede earlier conclusions; no incompatible populations are pooled.

## Source 1: `final_blr_results/ieee_paper_evidence/source_registry/MANUSCRIPT_SOURCE_REGISTER.md`

[EVIDENCE: `final_blr_results/ieee_paper_evidence/source_registry/MANUSCRIPT_SOURCE_REGISTER.md` | SHA-256 `ec94ea64280fd2212ed0f18a846c3a6b8eb191f4e134a0e100f11088c0a83470` | snapshot `1c46a4b`]

# Manuscript and source register

Expected historical file: `ST_PIGNN_IEEE_Big_Data_Conf(2).pdf`; not found in the repository or the checked home-directory search. No verified repository copy located. Exact manuscript quotations, figure/page mapping, and reference-by-reference correction therefore remain UNVERIFIABLE pending transfer through the repository's normal file-transfer mechanism.

The rejected manuscript title supplied by the author is “Spatio-Temporal Physics-Informed Graph Neural Networks to aid Urban Toxicity Navigation for Vulnerable Commuters”. Its claims are historical only. `claude_paper.md` and other adjacent drafts are not treated as the supplied PDF.

Expected reviews: four IEEE BigData 2026 reviews and two IEEE DELCON 2026 reviews. Full texts are absent. Matrices list issue topics supplied in the task and actual counter-evidence, but reviewer assignment and exact wording are intentionally blank/pending.

Primary verified internal sources are the frozen v2j–v2r reports, raw saved summary/prediction tables where available, Git commit `a5b396da3f41c2d626ba072e8cec1a0ee15d383d` (package start), and linked artifact paths in the experiment register.

Chronological experiment inventory: `CHRONOLOGY.md`; machine-readable register: `EXPERIMENT_SOURCE_REGISTER.csv`.

## Source 2: `final_blr_results/ieee_paper_evidence/claims/LIMITATIONS.md`

[EVIDENCE: `final_blr_results/ieee_paper_evidence/claims/LIMITATIONS.md` | SHA-256 `d5818b48f5d6de4be54139660ea6b6b7c5b33ecbd9c9ec8ebda8ebcb6999a6b2` | snapshot `1c46a4b`]

# Limitations

Bengaluru test exposure; weather protocol mismatch across model generations; only 11 spatially scored stations and four unscored; negative LOSO results; sparse support and no road truth; no calibrated road uncertainty; original notebook target-hour leakage and omitted partition boundaries; no corrected ST-PIGNN checkpoints for IG; many Captum completeness flags; no physics mass conservation/source term; no RGDR comparative training; no validated routing/exposure evaluation; missing original manuscript PDF and review texts; ; source data/checkpoint redistribution and exact versions vary by round.


The full classification table is `CLAIM_CLASSIFICATIONS.csv`; evidence paths are exact repository-relative sources.

## Source 3: `final_blr_results/city_scale/final_evidence/KNOWN_LIMITATIONS.md`

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

## Source 4: `final_blr_results/second_city_handover/SECOND_CITY_RESEARCH_GATES.md`

[EVIDENCE: `final_blr_results/second_city_handover/SECOND_CITY_RESEARCH_GATES.md` | SHA-256 `6971b49ab625d9cc2448965ff2b121d89cc2b5616d9c0b3cfbcf4e1cf2d18e8e` | snapshot `1c46a4b`]

# Research gates

**Gate 0: eligibility.** Source-level hourly inventory, instrument comparability, station count, operating duration, spatial coverage, license, weather alignment. Fail => no training.

**Gate 1: protocol.** Supervisor approves frozen forecast-time information set, spatial and temporal split, baselines, physical quantities, statistical family, and resource limits.

**Gate 2: reproducibility.** Pin hashes, environment, transforms, code and backup; dry-run data audit without test-score access.

**Gate 3: bounded pilot.** Only after explicit training authorization; measure runtime and VRAM, validation-only debugging, restart-safe checkpoints.

**Gate 4: locked evaluation.** One untouched external-city test; independent-site analysis and multiplicity plan; preserve negative outcomes.

**Gate 5: claims.** Predictive performance, physics validity, spatial transfer, road estimates, and routing each require separate evidence. No gate implies another.
