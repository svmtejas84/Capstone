"""Validation-only verification, followed by one-time exposed-test scoring."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np
import torch

from src.stpignn.evaluation import evaluate_arrays
from final_blr_results.controlled_validation_v3.scripts.smoke_gpu import CutoffContext, ARR, FIT, V3
from final_blr_results.controlled_validation_v3.scripts.train_controls import BASE_CFG, HORIZONS, SEEDS, hash_file, atomic_json
from final_blr_results.controlled_validation_v4_review_closure.scripts.train_sensitivity import V4
from final_blr_results.controlled_validation_v5.scripts.train_graph_lag import V5, ExperimentalContext, VARIANTS as GL_VARIANTS, CROSS_VARIANTS
from final_blr_results.controlled_validation_v5.scripts.train_fairness import FAMILIES

EXPECTED = "bd08d733f924387da82e758d1060703dfcdd121f360b7e8765189d8b7446e202"
HISTORICAL = {
    "true_wind": {0.06: (V3, "true_wind"), 0.3: (V4, "true_wind_03"), 1.0: (V4, "true_wind_10")},
    "within_month_shuffle": {0.06: (V3, "shuffled_wind")},
    "full_shuffle": {0.06: (V4, "full_shuffle_006")},
    "reverse_wind": {0.06: (V4, "reverse_wind_006")},
    "constant_north": {0.06: (V4, "constant_north_006")},
    "laplacian": {0.06: (V3, "laplacian")},
}


def cell_path(family, strength, seed):
    if strength in HISTORICAL[family]:
        root, name = HISTORICAL[family][strength]
        return root / "training/final" / f"h6_seed{seed}_{name}", root, name
    name = f"{family}_lambda{strength:g}"
    return V5 / "training/fairness" / f"h6_seed{seed}_{name}", V5, name


def verify_cell(cell, h, seed, variant=None):
    rec = json.loads((cell / "COMPLETE.json").read_text())
    ckpt = cell / "best.pt"
    assert rec["array_sha256"] == EXPECTED
    assert int(rec["horizon_hours"]) == h and int(rec["seed"]) == seed
    assert 10 <= int(rec["best_epoch"]) <= int(rec["epochs_run"]) <= 30
    assert abs(float(rec["validation_mae"])) < 1e6
    assert hash_file(ckpt) == rec["checkpoint_sha256"]
    if variant is not None: assert rec["variant"] == variant
    payload = torch.load(ckpt, map_location="cpu", weights_only=False)
    assert payload["array_sha256"] == EXPECTED
    assert payload["seed"] == seed and payload["horizon"] == h
    assert all(bool(torch.isfinite(v).all()) for v in payload["state_dict"].values())
    return rec


def verify():
    assert hash_file(ARR) == EXPECTED
    for stage in ("graph", "lag", "cross", "fairness"):
        assert (V5 / "training" / f"{stage}_COMPLETE").exists(), stage
        assert (V5 / "logs" / stage / "COMPLETE").exists(), stage
    count = 0
    for h in HORIZONS:
        for variant in GL_VARIANTS:
            for seed in SEEDS:
                cell = V5 / "training" / variant / f"h{h}_seed{seed}"
                rec = verify_cell(cell, h, seed, variant)
                assert rec["learning_rate"] == {1:.001,3:.0003,6:.0003,12:.0003,24:.0003}[h]
                count += 1
    assert count == 100
    for variant in CROSS_VARIANTS:
        for seed in SEEDS:
            verify_cell(V5 / "training" / variant / f"h6_seed{seed}", 6, seed, variant)
    count += 10
    rows=[]
    for family in HISTORICAL:
        for strength in (.06, .3, 1.):
            vals=[]
            for seed in SEEDS:
                cell, root, name = cell_path(family, strength, seed)
                rec = verify_cell(cell, 6, seed, name)
                assert abs(float(rec["learning_rate"])-.0003)<1e-12
                vals.append(float(rec["validation_mae"]))
            rows.append(dict(family=family,lambda_max=strength,mean_five_seed_validation_mae=float(np.mean(vals)),
                             sd_five_seed_validation_mae=float(np.std(vals,ddof=1)),seeds=5,
                             training_sources="V3/V4 frozen" if strength in HISTORICAL[family] else "new V5"))
    assert len(rows)==18
    chosen={}
    for family in HISTORICAL:
        pool=[r for r in rows if r["family"]==family]
        best=min(pool,key=lambda r:(r["mean_five_seed_validation_mae"],r["lambda_max"]))
        chosen[family]=best["lambda_max"]
    p=V5/"metrics/FAIRNESS_GRID_VALIDATION.csv";p.parent.mkdir(exist_ok=True)
    with p.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    atomic_json(V5/"metrics/FAIRNESS_VALIDATION_SELECTION.json",chosen)
    atomic_json(V5/"verification/training_verified.json",dict(status="PASS",new_cells=count+50,
        graph_lag_cross_cells=count,fairness_new_cells=50,fairness_grid_cells=90,array_sha256=EXPECTED,selected=chosen))
    print(json.dumps(dict(status="PASS",new_cells=count+50,selected=chosen),indent=2))


def save_npz_once(path, **arrays):
    if path.exists():
        with np.load(path) as z:
            for k, a in arrays.items(): assert np.array_equal(z[k], a, equal_nan=True)
        return
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_name(path.stem+".tmp.npz")
    np.savez_compressed(tmp,**arrays)
    tmp.replace(path)


def evaluate_cell(ctx, cell, h, seed, variant):
    rec=verify_cell(cell,h,seed,variant)
    payload=torch.load(cell/"best.pt",map_location="cpu",weights_only=False)
    model=ctx.make("stpignn_lambda0")
    model.load_state_dict(payload["state_dict"],strict=True)
    result=ctx.evaluate(model,"stpignn_lambda0","test",collect=True)
    return result,rec


def score():
    assert (V5/"verification/training_verified.json").exists()
    assert not (V5/"metrics/NEW_TEST_SCORES.csv").exists(), "one-time test score guard"
    ref={}
    for h in HORIZONS:
        with np.load(V3/"predictions"/f"h{h}_zero_ensemble.npz") as z:
            ref[h]={k:z[k] for k in ("truth","time_index","station_index")}
    atomic_json(V5/"verification/test_unlock.json",dict(status="EXPLORATORY",reason="all frozen validation-selected cells verified",
        array_sha256=EXPECTED,previously_exposed_test=True))
    rows=[]

    def append_score(h,variant,seed,result,sha):
        for k in ref[h]: assert np.array_equal(result[k],ref[h][k])
        assert len(result["pred"])==14583 and np.isfinite(result["pred"]).all()
        met=evaluate_arrays(result["pred"],result["truth"],np.ones(len(result["pred"]),bool))
        rows.append(dict(horizon_hours=h,variant=variant,seed=seed,mae=met["mae"],rmse=met["rmse"],
                         r2=met["r2"],scored_pairs=met["n"],checkpoint_sha256=sha,
                         test_status="exposed exploratory"))

    for h in HORIZONS:
        for variant in GL_VARIANTS:
            ctx=ExperimentalContext(h,variant)
            preds=[]
            for seed in SEEDS:
                cell=V5/"training"/variant/f"h{h}_seed{seed}"
                result,rec=evaluate_cell(ctx,cell,h,seed,variant)
                save_npz_once(V5/"predictions"/f"h{h}_{variant}_seed{seed}.npz",
                              **{k:result[k] for k in ("pred","truth","time_index","station_index")})
                append_score(h,variant,seed,result,rec["checkpoint_sha256"])
                preds.append(result["pred"])
            ensemble=dict(pred=np.mean(np.stack(preds),axis=0),**ref[h])
            save_npz_once(V5/"predictions"/f"h{h}_{variant}_ensemble.npz",**ensemble)
            append_score(h,variant,"ensemble",ensemble,"")
    for variant in CROSS_VARIANTS:
        ctx=ExperimentalContext(6,variant)
        preds=[]
        for seed in SEEDS:
            cell=V5/"training"/variant/f"h6_seed{seed}"
            result,rec=evaluate_cell(ctx,cell,6,seed,variant)
            save_npz_once(V5/"predictions"/f"h6_{variant}_seed{seed}.npz",
                          **{k:result[k] for k in ("pred","truth","time_index","station_index")})
            append_score(6,variant,seed,result,rec["checkpoint_sha256"])
            preds.append(result["pred"])
        ensemble=dict(pred=np.mean(np.stack(preds),axis=0),**ref[6])
        save_npz_once(V5/"predictions"/f"h6_{variant}_ensemble.npz",**ensemble)
        append_score(6,variant,"ensemble",ensemble,"")
    ctx=CutoffContext(6,BASE_CFG,ARR,FIT)
    for family in HISTORICAL:
        for strength in (.06,.3,1.):
            variant=f"{family}_lambda{strength:g}"
            preds=[]
            for seed in SEEDS:
                cell,root,name=cell_path(family,strength,seed)
                if root!=V5:
                    with np.load(root/"predictions"/f"h6_{name}_seed{seed}.npz") as z:
                        result={k:z[k] for k in ("pred","truth","time_index","station_index")}
                    rec=verify_cell(cell,6,seed,name)
                else:
                    result,rec=evaluate_cell(ctx,cell,6,seed,name)
                    save_npz_once(V5/"predictions"/f"h6_{name}_seed{seed}.npz",
                                  **{k:result[k] for k in ("pred","truth","time_index","station_index")})
                append_score(6,variant,seed,result,rec["checkpoint_sha256"])
                preds.append(result["pred"])
            ensemble=dict(pred=np.mean(np.stack(preds),axis=0),**ref[6])
            if strength not in HISTORICAL[family]:
                save_npz_once(V5/"predictions"/f"h6_{family}_lambda{strength:g}_ensemble.npz",**ensemble)
            append_score(6,variant,"ensemble",ensemble,"")
    p=V5/"metrics/NEW_TEST_SCORES.csv";p.parent.mkdir(exist_ok=True)
    tmp=p.with_suffix(".tmp")
    with tmp.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    tmp.replace(p)
    print(json.dumps(dict(score_rows=len(rows),graph_lag_cross_conditions=22,fairness_grid_conditions=18,
                          test_population=14583,truth_status="historically exposed")),flush=True)


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--stage",choices=["verify","score"],required=True);a=p.parse_args()
    if a.stage=="verify":verify()
    else:score()
