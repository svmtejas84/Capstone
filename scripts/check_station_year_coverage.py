"""
Check which station years are present in data/processed/stations.

This is a lightweight guard for downstream jobs that expect specific years.

Usage:
    python scripts/check_station_year_coverage.py
    python scripts/check_station_year_coverage.py --require-year 2023
    python scripts/check_station_year_coverage.py --root data/processed/stations --require-year 2022 --require-year 2024
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def _extract_years(path: Path) -> set[int]:
    df = pd.read_parquet(path)
    if "time" in df.columns:
        ts = pd.to_datetime(df["time"], errors="coerce")
    else:
        ts = pd.to_datetime(df.index, errors="coerce")
    ts = ts.dropna()
    if ts.empty:
        return set()
    return set(ts.dt.year.astype(int).tolist())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="data/processed/stations", help="Folder containing year-split station parquet files")
    parser.add_argument(
        "--require-year",
        type=int,
        action="append",
        default=[],
        help="Require that the given year exists in at least one station parquet file; repeatable.",
    )
    args = parser.parse_args()

    root = Path(args.root)
    files = sorted(root.glob("*.parquet"))
    if not files:
        print(f"ERROR: no parquet files found under {root}")
        return 1

    present_years: set[int] = set()
    file_years: dict[str, list[int]] = {}
    for path in files:
        years = sorted(_extract_years(path))
        file_years[path.name] = years
        present_years.update(years)

    print("=== Station Year Coverage ===")
    for name, years in file_years.items():
        print(f" - {name}: {years if years else 'empty'}")

    missing_required = [year for year in args.require_year if year not in present_years]
    if missing_required:
        print("\nFAIL: required station years are missing")
        for year in missing_required:
            print(f" - {year}")
        return 1

    if 2023 not in present_years:
        print("\nNOTE: 2023 station observations are absent; this is expected in the current source data.")

    print("\nSTATUS: PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
