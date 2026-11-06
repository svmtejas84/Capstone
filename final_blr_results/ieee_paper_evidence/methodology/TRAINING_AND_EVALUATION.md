# Training and evaluation

Keep each round's split, features, model selection, and test population separate. The v2l frozen comparisons use 14,583 matched station-hour pairs over 177 UTC days at each horizon, 11 scored sites. v2m contains all 50 MLP/TCN model-seed-horizon cells and ten frozen primary comparisons; its weather protocol differs from historical ST-PIGNN. Bengaluru's test set has repeated exposure and is exploratory, not independent confirmation.

No experiments were run to create this evidence package. v2m archived individual predictions were used to recompute 50 individual model-seed cells, ten five-seed ensemble metrics and the ten frozen paired ST-PIGNN contrasts; v2r LOSO paired predictions were used to independently recalculate pooled and site metrics. `results/RESULTS_VERIFICATION.md` labels provenance. Statistical comparisons are within their original frozen family; do not create new favorable multiplicity families.
