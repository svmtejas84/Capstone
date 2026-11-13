# Protocol amendment 01 — label-independent shuffled-wind permutation

Frozen during v3 matched-control training, before any v3 test evaluation. The first implementation constructed the shuffle from `ctx.hours[split]`, which is selected using observed-target availability. It did not use target **values**, but its permutation index depended on the target mask and therefore did not satisfy the frozen control definition.

The final worker was stopped after five completed h1/seed11 cells, with no test evaluation. The completed shuffled-wind cell was preserved under `training/invalidated_pre_amendment/`; the other four completed cells are retained because their implementation did not depend on this shuffle. The interrupted next cell retains its partial checkpoint. No test score or final comparison was available when this change was made.

The corrected shuffled control permutes precomputed directional masks among **all hourly timestamps in the same calendar month**, using fixed RNG seed 4303. Month grouping uses timestamps only, not target values or availability. Predictive weather features remain unchanged. This retains a seasonal wind-mask distribution, is deterministic, and does not select the permutation using targets. All h1/seed11 shuffled-control training must be rerun from scratch. Other frozen models, primary comparisons, seeds, horizons, optimizer and test-lock rules are unchanged.

The original frozen protocol remains intact; this is a recorded implementation correction, not a test-guided hyperparameter change.
