# v2v change log

- Corrected F01 to separate historical partitioned road-network implementation, corrected station-graph evaluation, and experimental decoder/routing lane; directional regularization now originates from predictions as a training-only objective, with λ=0 and Laplacian shown as separate conditions.
- Reconciled F08 utilization: 4.5918% is the maximum in the original concentration scenario; 5.4054% occurs in the `spatial_sine` perturbation. Three means perturbation scenarios, in addition to the original field.
- Added all 17 saved retrospective benchmark variants and separately labeled the cutoff-safe MLP/TCN protocol.
- Added seven-day paired directional-minus-Laplacian confidence intervals and exact 5/5 sign-test result. Existing 0.0175 adjusted p-values are explained as the finite resampling/Holm floor, not precise continuous p-values.
- Added equal-station and pooled station holdout summaries, station bootstrap and nested time-block intervals; kept decoder protocol separate.
- Rebuilt Captum visuals from raw tensors and kept the one-hour and six-hour model variants separate.
- Added quantitative data coverage, missingness, validation/test distribution, implementation fact, and variant-selection audits.
- Added scientific captions, complete table set, source hashes, static verification, and a checksum-verified archive.
