"""Restart-safe graph topology and lag-24 controls; train/validation only.

Test labels are never read by this driver. Score with score_new.py after all
predeclared cells have been verified and training is complete.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import time
from pathlib import Path

import numpy as np
import torch

from scripts.benchmark_v2j import seed_all
from final_blr_results.controlled_validation_v3.scripts.smoke_gpu import CutoffContext, ARR, FIT, V3
from final_blr_results.controlled_validation_v3.scripts.train_controls import BASE_CFG, SEEDS, HORIZONS, hash_file, atomic_json, torch_save_atomic

V5 = V3.parent / "controlled_validation_v5"
LR = {1: .001, 3: .0003, 6: .0003, 12: .0003, 24: .0003}
VARIANTS = ("self_loops", "rewired", "lag24", "lookback36")
CROSS_VARIANTS = ("lag24_self_loops", "lag24_rewired")


def rewire_preserving_degree(edge_index: np.ndarray, seed: int = 5505) -> np.ndarray:
    """Directed destination swaps preserve each node's in/out degree exactly."""
    rng = np.random.default_rng(seed)
    e = np.array(edge_index, copy=True)
    pairs = set(map(tuple, e.T))
    accepted = 0
    for _ in range(4000):
        i, j = rng.choice(e.shape[1], 2, replace=False)
        a, b = map(int, e[:, i]); c, d = map(int, e[:, j])
        if len({a, b, c, d}) < 4 or (a, d) in pairs or (c, b) in pairs:
            continue
        pairs.remove((a, b)); pairs.remove((c, d))
        pairs.add((a, d)); pairs.add((c, b))
        e[1, i], e[1, j] = d, b
        accepted += 1
    assert accepted > 0 and len(pairs) == e.shape[1]
    assert np.array_equal(np.bincount(e[0], minlength=15), np.bincount(edge_index[0], minlength=15))
    assert np.array_equal(np.bincount(e[1], minlength=15), np.bincount(edge_index[1], minlength=15))
    assert not np.array_equal(e, edge_index)
    return e


class ExperimentalContext(CutoffContext):
    def __init__(self, horizon: int, variant: str):
        super().__init__(horizon, BASE_CFG, ARR, FIT)
        self.variant = variant
        self.array_sha256 = hash_file(ARR)
        if variant in ("self_loops", "lag24_self_loops"):
            e = np.stack((np.arange(self.n), np.arange(self.n)))
            self._set_edges(e)
        elif variant in ("rewired", "lag24_rewired"):
            self._set_edges(rewire_preserving_degree(self.edge_index.cpu().numpy()))
        if variant in ("lag24", "lag24_self_loops", "lag24_rewired"):
            # Only the final feature row receives the three extra channels.
            self.features = np.concatenate((self.features, np.zeros((*self.features.shape[:2], 3), np.float32)), axis=2)
            obs = self.observed
            self.latest_observed = np.maximum.accumulate(np.where(obs, np.arange(len(obs))[:, None], -1), axis=0)
        elif variant == "lookback36":
            self.history = 36
        elif variant not in ("self_loops", "rewired"):
            raise ValueError(variant)

    def _set_edges(self, e):
        e = np.asarray(e, np.int64)
        length = np.linalg.norm(self.xy[e[1]] - self.xy[e[0]], axis=1).astype(np.float32)
        if self.variant in ("self_loops", "lag24_self_loops"):
            assert len(e.T) == self.n and np.all(length == 0)
        else:
            assert len(e.T) == 60 and np.all(length > 0)
        self.edge_index = torch.as_tensor(e, device=self.device)
        self.edge_distance = torch.as_tensor(length[:, None], device=self.device)
        self.edge_attr = torch.log1p(self.edge_distance)
        self.edge_length = length

    def batches(self, name, shuffle_seed=None):
        if self.variant != "lookback36" and not self.variant.startswith("lag24"):
            yield from super().batches(name, shuffle_seed)
            return
        hours = self.hours[name].copy()
        if shuffle_seed is not None:
            np.random.default_rng(shuffle_seed).shuffle(hours)
        for start in range(0, len(hours), int(self.cfg["neural_batch_size"])):
            index = hours[start:start + int(self.cfg["neural_batch_size"])]
            cutoff = index - self.horizon
            # Only the first 24 historical hours can need left padding in L2.
            window = np.maximum(0, cutoff[:, None] - np.arange(self.history - 1, -1, -1)[None, :])
            assert np.all(window <= cutoff[:, None])
            x = self.features[window].copy()
            if self.variant.startswith("lag24"):
                daily_idx = index - 24
                daily_ok = (daily_idx >= 0) & (daily_idx < cutoff)
                safe_daily = np.maximum(daily_idx, 0)
                genuine = daily_ok[:, None] & self.observed[safe_daily]
                # Match the frozen same-hour-yesterday baseline's causal
                # fallback at the daily-lag timestamp, not a newer issue-time
                # observation. At h=24 these timestamps coincide.
                fallback_source = np.where(daily_idx[:, None] > 0,
                    self.latest_observed[np.maximum(daily_idx - 1, 0)], -1)
                source = np.where(genuine, daily_idx[:, None], fallback_source)
                age = np.where(source >= 0, cutoff[:, None] - source, 168)
                value = np.where(genuine, np.nan_to_num(self.y[safe_daily], nan=0), self.anchor[safe_daily])
                value = np.maximum(0, value)
                x[:, -1, :, 18] = (np.log1p(value) - self.mu) / self.sd
                x[:, -1, :, 19] = genuine.astype(np.float32)
                x[:, -1, :, 20] = np.minimum(age, 168) / 168
                assert np.all(source < cutoff[:, None])
            y = torch.as_tensor(np.nan_to_num(self.y[index], nan=0).copy(), device=self.device)
            valid = self.observed[index].copy()
            if name != "test":
                valid &= self.input_observed[cutoff]
            yield (index, torch.as_tensor(x, device=self.device), y,
                   torch.as_tensor(valid, device=self.device),
                   torch.as_tensor(self.anchor[cutoff].copy(), device=self.device),
                   torch.as_tensor(self.wind_along[cutoff].copy(), device=self.device))


def train_cell(ctx: ExperimentalContext, seed: int):
    v, h = ctx.variant, ctx.horizon
    out = V5 / "training" / v / f"h{h}_seed{seed}"
    out.mkdir(parents=True, exist_ok=True)
    done = out / "COMPLETE.json"
    if done.exists():
        r = json.loads(done.read_text())
        assert r["array_sha256"] == ctx.array_sha256 and r["variant"] == v and r["seed"] == seed
        assert hash_file(out / "best.pt") == r["checkpoint_sha256"]
        return r
    seed_all(seed)
    model = ctx.make("stpignn_lambda0")
    optimizer = torch.optim.AdamW(model.parameters(), lr=LR[h], weight_decay=.01)
    best, best_epoch, best_state, stale = float("inf"), 0, None, 0
    start_epoch, elapsed, hist = 1, 0., []
    partial = out / "partial.pt"
    if partial.exists():
        state = torch.load(partial, map_location="cpu", weights_only=False)
        model.load_state_dict(state["model"]); optimizer.load_state_dict(state["optimizer"])
        best, best_epoch, best_state, stale = state["best"], state["best_epoch"], state["best_state"], state["stale"]
        start_epoch, elapsed, hist = state["epoch"]+1, state["elapsed"], state["hist"]
        torch.set_rng_state(state["torch_rng"]); torch.cuda.set_rng_state_all(state["cuda_rng"])
        np.random.set_state(state["numpy_rng"]); random.setstate(state["python_rng"])
    start = time.perf_counter()
    for epoch in range(start_epoch, 31):
        model.train(); data_sum = 0.; batches = 0
        for _, x, y, valid, anchor, wind in ctx.batches("train", seed*1000+epoch):
            optimizer.zero_grad(set_to_none=True)
            z = ctx.forward(model, "stpignn_lambda0", x, anchor, wind)
            target = (torch.log1p(y.clamp_min(0)) - ctx.mu) / ctx.sd
            loss = ((z-target).square()*valid).sum()/valid.sum().clamp_min(1)
            if not bool(torch.isfinite(loss)):
                raise FloatingPointError((v,h,seed,epoch))
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), .3)
            optimizer.step(); data_sum += float(loss.detach()); batches += 1
        val = float(ctx.evaluate(model, "stpignn_lambda0", "validation")["mae"])
        if epoch >= 10:
            if val < best:
                best, best_epoch, stale = val, epoch, 0
                best_state = {k:p.detach().cpu().clone() for k,p in model.state_dict().items()}
            else: stale += 1
        hist.append(dict(epoch=epoch,validation_mae=val,mean_supervised_loss=data_sum/batches,
                         lambda_effective=0.,batches=batches))
        atomic_json(out / "epochs.json", hist)
        torch_save_atomic(partial, dict(epoch=epoch,model=model.state_dict(),optimizer=optimizer.state_dict(),
            best=best,best_epoch=best_epoch,best_state=best_state,stale=stale,elapsed=elapsed+time.perf_counter()-start,
            hist=hist,torch_rng=torch.get_rng_state(),cuda_rng=torch.cuda.get_rng_state_all(),
            numpy_rng=np.random.get_state(),python_rng=random.getstate()))
        if stale >= 5: break
    assert best_state is not None
    ckpt = out / "best.pt"
    torch_save_atomic(ckpt, dict(state_dict=best_state,variant=v,horizon=h,seed=seed,
        lr=LR[h],best_epoch=best_epoch,validation_mae=best,array_sha256=ctx.array_sha256,protocol="v5"))
    record = dict(variant=v,horizon_hours=h,seed=seed,learning_rate=LR[h],
        best_epoch=best_epoch,epochs_run=epoch,validation_mae=best,
        elapsed_seconds=elapsed+time.perf_counter()-start,parameter_count=sum(p.numel() for p in model.parameters()),
        edge_count=ctx.edge_index.shape[1],input_channels=ctx.features.shape[-1],history_hours=ctx.history,
        checkpoint_sha256=hash_file(ckpt),array_sha256=ctx.array_sha256)
    atomic_json(done, record)
    return record


def main():
    p = argparse.ArgumentParser(); p.add_argument("--stage", choices=["smoke","graph","lag","cross"], required=True)
    a = p.parse_args()
    assert torch.cuda.is_available()
    if a.stage == "smoke":
        for v in VARIANTS:
            ctx = ExperimentalContext(6, v)
            seed_all(11)
            index,x,y,valid,anchor,wind = next(ctx.batches("train"))
            assert x.shape[1] == (36 if v == "lookback36" else 12)
            assert x.shape[-1] == (21 if v == "lag24" else 18)
            model = ctx.make("stpignn_lambda0")
            z=ctx.forward(model,"stpignn_lambda0",x,anchor,wind)
            loss=((z-(torch.log1p(y.clamp_min(0))-ctx.mu)/ctx.sd).square()*valid).sum()/valid.sum()
            assert bool(torch.isfinite(loss)); loss.backward()
            assert all(g.grad is None or bool(torch.isfinite(g.grad).all()) for g in model.parameters())
            print(json.dumps(dict(variant=v,batch_shape=list(x.shape),edges=int(ctx.edge_index.shape[1]),
                                  params=sum(q.numel() for q in model.parameters()),loss=float(loss.detach()))),flush=True)
        return
    variants = VARIANTS[:2] if a.stage == "graph" else (VARIANTS[2:] if a.stage == "lag" else CROSS_VARIANTS)
    rows=[]
    for h in ((6,) if a.stage == "cross" else HORIZONS):
        for v in variants:
            ctx=ExperimentalContext(h,v)
            for seed in SEEDS:
                row=train_cell(ctx,seed); rows.append(row); print(json.dumps(row),flush=True)
    atomic_json(V5 / "training" / f"{a.stage}_summary.json", rows)
    (V5 / "training" / f"{a.stage}_COMPLETE").write_text("COMPLETE\n")


if __name__ == "__main__": main()
