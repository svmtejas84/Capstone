"""Train only the ten missing V5 six-hour penalty-grid conditions.

Historical λ=.06 cells and true-wind λ=.3/1.0 are reused, never overwritten.
Test evaluation is a separate guarded step.
"""
from __future__ import annotations

import argparse
import json
import random
import time

import numpy as np
import torch

from scripts.benchmark_v2j import seed_all
from src.stpignn.physics_v2 import batched_penalty
from final_blr_results.controlled_validation_v3.scripts.smoke_gpu import CutoffContext, ARR, FIT, V3
from final_blr_results.controlled_validation_v3.scripts.train_controls import BASE_CFG, SEEDS, hash_file, atomic_json, torch_save_atomic
from final_blr_results.controlled_validation_v3.scripts.train_controls import wind_masks as v3_masks
from final_blr_results.controlled_validation_v4_review_closure.scripts.train_sensitivity import wind_masks as v4_masks

V5 = V3.parent / "controlled_validation_v5"
FAMILIES = ("within_month_shuffle", "full_shuffle", "reverse_wind", "constant_north", "laplacian")
STRENGTHS = (.3, 1.)


def mask_for(ctx, family):
    if family == "within_month_shuffle": return v3_masks(ctx, "shuffled_wind")
    if family == "full_shuffle": return v4_masks(ctx, "full_shuffle_006")
    if family == "reverse_wind": return v4_masks(ctx, "reverse_wind_006")
    if family == "constant_north": return v4_masks(ctx, "constant_north_006")
    if family == "laplacian": return None
    raise ValueError(family)


def train_cell(ctx, family, strength, seed, masks):
    name = f"{family}_lambda{strength:g}"
    out = V5 / "training" / "fairness" / f"h6_seed{seed}_{name}"
    out.mkdir(parents=True, exist_ok=True)
    done = out / "COMPLETE.json"
    if done.exists():
        rec = json.loads(done.read_text())
        assert rec["array_sha256"] == hash_file(ARR) and hash_file(out / "best.pt") == rec["checkpoint_sha256"]
        return rec
    seed_all(seed)
    model = ctx.make("stpignn_lambda0")
    opt = torch.optim.AdamW(model.parameters(), lr=.0003, weight_decay=.01)
    best, best_epoch, best_state, stale = float("inf"), 0, None, 0
    epoch_start, elapsed, hist = 1, 0., []
    partial = out / "partial.pt"
    if partial.exists():
        state = torch.load(partial, map_location="cpu", weights_only=False)
        model.load_state_dict(state["model"]); opt.load_state_dict(state["optimizer"])
        best, best_epoch, best_state, stale = state["best"], state["best_epoch"], state["best_state"], state["stale"]
        epoch_start, elapsed, hist = state["epoch"]+1, state["elapsed"], state["hist"]
        torch.set_rng_state(state["torch_rng"]); torch.cuda.set_rng_state_all(state["cuda_rng"])
        np.random.set_state(state["numpy_rng"]); random.setstate(state["python_rng"])
    start = time.perf_counter()
    for epoch in range(epoch_start, 31):
        model.train()
        sums = dict(data=0., penalty=0., active=0, batches=0, zero_batches=0)
        for index,x,y,valid,anchor,wind in ctx.batches("train",seed*1000+epoch):
            opt.zero_grad(set_to_none=True)
            z = ctx.forward(model,"stpignn_lambda0",x,anchor,wind)
            target=(torch.log1p(y.clamp_min(0))-ctx.mu)/ctx.sd
            data=((z-target).square()*valid).sum()/valid.sum().clamp_min(1)
            pm=torch.expm1(z*ctx.sd+ctx.mu)/ctx.physical_scale
            if family == "laplacian":
                m=torch.ones((len(index),ctx.edge_index.shape[1]),device=ctx.device,dtype=torch.bool)
                reg=batched_penalty(pm,ctx.edge_index,m,ctx.edge_distance,"laplacian")
            else:
                m=torch.as_tensor(masks[index-ctx.horizon].copy(),device=ctx.device)
                reg=batched_penalty(pm,ctx.edge_index,m,ctx.edge_distance,"corrected_mask")
            lam=strength*min(1.,epoch/5.)
            loss=data+lam*reg
            if not bool(torch.isfinite(loss)):
                raise FloatingPointError((name,seed,epoch))
            loss.backward();torch.nn.utils.clip_grad_norm_(model.parameters(),.3);opt.step()
            sums["data"]+=float(data.detach());sums["penalty"]+=float(reg.detach())
            sums["active"]+=int(m.sum());sums["batches"]+=1;sums["zero_batches"]+=int(not bool(m.any()))
        val=float(ctx.evaluate(model,"stpignn_lambda0","validation")["mae"])
        if epoch>=10:
            if val<best:
                best,best_epoch,stale=val,epoch,0
                best_state={k:v.detach().cpu().clone() for k,v in model.state_dict().items()}
            else:stale+=1
        hist.append(dict(epoch=epoch,validation_mae=val,lambda_effective=lam,
                         mean_data_loss=sums["data"]/sums["batches"],mean_penalty=sums["penalty"]/sums["batches"],
                         mean_weighted_penalty=lam*sums["penalty"]/sums["batches"],
                         active_arcs=sums["active"],zero_arc_batches=sums["zero_batches"],batches=sums["batches"]))
        atomic_json(out / "epochs.json",hist)
        torch_save_atomic(partial,dict(epoch=epoch,model=model.state_dict(),optimizer=opt.state_dict(),
            best=best,best_epoch=best_epoch,best_state=best_state,stale=stale,elapsed=elapsed+time.perf_counter()-start,
            hist=hist,torch_rng=torch.get_rng_state(),cuda_rng=torch.cuda.get_rng_state_all(),
            numpy_rng=np.random.get_state(),python_rng=random.getstate()))
        if stale>=5:break
    assert best_state is not None
    ckpt=out/"best.pt"
    torch_save_atomic(ckpt,dict(state_dict=best_state,variant=name,horizon=6,seed=seed,lr=.0003,
        best_epoch=best_epoch,validation_mae=best,array_sha256=hash_file(ARR),protocol="v5"))
    rec=dict(variant=name,family=family,lambda_max=strength,horizon_hours=6,seed=seed,learning_rate=.0003,
        best_epoch=best_epoch,epochs_run=epoch,validation_mae=best,elapsed_seconds=elapsed+time.perf_counter()-start,
        effective_lambda_at_best=strength*min(1.,best_epoch/5.),checkpoint_sha256=hash_file(ckpt),
        array_sha256=hash_file(ARR),parameter_count=sum(p.numel() for p in model.parameters()))
    atomic_json(done,rec)
    return rec


def main():
    p=argparse.ArgumentParser();p.add_argument("--stage",choices=["smoke","final"],required=True);a=p.parse_args()
    assert torch.cuda.is_available()
    ctx=CutoffContext(6,BASE_CFG,ARR,FIT)
    if a.stage=="smoke":
        for family in FAMILIES:
            m=mask_for(ctx,family)
            if m is not None:assert m.shape==ctx.corrected_wind_mask.shape and m.dtype==bool
            print(json.dumps(dict(family=family,active_training_arcs=int(m[ctx.train_period].sum()) if m is not None else "all 60 per train hour")),flush=True)
        return
    rows=[]
    for family in FAMILIES:
        m=mask_for(ctx,family)
        for strength in STRENGTHS:
            for seed in SEEDS:
                rec=train_cell(ctx,family,strength,seed,m);rows.append(rec);print(json.dumps(rec),flush=True)
    atomic_json(V5/"training/fairness_summary.json",rows)
    (V5/"training/fairness_COMPLETE").write_text("COMPLETE\n")


if __name__=="__main__":main()
