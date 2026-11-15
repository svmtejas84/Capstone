"""Verify frozen inputs, all V5 cells, predictions, metrics and contrasts."""
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from final_blr_results.controlled_validation_v3.scripts.smoke_gpu import ARR, V3
from final_blr_results.controlled_validation_v3.scripts.train_controls import hash_file
from final_blr_results.controlled_validation_v5.scripts.train_graph_lag import V5

PROTOCOL_HASH="64682686b29660ff336ed6893e257950ce25c3e03683f68de088f6a808825266"
ARRAY_HASH="bd08d733f924387da82e758d1060703dfcdd121f360b7e8765189d8b7446e202"


def main():
    assert hash_file(V5/"PROTOCOL_FREEZE.md")==PROTOCOL_HASH
    assert hash_file(ARR)==ARRAY_HASH
    original=pd.read_csv(V5/"verification/SOURCE_HASHES.csv")
    amended=pd.read_csv(V5/"verification/SOURCE_HASHES_AMENDMENT.csv")
    amended2=pd.read_csv(V5/"verification/SOURCE_HASHES_AMENDMENT_02.csv")
    for _,r in original.iterrows():
        p=Path(r.path)
        # The initial graph trainer was amended before cross-factor fitting;
        # the original hash remains as a provenance record for initial cells.
        if p.name in ("train_graph_lag.py","run_stage.sh"):
            continue
        assert p.exists() and hash_file(p)==r.sha256,p
    for _,r in amended.iterrows():
        p=Path(r.path)
        if p.name=="train_graph_lag.py":
            continue
        assert p.exists() and hash_file(p)==r.sha256,p
    for _,r in amended2.iterrows():
        p=Path(r.path);assert p.exists() and hash_file(p)==r.sha256,p
    old=pd.read_csv("final_blr_results/controlled_validation_v4_review_closure/SOURCE_HASHES.csv")
    for _,r in old.iterrows():
        p=Path(r.path);assert p.exists() and hash_file(p)==r.sha256,p
    train=json.loads((V5/"verification/training_verified.json").read_text())
    assert train["new_cells"]==160
    cells=list((V5/"training").rglob("COMPLETE.json"))
    assert len(cells)==160,len(cells)
    scores=pd.read_csv(V5/"metrics/NEW_TEST_SCORES.csv")
    assert len(scores)==240 and set(scores.scored_pairs)=={14583}
    new_pred=list((V5/"predictions").glob("*.npz"))
    assert len(new_pred)==192,len(new_pred)
    for p in new_pred:
        with np.load(p) as z:
            assert len(z["pred"])==14583 and np.isfinite(z["pred"]).all()
            assert np.isfinite(z["truth"]).all()
    check={"GRAPH_TOPOLOGY_CONTRASTS.csv":10,"LAG_INFORMATION_CONTRASTS.csv":10,
           "LAG_MATCHED_GRAPH_CONTRASTS.csv":2,"FAIRNESS_SELECTED_CONTRASTS.csv":6,
           "V5_SEED_LEVEL.csv":140}
    for name,n in check.items():
        d=pd.read_csv(V5/"statistical_analysis"/name)
        assert len(d)==n,(name,len(d))
        assert np.isfinite(d.select_dtypes(include=["number"]).to_numpy()).all(),name
    assert len(pd.read_csv(V5/"ANCHOR_AGE_ALL_METHODS.csv"))==602
    assert len(pd.read_csv(V5/"COMPLETE_CONTRAST_REGISTER.csv"))==26
    assert len(pd.read_csv(V5/"PENALTY_DIAGNOSTICS_COMPLETE.csv"))==31
    assert len(pd.read_csv(V5/"metrics/FAIRNESS_GRADIENT_REPLAY.csv"))==90
    out=dict(status="PASS",protocol_sha256=PROTOCOL_HASH,array_sha256=ARRAY_HASH,
             historical_source_hashes_checked=len(old),v5_source_hashes_checked=len(original)+len(amended)+len(amended2)-3,
             new_cells=len(cells),new_prediction_npz=len(new_pred),score_rows=len(scores),
             new_ensemble_contrasts=28,seed_contrast_rows=140,
             note="exposed test; verification checks reproducibility, not scientific independence")
    (V5/"verification/verification_summary.json").write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps(out,indent=2))


if __name__=="__main__":main()
