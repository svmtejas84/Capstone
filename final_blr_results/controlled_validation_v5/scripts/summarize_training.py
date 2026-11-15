"""Compile V3/V4 reused and V5 new selected checkpoints and epochs."""
import csv
import json
from pathlib import Path

import numpy as np

from final_blr_results.controlled_validation_v3.scripts.smoke_gpu import V3
from final_blr_results.controlled_validation_v4_review_closure.scripts.train_sensitivity import V4
from final_blr_results.controlled_validation_v5.scripts.train_graph_lag import V5
from final_blr_results.controlled_validation_v5.scripts.verify_and_score import HISTORICAL, cell_path


def main():
    rows=[]

    def include(cell, source, role, family, strength):
        rec=json.loads((cell/"COMPLETE.json").read_text())
        epochs=json.loads((cell/"epochs.json").read_text())
        best=int(rec["best_epoch"])
        assert len(epochs)==int(rec["epochs_run"]) and 10<=best<=len(epochs)<=30
        ep=epochs[best-1]
        lam=float(rec.get("effective_lambda_at_best",0.))
        rows.append(dict(source=source,role=role,family=family,lambda_max=strength,
                         horizon_hours=int(rec["horizon_hours"]),seed=int(rec["seed"]),
                         variant=rec["variant"],learning_rate=float(rec["learning_rate"]),
                         batch_size=512,max_epochs=30,epochs_run=int(rec["epochs_run"]),
                         best_validation_epoch=best,validation_mae=float(rec["validation_mae"]),
                         effective_lambda_at_best=lam,
                         selected_epoch_supervised_loss=float(ep.get("mean_supervised_loss",ep.get("mean_data_loss",np.nan))),
                         selected_epoch_raw_penalty=float(ep.get("mean_penalty",0.)),
                         selected_epoch_active_arcs=int(ep.get("active_arcs",0)),
                         selected_epoch_zero_arc_batches=int(ep.get("zero_arc_batches",0)),
                         reached_30_epoch_cap=int(rec["epochs_run"])==30,
                         elapsed_fit_seconds=float(rec["elapsed_seconds"]),
                         checkpoint_path=str((cell/"best.pt").relative_to(Path.cwd())),
                         checkpoint_sha256=rec["checkpoint_sha256"],
                         source_array_sha256=rec["array_sha256"]))

    for h in (1,3,6,12,24):
        for seed in (11,23,37,51,79):
            include(V3/"training/final"/f"h{h}_seed{seed}_zero","V3 frozen","G0/L0 reference","zero",0.)
    for v in ("self_loops","rewired","lag24","lookback36"):
        for h in (1,3,6,12,24):
            for seed in (11,23,37,51,79):
                include(V5/"training"/v/f"h{h}_seed{seed}","V5 new","graph/temporal control",v,0.)
    for v in ("lag24_self_loops","lag24_rewired"):
        for seed in (11,23,37,51,79):
            include(V5/"training"/v/f"h6_seed{seed}","V5 new","lag-matched graph secondary",v,0.)
    for family in HISTORICAL:
        for strength in (.06,.3,1.):
            for seed in (11,23,37,51,79):
                cell,root,name=cell_path(family,strength,seed)
                include(cell,"V5 new" if root==V5 else ("V3 frozen" if root==V3 else "V4 frozen"),
                        "six-hour regularizer grid",family,strength)
    assert len(rows)==225,len(rows)
    p=V5/"TRAINING_SELECTION_REGISTER.csv"
    with p.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    new=[r for r in rows if r["source"]=="V5 new"]
    assert len(new)==160
    summary=dict(all_unique_context_rows=len(rows),new_v5_fit_rows=len(new),
                 recorded_new_fit_seconds=sum(r["elapsed_fit_seconds"] for r in new),
                 recorded_new_fit_hours=sum(r["elapsed_fit_seconds"] for r in new)/3600,
                 new_runs_reaching_30_epoch_cap=sum(r["reached_30_epoch_cap"] for r in new),
                 historic_zero_selection_asymmetry="shared LR selected from V3 zero penalty seed11")
    (V5/"metrics/training_summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,indent=2))


if __name__=="__main__":main()
