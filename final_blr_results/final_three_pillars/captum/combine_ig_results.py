"""Combine versioned row-level Captum records without pooling model protocols."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent
v2c_out = ROOT / "IG_RESULTS_v2c.csv"
combined_path = ROOT / "IG_RESULTS.csv"
v2r_path = ROOT / "v2r_heldout_h6" / "IG_RESULTS.csv"

v2c = pd.read_csv(v2c_out if v2c_out.exists() else combined_path)
v2c["analysis_version"] = "v2c_h1"
v2c.to_csv(v2c_out, index=False)
v2r = pd.read_csv(v2r_path)
v2r["analysis_version"] = "v2r_outer_loso_h6"
all_rows = pd.concat([v2c, v2r], ignore_index=True, sort=False)
all_rows.to_csv(combined_path, index=False)
assert len(v2c) == 54 and len(v2r) == 18 and len(all_rows) == 72
assert set(all_rows["analysis_version"]) == {"v2c_h1", "v2r_outer_loso_h6"}
print(f"combined rows={len(all_rows)}; versions={all_rows.analysis_version.value_counts().to_dict()}")
