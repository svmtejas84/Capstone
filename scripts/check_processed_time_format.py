"""
Validate time format consistency across processed Parquet files.

Guardrails enforced:
- All physical timestamp/date columns in data/processed must share one dtype.
- Timestamp columns must be timezone-naive (no embedded tz in parquet schema).
- String-like time/date columns must be parseable (sampled check).

Exit code:
- 0 on success
- 1 on any detected inconsistency

Usage:
    python scripts/check_processed_time_format.py
    python scripts/check_processed_time_format.py --root data/processed
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq
from pandas.api.types import is_string_dtype

TIME_NAME_RE = re.compile(r"(time|date|timestamp|datetime|hour|minute|second|dt)", re.IGNORECASE)


def _is_time_like_column(name: str) -> bool:
    return bool(TIME_NAME_RE.search(name))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="data/processed", help="Root directory containing processed parquet files")
    parser.add_argument(
        "--sample-rows",
        type=int,
        default=5000,
        help="Rows sampled per file for string parseability checks",
    )
    args = parser.parse_args()

    root = Path(args.root)
    parquet_files = sorted(root.rglob("*.parquet"))

    if not parquet_files:
        print(f"ERROR: no parquet files found under {root}")
        return 1

    physical_time_types: set[str] = set()
    tz_aware_columns: list[tuple[str, str, str]] = []
    string_parse_failures: list[tuple[str, str, float]] = []

    for file_path in parquet_files:
        table = pq.read_table(file_path)
        schema = table.schema
        sample_df = (
            table.slice(0, min(table.num_rows, args.sample_rows)).to_pandas()
            if table.num_rows
            else pd.DataFrame()
        )

        for field in schema:
            col_name = field.name
            if not _is_time_like_column(col_name):
                continue

            dtype = str(field.type)
            if dtype.startswith("timestamp") or dtype.startswith("date"):
                physical_time_types.add(dtype)
                if "tz=" in dtype:
                    tz_aware_columns.append((str(file_path), col_name, dtype))

            if col_name in sample_df.columns and is_string_dtype(sample_df[col_name]):
                vals = sample_df[col_name].dropna().astype(str).str.strip()
                vals = vals[vals != ""]
                if len(vals):
                    parsed = pd.to_datetime(vals, errors="coerce", utc=True)
                    ratio = float(parsed.notna().mean())
                    if ratio < 1.0:
                        string_parse_failures.append((str(file_path), col_name, ratio))

    print("=== Processed Time Format Guard ===")
    print(f"Parquet files scanned: {len(parquet_files)}")

    if physical_time_types:
        print("Physical time dtypes observed:")
        for dt in sorted(physical_time_types):
            print(f" - {dt}")
    else:
        print("Physical time dtypes observed: (none)")

    failed = False

    if len(physical_time_types) > 1:
        failed = True
        print("\nFAIL: multiple physical time dtypes detected")

    if tz_aware_columns:
        failed = True
        print("\nFAIL: timezone-aware parquet timestamp columns detected")
        for file_path, col_name, dtype in tz_aware_columns:
            print(f" - {file_path} :: {col_name}[{dtype}]")

    if string_parse_failures:
        failed = True
        print("\nFAIL: unparseable string time/date values detected")
        for file_path, col_name, ratio in string_parse_failures:
            print(f" - {file_path} :: {col_name} parse_success_ratio={ratio:.3f}")

    if failed:
        print("\nSTATUS: FAILED")
        return 1

    print("\nSTATUS: PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
