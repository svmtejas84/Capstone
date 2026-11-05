# Validation-selection audit

`selected_configurations.csv` has every h/model/seed and `results/benchmark_selection_v2j.csv` has every one of the four LR trials for each h/model (60 relevant trials total). `results/benchmark_runs_v2j.csv` has all 75 final test seed runs. No failed or missing final seed was excluded. The same search grid, seed 11, 30-epoch cap, patience five, validation MAE criterion and test mask apply to physics, λ=0 and Laplacian. The chosen LR is the minimum recorded validation MAE for each model/horizon; all other seeds use that LR. The source contains no test-metric selection branch. The run log contains all SELECT and FINAL records and five DONE markers; no `--refresh-models` command appears in the supervised manifest.

| h | Physics LR | λ=0 LR | Laplacian LR |
|---:|---:|---:|---:|
| 1 | 0.001 | 0.0001 | 0.001 |
| 3 | 0.003 | 0.003 | 0.003 |
| 6 | 0.0003 | 0.003 | 0.001 |
| 12 | 0.001 | 0.003 | 0.003 |
| 24 | 0.001 | 0.003 | 0.003 |

Selected λ=0 LR lies at the lower grid boundary at h=1 and the upper boundary at h=3,6,12,24; physics is at the upper boundary at h=3. All final runs stopped before the 30-epoch cap, consistent with validation early stopping. Different selected LRs and best epochs are legitimate consequences of the fixed validation procedure but prevent attribution to the penalty at a common optimizer setting. Search seed 11 is also included in the final five-seed average. The supervisor manifest omitted explicit config/seed environment fields, a provenance weakness mitigated here by YAML/source/row/log evidence, not by assumption. There are no v2j trained checkpoints to inspect or reselect; no test-based re-selection was performed.
