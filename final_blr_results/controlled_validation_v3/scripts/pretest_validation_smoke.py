"""Check checkpoint reload and paired validation scoring before test unlock."""
import json
import numpy as np
import torch
from final_blr_results.controlled_validation_v3.scripts.smoke_gpu import CutoffContext,ARR,FIT,V3
from final_blr_results.controlled_validation_v3.scripts.train_controls import BASE_CFG,hash_file
from final_blr_results.controlled_validation_v3.scripts.train_baselines import BaselineContext


def score(ctx,name,cell):
    rec=json.loads((cell/"COMPLETE.json").read_text())
    ckpt=cell/"best.pt"
    assert hash_file(ckpt)==rec["checkpoint_sha256"]
    payload=torch.load(ckpt,map_location="cpu",weights_only=False)
    model=ctx.make("stpignn_lambda0")
    model.load_state_dict(payload["state_dict"],strict=True)
    result=ctx.evaluate(model,"stpignn_lambda0","validation",collect=True)
    assert abs(result["mae"]-rec["validation_mae"])<1e-4
    assert np.isfinite(result["pred"]).all()
    return result


def main():
    h=6;s=11
    a=score(CutoffContext(h,BASE_CFG,ARR,FIT),"true_wind",V3/"training/final"/f"h{h}_seed{s}_true_wind")
    b=score(BaselineContext("gru_only",h),"gru_only",V3/"training/baselines/gru_only/final"/f"h{h}_seed{s}")
    for key in ("time_index","station_index","truth"):
        assert np.array_equal(a[key],b[key]),key
    print(json.dumps(dict(status="PASS",split="validation only",horizon=h,seed=s,
                          paired_observed_targets=int(a["n"]),
                          true_wind_validation_mae=float(a["mae"]),
                          gru_only_validation_mae=float(b["mae"])),indent=2))


if __name__=="__main__":main()
