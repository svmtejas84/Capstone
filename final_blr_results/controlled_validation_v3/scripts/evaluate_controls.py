"""One-time exposed-test evaluation after all 125 matched-control cells complete."""
import csv
import datetime as dt
import json
from pathlib import Path
import numpy as np
import torch
from final_blr_results.controlled_validation_v3.scripts.smoke_gpu import CutoffContext, ARR, FIT, V3
from final_blr_results.controlled_validation_v3.scripts.train_controls import (
    BASE_CFG, HORIZONS, SEEDS, VARIANTS, hash_file, atomic_json)
from src.stpignn.evaluation import evaluate_arrays


def main():
    root = V3 / "training"
    missing = [str(root/"final"/f"h{h}_seed{s}_{v}"/"COMPLETE.json")
               for h in HORIZONS for s in SEEDS for v in VARIANTS
               if not (root/"final"/f"h{h}_seed{s}_{v}"/"COMPLETE.json").exists()]
    if missing: raise RuntimeError(f"Test locked: {len(missing)} final cells incomplete; first: {missing[0]}")
    if not (root/"final_COMPLETE").exists(): raise RuntimeError("Final training marker absent")
    if not (root/"baselines/final_COMPLETE").exists():
        raise RuntimeError("Test locked: same-information neural baselines incomplete")
    unlock=V3/"verification/test_unlock.json"
    if unlock.exists():
        assert json.loads(unlock.read_text())["array_sha256"]==hash_file(ARR)
    else:
        atomic_json(unlock,dict(utc=dt.datetime.now(dt.timezone.utc).isoformat(),
                               reason="all 125 frozen matched-control cells complete",
                               exposed_historical_test=True,array_sha256=hash_file(ARR)))
    pred_dir=V3/"predictions"; pred_dir.mkdir(exist_ok=True)
    out=V3/"metrics/matched_controls.csv"; out.parent.mkdir(exist_ok=True)
    if out.exists(): raise RuntimeError("Control evaluation already complete; do not repeat")
    def save_once(path, **arrays):
        if path.exists(): return
        tmp=path.with_name(path.stem+".tmp.npz")
        np.savez_compressed(tmp,**arrays)
        tmp.replace(path)
    rows=[]
    for h in HORIZONS:
        ctx=CutoffContext(h, BASE_CFG, ARR, FIT)
        horizon_reference=None
        for v in VARIANTS:
            pmat=[]; reference=None
            for s in SEEDS:
                cell=root/"final"/f"h{h}_seed{s}_{v}"
                record=json.loads((cell/"COMPLETE.json").read_text())
                ckpt=cell/"best.pt"
                assert record["checkpoint_sha256"]==hash_file(ckpt)
                payload=torch.load(ckpt,map_location="cpu",weights_only=False)
                assert payload["variant"]==v and payload["horizon"]==h and payload["seed"]==s
                saved=pred_dir/f"h{h}_{v}_seed{s}.npz"
                if saved.exists():
                    with np.load(saved) as z:
                        result={k:z[k] for k in ("pred","truth","time_index","station_index")}
                    result.update(evaluate_arrays(result["pred"],result["truth"],np.ones(len(result["pred"]),bool)))
                else:
                    model=ctx.make("stpignn_lambda0")
                    model.load_state_dict(payload["state_dict"],strict=True)
                    result=ctx.evaluate(model,"stpignn_lambda0","test",collect=True)
                    save_once(saved,pred=result["pred"],truth=result["truth"],
                              time_index=result["time_index"],station_index=result["station_index"])
                assert np.isfinite(result["pred"]).all() and np.isfinite(result["truth"]).all()
                keys=np.stack([result["time_index"],result["station_index"]],axis=1)
                if reference is None: reference=(keys,result["truth"])
                else:
                    assert np.array_equal(keys,reference[0])
                    assert np.array_equal(result["truth"],reference[1])
                if horizon_reference is None: horizon_reference=reference
                else:
                    assert np.array_equal(keys,horizon_reference[0])
                    assert np.array_equal(result["truth"],horizon_reference[1])
                pmat.append(result["pred"])
                rows.append(dict(horizon_hours=h,variant=v,seed=s,mae=result["mae"],rmse=result["rmse"],
                                 r2=result["r2"],n=result["n"],population="exposed historical test"))
            ensemble=np.mean(np.stack(pmat),axis=0)
            er=evaluate_arrays(ensemble,reference[1],np.ones(len(ensemble),bool))
            rows.append(dict(horizon_hours=h,variant=v,seed="ensemble",mae=er["mae"],rmse=er["rmse"],
                             r2=er["r2"],n=er["n"],population="exposed historical test"))
            save_once(pred_dir/f"h{h}_{v}_ensemble.npz",pred=ensemble,truth=reference[1],
                      time_index=reference[0][:,0],station_index=reference[0][:,1])
    tmp=out.with_suffix(".csv.tmp")
    with tmp.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    tmp.replace(out)
    print(f"Evaluated {len(rows)} seed/ensemble rows; exposed historical test only")


if __name__=="__main__": main()
