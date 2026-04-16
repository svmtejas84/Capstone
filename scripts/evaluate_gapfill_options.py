"""
Evaluate model-agnostic gapfilling options without modifying raw data.

This script builds a benchmark from observed station values by masking a sample
of known points, predicting them with multiple fill methods, and scoring each
method by pollutant.

Read-only inputs:
- data/raw/stations/meta.parquet
- data/raw/stations/2022.parquet
- data/raw/stations/2024.parquet
- data/raw/stations/2025.parquet
- data/raw/stations/2026_partial.parquet

Outputs:
- data/processed/gapfill/gapfill_benchmark_method_scores.parquet
- data/processed/gapfill/gapfill_benchmark_report.md
- data/processed/gapfill/gapfill_selected_method_policy.parquet

Usage:
    python scripts/evaluate_gapfill_options.py
    python scripts/evaluate_gapfill_options.py --sample-per-pollutant 3000
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

INPUT_FILES = [
    Path("data/raw/stations/2022.parquet"),
    Path("data/raw/stations/2024.parquet"),
    Path("data/raw/stations/2025.parquet"),
    Path("data/raw/stations/2026_partial.parquet"),
]
META_PATH = Path("data/raw/stations/meta.parquet")

OUT_DIR = Path("data/processed/gapfill")
SCORES_OUT = OUT_DIR / "gapfill_benchmark_method_scores.parquet"
REPORT_OUT = OUT_DIR / "gapfill_benchmark_report.md"
POLICY_OUT = OUT_DIR / "gapfill_selected_method_policy.parquet"

DEFAULT_POLLUTANTS = ["pm10", "pm25", "no2", "so2", "co"]
DEFAULT_SAMPLE_PER_POLLUTANT = 2000
DEFAULT_SEED = 42


@dataclass(frozen=True)
class MethodScore:
    pollutant: str
    method: str
    sample_count: int
    predicted_count: int
    coverage: float
    mae: float
    rmse: float
    mape_pct: float
    smape_pct: float
    normalized_mae: float
    p90_abs_error: float


def haversine_matrix(lat: np.ndarray, lon: np.ndarray) -> np.ndarray:
    r = 6_371_000.0
    lat_rad = np.radians(lat)
    lon_rad = np.radians(lon)

    lat1 = lat_rad[:, None]
    lat2 = lat_rad[None, :]
    lon1 = lon_rad[:, None]
    lon2 = lon_rad[None, :]

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = np.sin(dlat / 2.0) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0) ** 2
    c = 2.0 * np.arctan2(np.sqrt(a), np.sqrt(1.0 - a))
    return r * c


def load_station_long(pollutants: list[str]) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    needed = {"parameter", "value", "station_id", "station_name"}

    for path in INPUT_FILES:
        if not path.exists():
            continue
        df = pd.read_parquet(path)
        if not needed.issubset(df.columns):
            continue

        idx = pd.to_datetime(df.index)
        if idx.tz is not None:
            idx = idx.tz_convert("Asia/Kolkata").tz_localize(None)

        part = df[list(needed)].copy()
        part.insert(0, "time", idx)
        part = part[part["parameter"].isin(pollutants)]
        part = part.dropna(subset=["time", "station_id", "value", "parameter"])
        frames.append(part)

    if not frames:
        raise FileNotFoundError("No usable station parquet files found for benchmarking.")

    merged = pd.concat(frames, ignore_index=True)
    merged["station_id"] = merged["station_id"].astype(int)
    merged["value"] = pd.to_numeric(merged["value"], errors="coerce")
    merged = merged.dropna(subset=["value"])

    # Canonical hourly view for benchmarking.
    merged["time"] = pd.to_datetime(merged["time"]).dt.floor("h")
    merged = (
        merged.groupby(["time", "station_id", "station_name", "parameter"], observed=True)["value"]
        .mean()
        .reset_index()
    )
    return merged


def pick_samples(wide: pd.DataFrame, sample_n: int, rng: np.random.Generator) -> list[tuple[pd.Timestamp, int, float]]:
    rows, cols = np.where(~np.isnan(wide.values))
    if len(rows) == 0:
        return []

    n = min(sample_n, len(rows))
    chosen = rng.choice(len(rows), size=n, replace=False)

    samples: list[tuple[pd.Timestamp, int, float]] = []
    col_ids = wide.columns.to_numpy()
    idx_vals = wide.index.to_numpy()
    vals = wide.values

    for i in chosen:
        r = rows[i]
        c = cols[i]
        samples.append((pd.Timestamp(idx_vals[r]), int(col_ids[c]), float(vals[r, c])))
    return samples


def temporal_linear_predict(series: pd.Series, ts: pd.Timestamp) -> float:
    s = series.copy()
    if ts not in s.index:
        return np.nan
    s.loc[ts] = np.nan
    pred = s.sort_index().interpolate(method="time", limit_direction="both").get(ts, np.nan)
    return float(pred) if pd.notna(pred) else np.nan


def temporal_climatology_predict(series: pd.Series, ts: pd.Timestamp) -> float:
    s = series.copy()
    if ts not in s.index:
        return np.nan
    s.loc[ts] = np.nan

    mask = s.notna()
    if not mask.any():
        return np.nan

    df = pd.DataFrame({"v": s[mask]})
    df["hod"] = df.index.hour
    df["dow"] = df.index.dayofweek

    grp = df.groupby(["hod", "dow"], observed=True)["v"].median()
    key = (ts.hour, ts.dayofweek)
    if key in grp.index:
        return float(grp.loc[key])

    # Fallback hierarchy for sparse groups.
    by_hod = df.groupby("hod", observed=True)["v"].median()
    if ts.hour in by_hod.index:
        return float(by_hod.loc[ts.hour])

    return float(df["v"].median())


def build_temporal_climatology_cache(series: pd.Series) -> tuple[pd.Series, pd.Series, float] | None:
    known = series.dropna()
    if known.empty:
        return None
    df = pd.DataFrame({"v": known})
    df["hod"] = df.index.hour
    df["dow"] = df.index.dayofweek
    grp_hd = df.groupby(["hod", "dow"], observed=True)["v"].median()
    grp_h = df.groupby("hod", observed=True)["v"].median()
    global_med = float(df["v"].median())
    return grp_hd, grp_h, global_med


def temporal_climatology_predict_cached(
    cache: tuple[pd.Series, pd.Series, float] | None,
    ts: pd.Timestamp,
) -> float:
    if cache is None:
        return np.nan
    grp_hd, grp_h, global_med = cache
    key = (ts.hour, ts.dayofweek)
    if key in grp_hd.index:
        return float(grp_hd.loc[key])
    if ts.hour in grp_h.index:
        return float(grp_h.loc[ts.hour])
    return global_med


def spatial_idw_predict(
    wide: pd.DataFrame,
    ts: pd.Timestamp,
    station_id: int,
    station_to_pos: dict[int, int],
    dist_matrix: np.ndarray,
) -> float:
    if ts not in wide.index or station_id not in wide.columns:
        return np.nan

    row = wide.loc[ts]
    row = row.drop(labels=[station_id], errors="ignore")
    row = row.dropna()
    if row.empty:
        return np.nan

    s_pos = station_to_pos.get(station_id)
    if s_pos is None:
        return np.nan

    cand_ids = row.index.to_numpy(dtype=int)
    cand_pos = np.array([station_to_pos[c] for c in cand_ids], dtype=int)
    d = dist_matrix[s_pos, cand_pos]

    # Avoid divide-by-zero if duplicates in metadata.
    w = 1.0 / (np.square(d) + 1.0)
    v = row.to_numpy(dtype=float)
    return float(np.sum(w * v) / np.sum(w))


def evaluate_pollutant(
    pollutant_df: pd.DataFrame,
    meta: pd.DataFrame,
    sample_n: int,
    rng: np.random.Generator,
) -> list[MethodScore]:
    wide = pollutant_df.pivot_table(index="time", columns="station_id", values="value", aggfunc="mean").sort_index()
    samples = pick_samples(wide, sample_n=sample_n, rng=rng)
    if not samples:
        return []

    station_ids = [int(c) for c in wide.columns]
    coords = meta.set_index("id").reindex(station_ids)
    keep = coords["lat"].notna() & coords["lon"].notna()

    valid_station_ids = [sid for sid, ok in zip(station_ids, keep.to_numpy()) if bool(ok)]
    if len(valid_station_ids) < 2:
        return []

    # Restrict spatial matrix to stations with coordinates.
    wide_spatial = wide[valid_station_ids]
    coords = coords.loc[valid_station_ids]
    dist = haversine_matrix(coords["lat"].to_numpy(dtype=float), coords["lon"].to_numpy(dtype=float))
    station_to_pos = {sid: i for i, sid in enumerate(valid_station_ids)}

    methods = {
        "temporal_linear": [],
        "temporal_climatology": [],
        "spatial_idw": [],
        "hybrid_linear_idw": [],
        "station_median": [],
    }

    truths: list[float] = []

    # Cache station-level climatology and medians once for speed.
    climatology_cache: dict[int, tuple[pd.Series, pd.Series, float] | None] = {}
    station_medians: dict[int, float] = {}
    for sid in station_ids:
        s = wide[sid]
        climatology_cache[sid] = build_temporal_climatology_cache(s)
        station_medians[sid] = float(s.dropna().median()) if s.notna().any() else np.nan

    for ts, sid, truth in samples:
        truths.append(truth)

        series = wide[sid] if sid in wide.columns else pd.Series(dtype=float)

        pred_tlin = temporal_linear_predict(series, ts)
        pred_tclim = temporal_climatology_predict_cached(climatology_cache.get(sid), ts)

        pred_idw = np.nan
        if sid in wide_spatial.columns:
            pred_idw = spatial_idw_predict(
                wide=wide_spatial,
                ts=ts,
                station_id=sid,
                station_to_pos=station_to_pos,
                dist_matrix=dist,
            )

        if pd.notna(pred_tlin) and pd.notna(pred_idw):
            pred_hybrid = 0.6 * pred_tlin + 0.4 * pred_idw
        elif pd.notna(pred_tlin):
            pred_hybrid = pred_tlin
        elif pd.notna(pred_idw):
            pred_hybrid = pred_idw
        else:
            pred_hybrid = pred_tclim

        station_med = station_medians.get(sid, np.nan)

        methods["temporal_linear"].append(pred_tlin)
        methods["temporal_climatology"].append(pred_tclim)
        methods["spatial_idw"].append(pred_idw)
        methods["hybrid_linear_idw"].append(pred_hybrid)
        methods["station_median"].append(station_med)

    truth_arr = np.array(truths, dtype=float)
    eps = 1e-6
    scale = max(float(np.median(np.abs(truth_arr))), eps)

    out: list[MethodScore] = []
    n = len(truth_arr)

    for method, preds in methods.items():
        p = np.array(preds, dtype=float)
        mask = ~np.isnan(p)
        pred_n = int(mask.sum())

        if pred_n == 0:
            out.append(
                MethodScore(
                    pollutant=str(pollutant_df["parameter"].iloc[0]),
                    method=method,
                    sample_count=n,
                    predicted_count=0,
                    coverage=0.0,
                    mae=np.nan,
                    rmse=np.nan,
                    mape_pct=np.nan,
                    smape_pct=np.nan,
                    normalized_mae=np.nan,
                    p90_abs_error=np.nan,
                )
            )
            continue

        t = truth_arr[mask]
        pr = p[mask]
        ae = np.abs(pr - t)
        mae = float(np.mean(ae))
        rmse = float(np.sqrt(np.mean(np.square(pr - t))))
        mape = float(np.mean(ae / np.maximum(np.abs(t), eps)) * 100.0)
        smape = float(np.mean(2.0 * ae / np.maximum(np.abs(t) + np.abs(pr), eps)) * 100.0)
        nmae = float(mae / scale)
        p90 = float(np.quantile(ae, 0.90))

        out.append(
            MethodScore(
                pollutant=str(pollutant_df["parameter"].iloc[0]),
                method=method,
                sample_count=n,
                predicted_count=pred_n,
                coverage=float(pred_n / n),
                mae=mae,
                rmse=rmse,
                mape_pct=mape,
                smape_pct=smape,
                normalized_mae=nmae,
                p90_abs_error=p90,
            )
        )

    return out


def recommend(df_scores: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    # Primary rank metric emphasizes quality then coverage.
    rank_df = df_scores.copy()
    rank_df["quality_score"] = rank_df["normalized_mae"]
    rank_df["smape_score"] = rank_df["smape_pct"] / 100.0
    rank_df["coverage_penalty"] = 1.0 - rank_df["coverage"]
    rank_df["composite"] = rank_df["quality_score"] + 0.60 * rank_df["smape_score"] + 0.25 * rank_df["coverage_penalty"]

    per_pollutant = (
        rank_df.sort_values(["pollutant", "composite", "rmse"]) 
        .groupby("pollutant", observed=True)
        .head(1)
        .reset_index(drop=True)
    )

    overall = (
        rank_df.groupby("method", observed=True)
        .agg(
            pollutants=("pollutant", "nunique"),
            avg_composite=("composite", "mean"),
            avg_coverage=("coverage", "mean"),
            avg_nmae=("normalized_mae", "mean"),
            avg_smape=("smape_pct", "mean"),
        )
        .reset_index()
        .sort_values(["avg_composite", "avg_nmae"])
    )

    return per_pollutant, overall


def write_report(
    scores: pd.DataFrame,
    best_per_pollutant: pd.DataFrame,
    overall: pd.DataFrame,
    sample_per_pollutant: int,
    seed: int,
) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    lines.append("# Gapfill Options Evaluation")
    lines.append("")
    lines.append("This report evaluates candidate gapfilling methods on observed data by masking known points.")
    lines.append("")
    lines.append("## Benchmark Setup")
    lines.append("")
    lines.append(f"- Sample points per pollutant: {sample_per_pollutant}")
    lines.append(f"- Random seed: {seed}")
    lines.append("- Inputs: station files for 2022, 2024, 2025, 2026_partial (read-only)")
    lines.append("- Methods: temporal_linear, temporal_climatology, spatial_idw, hybrid_linear_idw, station_median")
    lines.append("")

    lines.append("## Best Method Per Pollutant")
    lines.append("")
    lines.append("| Pollutant | Best Method | Coverage | MAE | RMSE | MAPE % | sMAPE % | P90 Abs Error |")
    lines.append("|---|---|---:|---:|---:|---:|---:|---:|")
    for r in best_per_pollutant.itertuples(index=False):
        lines.append(
            f"| {r.pollutant} | {r.method} | {r.coverage:.3f} | {r.mae:.4f} | {r.rmse:.4f} | "
            f"{r.mape_pct:.2f} | {r.smape_pct:.2f} | {r.p90_abs_error:.4f} |"
        )

    lines.append("")
    lines.append("## Overall Ranking")
    lines.append("")
    lines.append("| Method | Pollutants | Avg Composite | Avg Coverage | Avg Normalized MAE | Avg sMAPE % |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for r in overall.itertuples(index=False):
        lines.append(
            f"| {r.method} | {int(r.pollutants)} | {r.avg_composite:.4f} | {r.avg_coverage:.3f} | "
            f"{r.avg_nmae:.4f} | {r.avg_smape:.2f} |"
        )

    lines.append("")
    lines.append("## Recommendation")
    lines.append("")

    if overall.empty:
        lines.append("No recommendation available; scoring table is empty.")
    else:
        top_method = str(overall.iloc[0]["method"])
        lines.append(f"- Primary default: `{top_method}`")
        lines.append("- Policy: keep raw observations immutable and store imputed values in a separate derived layer.")
        lines.append("- For production: attach confidence tiers (observed, high-confidence-imputed, low-confidence-inferred).")

    lines.append("")
    lines.append("## Full Scores")
    lines.append("")
    lines.append("| Pollutant | Method | Coverage | MAE | RMSE | MAPE % | sMAPE % | Normalized MAE | P90 Abs Error |")
    lines.append("|---|---|---:|---:|---:|---:|---:|---:|---:|")

    for r in scores.sort_values(["pollutant", "normalized_mae", "smape_pct", "coverage"], ascending=[True, True, True, False]).itertuples(index=False):
        lines.append(
            f"| {r.pollutant} | {r.method} | {r.coverage:.3f} | {r.mae:.4f} | {r.rmse:.4f} | "
            f"{r.mape_pct:.2f} | {r.smape_pct:.2f} | {r.normalized_mae:.4f} | {r.p90_abs_error:.4f} |"
        )

    REPORT_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample-per-pollutant", type=int, default=DEFAULT_SAMPLE_PER_POLLUTANT)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--pollutants", type=str, default=",".join(DEFAULT_POLLUTANTS))
    args = parser.parse_args()

    pollutants = [p.strip() for p in args.pollutants.split(",") if p.strip()]
    if not pollutants:
        raise ValueError("At least one pollutant must be provided.")

    meta = pd.read_parquet(META_PATH)
    need_meta = {"id", "lat", "lon"}
    if not need_meta.issubset(meta.columns):
        raise ValueError(f"meta.parquet must include columns: {sorted(need_meta)}")

    long_df = load_station_long(pollutants)

    rng = np.random.default_rng(args.seed)
    all_scores: list[MethodScore] = []

    for pollutant in pollutants:
        p_df = long_df[long_df["parameter"] == pollutant].copy()
        if p_df.empty:
            continue

        scores = evaluate_pollutant(
            pollutant_df=p_df,
            meta=meta,
            sample_n=int(args.sample_per_pollutant),
            rng=rng,
        )
        all_scores.extend(scores)

    if not all_scores:
        raise RuntimeError("No scores produced. Check that station data has usable observed values.")

    out_df = pd.DataFrame([s.__dict__ for s in all_scores])

    best_per_pollutant, overall = recommend(out_df)

    # Production policy snapshot for downstream consumers.
    policy_rows = []
    for pollutant, grp in out_df.groupby("pollutant", observed=True):
        ranked = grp.copy()
        ranked["composite"] = ranked["normalized_mae"] + 0.60 * (ranked["smape_pct"] / 100.0) + 0.25 * (1.0 - ranked["coverage"])
        ranked = ranked.sort_values(["composite", "rmse"])
        primary = ranked.iloc[0]
        fallback = ranked.iloc[1] if len(ranked) > 1 else ranked.iloc[0]
        policy_rows.append(
            {
                "pollutant": pollutant,
                "primary_method": str(primary["method"]),
                "fallback_method": str(fallback["method"]),
                "primary_p90_abs_error": float(primary["p90_abs_error"]),
                "primary_smape_pct": float(primary["smape_pct"]),
            }
        )
    policy_df = pd.DataFrame(policy_rows).sort_values("pollutant")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_df.to_parquet(SCORES_OUT, index=False)
    policy_df.to_parquet(POLICY_OUT, index=False)
    write_report(
        scores=out_df,
        best_per_pollutant=best_per_pollutant,
        overall=overall,
        sample_per_pollutant=int(args.sample_per_pollutant),
        seed=int(args.seed),
    )

    print("Gapfill evaluation complete")
    print(f"Scores: {SCORES_OUT}")
    print(f"Policy: {POLICY_OUT}")
    print(f"Report: {REPORT_OUT}")


if __name__ == "__main__":
    main()
