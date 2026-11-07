# v2u figure and table methodology

This package uses saved results only. Plot construction was frozen in `ASSET_PROTOCOL.md` before rendering. Source SHA-256 fingerprints are in `../verification/SOURCE_HASHES.csv`; figure-level captions identify exact input paths. The raw full-city plotting CSV is a derived copy of one saved v2r Parquet snapshot, included only in the local ZIP.

## Aggregation and populations

- **F03/T02:** v2j forecasting values are recomputed from saved paired predictions; v2m MLP/TCN ensemble values use the v2m comparison table. The protocols differ in weather aggregation. No cross-protocol pooled statistic was computed.
- **F04/T03:** ensemble differences subtract saved ensemble MAEs; negative values favor the directional model. Individual-seed paired values come from the v2l seed audit. T03 seven-day intervals and Holm values refer to the directional-versus-λ=0 comparison only; the Laplacian difference is descriptive.
- **F05/T04:** W6 per-site bars select the uncorrected seasonal-bias rows, `train_mean` anchored ST-PIGNN, and `baseline` anchored weather/static ridge. v2r spatial decoder pooled metrics occupy a distinct panel/table.
- **F06/T06:** signed tensors are retained. Feature bars sum absolute IG over all 12 lags and 15 graph nodes, then average across primary training-mean-baseline records. Temporal curves sum over nodes and features per lag, with absolute and signed values plotted separately. Feature×lag cells sum absolute IG over nodes and average over records. v2c h1 and v2r outer-LOSO h6 are separate variants. The 64-step Captum settings are inherited from the saved attribution methodology; no attribution was recomputed.
- **F07/T05:** the earliest saved v2r origin is plotted at every stored UTM node coordinate. Colors are the saved neural-decoder output, without added smoothing. Distance to eligible monitor is a support diagnostic, not a calibrated uncertainty interval. Poor-support nodes are overlaid where the stored `poor_support_gt5km` flag is true.
- **F08/T07:** original-field assignment rates sum nine frozen demand batches per method. Trade-off values average batch-level paired percentages for the common-admitted population. Perturbation stability uses the saved three prespecified stress scenarios. City benchmark capacity utilization was low; deterministic toy tests establish the corrected allocator's capacity-feasibility behavior under stress.

## Environment and exact commands

Repository branch at source freeze: `research/bengaluru-v2r-final`; commit `113bae4cff4c7cfa296ec1672ab7fbc3de4849ec`. Python 3.9, Matplotlib 3.9.4, pandas 2.3.3, NumPy 1.26.4. Rendering uses Matplotlib Agg and a writable `/tmp` config directory. The saved historical partition pickle requires the audited `SpatialPartition` compatibility class; no KMeans refit occurs.

```sh
cd /home/jupyter-1nt23cb058/Capstone
python final_blr_results/ieee_publication_assets/scripts/build_assets.py
python final_blr_results/ieee_publication_assets/scripts/build_tables.py
python final_blr_results/ieee_publication_assets/scripts/verify_package.py
```

PNG files use 300 dpi. PDF/SVG are vector for labels and plots; large graph and city node layers are intentionally rasterized within vector containers to keep files practical. `pdflatex` and `latexmk` were unavailable. LaTeX paths receive static checks; copy or adjust paths for the final manuscript project.

No model was trained, no new concentration prediction was generated, and no scientific result was altered in this round.
