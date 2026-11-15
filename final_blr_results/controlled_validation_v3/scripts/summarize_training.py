"""Summarize saved fit records without reading the exposed test period."""
import json
from pathlib import Path
import pandas as pd
from final_blr_results.controlled_validation_v3.scripts.train_controls import V3


def main():
    root=V3/"training"
    rows=[]
    for label,glob in [
        ("control_selection","selection/*/COMPLETE.json"),
        ("control_final","final/*/COMPLETE.json"),
        ("baseline_selection","baselines/*/selection/*/COMPLETE.json"),
        ("baseline_final","baselines/*/final/*/COMPLETE.json"),
        ("invalidated_selection","invalidated_pre_causal_shift/selection/*/COMPLETE.json"),
        ("invalidated_final","invalidated_pre_causal_shift/final/*/COMPLETE.json")]:
        for path in sorted(root.glob(glob)):
            rec=json.loads(path.read_text())
            hist_path=path.parent/"epochs.json"
            hist=json.loads(hist_path.read_text()) if hist_path.exists() else []
            best=next((e for e in hist if e["epoch"]==rec["best_epoch"]),{})
            parts=path.parent.relative_to(root).parts
            model=parts[1] if label.startswith("baseline_") else rec.get("variant","unknown")
            rows.append(dict(stage=label,cell=str(path.parent.relative_to(V3)),
                             model=model,
                             horizon_hours=rec["horizon_hours"],seed=rec["seed"],
                             learning_rate=rec["learning_rate"],best_epoch=rec["best_epoch"],
                             epochs_run=rec["epochs_run"],validation_mae=rec["validation_mae"],
                             effective_lambda_at_best=rec.get("effective_lambda_at_best",0.),
                             best_epoch_data_loss=best.get("mean_data_loss"),
                             best_epoch_penalty=best.get("mean_penalty"),
                             best_epoch_weighted_penalty=(best.get("mean_penalty",0.)*rec.get("effective_lambda_at_best",0.) if best else None),
                             best_epoch_active_arcs=best.get("active_arcs"),
                             best_epoch_zero_arc_batches=best.get("zero_arc_batches"),
                             best_epoch_batches=best.get("batches"),
                             elapsed_seconds=rec["elapsed_seconds"],
                             array_sha256=rec["array_sha256"],
                             checkpoint_sha256=rec["checkpoint_sha256"]))
    df=pd.DataFrame(rows)
    out=V3/"metrics";out.mkdir(exist_ok=True)
    df.to_csv(out/"training_diagnostics.csv",index=False)
    resource=df.groupby("stage",as_index=False).agg(completed_cells=("cell","count"),
                                                      completed_fit_seconds=("elapsed_seconds","sum"))
    resource["completed_fit_hours"]=resource.completed_fit_seconds/3600
    resource.to_csv(out/"resource_usage.csv",index=False)
    print(resource.to_string(index=False))


if __name__=="__main__": main()
