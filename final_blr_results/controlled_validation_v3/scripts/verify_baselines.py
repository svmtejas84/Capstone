"""Verify baseline cell identity, hashes, epochs, and validation selection."""
import csv
import json
import sys
from final_blr_results.controlled_validation_v3.scripts.train_controls import V3,ARR,HORIZONS,SEEDS,LRS,hash_file
from final_blr_results.controlled_validation_v3.scripts.train_baselines import MODELS

def check(path,name,h,s,lr):
    r=json.loads((path/"COMPLETE.json").read_text())
    ident=json.loads((path/"model_identity.json").read_text())
    assert ident["model"]==name and ident["horizon"]==h and ident["seed"]==s
    assert r["seed"]==s and r["horizon_hours"]==h and r["learning_rate"]==lr
    assert r["array_sha256"]==hash_file(ARR)
    assert r["checkpoint_sha256"]==hash_file(path/"best.pt")
    hist=json.loads((path/"epochs.json").read_text())
    assert len(hist)==r["epochs_run"] and 10<=r["best_epoch"]<=r["epochs_run"]<=30
    return r

def main(stage):
    root=V3/"training/baselines"
    assert (root/f"{stage}_COMPLETE").exists()
    rows=[];choices=[]
    for name in MODELS:
        for h in HORIZONS:
            candidates=[check(root/name/"selection"/f"h{h}_lr{lr:g}",name,h,11,lr) for lr in LRS]
            best=min(candidates,key=lambda r:(r["validation_mae"],r["learning_rate"]))
            choices.append(dict(model=name,horizon_hours=h,learning_rate=best["learning_rate"],validation_mae=best["validation_mae"]))
            rows.extend(candidates)
            if stage=="final":
                for s in SEEDS:
                    rows.append(check(root/name/"final"/f"h{h}_seed{s}",name,h,s,best["learning_rate"]))
    expected=120 if stage=="selection" else 270
    assert len(rows)==expected
    out=V3/"verification/baseline_selected_lrs.csv";out.parent.mkdir(exist_ok=True)
    with out.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(choices[0]));w.writeheader();w.writerows(choices)
    print(f"Verified {len(rows)} baseline {stage} cells, identities, hashes and selected LR")

if __name__=="__main__":main(sys.argv[1])
