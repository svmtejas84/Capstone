"""
Build a derived station gapfill layer in data/processed without modifying raw data.

Inputs (read-only):
- data/raw/stations/meta.parquet
- data/raw/stations/2022.parquet
- data/raw/stations/2024.parquet
- data/raw/stations/2025.parquet
- data/raw/stations/2026_partial.parquet
- data/processed/gapfill/gapfill_selected_method_policy.parquet

Outputs:
- data/processed/gapfill/station_timeseries_observed_imputed.parquet
- data/processed/gapfill/station_timeseries_unresolved_index.parquet
- data/processed/gapfill/station_timeseries_imputation_summary.parquet
- data/processed/gapfill/station_timeseries_imputation_build_report.md

Usage:
    python scripts/build_gapfill_derived_layer.py
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

RAW_FILES = [
    Path("data/raw/stations/2022.parquet"),
    Path("data/raw/stations/2024.parquet"),
    Path("data/raw/stations/2025.parquet"),
    Path("data/raw/stations/2026_partial.parquet"),
]
META_PATH = Path("data/raw/stations/meta.parquet")
POLICY_PATH = Path("data/processed/gapfill/gapfill_selected_method_policy.parquet")

OUT_DIR = Path("data/processed/gapfill")
DERIVED_OUT = OUT_DIR / "station_timeseries_observed_imputed.parquet"
MISSING_OUT = OUT_DIR / "station_timeseries_unresolved_index.parquet"
SUMMARY_OUT = OUT_DIR / "station_timeseries_imputation_summary.parquet"
BUILD_REPORT_OUT = OUT_DIR / "station_timeseries_imputation_build_report.md"

DEFAULT_POLLUTANTS = ["pm10", "pm25", "no2", "so2", "co"]


@dataclass(frozen=True)
class Policy:
    primary_method: str
    fallback_method: str
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
    need = {"parameter", "value", "station_id", "station_name"}

    for p in RAW_FILES:
        if not p.exists():
            continue
        df = pd.read_parquet(p)
        if not need.issubset(df.columns):
            continue

        idx = pd.to_datetime(df.index)
        if idx.tz is not None:
            idx = idx.tz_convert("Asia/Kolkata").tz_localize(None)

        part = df[list(need)].copy()
        part.insert(0, "time", idx)
        part = part[part["parameter"].isin(pollutants)]
        part = part.dropna(subset=["time", "station_id", "value", "parameter"])
        frames.append(part)

    if not frames:
        raise FileNotFoundError("No raw station files available for derived gapfill build.")

    merged = pd.concat(frames, ignore_index=True)
    merged["station_id"] = merged["station_id"].astype(int)
    merged["value"] = pd.to_numeric(merged["value"], errors="coerce")
    merged = merged.dropna(subset=["value"])

    merged["time"] = pd.to_datetime(merged["time"]).dt.floor("h")
    merged = (
        merged.groupby(["time", "station_id", "station_name", "parameter"], observed=True)["value"]
        .mean()
        .reset_index()
    )
    return merged


def load_policy() -> dict[str, Policy]:
    if not POLICY_PATH.exists():
        raise FileNotFoundError(
            "Policy file missing. Run scripts/evaluate_gapfill_options.py first."
        )

    df = pd.read_parquet(POLICY_PATH)
    out: dict[str, Policy] = {}
    for r in df.itertuples(index=False):
        out[str(r.pollutant)] = Policy(
            primary_method=str(r.primary_method),
            fallback_method=str(r.fallback_method),
            p90_abs_error=float(r.primary_p90_abs_error),
        )
    return out


def temporal_climatology(series: pd.Series) -> pd.Series:
    s = series.copy()
    known = s.dropna()
    if known.empty:
        return s

    df = pd.DataFrame({"v": known})
    df["hod"] = df.index.hour
    df["dow"] = df.index.dayofweek
    grp_hd = df.groupby(["hod", "dow"], observed=True)["v"].median()
    grp_h = df.groupby("hod", observed=True)["v"].median()
    global_med = float(df["v"].median())

    missing = s.index[s.isna()]
    for ts in missing:
        key = (ts.hour, ts.dayofweek)
        if key in grp_hd.index:
            s.loc[ts] = float(grp_hd.loc[key])
        elif ts.hour in grp_h.index:
            s.loc[ts] = float(grp_h.loc[ts.hour])
        else:
            s.loc[ts] = global_med
    return s


def apply_spatial_idw(
    observed_wide: pd.DataFrame,
    target_wide: pd.DataFrame,
    station_ids: list[int],
    station_to_pos: dict[int, int],
    dist_matrix: np.ndarray,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    filled = target_wide.copy()
    source_count = pd.DataFrame(0, index=target_wide.index, columns=target_wide.columns, dtype=int)

    for sid in station_ids:
        if sid not in filled.columns:
            continue
        miss_idx = filled.index[filled[sid].isna()]
        if len(miss_idx) == 0:
            continue

        sid_pos = station_to_pos.get(sid)
        if sid_pos is None:
            continue

        for ts in miss_idx:
            if ts not in observed_wide.index:
                continue
            row = observed_wide.loc[ts].drop(labels=[sid], errors="ignore").dropna()
            if len(row) < 2:
                continue

            cand_ids = row.index.to_numpy(dtype=int)
            cand_pos = np.array([station_to_pos[c] for c in cand_ids], dtype=int)
            d = dist_matrix[sid_pos, cand_pos]
            w = 1.0 / (np.square(d) + 1.0)
            v = row.to_numpy(dtype=float)
            val = float(np.sum(w * v) / np.sum(w))

            filled.at[ts, sid] = val
            source_count.at[ts, sid] = int(len(cand_ids))

    return filled, source_count


def gap_lengths(mask_missing: pd.Series) -> pd.Series:
    # For each missing timestamp, assigns size of its contiguous gap block in hours.
    out = pd.Series(0, index=mask_missing.index, dtype=int)
    if mask_missing.sum() == 0:
        return out

    grp = (mask_missing != mask_missing.shift()).cumsum()
    sizes = mask_missing.groupby(grp).transform("sum")
    out[mask_missing] = sizes[mask_missing].astype(int)
    return out


def build_for_pollutant(
    long_df: pd.DataFrame,
    pollutant: str,
    meta: pd.DataFrame,
    policy: Policy,
    run_id: str,
    use_spatial_idw: bool,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    p_df = long_df[long_df["parameter"] == pollutant].copy()
    if p_df.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    wide_obs = p_df.pivot_table(index="time", columns="station_id", values="value", aggfunc="mean").sort_index()
    station_ids = [int(c) for c in wide_obs.columns]

    # Use observed timestamps only to avoid fabricating entirely unobserved timelines.
    full_index = pd.DatetimeIndex(wide_obs.index.unique()).sort_values()
    wide_obs = wide_obs.reindex(full_index)

    coords = meta.set_index("id").reindex(station_ids)
    valid = coords["lat"].notna() & coords["lon"].notna()
    spatial_ids = [sid for sid, ok in zip(station_ids, valid.to_numpy()) if bool(ok)]

    station_to_pos = {sid: i for i, sid in enumerate(spatial_ids)}
    dist = (
        haversine_matrix(
            coords.loc[spatial_ids, "lat"].to_numpy(dtype=float),
            coords.loc[spatial_ids, "lon"].to_numpy(dtype=float),
        )
        if spatial_ids
        else np.empty((0, 0), dtype=float)
    )

    method_tag = pd.DataFrame("observed", index=wide_obs.index, columns=wide_obs.columns, dtype=object)
    confidence = pd.DataFrame(1.0, index=wide_obs.index, columns=wide_obs.columns, dtype=float)
    uncertainty = pd.DataFrame(0.0, index=wide_obs.index, columns=wide_obs.columns, dtype=float)
    source_count = pd.DataFrame(1, index=wide_obs.index, columns=wide_obs.columns, dtype=int)
    tier = pd.DataFrame("A", index=wide_obs.index, columns=wide_obs.columns, dtype=object)

    result = wide_obs.copy()
    initial_missing = result.isna()

    # Step 1: temporal linear (bounded to avoid overreach).
    lin = result.interpolate(method="time", limit=24, limit_direction="both")
    m = result.isna() & lin.notna()
    result = result.where(~m, lin)
    method_tag = method_tag.where(~m, "temporal_linear")
    confidence = confidence.where(~m, 0.85)
    uncertainty = uncertainty.where(~m, policy.p90_abs_error)
    tier = tier.where(~m, "B")

    # Step 2: optional spatial IDW fallback.
    if use_spatial_idw and spatial_ids:
        base_for_idw = wide_obs[spatial_ids]
        target_for_idw = result[spatial_ids]
        idw_filled, idw_count = apply_spatial_idw(
            observed_wide=base_for_idw,
            target_wide=target_for_idw,
            station_ids=spatial_ids,
            station_to_pos=station_to_pos,
            dist_matrix=dist,
        )
        for sid in spatial_ids:
            sid_mask = result[sid].isna() & idw_filled[sid].notna()
            if sid_mask.any():
                result.loc[sid_mask, sid] = idw_filled.loc[sid_mask, sid]
                method_tag.loc[sid_mask, sid] = "spatial_idw"
                confidence.loc[sid_mask, sid] = 0.70
                uncertainty.loc[sid_mask, sid] = policy.p90_abs_error * 1.15
                source_count.loc[sid_mask, sid] = idw_count.loc[sid_mask, sid]
                tier.loc[sid_mask, sid] = "B"

    # Step 3: temporal climatology fallback.
    for sid in station_ids:
        s = result[sid]
        if not s.isna().any():
            continue
        filled = temporal_climatology(s)
        sid_mask = s.isna() & filled.notna()
        if sid_mask.any():
            result.loc[sid_mask, sid] = filled.loc[sid_mask]
            method_tag.loc[sid_mask, sid] = "temporal_climatology"
            confidence.loc[sid_mask, sid] = 0.55
            uncertainty.loc[sid_mask, sid] = policy.p90_abs_error * 1.35
            source_count.loc[sid_mask, sid] = 1
            tier.loc[sid_mask, sid] = "C"

    # Step 4: station median final fallback.
    for sid in station_ids:
        s = result[sid]
        if not s.isna().any():
            continue
        med = float(wide_obs[sid].dropna().median()) if wide_obs[sid].notna().any() else np.nan
        if np.isnan(med):
            continue
        sid_mask = s.isna()
        result.loc[sid_mask, sid] = med
        method_tag.loc[sid_mask, sid] = "station_median"
        confidence.loc[sid_mask, sid] = 0.35
        uncertainty.loc[sid_mask, sid] = policy.p90_abs_error * 1.60
        source_count.loc[sid_mask, sid] = 1
        tier.loc[sid_mask, sid] = "C"

    # Gap size metadata from original observed matrix.
    gap_hours = pd.DataFrame(0, index=wide_obs.index, columns=wide_obs.columns, dtype=int)
    for sid in station_ids:
        g = gap_lengths(initial_missing[sid])
        gap_hours[sid] = g

    def to_long(df: pd.DataFrame, value_name: str) -> pd.DataFrame:
        tmp = df.copy()
        tmp.index.name = "time"
        out = tmp.reset_index().melt(id_vars=["time"], var_name="station_id", value_name=value_name)
        out["station_id"] = out["station_id"].astype(int)
        return out

    # Convert wide artifacts to long form.
    base = to_long(result, "value")
    base["parameter"] = pollutant

    obs = to_long(wide_obs, "observed_value")

    meth = to_long(method_tag, "impute_method")

    conf = to_long(confidence, "impute_confidence")

    unc = to_long(uncertainty, "impute_uncertainty_abs")

    sc = to_long(source_count, "impute_source_count")

    tr = to_long(tier, "impute_tier")

    gh = to_long(gap_hours, "gap_hours")

    out = base.merge(obs, on=["time", "station_id"], how="left")
    out = out.merge(meth, on=["time", "station_id"], how="left")
    out = out.merge(conf, on=["time", "station_id"], how="left")
    out = out.merge(unc, on=["time", "station_id"], how="left")
    out = out.merge(sc, on=["time", "station_id"], how="left")
    out = out.merge(tr, on=["time", "station_id"], how="left")
    out = out.merge(gh, on=["time", "station_id"], how="left")

    out["is_imputed"] = out["observed_value"].isna() & out["value"].notna()
    out["impute_run_id"] = run_id

    names = p_df[["station_id", "station_name"]].drop_duplicates()
    out = out.merge(names, on="station_id", how="left")

    missing = out[out["value"].isna()].copy()
    if len(missing):
        missing["missing_reason"] = "no_observation_and_no_reliable_fallback"

    summary = (
        out[out["value"].notna()]
        .groupby(["parameter", "impute_method", "impute_tier", "is_imputed"], observed=True)
        .size()
        .rename("rows")
        .reset_index()
    )

    return out, missing, summary


def write_report(
    derived: pd.DataFrame,
    missing: pd.DataFrame,
    summary: pd.DataFrame,
    policy_df: pd.DataFrame,
    run_id: str,
) -> None:
    lines: list[str] = []
    lines.append("# Station Gapfill Derived Layer Build")
    lines.append("")
    lines.append(f"Run ID: {run_id}")
    lines.append("")
    lines.append("## Inputs")
    lines.append("")
    lines.append("- Raw station files were read-only.")
    lines.append("- Gapfill policy from evaluator was applied per pollutant.")
    lines.append("")

    lines.append("## Output Counts")
    lines.append("")
    lines.append(f"- Derived rows (including observed + imputed + unresolved): {len(derived)}")
    lines.append(f"- Missing unresolved rows: {len(missing)}")
    lines.append(f"- Materialized rows (value not null): {int(derived['value'].notna().sum())}")
    lines.append(f"- Imputed rows: {int(derived['is_imputed'].sum())}")
    lines.append("")

    lines.append("## Method Mix")
    lines.append("")
    lines.append("| Pollutant | Method | Tier | Is Imputed | Rows |")
    lines.append("|---|---|---|---|---:|")
    for r in summary.sort_values(["parameter", "impute_method", "impute_tier", "is_imputed"]).itertuples(index=False):
        lines.append(
            f"| {r.parameter} | {r.impute_method} | {r.impute_tier} | {bool(r.is_imputed)} | {int(r.rows)} |"
        )

    lines.append("")
    lines.append("## Policy Snapshot")
    lines.append("")
    lines.append("| Pollutant | Primary Method | Fallback Method | P90 Abs Error |")
    lines.append("|---|---|---|---:|")
    for r in policy_df.sort_values("pollutant").itertuples(index=False):
        lines.append(
            f"| {r.pollutant} | {r.primary_method} | {r.fallback_method} | {float(r.primary_p90_abs_error):.4f} |"
        )

    BUILD_REPORT_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pollutants", type=str, default=",".join(DEFAULT_POLLUTANTS))
    parser.add_argument(
        "--use-spatial-idw",
        action="store_true",
        help="Enable spatial IDW fallback for unresolved values (slower).",
    )
    args = parser.parse_args()

    pollutants = [p.strip() for p in args.pollutants.split(",") if p.strip()]
    if not pollutants:
        raise ValueError("At least one pollutant must be provided.")

    policy_map = load_policy()
    policy_df = pd.read_parquet(POLICY_PATH)
    meta = pd.read_parquet(META_PATH)
    need = {"id", "lat", "lon"}
    if not need.issubset(meta.columns):
        raise ValueError(f"meta.parquet must contain columns {sorted(need)}")

    long_df = load_station_long(pollutants)
    run_id = datetime.now().strftime("gapfill_%Y%m%d_%H%M%S")

    all_derived: list[pd.DataFrame] = []
    all_missing: list[pd.DataFrame] = []
    all_summary: list[pd.DataFrame] = []

    for pollutant in pollutants:
        if pollutant not in policy_map:
            continue
        d, m, s = build_for_pollutant(
            long_df=long_df,
            pollutant=pollutant,
            meta=meta,
            policy=policy_map[pollutant],
            run_id=run_id,
            use_spatial_idw=args.use_spatial_idw,
        )
        if not d.empty:
            all_derived.append(d)
        if not m.empty:
            all_missing.append(m)
        if not s.empty:
            all_summary.append(s)

    if not all_derived:
        raise RuntimeError("No derived rows produced.")

    derived_df = pd.concat(all_derived, ignore_index=True)
    missing_df = pd.concat(all_missing, ignore_index=True) if all_missing else pd.DataFrame()
    summary_df = (
        pd.concat(all_summary, ignore_index=True)
        .groupby(["parameter", "impute_method", "impute_tier", "is_imputed"], observed=True, as_index=False)["rows"]
        .sum()
    ) if all_summary else pd.DataFrame()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    derived_df.to_parquet(DERIVED_OUT, index=False)
    missing_df.to_parquet(MISSING_OUT, index=False)
    summary_df.to_parquet(SUMMARY_OUT, index=False)
    write_report(
        derived=derived_df,
        missing=missing_df,
        summary=summary_df,
        policy_df=policy_df,
        run_id=run_id,
    )

    print("Derived gapfill build complete")
    print(f"Derived : {DERIVED_OUT}")
    print(f"Missing : {MISSING_OUT}")
    print(f"Summary : {SUMMARY_OUT}")
    print(f"Report  : {BUILD_REPORT_OUT}")


if __name__ == "__main__":
    main()
