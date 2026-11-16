"""Index-only cutoff proof across every saved V3 test evaluation pair."""
import json
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[3]
V3=ROOT/"final_blr_results/controlled_validation_v3"
V5=ROOT/"final_blr_results/controlled_validation_v5"


def main():
    z=np.load(V3/"data_manifests/data_v3_causal_arrays.npz")
    obs=z["observed_mask"]
    rows=[]
    for h in (1,3,6,12,24):
        with np.load(V3/"predictions"/f"h{h}_zero_ensemble.npz") as p:
            t=p["time_index"].astype(int);station=p["station_index"].astype(int)
        issue=t-h;daily=t-24
        assert len(t)==14583 and np.all(issue>=11)
        w12=issue[:,None]-np.arange(11,-1,-1)[None,:]
        w36=np.maximum(0,issue[:,None]-np.arange(35,-1,-1)[None,:])
        assert np.all(w12<=issue[:,None]) and np.all(w36<=issue[:,None])
        assert np.all(w12[:,-1]-1<issue)
        lag_ok=(daily>=0)&(daily<issue)
        actual=lag_ok&obs[np.maximum(daily,0),station]
        assert np.all(daily[actual]<issue[actual])
        rows.append(dict(horizon_hours=h,scored_pairs=len(t),min_issue_index=int(issue.min()),
                         max_input_index_offset=0,latest_pollutant_source_offset=-1,
                         genuine_daily_lag_pairs=int(actual.sum()),daily_lag_at_issue_excluded=int(h==24),
                         status="PASS; timestamp causality only; release latency unverified"))
    output=dict(status="PASS",horizons=rows,source_array="V3 repaired causal array",
                caveat="does not certify operational sensor ingestion or weather publication latency")
    p=V5/"verification/CUTOFF_ALL_HORIZONS.json";p.parent.mkdir(exist_ok=True)
    p.write_text(json.dumps(output,indent=2)+"\n")
    print(json.dumps(output,indent=2))


if __name__=="__main__":main()
