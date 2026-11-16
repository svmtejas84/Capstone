"""Descriptive paired daily-lag comparison named in the frozen V5 protocol.

This comparison was not part of the 10-member frozen temporal inference family.
Its intervals are exploratory and are never used for model selection.
"""
import csv

import numpy as np
import pandas as pd

from final_blr_results.controlled_validation_v3.scripts.analyze_controls import block_analysis
from final_blr_results.controlled_validation_v3.scripts.smoke_gpu import ARR, V3
from final_blr_results.controlled_validation_v5.scripts.train_graph_lag import V5


def main():
    times = pd.to_datetime(np.load(ARR)["times_ns"], utc=True)
    rows = []
    for h in (1, 3, 6, 12, 24):
        with np.load(V5 / "predictions" / f"h{h}_lag24_ensemble.npz") as a:
            with np.load(V3 / "predictions" / f"h{h}_same_hour_yesterday.npz") as b:
                for key in ("truth", "time_index", "station_index"):
                    assert np.array_equal(a[key], b[key]), key
                error_a = np.abs(a["pred"] - a["truth"])
                error_b = np.abs(b["pred"] - b["truth"])
                day = times[a["time_index"]].floor("D").asi8
                ci, _, blocks, days = block_analysis(day, error_a - error_b, 58000 + h)
                rows.append(dict(horizon_hours=h,scored_pairs=len(error_a),
                    lag24_model_mae_ug_m3=float(error_a.mean()),
                    same_hour_yesterday_mae_ug_m3=float(error_b.mean()),
                    lag24_minus_simple_baseline_ug_m3=float((error_a - error_b).mean()),
                    ci95_low_ug_m3=float(ci[0]),ci95_high_ug_m3=float(ci[1]),
                    utc_days=days,nonoverlap_7day_blocks=blocks,
                    status="post-score descriptive comparison named in frozen protocol; exposed test"))
    out = V5 / "statistical_analysis/DAILY_LAG_SIMPLE_BASELINE.csv"
    with out.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader();writer.writerows(rows)
    print(out, len(rows))


if __name__ == "__main__":
    main()
