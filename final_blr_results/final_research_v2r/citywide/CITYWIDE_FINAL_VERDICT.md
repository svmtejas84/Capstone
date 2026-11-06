# v2r citywide forecasting verdict

| Criterion | Result | Evidence |
|---|---|---|
| Valid h=6 source forecasts generated | **YES, exploratory** | 15 outer station-isolated corrected GINE–GRU folds; 30 inner/outer fit cells complete. Cutoff assertions and per-fold manifests record issue-time safety. |
| Compact decoder trained | **YES** | Frozen 1,249-parameter architecture; 9,819 cross-fitted training examples, 7,203 validation examples; selected epoch 3, validation MAE 13.127 µg/m³. |
| Spatial holdout evaluation | **COMPLETE, unfavorable** | 11 scored stations, 14,583 pairs; four stations unscored. Decoder pooled MAE 27.360, IDW 20.154, training-only spatial mean 20.634. |
| Decoder improvement over controls | **NO** | Decoder MAE higher than each control at 9/11 sites; station-bootstrap equal-site ΔMAE vs IDW +5.101 (95% CI +1.815,+8.302). |
| Full road-node execution | **COMPLETE as a computational demonstration** | 154,902/154,902 nodes at three prespecified h=6 target timestamps; all outputs finite and geographically indexed. |
| Forecast-time input validity | **PASS for the recorded pipeline** | Outer station forecasts used 12 history hours ending at target−6 h; each support station's estimate comes from the outer GINE–GRU fold that excluded that station. No target-time PM observations were supplied. |
| Independent roadside accuracy | **NOT ESTABLISHED** | No road-level reference measurements; station LOSO is unfavorable for decoder and only eleven spatial sites were scored. |

## Execution and artifacts

Targets are 2025-10-08 13:00, 2026-02-10 07:00 and 2026-03-28 23:00 UTC. Each output contains 154,902 road-node rows, preserving `node_index` and `osmid`, coordinates in UTM metres, all 13 supporting station IDs, the IDW comparator, decoder estimate, nearest-support distance, convex-hull flag and >5 km support flag. Prediction tables and city figures are in `road_predictions/` and `figures/`.

The supervised road-output stage took 56.44 seconds including final decoder fitting, three maps and artifact writing; per-snapshot full graph processing took 1.12–1.30 seconds (about 119k–138k nodes/s), peak process RSS 1.36–1.49 GB, and GPU VRAM 0 for the road-node expansion. The source station models were trained on the V100 (maximum measured allocation 1.831 GB per fold model). Prefix checks for 1,000 and 10,000 nodes matched full-output IDW and decoder predictions exactly (max absolute difference 0). The full results include three files of 8.9 MB each. Inference completion demonstrates computational coverage, not physical validity or accuracy.

## Classification

Citywide outputs are **EXPERIMENTAL NEURAL-ASSISTED ROAD-NODE ESTIMATES**, not observed concentrations, not independently validated roadside predictions, and not evidence that the original 154,902-node road GNN was restored. The corrected GINE–GRU forecasts monitored stations; a compact spatial decoder propagates them to road coordinates. The decoder loses to both spatial controls in held-out evaluation. Support is weak over 19.45% of road nodes under the uncalibrated nearest-station >5 km diagnostic; 60.58% lie outside the convex hull of the 15 stations. These are support diagnostics, not calibrated intervals.

Known limits: eleven scored station sites, four unscored; repeated exposure to Bengaluru data; station-to-road extrapolation; no roadside truth; no calibrated prediction intervals; station meteorology is spatially sparse; 13-nearest support forecasts may share source-model errors; model selection was validation-only but all evidence is exploratory. Do not claim accurate citywide concentration, traffic exposure validity, or ST-PIGNN road-graph inference.
