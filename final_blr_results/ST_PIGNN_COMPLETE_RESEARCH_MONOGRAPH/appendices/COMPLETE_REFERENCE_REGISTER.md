# Complete Reference Register

This register reproduces the cited source records below, retaining their original protocol and status. Later source exhibits can supersede earlier conclusions; no incompatible populations are pooled.

## Source 1: `final_blr_results/ieee_paper_evidence/references/CITATION_ISSUES.md`

[EVIDENCE: `final_blr_results/ieee_paper_evidence/references/CITATION_ISSUES.md` | SHA-256 `5ff6d9c8e3f02a1503962e18278acb2d9989a76cce5f2cca4217e16d46ee73d7` | snapshot `1c46a4b`]

# Citation issues and required source transfer

The original IEEE manuscript PDF and its bibliography are absent. Therefore no claim is made that its reference list has been completely audited. Before drafting, transfer the PDF and verify every cited author's spelling, year, venue, title, DOI, and whether it supports the adjacent claim. Existing v2p prior-art references are leads; check publisher/proceedings pages before importing. Do not cite the RGDR prior-art scan as proof of novelty.

The final v2p review also identifies SA-PINNs, loss-balanced PINNs, AirPhyNet, GraPhy, and TransNet as close context. Those exact bibliographic records should be checked against source proceedings/publisher records before manuscript import; they are not silently copied into the verified bibliography here.

## Source 2: `final_blr_results/ieee_paper_evidence/references/PRIOR_ART_MATRIX.md`

[EVIDENCE: `final_blr_results/ieee_paper_evidence/references/PRIOR_ART_MATRIX.md` | SHA-256 `6f1aeccc8bd419ab796ac922fe771c086db257e67604496961e644138f086078` | snapshot `1c46a4b`]

# Prior-art matrix

| Topic | Verified source | What it establishes | Boundary for this work |
|---|---|---|---|
| Missingness masks and elapsed-time features | Che et al. 2018, GRU-D, DOI 10.1038/s41598-018-24271-9 | Informative missingness and time intervals can be model inputs. | Does not establish RGDR predictive value. |
| Graph time-series imputation | Cini et al. 2022, GRIN, ICLR | Spatial message passing can support sensor-series imputation. | Different task; no claim of novelty for graph imputation. |
| Physics-guided air-quality forecasting | Hettige et al. 2024, AirPhyNet, ICLR | Explicit advection/diffusion-inspired differential-equation graph model. | ST-PIGNN's hinge is materially less complete and not a PDE solver. |
| Adaptive physics loss / wind-aware models | v2p prior-art review records SA-PINNs, loss balancing, GraPhy and TransNet; primary references require careful manuscript-level citation verification. | Related mechanisms exist. | RGDR novelty remains NOT ESTABLISHED. |

Reference metadata above was checked against publisher/proceedings or OpenReview/arXiv primary pages on 2026-11-06. The rejected manuscript bibliography cannot be audited without its PDF.

## Source 3: `final_blr_results/citywide_extension/v2p_rgdr/RGDR_PRIOR_ART_REVIEW.md`

[EVIDENCE: `final_blr_results/citywide_extension/v2p_rgdr/RGDR_PRIOR_ART_REVIEW.md` | SHA-256 `ad41dbcfbfc82d95872d4dae7f206f3f22e0da9a623605a8fb8ac1bc8fe9c154` | snapshot `1c46a4b`]

# RGDR prior-art review (primary sources, checked 2026-11-06)

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
