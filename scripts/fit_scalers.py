"""Offline utility to fit per-zone linear scalers from CSV data.

CSV columns: zone_id,raw_pred,obs,timestamp

Writes JSON of scalers to stdout or optionally to a Redis instance.
"""
from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from statistics import mean
from typing import Dict, List, Tuple

try:
    import numpy as np
except Exception:
    np = None


def fit_linear(xs: List[float], ys: List[float]) -> Tuple[float, float]:
    if not xs:
        return 1.0, 0.0
    if np is None:
        # simple least-squares using normal equations without numpy
        n = len(xs)
        mx = sum(xs) / n
        my = sum(ys) / n
        num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
        den = sum((x - mx) ** 2 for x in xs)
        if den == 0:
            return 1.0, my - mx
        a = num / den
        b = my - a * mx
        return float(a), float(b)
    else:
        A = np.vstack([xs, np.ones(len(xs))]).T
        a, b = np.linalg.lstsq(A, ys, rcond=None)[0]
        return float(a), float(b)


def main(csv_path: str):
    groups: Dict[str, List[Tuple[float, float]]] = defaultdict(list)
    with open(csv_path, newline="") as fh:
        rdr = csv.DictReader(fh)
        for row in rdr:
            zid = row.get("zone_id") or row.get("edge_id") or "global"
            try:
                raw = float(row.get("raw_pred", row.get("raw", 0.0)))
                obs = float(row.get("obs", row.get("observation", 0.0)))
            except Exception:
                continue
            groups[zid].append((raw, obs))

    out = {}
    for zid, pairs in groups.items():
        xs = [p[0] for p in pairs]
        ys = [p[1] for p in pairs]
        a, b = fit_linear(xs, ys)
        out[zid] = {"a": a, "b": b, "n": len(xs), "mean_raw": mean(xs) if xs else None, "mean_obs": mean(ys) if ys else None}

    sys.stdout.write(json.dumps(out, indent=2))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python scripts/fit_scalers.py data.csv")
        sys.exit(2)
    main(sys.argv[1])
