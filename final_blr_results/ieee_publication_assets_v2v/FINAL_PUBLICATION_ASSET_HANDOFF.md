# Final publication asset handoff — v2v

## Package status

The package contains 11 regenerated figure assets: F01, F02, F03, F03b, F04, F05, F06a, F06b, F07, F08, and F08b. It contains 11 CSV/TeX result table pairs covering T01–T08, with separate W6 and decoder protocols and a separate major-feature attribution table. Each figure has PNG, vector PDF, SVG, and a caption sidecar. `captions/PUBLICATION_FIGURE_CAPTIONS.md` provides manuscript-ready scientific captions without drafting manuscript prose.

## Recommended figure use

Main figures: F01 architecture; F02 graph/stations; F03 benchmark (state protocol distinction); F04 regularization ablations (heading “Directional Regularization and Ablation Analysis”); F05 held-out station evidence; F06a/F06b only if space permits and explicitly as distinct variants; F07 only as experimental estimates; F08 only as scenario-based feasibility and modeled trade-off. F03b and F08b are supplementary.

## Main corrections

F08 original-field maximum utilization is 4.5918%. The 5.4054% maximum belongs to the `spatial_sine` perturbation. F03 adds the 17-variant benchmark inventory and preserves the separate cutoff-safe MLP/TCN comparison. F04 includes paired seven-day moving-block directional-minus-Laplacian CIs at all horizons and the five-of-five h6 seed sign test (two-sided p=0.0625). F05 distinguishes pooled and equal-station estimates and includes station bootstrap intervals. F06 shows actual raw-array feature and temporal IG; h1 and h6 variants are not a controlled horizon comparison. F07 reports both pooled and equal-station decoder comparisons.

## Evidence boundaries

No model was trained and no new forecast was generated. Captum inputs came from saved arrays. Figures are based on frozen results and saved prediction artifacts. Test-set exposure limits confirmatory interpretation. Captum is not causal. The directional penalty is not mass conservation. City estimates are not validated roadside measurements. Route modeled dose is not human exposure.

## Regeneration

Run `python final_blr_results/ieee_publication_assets_v2v/scripts/build_assets.py`, `python final_blr_results/ieee_publication_assets_v2v/scripts/build_tables.py`, and `python final_blr_results/ieee_publication_assets_v2v/scripts/verify_package.py` from the repository root. Source hashes are in `verification/SOURCE_HASHES.csv`; generated-file hashes are in `verification/CHECKSUMS.csv`. The PDF archive is `archive/IEEE_PUBLICATION_ASSETS_v2v.zip`.

## LaTeX

Include the snippets from `latex/figures.tex` and `latex/tables.tex` in the separately maintained manuscript. Paths assume inclusion from the repository root. The environment had no detected `pdflatex` or `latex`; snippets were checked statically. No manuscript file or PDF is included.
