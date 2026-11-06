"""Regenerate v2n per-station LOSO table from immutable v2j saved summaries."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
df = pd.read_csv(ROOT / "results/loso_per_station_v2j.csv")
sel = df[(df.anchor == "train_mean") & (~df.seasonal_bias_corrected) &
         df.method.isin(["stpignn_original", "ridge_weather_static", "idw", "ordinary_kriging", "gp_rbf", "station_train_mean"])]
base = df[(df.anchor == "baseline") & (~df.seasonal_bias_corrected) &
          df.method.isin(["ridge_weather_static", "idw", "ordinary_kriging", "gp_rbf", "station_train_mean"])]
model = sel[sel.method == "stpignn_original"]
table = pd.concat([model, base], ignore_index=True)
table = table[["station_id", "method", "n", "mae", "rmse", "r2"]].sort_values(["station_id", "method"])
assert table.station_id.nunique() == 11
assert set(table.groupby("station_id").size()) == {6}
table.to_csv(OUT / "loso_per_station_comparison.csv", index=False)
print(f"{len(table)} rows; {table.station_id.nunique()} spatial sites")
