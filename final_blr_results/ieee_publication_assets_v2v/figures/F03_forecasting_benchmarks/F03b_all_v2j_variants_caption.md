# Complete retrospective-weather model variant comparison

Small multiples show all 17 archived model variants separately at five horizons (14,583 pairs per horizon). All curves belong to the retrospective centered-weather station evaluation; variants are exploratory and share an exposed test period. MLP/TCN are not shown because their cutoff-safe protocol differs.

Source artifacts:
- `final_blr_results/ieee_paper_evidence/results/RECOMPUTED_V2J_BENCHMARK.csv` (SHA-256 `bdcba74da9e98af6751bb3920490ec20848d548c829c2f928e1c56c02f642fcc`)

Derived source data: `source_data/F03_all_variants.csv`.

Regenerate: `python final_blr_results/ieee_publication_assets_v2v/scripts/build_assets.py`.
