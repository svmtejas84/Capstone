"""Frozen-population descriptive per-site and seed summaries from saved predictions."""
import csv
from math import comb
import numpy as np
import pandas as pd
from final_blr_results.controlled_validation_v3.scripts.train_controls import V3,ARR,HORIZONS,SEEDS,VARIANTS
from final_blr_results.controlled_validation_v3.scripts.train_baselines import MODELS


def write_csv(path,rows):
    with path.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def main():
    assert (V3/"metrics/matched_controls.csv").exists() and (V3/"metrics/baselines.csv").exists()
    z=np.load(ARR); ids=z["station_ids"]
    classical=["persistence","same_hour_yesterday","station_train_mean","climatology_hod_dow","weather_ridge"]
    site=[]
    for h in HORIZONS:
        for name in VARIANTS+MODELS+classical:
            suffix="" if name in classical else "_ensemble"
            path=V3/"predictions"/f"h{h}_{name}{suffix}.npz"
            with np.load(path) as p:
                pred=p["pred"];truth=p["truth"];station=p["station_index"]
            for j,sid in enumerate(ids):
                mask=station==j;n=int(mask.sum())
                err=pred[mask]-truth[mask]
                denom=float(np.sum((truth[mask]-truth[mask].mean())**2)) if n else 0.
                site.append(dict(horizon_hours=h,model=name,station_id=str(sid),observed_pairs=n,
                                 mae_ug_m3=float(np.abs(err).mean()) if n else "",
                                 rmse_ug_m3=float(np.sqrt(np.mean(err**2))) if n else "",
                                 r2=float(1-np.sum(err**2)/denom) if n>1 and denom>0 else "",
                                 population="exposed historical temporal test; not spatial holdout"))
    write_csv(V3/"metrics/per_station_descriptive.csv",site)
    controls=pd.read_csv(V3/"metrics/matched_controls.csv")
    per=[];summary=[]
    for h in HORIZONS:
        a=controls[(controls.horizon_hours==h)&(controls.variant=="true_wind")&
                   (controls.seed.astype(str).isin([str(s) for s in SEEDS]))].set_index("seed")
        for v in VARIANTS:
            if v=="true_wind":continue
            b=controls[(controls.horizon_hours==h)&(controls.variant==v)&
                       (controls.seed.astype(str).isin([str(s) for s in SEEDS]))].set_index("seed")
            diffs=[]
            for s in SEEDS:
                d=float(a.loc[str(s),"mae"]-b.loc[str(s),"mae"])
                diffs.append(d)
                per.append(dict(horizon_hours=h,comparator=v,seed=s,
                                true_minus_comparator_mae_ug_m3=d))
            k=sum(d<0 for d in diffs); ties=sum(d==0 for d in diffs); n=len(diffs)-ties
            lower=min(k,n-k)
            p=min(1.,2*sum(comb(n,i) for i in range(lower+1))/(2**n)) if n else 1.
            summary.append(dict(horizon_hours=h,comparator=v,mean_seed_difference_ug_m3=float(np.mean(diffs)),
                                favorable_seeds=k,unfavorable_seeds=sum(d>0 for d in diffs),ties=ties,
                                exact_two_sided_sign_p=p,
                                interpretation="exploratory; seeds are not independent sites"))
    write_csv(V3/"statistical_analysis/seed_level_differences.csv",per)
    write_csv(V3/"statistical_analysis/seed_sign_tests.csv",summary)
    print(f"Wrote {len(site)} per-station rows and {len(summary)} exploratory seed comparisons")


if __name__=="__main__":main()
