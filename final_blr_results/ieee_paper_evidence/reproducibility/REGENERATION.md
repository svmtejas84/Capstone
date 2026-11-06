# Regeneration instructions

This is an evidence-only consolidation. It runs no model fitting. It recomputes metrics solely from previously saved prediction parquets in preserved archives and saved v2r output.

From repository root, with pandas, pyarrow, Matplotlib and pyproj available, run the bounded evidence-only rebuild:

```sh
python final_blr_results/ieee_paper_evidence/reproducibility/rebuild_package.py
```

The orchestrator runs the individual extraction, metric verification, table, figure, and checksum scripts in order. It reads saved prediction files and writes only to the evidence package. It does not access new targets or fit models.

For original studies, use round-specific procedures only when specifically authorized: v2l `final_blr_results/physics_audit/reproducibility/regenerate_v2l.sh`, v2m `final_blr_results/baselines/v2m/reproducibility/regeneration_instructions.md`, v2r `final_blr_results/final_research_v2r/reproducibility/REPRODUCIBILITY.md`.

The original rejected manuscript and six review reports are missing. The full original bibliography therefore cannot be audited. v2l frozen p-values and intervals are cited from source artifacts and are not recalculated under a new family.
