# Monograph verification report

This audit checks the generated documentation and selected saved numerical evidence. It does not rerun model training or reconstruct missing external sources.

- Volumes: **16/16**; appendices: **15/15**; master/volume/appendix words: **103,051**.
- Distinct source artifacts across exhibits, appendices, tables, figures and code: **180**. Full report exhibits: **100**; direct notebook/code checks: **16**.
- Copied numeric tables: **19**, all source SHA-256 matched; figures: **14 PNG/PDF pairs**, all source SHA-256 matched.
- The equation register contains **11** rendered display equations, with version/units boundaries.
- Authored internal links broken: **0**. Source/figure/table hash mismatches: **0**.
- Experiment source-register rows: **20**. Original notebook: **26 code cells**, SHA-256 `242d0cf3d2f95c78a011841ed2aec2e100cc8c326e6211c918a8bd70504b8161`.
- Rechecked v2r decoder pooled MAEs and population, v2m Holm-surviving comparisons, v2t saved-output integrity and comparison-row completeness. All assertions passed.
- No conflict is silently repaired. Historical v2n handoff states corrected ST-PIGNN IG unavailable; the later three-pillar recovery added v2c and v2r h=6 checkpoint IG, not missing final v2j weights. The master and Volume 11 distinguish these versioned results.
- Original submitted PDF and six full reviews remain absent. Exact paper pages/figures, quotations, reviewer assignments and original reference audit are **BLOCKED BY MISSING SOURCE**. This is a source limitation, not a completed reconciliation.
- Independent street-level accuracy, real exposure reduction, RGDR predictive superiority, mass-conservation of historical checkpoints and second-city replication remain unsupported or unevaluated.
- PDF edition not generated because `pandoc` was not installed; Markdown is authoritative.

## Reproduction

`python final_blr_results/ST_PIGNN_COMPLETE_RESEARCH_MONOGRAPH/verify_monograph.py` from the repository root. The source snapshot commit is reachable and source hashes are in `source_registry/SOURCE_COVERAGE.csv`.
