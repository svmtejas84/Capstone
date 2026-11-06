# Final paper evidence handoff (not a manuscript)

## Research record

The evidence package consolidates Bengaluru results from the historical production notebook through v2r. The original ten-page IEEE BigData manuscript PDF and four BigData/two DELCON full review texts were not found in the repository. They are explicitly pending transfer; exact quotations, reviewer assignment, original page/figure mapping and complete bibliography audit remain unavailable. This handoff does not draft any paper section.

## What was implemented

The historical production notebook implements a 16-channel GINE–GRU over road partitions with a legacy directional hinge and a surviving old checkpoint. It does not provide a scientifically defensible corrected road forecast: target-hour pollutant input, copied station histories, timeline wrap risk, sparse supervision and omitted partition boundaries were documented. The corrected experiment instead forecasts on a separate 15-station, 60-directed-edge kNN graph using 18 channels and a 12-hour history. It predicts observed monitoring-station targets, not road labels.

## Dataset and authoritative evidence

Bengaluru station forecasting uses a small 15-monitor dataset with sparse labels. v2j historical ST-PIGNN weather information differs from v2m's cutoff-safe MLP/TCN weather input. v2l reused saved v2j predictions for physical-penalty attribution; v2m completed 50 MLP/TCN cells and ten frozen comparisons. v2n–v2r consolidated road graph, attribution, spatial estimation, recovery, decoder validation, and RGDR feasibility. The 20-row machine-readable experiment register is `source_registry/EXPERIMENT_SOURCE_REGISTER.csv`; methodological source paths and chronology are linked there.

## Strongest positive findings

- The station-level system produces exploratory multi-horizon forecasts on the stated monitoring population.
- In the fixed v2m comparison family, ST-PIGNN had lower MAE than MLP at h=6 (−0.8066 µg/m³, Holm p=.0049975) and h=12 (−0.5171, Holm p=.0089955), but the input weather protocols differ. No ST-PIGNN–TCN contrast survived Holm.
- Directional regularization had comparatively favorable h=6 evidence; results vary by horizon and seed.
- The 154,902-node road network passed structural topology checks, and v2r generated finite estimates for every road node at three frozen h=6 targets.
- v2r issue-time-safe station source forecasts were fit across spatial folds; exact pipeline and checkpoints are inventoried in its methodology/archive.

## Strongest negative findings

- Corrected W6 LOSO loses to weather/static ridge: MAE 22.314 versus 20.624 µg/m³ on 11 scored spatial sites; four stations have no test targets.
- The v2r decoder loses to train-only mean and forecast-IDW (27.360 versus 20.634 and 20.154 MAE), with decoder worse at 9/11 sites. v2j benchmark metrics were independently recomputed for 85 model-horizon rows; all v2m 50 individual cells, 10 five-seed ensembles, and 10 frozen paired deltas were also checked against archived predictions. v2r pooled and per-site LOSO summaries were recalculated from paired outputs. The road maps are experimental neural-assisted estimates, not validated road concentrations.
- v2l penalty gains are horizon-dependent; h=24 is unfavorable, and physics did not establish conservation, PDE fidelity, or specificity beyond generic smoothing.
- RGDR binary and continuous gates retain too little train directional mass; v2r stopped before predictive model fitting. Prediction gain is NOT EVALUATED and novelty NOT ESTABLISHED.
- Captum is available for v2m MLP/TCN only; 85/228 completeness records were flagged. Corrected ST-PIGNN IG is unavailable.
- No roadside accuracy, calibrated road uncertainty, or independent replication is established. Routing code and an offline simulator exist, but one saved 1,000-trip run admitted only 444 trips; admitted-only dose increased 0.121% and mean travel time increased 0.146%. Its static PM2.5 field is unvalidated, and no route/exposure effectiveness is established.

## Reviewer reconciliation

Conference-specific matrices include every issue category supplied in the task and the actual available counter-evidence. They do not fabricate exact review wording or reviewer assignment. Source reviews must be transferred to resolve pending points. Valid criticisms that remain should be acknowledged; claim withdrawal is an acceptable resolution.

## Claim boundaries

Supportable: exploratory station forecasting on the defined observed monitor population; limited protocol-labeled neural comparison; mixed regularization effect; graph structural integrity; computational generation of road estimates; software-level RGDR math/tests; descriptive v2m IG with numerical flags.

Must be withdrawn or explicitly not established: broad superiority to neural baselines, physical conservation/advection-diffusion, causal transport, accurate citywide/roadside concentrations, validated exposure-aware routing, RGDR novelty or predictive superiority, and independent replication. Full list: `claims/`.

## Tables and figures

There are 15 CSV result tables under `results/`, 21 table/export entries in `tables/table_manifest.csv` (including recomputation checks and the figure manifest), and 14 publication-style diagnostic figures (PNG and PDF) catalogued in `figures/figure_manifest.csv`. Figures include horizon benchmarks, physics effects/seed stability/Laplacian comparisons, spatial pooled/per-site/coverage, road support and station locations, city execution, RGDR exposure, and Captum completeness. They use saved outputs and are descriptive, not new experiments.

## Missing artifacts and reproducibility

Missing: original PDF, six full review reports, original bibliography source, and corrected ST-PIGNN Captum weights. Saved v2m prediction parquet members were read directly from the existing ZIP archive for metric verification; the package does not duplicate those inputs. Some other historical source inputs/checkpoints are local-only or contained in prior verified archives. Follow `reproducibility/REGENERATION.md`; hashes and environment records are in that directory. No ZIP or checkpoint artifact is committed here.

## Second-city handover

`final_blr_results/second_city_handover/` is a separate independent-replication handoff. London and Copenhagen data gates remain blocked; neither has eligibility evidence or training approval. The next session should perform eligibility and protocol review only unless separately authorized.
