"""Read-only paired architectural audit of the saved corrected-weather predictions."""
import csv
import glob
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
PAIRS = [("stpignn_original", name) for name in
         ("vanilla_gcn", "gru_only", "st_gru_gcn", "stpignn_lambda0", "stpignn_laplacian")]
PAIRS += [("gine_gru_wind", name) for name in ("gru_only", "st_gru_gcn")]
SEEDS = {11, 23, 37, 51, 79}


def load(horizon, model):
    paths = sorted(glob.glob(str(ROOT / f"results/benchmark_predictions_h{horizon}_{model}_seed*_v2j.parquet")))
    if not paths:
        return None, "no saved predictions"
    frames = [pd.read_parquet(path) for path in paths]
    seeds = {int(frame.seed.iloc[0]) for frame in frames}
    if seeds != SEEDS:
        return None, f"incomplete seeds: {sorted(seeds)}"
    data = pd.concat(frames, ignore_index=True)
    key = ["target_time_utc", "station_id"]
    if data.duplicated(key + ["seed"]).any() or data.groupby(key).seed.nunique().min() != 5:
        return None, "duplicate or incomplete seed pairs"
    grouped = data.groupby(key, as_index=False).agg(y=("target_ug_m3", "first"),
                                                       pred=("prediction_ug_m3", "mean"),
                                                       y_unique=("target_ug_m3", "nunique"))
    if grouped.y_unique.max() != 1:
        return None, "target differs between seeds"
    return grouped.set_index(key).sort_index(), None


def metrics(y, pred):
    error = pred-y
    return float(np.abs(error).mean()), float(np.sqrt(np.square(error).mean())), float(1-np.square(error).sum()/np.square(y-y.mean()).sum())


def main():
    rows = []
    for horizon in (1, 3, 6, 12, 24):
        cache = {name: load(horizon, name) for name in set(sum(([a,b] for a,b in PAIRS), []))}
        for first, baseline in PAIRS:
            a, err_a = cache[first]; b, err_b = cache[baseline]
            base = {"horizon_hours": horizon, "model": first, "baseline": baseline,
                    "difference_definition": "MAE(model)-MAE(baseline)", "seed_aggregation": "mean prediction across 5 fixed seeds"}
            if err_a or err_b:
                rows.append({**base, "status": "UNVERIFIABLE", "reason": err_a or err_b}); continue
            if not a.index.equals(b.index) or not np.array_equal(a.y.to_numpy(), b.y.to_numpy()):
                rows.append({**base, "status": "UNVERIFIABLE", "reason": "prediction keys or targets differ"}); continue
            y = a.y.to_numpy(dtype=float); pa = a.pred.to_numpy(dtype=float); pb = b.pred.to_numpy(dtype=float)
            days, day_idx = np.unique(pd.to_datetime(a.index.get_level_values(0), utc=True).date, return_inverse=True)
            counts = np.bincount(day_idx); day_diff = np.bincount(day_idx, weights=np.abs(pa-y)-np.abs(pb-y))
            rng = np.random.default_rng(4303+horizon*100+len(rows))
            samples = rng.integers(0, len(days), size=(2000, len(days)))
            boot = day_diff[samples].sum(1)/counts[samples].sum(1)
            observed = float(day_diff.sum()/counts.sum())
            flips = rng.choice((-1,1), size=(2000,len(days)))
            null = (flips*day_diff).sum(1)/counts.sum()
            p = float((1+np.count_nonzero(np.abs(null)>=abs(observed)))/2001)
            m_a = metrics(y,pa); m_b = metrics(y,pb)
            rows.append({**base,"status":"VERIFIED","reason":"", "evaluation_pairs":len(y),
                         "utc_days":len(days),"seeds": "11,23,37,51,79", "model_mae":m_a[0],"model_rmse":m_a[1],
                         "model_r2":m_a[2],"baseline_mae":m_b[0],"baseline_rmse":m_b[1],"baseline_r2":m_b[2],
                         "paired_mae_difference":observed,"nominal_ci_low":np.quantile(boot,.025),
                         "nominal_ci_high":np.quantile(boot,.975),"nominal_ci_excludes_zero":bool(np.quantile(boot,.975)<0 or np.quantile(boot,.025)>0),
                         "sign_flip_p_two_sided":p})
    valid = sorted((i for i,r in enumerate(rows) if r["status"]=="VERIFIED"),key=lambda i:rows[i]["sign_flip_p_two_sided"])
    maximum=0.0; family=len(valid)
    for rank,i in enumerate(valid):
        maximum=max(maximum,min(1.0,(family-rank)*rows[i]["sign_flip_p_two_sided"]))
        rows[i]["holm_adjusted_p"] = maximum
        rows[i]["holm_reject_0_05"] = maximum<.05
        rows[i]["holm_family"] = "all 7 architecture pairs x 5 horizons (35 tests)"
    columns=list(dict.fromkeys(key for row in rows for key in row))
    with (OUT/"paired_architecture_comparisons.csv").open("w",newline="") as stream:
        writer=csv.DictWriter(stream,fieldnames=columns);writer.writeheader();writer.writerows(rows)
    print(len(rows), "comparisons; verified", len(valid), "Holm rejects",sum(r.get("holm_reject_0_05",False) for r in rows))


if __name__ == "__main__": main()
