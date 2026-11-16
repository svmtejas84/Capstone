"""Verify every reused V3/V4 ensemble equals its five saved seed predictions."""
import json
import numpy as np

from final_blr_results.controlled_validation_v3.scripts.smoke_gpu import V3
from final_blr_results.controlled_validation_v5.scripts.verify_and_score import V5, HISTORICAL


def check(root,h,name):
    base=root/"predictions"/f"h{h}_{name}"
    seed=[];reference=None
    for s in (11,23,37,51,79):
        with np.load(str(base)+f"_seed{s}.npz") as z:
            current={k:z[k] for k in ("pred","truth","time_index","station_index")}
        if reference is not None:
            for k in ("truth","time_index","station_index"):assert np.array_equal(current[k],reference[k])
        reference=current;seed.append(current["pred"])
    with np.load(str(base)+"_ensemble.npz") as z:
        for k in ("truth","time_index","station_index"):assert np.array_equal(z[k],reference[k])
        max_abs=float(np.max(np.abs(z["pred"]-np.mean(np.stack(seed),axis=0))))
    assert max_abs<2e-5,(name,max_abs)
    return dict(source=str(base),horizon_hours=h,scored_pairs=len(reference["pred"]),
                max_abs_saved_ensemble_minus_five_seed_mean=max_abs)


def main():
    rows=[]
    for h in (1,3,6,12,24):rows.append(check(V3,h,"zero"))
    for family in HISTORICAL:
        for strength, (root,name) in HISTORICAL[family].items():
            rows.append(check(root,6,name))
    assert len(rows)==13
    out=dict(status="PASS",reused_ensemble_files=len(rows),details=rows)
    p=V5/"verification/REUSED_PREDICTION_VERIFICATION.json";p.parent.mkdir(exist_ok=True)
    p.write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps(dict(status="PASS",reused_ensemble_files=len(rows),max_error=max(r["max_abs_saved_ensemble_minus_five_seed_mean"] for r in rows))))


if __name__=="__main__":main()
