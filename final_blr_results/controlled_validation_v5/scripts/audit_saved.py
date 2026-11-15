"""Read frozen V3/V4 predictions; write V5 descriptive evidence only."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from src.stpignn.station_graph import directed_knn_graph

ROOT = Path(__file__).resolve().parents[3]
V3 = ROOT / "final_blr_results/controlled_validation_v3"
V4 = ROOT / "final_blr_results/controlled_validation_v4_review_closure"
V5 = ROOT / "final_blr_results/controlled_validation_v5"
ARRAY = V3 / "data_manifests/data_v3_causal_arrays.npz"
EXPECTED = "bd08d733f924387da82e758d1060703dfcdd121f360b7e8765189d8b7446e202"
H = (1, 3, 6, 12, 24)
V3_METHODS = ("persistence", "same_hour_yesterday", "station_train_mean",
              "climatology_hod_dow", "weather_ridge", "gru_only", "vanilla_gcn",
              "st_gru_gcn", "adaptive_graph_st", "mlp", "tcn", "zero",
              "true_wind", "shuffled_wind", "rotated_wind", "laplacian")
V4_METHODS = ("reverse_wind_006", "constant_north_006", "full_shuffle_006",
              "true_wind_03", "true_wind_10", "laplacian_matched")
DETERMINISTIC = set(V3_METHODS[:5])
BUCKETS = (("1h", lambda a: a == 1),
           ("2-3h", lambda a: (a >= 2) & (a <= 3)),
           ("4-6h", lambda a: (a >= 4) & (a <= 6)),
           ("7-12h", lambda a: (a >= 7) & (a <= 12)),
           ("13-24h", lambda a: (a >= 13) & (a <= 24)),
           (">24h", lambda a: a > 24),
           ("no_observed_anchor", lambda a: a < 0))


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for part in iter(lambda: f.read(4 * 1024 * 1024), b""):
            h.update(part)
    return h.hexdigest()


def load(h, method, seed=None):
    root = V4 if method in V4_METHODS else V3
    suffix = "" if method in DETERMINISTIC else ("_ensemble" if seed is None else f"_seed{seed}")
    path = root / "predictions" / f"h{h}_{method}{suffix}.npz"
    with np.load(path) as z:
        data = {k: z[k] for k in ("pred", "truth", "time_index", "station_index")}
    return data, path


def aligned(a, b):
    for key in ("truth", "time_index", "station_index"):
        if not np.array_equal(a[key], b[key]):
            raise AssertionError(("different evaluation population", key))


def save(rows, name):
    path = V5 / name
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(path, index=False, float_format="%.12g")
    return path


def main():
    assert sha(ARRAY) == EXPECTED
    arr = np.load(ARRAY)
    obs = arr["observed_mask"]
    last = np.maximum.accumulate(np.where(obs, np.arange(len(obs))[:, None], -1), axis=0)
    reference = {}
    ages = []
    for h in H:
        ref, _ = load(h, "zero")
        reference[h] = ref
        issue = ref["time_index"] - h
        station = ref["station_index"]
        prev = np.where(issue > 0, last[np.maximum(issue - 1, 0), station], -1)
        age = np.where(prev >= 0, issue - prev, -1)
        assert np.all((age == -1) | (age >= 1))
        methods = V3_METHODS + (V4_METHODS if h == 6 else ())
        for method in methods:
            p, path = load(h, method)
            aligned(ref, p)
            err = p["pred"] - p["truth"]
            for label, predicate in BUCKETS:
                mask = predicate(age)
                if not mask.any():
                    continue
                ages.append(dict(method=method, horizon_hours=h, anchor_age_bucket=label,
                                 anchor_age_definition="issue minus latest genuinely observed PM2.5 row strictly before issue; no prior observation is fallback",
                                 scored_pairs=int(mask.sum()), fraction_of_scored_pairs=float(mask.mean()),
                                 mae_ug_m3=float(np.mean(np.abs(err[mask]))),
                                 rmse_ug_m3=float(np.sqrt(np.mean(err[mask] ** 2))),
                                 prediction_path=str(path.relative_to(ROOT)),
                                 evaluation="exposed Bengaluru test; descriptive"))
    save(ages, "ANCHOR_AGE_ALL_METHODS.csv")

    # Preserve the frozen V3 20-member and later exploratory V4 6-member families.
    a = pd.read_csv(V4 / "COMPLETE_20_CONTRAST_RESULTS.csv")
    b = pd.read_csv(V4 / "statistical_analysis/V4_SIX_CONTRASTS.csv")
    assert len(a) == 20 and len(b) == 6
    a["family"] = "V3 frozen 20"; b["family"] = "V4 later exploratory 6"
    assert set(a.columns) - {"holm_20_p", "family"} == set(b.columns) - {"holm_6_p", "family"}
    save(pd.concat((a, b), ignore_index=True), "COMPLETE_CONTRAST_REGISTER.csv")
    seeds_a = pd.read_csv(V4 / "SEED_LEVEL_REGULARIZATION_RESULTS.csv")
    seeds_b = pd.read_csv(V4 / "statistical_analysis/V4_SEED_CONTRASTS.csv")
    seeds_a["family"] = "V3 frozen 20"; seeds_b["family"] = "V4 later exploratory 6"
    save(pd.concat((seeds_a, seeds_b), ignore_index=True), "SEED_LEVEL_COMPARISONS.csv")

    # One common actual-wind diagnostic, based only on saved scored predictions.
    edge, _ = directed_knn_graph(arr["coordinates"], 4)
    src, dst = edge.numpy()
    xy = arr["coordinates"]
    bearing = np.arctan2((xy[dst] - xy[src])[:, 0], (xy[dst] - xy[src])[:, 1])
    towards = np.deg2rad((arr["raw_wind_degrees"].astype(float) + 180) % 360)
    angle = np.abs(np.angle(np.exp(1j * (towards[:, None] - bearing[None, :]))))
    windmask = np.isfinite(towards[:, None]) & (angle <= np.deg2rad(37.5))
    scale = float(json.loads((ROOT / "results/data_v2j_fit.json").read_text())["fit"]["target_standard_std"])
    grad = pd.read_csv(V4 / "PENALTY_GRADIENT_REPLAY.csv")
    diagnostics = []
    for h in H:
        for method in (V3_METHODS[11:] + (V4_METHODS if h == 6 else ())):
            p, path = load(h, method)
            hours, inverse = np.unique(p["time_index"], return_inverse=True)
            pred = np.full((len(hours), len(xy)), np.nan)
            pred[inverse, p["station_index"]] = p["pred"]
            eligible = windmask[hours - h] & np.isfinite(pred[:, src]) & np.isfinite(pred[:, dst])
            diff = (pred[:, dst] - pred[:, src]) / scale
            positive = np.maximum(diff, 0)
            n = int(eligible.sum())
            viol = int(np.count_nonzero((diff > .05) & eligible))
            row = dict(method=method, horizon_hours=h,
                       eligible_directed_arcs=n, observed_endpoint_definition="both endpoint predictions scored against observed target at same target hour",
                       actual_wind_mask="wind at issue; bearing source to destination; +/-37.5 deg cone",
                       threshold_normalized=.05, threshold_ug_m3=.05 * scale,
                       violations=viol, violation_frequency=viol / n if n else np.nan,
                       mean_squared_positive_ordering_difference_normalized=float(np.mean(positive[eligible] ** 2)) if n else np.nan,
                       raw_penalty="NOT MEASURED: training penalty uses all predicted nodes; diagnostic denominator differs",
                       weighted_penalty="NOT MEASURED: see checkpoint-local first-batch replay where available",
                       gradient_ratio="NOT MEASURED: see checkpoint-local first-batch replay where available",
                       prediction_path=str(path.relative_to(ROOT)))
            replay = grad[(grad.horizon_hours == h) & (grad.variant == method)]
            if len(replay) == 1:
                r = replay.iloc[0]
                row.update(raw_penalty=float(r.raw_regularization_loss), weighted_penalty=float(r.weighted_regularization_loss),
                           gradient_ratio=float(r.gradient_ratio), gradient_replay_scope="seed11 selected checkpoint, first train batch; distinct from exposed-test diagnostic")
            diagnostics.append(row)
    save(diagnostics, "PENALTY_DIAGNOSTICS_COMPLETE.csv")
    d = pd.DataFrame(diagnostics)
    for method, expected_freq, expected_sq in (("true_wind", .249785, .2383), ("zero", .246003, .2934)):
        r = d[(d.horizon_hours == 6) & (d.method == method)].iloc[0]
        assert abs(r.violation_frequency - expected_freq) < 1e-5
        assert abs(r.mean_squared_positive_ordering_difference_normalized - expected_sq) < 1e-3
    output = dict(array_sha256=EXPECTED, methods=16, anchor_rows=len(ages), original_contrasts=len(a),
                  additional_contrasts=len(b), seed_rows=len(seeds_a) + len(seeds_b), diagnostic_rows=len(diagnostics),
                  h6_fresh_anchor_pairs=int(pd.DataFrame(ages).query("horizon_hours == 6 and method == 'zero' and anchor_age_bucket == '1h'").scored_pairs.iloc[0]))
    (V5 / "verification").mkdir(exist_ok=True)
    (V5 / "verification/saved_audit_summary.json").write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
