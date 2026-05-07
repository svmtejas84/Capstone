# ST-PIGNN Backtest Summary

Generated from:

```bash
python scripts/evaluate_stpignn_holdout.py \
  --max-samples 1000 \
  --max-nodes 96 \
  --hops 1 \
  --horizons 1,3,6,12 \
  --out docs/stpignn_holdout_report.json
```

## Result

The checkpoint loads and runs, but persistence is the strongest baseline on this holdout.

| Horizon | Samples | Persistence RMSE PM2.5 | ST-PIGNN RMSE PM2.5 | Station Mean RMSE PM2.5 |
| --- | ---: | ---: | ---: | ---: |
| 1h | 1000 | 0.8043 | 49.3458 | 86.8900 |
| 3h | 1000 | 1.0459 | 49.3606 | 86.8977 |
| 6h | 1000 | 1.1840 | 49.3870 | 86.8988 |
| 12h | 1000 | 1.3133 | 49.3654 | 86.8829 |

## Interpretation

The current ST-PIGNN checkpoint beats a station-mean baseline, but it does not beat persistence at 1-12 hour horizons. The operational routing default should remain persistence-first until the model target and training setup are revised.

The most likely issue is target design, not GPU capacity. The current model predicts absolute next-step concentration, while the data is highly persistent. A learned model needs to predict something persistence does not already solve.

## Recommended Next Model Work

1. Train/evaluate a delta target: `future_pm25 - latest_pm25`.
2. Add persistence residual loss: model predicts correction over persistence.
3. Evaluate spike/anomaly risk separately from absolute concentration.
4. Use horizons where meteorology matters more: 6h, 12h, 24h.
5. Keep route dosimetry post-model, not inside the GNN.
