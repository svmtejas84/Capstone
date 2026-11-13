"""Restart-safe validation-selected matched regularization campaign.

Train/validation only. Test predictions are deliberately absent from this driver.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
import os
import random
import time
from pathlib import Path

import numpy as np
import torch
from src.stpignn.physics_v2 import batched_penalty
from scripts.benchmark_v2j import seed_all
from final_blr_results.controlled_validation_v3.scripts.smoke_gpu import CutoffContext, ARR, FIT, V3

SEEDS = [11, 23, 37, 51, 79]
HORIZONS = [1, 3, 6, 12, 24]
LRS = [0.0001, 0.0003, 0.001, 0.003]
VARIANTS = ["zero", "true_wind", "shuffled_wind", "rotated_wind", "laplacian"]
BASE_CFG = dict(neural_batch_size=512, station_graph_neighbours=4, neural_hidden_dim=64,
                neural_weight_decay=.01, neural_max_epochs=30, neural_early_stopping_patience=5,
                lambda_original=.06)


def atomic_json(path, obj):
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")
    temp.replace(path)


def hash_file(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(4*1024*1024), b""):
            h.update(b)
    return h.hexdigest()


def torch_save_atomic(path, payload):
    tmp = path.with_suffix(".tmp")
    torch.save(payload, tmp)
    tmp.replace(path)


def wind_masks(ctx, variant):
    base = ctx.corrected_wind_mask
    if variant == "shuffled_wind":
        result = base.copy()
        rng = np.random.default_rng(4303)
        for split in ("train", "validation", "test"):
            indices = ctx.hours[split] - ctx.horizon
            indices = np.unique(indices)
            result[indices] = base[rng.permutation(indices)]
        return result
    if variant == "rotated_wind":
        xy = ctx.xy
        src, dst = ctx.edge_index.cpu().numpy()
        diff = xy[dst] - xy[src]
        bearing = np.arctan2(diff[:, 0], diff[:, 1])
        original = np.load(ARR)["raw_wind_degrees"].astype(float)
        to = np.deg2rad((original + 180 + 90) % 360)
        angle = np.abs(np.angle(np.exp(1j * (to[:, None] - bearing[None, :]))))
        return np.isfinite(to[:, None]) & (angle <= np.deg2rad(37.5))
    return base


def train_cell(ctx, variant, lr, seed, out, select=False):
    out.mkdir(parents=True, exist_ok=True)
    done = out / "COMPLETE.json"
    if done.exists():
        record = json.loads(done.read_text())
        assert record["array_sha256"] == hash_file(ARR)
        return record
    seed_all(seed)
    model = ctx.make("stpignn_lambda0")
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=.01)
    best = float("inf"); best_epoch = 0; best_state = None; stale = 0
    start_epoch = 1; elapsed = 0.0
    history_path = out / "epochs.json"
    hist = []
    partial = out / "partial.pt"
    if partial.exists():
        state = torch.load(partial, map_location="cpu", weights_only=False)
        model.load_state_dict(state["model"]); optimizer.load_state_dict(state["optimizer"])
        best, best_epoch, best_state, stale = state["best"], state["best_epoch"], state["best_state"], state["stale"]
        start_epoch, elapsed, hist = state["epoch"]+1, state["elapsed"], state["hist"]
        torch.set_rng_state(state["torch_rng"]); np.random.set_state(state["numpy_rng"]); random.setstate(state["python_rng"])
    masks = wind_masks(ctx, variant)
    started = time.perf_counter()
    for epoch in range(start_epoch, 31):
        model.train()
        sums = dict(data=0., penalty=0., active=0, batches=0, zero_batches=0)
        for index, x, y, valid, anchor, wind in ctx.batches("train", seed*1000+epoch):
            optimizer.zero_grad(set_to_none=True)
            z = ctx.forward(model, "stpignn_lambda0", x, anchor, wind)
            target = (torch.log1p(y.clamp_min(0)) - ctx.mu) / ctx.sd
            data_loss = ((z-target).square()*valid).sum()/valid.sum().clamp_min(1)
            pm_norm = torch.expm1(z*ctx.sd+ctx.mu)/ctx.physical_scale
            if variant == "zero":
                reg = z.new_zeros(())
                active = 0
            elif variant == "laplacian":
                reg = batched_penalty(pm_norm, ctx.edge_index,
                                      torch.zeros((len(index), ctx.edge_index.shape[1]), device=ctx.device, dtype=torch.bool),
                                      ctx.edge_distance, "laplacian")
                active = len(index)*ctx.edge_index.shape[1]
            else:
                m = torch.as_tensor(masks[index-ctx.horizon].copy(), device=ctx.device)
                active = int(m.sum())
                reg = batched_penalty(pm_norm, ctx.edge_index, m, ctx.edge_distance, "corrected_mask")
            lam = 0. if variant == "zero" else .06*min(1.,epoch/5.)
            loss = data_loss + lam*reg
            if not bool(torch.isfinite(loss)): raise FloatingPointError((variant,ctx.horizon,seed,epoch))
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), .3)
            optimizer.step()
            sums["data"] += float(data_loss.detach()); sums["penalty"] += float(reg.detach())
            sums["active"] += active; sums["batches"] += 1; sums["zero_batches"] += int(active == 0)
        val = float(ctx.evaluate(model, "stpignn_lambda0", "validation")["mae"])
        if epoch >= 10:
            if val < best:
                best, best_epoch, stale = val, epoch, 0
                best_state = {k:v.detach().cpu().clone() for k,v in model.state_dict().items()}
            else:
                stale += 1
        hist.append(dict(epoch=epoch,validation_mae=val,lambda_effective=lam,
                         mean_data_loss=sums["data"]/sums["batches"],
                         mean_penalty=sums["penalty"]/sums["batches"],
                         active_arcs=sums["active"],zero_arc_batches=sums["zero_batches"],batches=sums["batches"]))
        atomic_json(history_path,hist)
        elapsed_now = elapsed + time.perf_counter()-started
        torch_save_atomic(partial,dict(epoch=epoch,model=model.state_dict(),optimizer=optimizer.state_dict(),
            best=best,best_epoch=best_epoch,best_state=best_state,stale=stale,elapsed=elapsed_now,hist=hist,
            torch_rng=torch.get_rng_state(),numpy_rng=np.random.get_state(),python_rng=random.getstate()))
        if stale >= 5: break
    assert best_state is not None
    ckpt = out / "best.pt"
    torch_save_atomic(ckpt,dict(state_dict=best_state,variant=variant,horizon=ctx.horizon,seed=seed,
        lr=lr,best_epoch=best_epoch,validation_mae=best,array_sha256=hash_file(ARR),protocol="v3"))
    record = dict(variant=variant,horizon_hours=ctx.horizon,seed=seed,learning_rate=lr,
        best_epoch=best_epoch,epochs_run=epoch,validation_mae=best,elapsed_seconds=elapsed+time.perf_counter()-started,
        effective_lambda_at_best=0. if variant=="zero" else .06*min(1.,best_epoch/5.),
        checkpoint_sha256=hash_file(ckpt),array_sha256=hash_file(ARR),selection_cell=select)
    atomic_json(done,record)
    return record


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=["selection","final"],required=True)
    args = parser.parse_args()
    assert torch.cuda.is_available()
    root = V3 / "training"; root.mkdir(exist_ok=True)
    all_results=[]
    for h in HORIZONS:
        ctx = CutoffContext(h, BASE_CFG, ARR, FIT)
        if args.stage == "selection":
            for lr in LRS:
                out = root / "selection" / f"h{h}_lr{lr:g}"
                r=train_cell(ctx,"zero",lr,11,out,select=True)
                all_results.append(r)
                print(json.dumps(r),flush=True)
        else:
            rows=[]
            for lr in LRS:
                p=root/"selection"/f"h{h}_lr{lr:g}"/"COMPLETE.json"
                if not p.exists(): raise FileNotFoundError(p)
                rows.append(json.loads(p.read_text()))
            chosen=min(rows,key=lambda r:(r["validation_mae"],r["learning_rate"]))["learning_rate"]
            for seed in SEEDS:
                for variant in VARIANTS:
                    out=root/"final"/f"h{h}_seed{seed}_{variant}"
                    r=train_cell(ctx,variant,chosen,seed,out)
                    all_results.append(r)
                    print(json.dumps(r),flush=True)
    atomic_json(root/f"{args.stage}_summary.json",all_results)
    (root/f"{args.stage}_COMPLETE").write_text("COMPLETE\n")


if __name__ == "__main__": main()
