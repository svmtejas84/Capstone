"""Frozen exploratory paired block analyses from one-time saved test predictions."""
import csv
from pathlib import Path
import numpy as np
import pandas as pd
from final_blr_results.controlled_validation_v3.scripts.train_controls import HORIZONS, V3

COMPARATORS=["zero","shuffled_wind","rotated_wind","laplacian"]


def load(h,v):
    z=np.load(V3/"predictions"/f"h{h}_{v}_ensemble.npz")
    return {k:z[k] for k in z.files}


def block_analysis(day, diff, seed):
    unique, inverse=np.unique(day,return_inverse=True)
    sums=np.bincount(inverse,weights=diff)
    counts=np.bincount(inverse)
    n=len(unique)
    rng=np.random.default_rng(seed)
    boot=np.empty(2000)
    for b in range(len(boot)):
        picked=[]
        while len(picked)<n:
            start=int(rng.integers(0,max(1,n-6)))
            picked.extend(range(start,min(start+7,n)))
        p=np.asarray(picked[:n])
        boot[b]=sums[p].sum()/counts[p].sum()
    ci=np.quantile(boot,[.025,.975])
    blocks=np.arange(n)//7
    bs=np.bincount(blocks,weights=sums)
    obs=abs(bs.sum())
    draws=100000; hits=0
    for start in range(0,draws,2000):
        m=min(2000,draws-start)
        sign=rng.integers(0,2,size=(m,len(bs)),dtype=np.int8)*2-1
        hits+=int(np.count_nonzero(np.abs(sign@bs)>=obs-1e-12))
    return ci,(hits+1)/(draws+1),len(bs),n


def holm(p):
    p=np.asarray(p,float); order=np.argsort(p); result=np.empty(len(p))
    adjusted=np.maximum.accumulate((len(p)-np.arange(len(p)))*p[order])
    result[order]=np.minimum(adjusted,1.)
    return result


def main():
    rows=[]
    for h in HORIZONS:
        true=load(h,"true_wind")
        for ci,v in enumerate(COMPARATORS):
            other=load(h,v)
            for k in ("time_index","station_index","truth"):
                assert np.array_equal(true[k],other[k])
            delta=np.abs(true["pred"]-true["truth"])-np.abs(other["pred"]-other["truth"])
            day=pd.to_datetime(np.load("final_blr_results/baselines/v2m/data/data_v2m_arrays.npz")["times_ns"][true["time_index"]],utc=True).floor("D").asi8
            lowhigh,p,blocks,days=block_analysis(day,delta,4303+h*10+ci)
            rows.append(dict(horizon_hours=h,contrast=f"true_wind_minus_{v}",paired_delta_mae_ug_m3=delta.mean(),
                             ci95_low_ug_m3=lowhigh[0],ci95_high_ug_m3=lowhigh[1],
                             block_signflip_p=p,paired_pairs=len(delta),utc_days=days,nonoverlap_blocks=blocks,
                             inference="exploratory; exposed historical test"))
    adj=holm([r["block_signflip_p"] for r in rows])
    for r,p in zip(rows,adj): r["holm_20_p"]=p
    out=V3/"statistical_analysis/primary_contrasts.csv";out.parent.mkdir(exist_ok=True)
    with out.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    print(f"Wrote {len(rows)} frozen contrasts")


if __name__=="__main__":main()
