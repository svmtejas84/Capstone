"""Complete V3 shuffled/rotated checkpoint-local gradient diagnostics.

No optimizer step. This is training-batch replay, separate from test-time
observed-endpoint ordering diagnostics.
"""
import csv
import json

import numpy as np
import pandas as pd
import torch

from src.stpignn.physics_v2 import batched_penalty
from final_blr_results.controlled_validation_v3.scripts.smoke_gpu import CutoffContext, ARR, FIT, V3
from final_blr_results.controlled_validation_v3.scripts.train_controls import BASE_CFG, SEEDS, hash_file, wind_masks

V5=V3.parent/"controlled_validation_v5"


def main():
    assert torch.cuda.is_available()
    rows=[]
    for h in (1,3,6,12,24):
        ctx=CutoffContext(h,BASE_CFG,ARR,FIT)
        index,x,y,valid,anchor,wind=next(ctx.batches("train"))
        for variant in ("shuffled_wind","rotated_wind"):
            cell=V3/"training/final"/f"h{h}_seed11_{variant}"
            rec=json.loads((cell/"COMPLETE.json").read_text())
            assert rec["checkpoint_sha256"]==hash_file(cell/"best.pt")
            payload=torch.load(cell/"best.pt",map_location="cpu",weights_only=False)
            model=ctx.make("stpignn_lambda0");model.load_state_dict(payload["state_dict"],strict=True)
            model.train()  # cuDNN backward; no optimizer/weight update
            z=ctx.forward(model,"stpignn_lambda0",x,anchor,wind)
            target=(torch.log1p(y.clamp_min(0))-ctx.mu)/ctx.sd
            data=((z-target).square()*valid).sum()/valid.sum().clamp_min(1)
            pm=torch.expm1(z*ctx.sd+ctx.mu)/ctx.physical_scale
            mask=torch.as_tensor(wind_masks(ctx,variant)[index-h].copy(),device=ctx.device)
            reg=batched_penalty(pm,ctx.edge_index,mask,ctx.edge_distance,"corrected_mask")
            lam=float(rec["effective_lambda_at_best"])
            params=list(model.parameters())
            gd=torch.autograd.grad(data,params,retain_graph=True,allow_unused=True)
            gr=torch.autograd.grad(reg,params,allow_unused=True)
            dvec=torch.cat([(g if g is not None else torch.zeros_like(p)).reshape(-1) for g,p in zip(gd,params)])
            rvec=torch.cat([(g if g is not None else torch.zeros_like(p)).reshape(-1) for g,p in zip(gr,params)])*lam
            dn=float(torch.linalg.vector_norm(dvec));rn=float(torch.linalg.vector_norm(rvec))
            rows.append(dict(horizon_hours=h,variant=variant,seed=11,raw_supervised_loss=float(data),
                             raw_regularization_loss=float(reg),effective_lambda=lam,
                             weighted_regularization_loss=float(lam*reg),supervised_gradient_norm=dn,
                             weighted_penalty_gradient_norm=rn,gradient_ratio=rn/dn if dn else np.nan,
                             active_arcs=int(mask.sum()),checkpoint_sha256=rec["checkpoint_sha256"],
                             scope="selected checkpoint, first frozen train batch; no optimizer step"))
            print(h,variant,rows[-1]["gradient_ratio"],flush=True)
    assert len(rows)==10
    p=V5/"PENALTY_GRADIENT_REPLAY_MISSING.csv"
    with p.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    d=pd.read_csv(V5/"PENALTY_DIAGNOSTICS_COMPLETE.csv")
    for r in rows:
        mask=(d.horizon_hours==r["horizon_hours"])&(d.method==r["variant"])
        assert mask.sum()==1
        for source,target in (("raw_regularization_loss","raw_penalty"),
                              ("weighted_regularization_loss","weighted_penalty"),
                              ("gradient_ratio","gradient_ratio")):
            d.loc[mask,target]=r[source]
        d.loc[mask,"gradient_replay_scope"]=r["scope"]
    d.to_csv(V5/"PENALTY_DIAGNOSTICS_COMPLETE.csv",index=False,float_format="%.12g")


if __name__=="__main__":main()
