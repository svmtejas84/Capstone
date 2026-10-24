"""Report individual LOSO seed metrics from the fixed Gate C predictions."""
from __future__ import annotations

import pandas as pd

from src.stpignn.evaluation import evaluate_arrays
from src.stpignn.paths import REPO_ROOT


def main():
    frame = pd.read_parquet(REPO_ROOT / "results/loso_predictions_v2.parquet")
    rows = []
    for (method, seed), group in frame.loc[frame.seed >= 0].groupby(["method", "seed"]):
        metrics = evaluate_arrays(group.prediction, group.target, group.target.notna())
        rows.append({"method": method, "seed": int(seed), **metrics})
    out = pd.DataFrame(rows).sort_values(["method", "seed"])
    out.to_csv(REPO_ROOT / "results/loso_seed_summary_v2.csv", index=False)
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
