"""Recompute every saved test metric and contrast without model inference."""
import csv
import hashlib
import json
import numpy as np
import pandas as pd
from src.stpignn.evaluation import evaluate_arrays
from final_blr_results.controlled_validation_v3.scripts.train_controls import V3,ARR,HORIZONS,hash_file
from final_blr_results.controlled_validation_v3.scripts.analyze_controls import block_analysis,holm


def metric_check(row,path):
    with np.load(path) as z:
        pred=z["pred"];truth=z["truth"];ti=z["time_index"];sj=z["station_index"]
    assert np.isfinite(pred).all() and np.isfinite(truth).all()
    assert len(pred)==len(truth)==len(ti)==len(sj)
    m=evaluate_arrays(pred,truth,np.ones(len(pred),bool))
    for k in ("mae","rmse","r2"):
        assert np.isclose(float(row[k]),m[k],atol=1e-5,rtol=1e-7),(path,k,row[k],m[k])
    assert int(row["n"])==int(m["n"])
    return ti,sj,truth


def main():
    assert json.loads((V3/"verification/test_unlock.json").read_text())["array_sha256"]==hash_file(ARR)
    source=[]
    with (V3/"data_manifests/source_checksums.csv").open() as f:
        source=list(csv.DictReader(f))
    for r in source:
        p=V3.parents[1]/r["path"]
        assert p.exists() and p.stat().st_size==int(r["bytes"])
        assert hash_file(p)==r["sha256"],p
    controls=pd.read_csv(V3/"metrics/matched_controls.csv")
    baselines=pd.read_csv(V3/"metrics/baselines.csv")
    assert len(controls)==150 and len(baselines)==205
    references={}
    count=0
    for _,r in controls.iterrows():
        path=V3/"predictions"/f'h{int(r.horizon_hours)}_{r.variant}_seed{r.seed}.npz' if str(r.seed)!="ensemble" else V3/"predictions"/f'h{int(r.horizon_hours)}_{r.variant}_ensemble.npz'
        ti,sj,truth=metric_check(r,path);h=int(r.horizon_hours)
        if h not in references:references[h]=(ti,sj,truth)
        else:
            assert all(np.array_equal(a,b) for a,b in zip((ti,sj,truth),references[h]))
        count+=1
    classical={"persistence","same_hour_yesterday","station_train_mean","climatology_hod_dow","weather_ridge"}
    for _,r in baselines.iterrows():
        h=int(r.horizon_hours);name=r.model;seed=str(r.seed)
        suffix="" if name in classical else ("_ensemble" if seed=="ensemble" else f"_seed{seed}")
        path=V3/"predictions"/f"h{h}_{name}{suffix}.npz"
        ti,sj,truth=metric_check(r,path)
        assert all(np.array_equal(a,b) for a,b in zip((ti,sj,truth),references[h]))
        count+=1
    contrasts=pd.read_csv(V3/"statistical_analysis/primary_contrasts.csv")
    assert len(contrasts)==20
    original=np.load("final_blr_results/baselines/v2m/data/data_v2m_arrays.npz")
    rawp=[]
    names=["zero","shuffled_wind","rotated_wind","laplacian"]
    for _,r in contrasts.iterrows():
        h=int(r.horizon_hours);v=r.contrast.removeprefix("true_wind_minus_")
        ci=names.index(v)
        with np.load(V3/"predictions"/f"h{h}_true_wind_ensemble.npz") as z:
            t={k:z[k] for k in z.files}
        with np.load(V3/"predictions"/f"h{h}_{v}_ensemble.npz") as z:
            o={k:z[k] for k in z.files}
        for k in ("time_index","station_index","truth"):
            assert np.array_equal(t[k],o[k])
        d=np.abs(t["pred"]-t["truth"])-np.abs(o["pred"]-o["truth"])
        assert np.isclose(d.mean(),r.paired_delta_mae_ug_m3,atol=1e-6)
        day=pd.to_datetime(original["times_ns"][t["time_index"]],utc=True).floor("D").asi8
        ci95,p,blocks,days=block_analysis(day,d,4303+h*10+ci)
        assert np.allclose(ci95,[r.ci95_low_ug_m3,r.ci95_high_ug_m3],atol=1e-6)
        assert np.isclose(p,r.block_signflip_p,atol=1e-10)
        assert blocks==int(r.nonoverlap_blocks) and days==int(r.utc_days)
        rawp.append(p)
    assert np.allclose(holm(rawp),contrasts.holm_20_p.to_numpy(),atol=1e-10)
    summary=dict(status="PASS",source_hashes=len(source),metric_rows_verified=count,
                 test_pair_counts={str(h):len(references[h][0]) for h in HORIZONS},
                 frozen_contrasts_verified=len(contrasts),
                 caveat="Exposed historical test; no independent temporal or spatial confirmation")
    out=V3/"verification/results_verification.json"
    out.write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,indent=2))


if __name__=="__main__":main()
