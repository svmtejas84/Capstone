"""Independent numerical/format checks for V5 saved scores and assets."""
import json
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image

from src.stpignn.evaluation import evaluate_arrays
from final_blr_results.controlled_validation_v3.scripts.smoke_gpu import V3
from final_blr_results.controlled_validation_v5.scripts.train_graph_lag import V5
from final_blr_results.controlled_validation_v5.scripts.verify_and_score import HISTORICAL


def prediction_path(h, variant, seed):
    suffix = "_ensemble" if seed == "ensemble" else f"_seed{seed}"
    if "_lambda" not in variant:
        return V5 / "predictions" / f"h{h}_{variant}{suffix}.npz"
    family, strength_text = variant.rsplit("_lambda", 1)
    strength = float(strength_text)
    if strength in HISTORICAL[family]:
        root, name = HISTORICAL[family][strength]
        return root / "predictions" / f"h{h}_{name}{suffix}.npz"
    return V5 / "predictions" / f"h{h}_{variant}{suffix}.npz"


def main():
    scores = pd.read_csv(V5 / "metrics/NEW_TEST_SCORES.csv", dtype={"seed": str})
    assert len(scores) == 240
    worst = 0.0
    for row in scores.itertuples():
        path = prediction_path(int(row.horizon_hours), row.variant, row.seed)
        assert path.exists(), path
        with np.load(path) as z:
            metric = evaluate_arrays(z["pred"], z["truth"], np.ones(len(z["truth"]), bool))
        for key in ("mae", "rmse", "r2"):
            error = abs(float(metric[key]) - float(getattr(row, key)))
            worst = max(worst, error)
            assert error < 1e-5, (path, key, error)
        assert int(metric["n"]) == int(row.scored_pairs) == 14583

    figures = ("F1_graph_topology", "F2_lag_information", "F3_regularizer_grid", "F4_anchor_coverage")
    for name in figures:
        png, pdf, svg = ((V5 / "figures" / f"{name}.{ext}") for ext in ("png", "pdf", "svg"))
        with Image.open(png) as im:
            im.verify()
        with Image.open(png) as im:
            assert im.size[0] >= 1200 and im.size[1] >= 600
        data = pdf.read_bytes()
        assert data.startswith(b"%PDF") and b"%%EOF" in data[-1024:]
        assert ET.parse(svg).getroot().tag.endswith("svg")

    table_names = ("T1_GRAPH_TOPOLOGY", "T2_LAG_INFORMATION", "T3_REGULARIZER_GRID",
                   "T4_PAIRED_CONTRASTS", "T5_TRAINING_SELECTION", "S1_ANCHOR_AGE_ALL_METHODS",
                   "T6_SEED_LEVEL", "T7_DAILY_BASELINE", "T8_PENALTY_DIAGNOSTICS")
    for name in table_names:
        csv_path = V5 / "tables" / f"{name}.csv"
        tex_path = V5 / "tables" / f"{name}.tex"
        assert not pd.read_csv(csv_path).empty
        tex = tex_path.read_text()
        assert "\\begin{tabular}" in tex and "\\end{tabular}" in tex
    grid = pd.read_csv(V5 / "tables/T3_REGULARIZER_GRID.csv")
    assert len(grid) == 18 and int(grid.selected_on_validation.sum()) == 6
    daily = pd.read_csv(V5 / "statistical_analysis/DAILY_LAG_SIMPLE_BASELINE.csv")
    assert len(daily) == 5 and set(daily.scored_pairs) == {14583}
    assert np.allclose(daily.lag24_model_mae_ug_m3-daily.same_hour_yesterday_mae_ug_m3,
                       daily.lag24_minus_simple_baseline_ug_m3, atol=1e-5)
    receipt = dict(status="PASS",new_score_rows_recomputed=len(scores),max_abs_metric_discrepancy=worst,
                   figure_triplets_opened=len(figures),numeric_table_pairs_checked=len(table_names),
                   daily_baseline_rows_checked=len(daily),
                   scientific_scope="consistency and readability-file checks; not independent validation")
    (V5 / "verification/release_checks.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
