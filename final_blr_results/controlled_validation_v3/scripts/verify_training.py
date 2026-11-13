"""Check every frozen training cell and saved checkpoint without reading test labels."""
import csv
import json
from pathlib import Path
from final_blr_results.controlled_validation_v3.scripts.train_controls import (
    V3,ARR,HORIZONS,SEEDS,VARIANTS,LRS,hash_file)


def verify_cell(path,variant,h,seed,lr):
    meta=json.loads((path/"COMPLETE.json").read_text())
    assert meta["variant"]==variant and meta["horizon_hours"]==h and meta["seed"]==seed
    assert meta["learning_rate"]==lr and meta["array_sha256"]==hash_file(ARR)
    assert meta["checkpoint_sha256"]==hash_file(path/"best.pt")
    epochs=json.loads((path/"epochs.json").read_text())
    assert len(epochs)==meta["epochs_run"] and meta["best_epoch"]>=10
    assert meta["best_epoch"]<=meta["epochs_run"]<=30
    expected=0. if variant=="zero" else .06*min(1.,meta["best_epoch"]/5.)
    assert abs(meta["effective_lambda_at_best"]-expected)<1e-12
    assert all(x["batches"]>0 and 0<=x["zero_arc_batches"]<=x["batches"] for x in epochs)
    return meta


def main():
    root=V3/"training"
    rows=[]
    for h in HORIZONS:
        selection=[]
        for lr in LRS:
            selection.append(verify_cell(root/"selection"/f"h{h}_lr{lr:g}","zero",h,11,lr))
        chosen=min(selection,key=lambda r:(r["validation_mae"],r["learning_rate"]))["learning_rate"]
        for s in SEEDS:
            for v in VARIANTS:
                rec=verify_cell(root/"final"/f"h{h}_seed{s}_{v}",v,h,s,chosen)
                rows.append(rec)
    assert len(rows)==125
    out=V3/"verification/training_integrity.csv";out.parent.mkdir(exist_ok=True)
    with out.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    print("Verified 20 selection + 125 final control cells, hashes, epochs and matched LR")


if __name__=="__main__":main()
