# Captum checkpoint recovery

Candidate checkpoint inventory: `CHECKPOINT_MANIFEST.csv` (84 rows, paths, byte sizes, SHA-256, metadata, input channel count, protocol verdict). The inventory script is `../reproducibility/build_checkpoint_manifest.py`.

## Findings

- Final v2j corrected ST-PIGNN physics, λ=0 and Laplacian model configurations have saved 15-station prediction parquets and an explicit `NONE SAVED` checkpoint field in `final_blr_results/physics_audit/provenance/model_configurations.csv`. Their gradients cannot be recovered. Checkpoints are **MISSING**, not merely undiscovered under another shape.
- Earlier v2c has five corrected h=1 checkpoints and one-per-pair predictions. Their strict architecture load uses 13 input channels, h=1, log1p residual, 96 width. The wrapper reproduced selected saved predictions to ≤4.58e−5 µg/m³; these weights were used only as `v2c corrected h1`, never labeled v2j.
- v2r preserved h=6 seed-11 outer-LOSO fold checkpoints with 18 input channels, edge_dim 1, and metadata identifying held-out station and cutoff-safe weather. Corresponding `station_forecasts_all.parquet` rows support exact heldout prediction checks. A separate small IG analysis is run only for selected sites whose wrapper meets ≤1e−4 µg/m³; result files and exact used hashes are under `v2r_heldout_h6/`.
- Notebook root `citywide_stpignn_best.pt`/stable/autosave weights are 16-channel historical road-partition models, with target-hour leakage and copied source-station histories documented in the v2q recovery. They are **not compatible substitutes** for corrected station graph models.
- Earlier v2/v2b weights are inventoried but feature schema/split/data protocol differ from final v2j. Tensor compatibility alone does not make them v2j checkpoints.

No new training was performed. The top-level authorization prohibited GPU training; reproducing weights would also not recover historical model identity. Final v2j IG and physics/λ0/Laplacian attribution comparisons remain unavailable.
