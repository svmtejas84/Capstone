"""One-time mechanical move of notebook definitions into src.stpignn.

Saves the exact pre-edit notebook to results for the legacy audit. The script
changes only listed code cells and clears stale notebook outputs.
"""
from __future__ import annotations

import ast
import json
from pathlib import Path

from src.stpignn.paths import REPO_ROOT

NOTEBOOK = REPO_ROOT / "notebooks/production/evaluated_wind_advection.ipynb"
SNAPSHOT = REPO_ROOT / "results/legacy_canonical_notebook.ipynb"


def replace_definition(source: str, name: str, replacement: str) -> str:
    lines = source.splitlines(keepends=True)
    match = next(node for node in ast.parse(source).body
                 if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name == name)
    return "".join(lines[:match.lineno - 1]) + replacement + "\n" + "".join(lines[match.end_lineno:])


def update_cell(book: dict, number: int, source: str) -> None:
    book["cells"][number]["source"] = source.splitlines(keepends=True)


def main() -> None:
    if SNAPSHOT.exists():
        raise FileExistsError(f"Refusing to replace existing audit snapshot: {SNAPSHOT}")
    raw = NOTEBOOK.read_bytes()
    SNAPSHOT.write_bytes(raw)
    book = json.loads(raw)

    s = "".join(book["cells"][0]["source"])
    start = s.index("# 1. Directory Structure Alignment")
    end = s.index("# Import downstream", start)
    s = s[:start] + "from src.stpignn.paths import REPO_ROOT\nROOT_DIR = REPO_ROOT\n\n" + s[end:]
    s = s.replace("from gnn.model import STPIGNN, LossBreakdown", "from src.stpignn import STPIGNN\n    from gnn.model import LossBreakdown")
    update_cell(book, 0, s)

    s = "".join(book["cells"][2]["source"])
    s = replace_definition(s, "SpatialPartition", "from src.stpignn.legacy_canonical import SpatialPartition")
    update_cell(book, 2, s)

    s = "".join(book["cells"][7]["source"])
    s = replace_definition(s, "compute_dynamic_upwind_mask_vectorized",
                           "from src.stpignn.legacy_canonical import compute_dynamic_upwind_mask_vectorized as _legacy_mask\n"
                           "def compute_dynamic_upwind_mask_vectorized(cluster_obj, current_wind_dir_deg, cone_angle_deg=75.0):\n"
                           "    return _legacy_mask(cluster_obj.edge_bearings, current_wind_dir_deg, cone_angle_deg)")
    update_cell(book, 7, s)

    s = "".join(book["cells"][9]["source"])
    s = replace_definition(s, "TierAwareClusterDatasetV3",
                           "from src.stpignn.legacy_canonical import TierAwareClusterDatasetV3")
    s = s.replace("TierAwareClusterDatasetV3(cluster_data, t0=0, t1=87178, window=12, stride=GLOBAL_CFG[\"train_stride\"])",
                  "TierAwareClusterDatasetV3(cluster_data, t0=0, t1=87178, time_count=T_total, time_breaks=time_breaks, raw_node_indices=raw_node_indices, raw_targets=raw_targets, window=12, stride=GLOBAL_CFG[\"train_stride\"])")
    s = s.replace("TierAwareClusterDatasetV3(cluster_data, t0=87178, t1=87514, window=12, stride=GLOBAL_CFG[\"val_stride\"])",
                  "TierAwareClusterDatasetV3(cluster_data, t0=87178, t1=87514, time_count=T_total, time_breaks=time_breaks, raw_node_indices=raw_node_indices, raw_targets=raw_targets, window=12, stride=GLOBAL_CFG[\"val_stride\"])")
    update_cell(book, 9, s)

    s = "".join(book["cells"][13]["source"])
    for name in ("masked_mae_rmse_vectorized", "compute_wind_advection_penalty"):
        s = replace_definition(s, name, f"from src.stpignn.legacy_canonical import {name}")
    update_cell(book, 13, s)

    s = "".join(book["cells"][20]["source"])
    s = replace_definition(s, "compute_dynamic_upwind_mask_inline",
                           "from src.stpignn.legacy_canonical import compute_dynamic_upwind_mask_vectorized as _legacy_mask\n"
                           "def compute_dynamic_upwind_mask_inline(cluster_obj, current_wind_dir_deg, coords_matrix, device_target, cone_angle_deg=75.0):\n"
                           "    return _legacy_mask(cluster_obj.edge_bearings, current_wind_dir_deg, cone_angle_deg)")
    update_cell(book, 20, s)

    s = "".join(book["cells"][22]["source"])
    for name in ("VanillaGCN", "ST_GRUGCN"):
        s = replace_definition(s, name, f"from src.stpignn.legacy_canonical import {name}")
    update_cell(book, 22, s)

    s = "".join(book["cells"][24]["source"])
    begin = s.index("final_preds = torch.cat(all_flat_preds)")
    end = s.index("print(\"\\n\" + \"=\"*80)", begin)
    s = s[:begin] + ("from src.stpignn.legacy_canonical import legacy_global_metrics\n"
                     "final_preds, final_targets, global_mae, global_rmse, global_median_err = legacy_global_metrics(\n"
                     "    all_flat_preds, all_flat_targets, TARGET_SCALE)\n"
                     "global_mse = float(np.mean((final_preds - final_targets) ** 2))\n\n") + s[end:]
    update_cell(book, 24, s)

    s = "".join(book["cells"][17]["source"])
    s = s.replace('mae_val, rmse_val, r2_str = 46.2134, 47.1082, "0.0124"',
                  'mae_val, rmse_val, r2_str = float("nan"), float("nan"), "N/A"')
    update_cell(book, 17, s)

    for cell in book["cells"]:
        if cell["cell_type"] == "code":
            cell["outputs"] = []
            cell["execution_count"] = None
    NOTEBOOK.write_text(json.dumps(book, ensure_ascii=False, indent=1) + "\n")
    print(f"Rewired {NOTEBOOK}; legacy snapshot {SNAPSHOT}")


if __name__ == "__main__":
    main()
