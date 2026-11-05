# Final v2m Bengaluru baseline verdict

All 50/50 final cells completed on the V100, with five checkpoints and prediction files per model/horizon, each guarded by SHA-256 completion markers. This is an exploratory analysis on an exposed test set. Historical ST-PIGNN and other controls used centered v2j weather, whereas MLP/TCN used the corrected cutoff-safe v2m weather input. The comparisons below have exact matched targets and timestamps but are **cross-protocol**, not identical-input architectural ablations.

## Five-seed ensemble metrics

| Horizon | MLP MAE / RMSE / R² | TCN MAE / RMSE / R² | Historical ST-PIGNN MAE | Strongest historical statistical baseline |
|---:|---:|---:|---:|---|
| 1 | 8.016 / 24.631 / 0.559 | 8.080 / 25.098 / 0.542 | 8.026 | persistence 8.116 |
| 3 | 12.543 / 32.209 / 0.245 | 12.268 / 31.571 / 0.275 | 12.342 | persistence 13.244 |
| 6 | 15.513 / 36.678 / 0.021 | 14.868 / 34.724 / 0.123 | 14.706 | same_hour_yesterday 14.130 |
| 12 | 16.026 / 35.090 / 0.104 | 15.278 / 34.235 / 0.147 | 15.509 | same_hour_yesterday 14.130 |
| 24 | 13.840 / 29.340 / 0.374 | 13.894 / 29.265 / 0.377 | 13.902 | persistence 14.130 |

## Prespecified ten paired comparisons

Difference is ST-PIGNN MAE minus new baseline MAE; negative favors ST-PIGNN. CIs are nominal paired UTC-day bootstrap intervals; p-values are two-sided day-level sign-flip Monte Carlo values with Holm adjustment across all ten tests.

| h | Baseline | Difference | Nominal 95% CI | Raw p | Holm p | Holm verdict |
|---:|---|---:|---:|---:|---:|---|
| 1 | mlp | +0.009 | [-0.048, +0.063] | 0.7396 | 1.0000 | no ST-PIGNN advantage |
| 1 | tcn | -0.054 | [-0.133, +0.029] | 0.2094 | 1.0000 | no ST-PIGNN advantage |
| 3 | mlp | -0.202 | [-0.370, -0.047] | 0.0105 | 0.0840 | no ST-PIGNN advantage |
| 3 | tcn | +0.073 | [-0.080, +0.215] | 0.3283 | 1.0000 | no ST-PIGNN advantage |
| 6 | mlp | -0.807 | [-1.082, -0.519] | 0.0005 | 0.0050 | ST-PIGNN lower |
| 6 | tcn | -0.161 | [-0.373, +0.054] | 0.1584 | 0.9505 | no ST-PIGNN advantage |
| 12 | mlp | -0.517 | [-0.796, -0.256] | 0.0010 | 0.0090 | ST-PIGNN lower |
| 12 | tcn | +0.231 | [+0.024, +0.433] | 0.0300 | 0.2099 | no ST-PIGNN advantage |
| 24 | mlp | +0.062 | [-0.229, +0.372] | 0.6737 | 1.0000 | no ST-PIGNN advantage |
| 24 | tcn | +0.007 | [-0.265, +0.278] | 0.9620 | 1.0000 | no ST-PIGNN advantage |

ST-PIGNN has lower MAE than MLP at h=6 and h=12 after exploratory Holm adjustment. No ST-PIGNN versus TCN contrast survives adjustment. At h=3 versus MLP, the nominal interval excludes zero but Holm p=0.084. At h=12 TCN has lower MAE than historical ST-PIGNN with a nominal interval excluding zero, but Holm p=0.210. These are matched-target, different-weather-input comparisons and cannot isolate architecture.

## Individual seeds, ensembles, and training

| Model | h | Mean individual MAE | Five-seed ensemble MAE | Selected LR |
|---|---:|---:|---:|---:|
| mlp | 1 | 8.154 | 8.016 | 0.0003 |
| mlp | 3 | 12.856 | 12.543 | 0.003 |
| mlp | 6 | 15.908 | 15.513 | 0.0003 |
| mlp | 12 | 16.340 | 16.026 | 0.001 |
| mlp | 24 | 14.025 | 13.840 | 0.001 |
| tcn | 1 | 8.190 | 8.080 | 0.0001 |
| tcn | 3 | 12.561 | 12.268 | 0.003 |
| tcn | 6 | 15.388 | 14.868 | 0.003 |
| tcn | 12 | 15.648 | 15.278 | 0.003 |
| tcn | 24 | 14.240 | 13.894 | 0.003 |

All ten ensembles improve on the mean individual-seed MAE. The individual-seed spread and complete per-seed MAE/RMSE/R² are in `comparisons/individual_seed_metrics.csv`; no missing seeds were substituted. MLP has 18,113 parameters; TCN has 16,641. The sum of final-cell training times is 84.8 s; the full supervised all-groups run (selection plus final fits) took about 166 s. Peak PyTorch allocated GPU memory was 125,483,008 bytes (about 120 MiB). The earlier MLP h=1 group ran separately. Four LR candidates had the same seed-11 validation-selection opportunity per model/horizon; selected TCN LR is at the upper grid boundary for h=3,6,12,24. No test-selected config or silently skipped seed was found. Per-epoch loss/validation histories were not recorded by the inherited fit function and are unavailable; saved final validation metrics and best epochs remain in per-cell metrics and group selection files.

## Relation to established baselines

Both new models have lower MAE than historical persistence at every horizon. They are below historical same-hour-yesterday at h=1,3,24 and above it at h=6,12. At h=6 and h=12, same-hour-yesterday remains the strongest historical statistical baseline, and neither new neural model beats it. TCN is below MLP in MAE at h=3,6,12, while MLP is below TCN at h=1,24. Historical GRU-only is below both new models at h=1 and h=6, while TCN is below GRU-only at h=3 and h=12; MLP is below GRU-only at h=24. See `comparisons/secondary_comparisons.csv` for all matched-pair descriptive values. These facts do not justify a general claim that graph/physics complexity improves forecasting under the cutoff-safe information set.

## Scientific limits and archive status

The weather correction changes inputs but not targets or evaluation masks. Historical neural checkpoints were not retrained; all cross-protocol contrasts are descriptive. The test set was repeatedly examined, there were six prior post-hoc deviations, and the 500 µg/m³ ceiling and sparse stations limit generalization. There is no validated full-road or street-level accuracy, measured emissions Q, or external replication. The pre-training local ZIP was checksum verified; its independent external copy is pending under the supervisor exception. The separate supplementary ZIP is `reproducibility/research_results_v2m.zip` (15,762,253 bytes, SHA-256 `f669952674bcc24a15fe6f5a5c492d3b6492f2e625d2179954aee6f51b6fef3b`); 275 members passed ZIP CRC and per-member SHA-256 verification. Its external copy is also pending. The descriptive plot is `figures/mae_by_horizon_v2m.png`.
