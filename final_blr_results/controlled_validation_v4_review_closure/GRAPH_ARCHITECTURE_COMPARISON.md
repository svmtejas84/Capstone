# Matched-pair graph-architecture comparison

All results in `statistical_analysis/GRAPH_ARCHITECTURE_CONTRASTS.csv` use saved V3 predictions on the same 14,583 observed target-time/station pairs for each horizon. The sign is unregularized GINEConv–GRU minus comparator: negative favors GINEConv–GRU. The prespecified 15 contrasts are versus GRU-only, TCN and MLP at 1, 3, 6, 12 and 24 hours. `statistical_analysis/GRAPH_ARCHITECTURE_SEEDS.csv` has 75 seed-matched individual-model comparisons. All share the repaired 18-channel timestamp-causal information protocol, but architecture-specific parameter counts and validation-selected learning rates differ; this is a model-procedure comparison, not a strict isolated graph-module ablation.

| Horizon | GINE–GRU minus GRU-only | GINE–GRU minus TCN | GINE–GRU minus MLP | Units |
|---:|---:|---:|---:|---|
| 1 | −0.259 | −0.035 | −0.101 | µg/m³ |
| 3 | −0.046 | +0.019 | +0.009 | µg/m³ |
| 6 | −0.235 | −0.306 | −0.298 | µg/m³ |
| 12 | −0.783 | −0.264 | −0.726 | µg/m³ |
| 24 | −0.452 | −0.136 | −0.071 | µg/m³ |

Seven-day moving-block intervals and 100,000-draw nonoverlap-block sign-flip p-values are in the CSV. After Holm adjustment across 15 tests, the GRU-only contrasts at 1h, 12h and 24h have adjusted p <0.05 under the sign-flip procedure; most other adjusted contrasts do not. At 6h several moving-block intervals exclude zero while sign-flip p-values are >0.05, reflecting different dependence treatments. No independent holdout or external city was evaluated. Lower paired MAE on the exposed temporal population does not establish graph necessity or general geographic transfer.

Method and source: V3 saved `predictions/h{h}_{variant}_ensemble.npz` and individual seed NPZs; V4 `scripts/audit_saved.py` imports the frozen V3 block-analysis function, uses a separate deterministic RNG stream for the architecture family, and writes only V4 files. Parameter counts and LR policies are in `COMPLETE_MODEL_AND_BASELINE_REGISTER.csv`.
