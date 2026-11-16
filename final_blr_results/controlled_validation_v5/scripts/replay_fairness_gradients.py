"""Checkpoint-local, first-train-batch gradient audit; no optimizer step."""
import csv
import json

import numpy as np
import torch

from src.stpignn.physics_v2 import batched_penalty
from final_blr_results.controlled_validation_v3.scripts.smoke_gpu import CutoffContext, ARR, FIT
from final_blr_results.controlled_validation_v3.scripts.train_controls import BASE_CFG, SEEDS, hash_file
from final_blr_results.controlled_validation_v5.scripts.train_fairness import FAMILIES, mask_for
from final_blr_results.controlled_validation_v5.scripts.verify_and_score import V5, cell_path, HISTORICAL


def main():
    assert torch.cuda.is_available()
    ctx=CutoffContext(6,BASE_CFG,ARR,FIT)
    index,x,y,valid,anchor,wind=next(ctx.batches("train"))
    rows=[]
    for family in HISTORICAL:
        masks=mask_for(ctx,family) if family in FAMILIES else ctx.corrected_wind_mask
        for strength in (.06,.3,1.):
            for seed in SEEDS:
                cell,root,name=cell_path(family,strength,seed)
                rec=json.loads((cell/"COMPLETE.json").read_text())
                assert rec["checkpoint_sha256"]==hash_file(cell/"best.pt")
                payload=torch.load(cell/"best.pt",map_location="cpu",weights_only=False)
                model=ctx.make("stpignn_lambda0");model.load_state_dict(payload["state_dict"],strict=True)
                # cuDNN GRU backward requires train mode. No optimizer exists.
                model.train()
                z=ctx.forward(model,"stpignn_lambda0",x,anchor,wind)
                target=(torch.log1p(y.clamp_min(0))-ctx.mu)/ctx.sd
                data=((z-target).square()*valid).sum()/valid.sum().clamp_min(1)
                pm=torch.expm1(z*ctx.sd+ctx.mu)/ctx.physical_scale
                if family=="laplacian":
                    m=torch.ones((len(index),ctx.edge_index.shape[1]),device=ctx.device,dtype=torch.bool)
                    reg=batched_penalty(pm,ctx.edge_index,m,ctx.edge_distance,"laplacian")
                else:
                    m=torch.as_tensor(masks[index-6].copy(),device=ctx.device)
                    reg=batched_penalty(pm,ctx.edge_index,m,ctx.edge_distance,"corrected_mask")
                lam=float(rec["effective_lambda_at_best"])
                params=list(model.parameters())
                gd=torch.autograd.grad(data,params,retain_graph=True,allow_unused=True)
                gr=torch.autograd.grad(reg,params,allow_unused=True)
                dvec=torch.cat([(g if g is not None else torch.zeros_like(p)).reshape(-1) for g,p in zip(gd,params)])
                rvec=torch.cat([(g if g is not None else torch.zeros_like(p)).reshape(-1) for g,p in zip(gr,params)])*lam
                dn=float(torch.linalg.vector_norm(dvec));rn=float(torch.linalg.vector_norm(rvec))
                cos=float(torch.dot(dvec,rvec)/(torch.linalg.vector_norm(dvec)*torch.linalg.vector_norm(rvec)+1e-20)) if rn else 0.
                rows.append(dict(family=family,lambda_max=strength,seed=seed,best_epoch=int(rec["best_epoch"]),
                                 effective_lambda=lam,first_train_batch_hours=len(index),observed_targets=int(valid.sum()),
                                 active_arcs=int(m.sum()),active_arc_fraction=float(m.float().mean()),
                                 raw_supervised_loss=float(data),raw_penalty=float(reg),
                                 weighted_penalty=float(lam*reg),supervised_gradient_norm=dn,
                                 weighted_penalty_gradient_norm=rn,gradient_ratio=rn/dn if dn else np.nan,
                                 gradient_cosine=cos,checkpoint_sha256=rec["checkpoint_sha256"],
                                 scope="selected checkpoint, first frozen train batch; no optimizer step"))
                del model,z,pm,data,reg,gd,gr,dvec,rvec
    assert len(rows)==90
    path=V5/"metrics/FAIRNESS_GRADIENT_REPLAY.csv";path.parent.mkdir(exist_ok=True)
    with path.open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    print(json.dumps(dict(rows=len(rows),mean_gradient_ratio=float(np.mean([r["gradient_ratio"] for r in rows])))))


if __name__=="__main__":main()
