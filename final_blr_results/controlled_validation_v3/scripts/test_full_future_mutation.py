"""Rebuild candidate features twice, perturbing raw future rows in memory only."""
import json
import numpy as np
import pandas as pd
import src.stpignn.data_v2 as dv
from final_blr_results.controlled_validation_v3.scripts.smoke_gpu import V3


def main():
    issue=pd.Timestamp("2025-10-01T12:00:00Z")
    cfg="configs/data_v2.yaml"
    baseline,_=dv.build(cfg,weather_half_hour_rule=True,weather_cutoff_safe=True)
    original=dv._load_raw_table
    changed=dict(station_rows=0,weather_rows=0)
    def modified(pattern,skip_meta=False):
        frame,paths=original(pattern,skip_meta=skip_meta)
        frame=frame.copy()
        if "stations" in pattern:
            times=pd.to_datetime(frame["time"],utc=True)
            mask=times>issue
            changed["station_rows"]=int(mask.sum())
            frame.loc[mask,"value"]=0.0
        elif "weather" in pattern:
            times=dv.weather_utc_half_hours(frame["time"])
            mask=times>issue
            changed["weather_rows"]=int(mask.sum())
            for name,value in (("temperature_2m",25.),("relative_humidity_2m",50.),("wind_speed_10m",2.),("wind_direction_10m",180.)):
                if name in frame:frame.loc[mask,name]=value
        return frame,paths
    dv._load_raw_table=modified
    try:
        after,_=dv.build(cfg,weather_half_hour_rule=True,weather_cutoff_safe=True)
    finally:
        dv._load_raw_table=original
    ix=baseline.times.get_loc(issue)
    assert changed["station_rows"]>0 and changed["weather_rows"]>0
    base_causal=baseline.features.copy();after_causal=after.features.copy()
    base_causal[1:,:,:5]=baseline.features[:-1,:,:5]
    after_causal[1:,:,:5]=after.features[:-1,:,:5]
    base_causal[0,:,:5]=0.;after_causal[0,:,:5]=0.
    bad=~np.isclose(base_causal[:ix+1],after_causal[:ix+1],rtol=0,atol=0,equal_nan=True)
    if bad.any():
        first=np.argwhere(bad)[0]
        print(json.dumps(dict(first_changed_hour=int(first[0]),first_changed_station=int(first[1]),
            first_changed_feature=int(first[2]),first_utc=str(baseline.times[first[0]]),
            before=float(baseline.features[tuple(first)]),after=float(after.features[tuple(first)]),
            changed_counts_by_channel=bad.sum(axis=(0,1)).tolist()),indent=2),flush=True)
    assert not bad.any(),"Post-issue raw mutation changed an earlier feature"
    assert np.array_equal(baseline.imputed_target[:ix],after.imputed_target[:ix])
    assert np.array_equal(baseline.observed_mask[:ix],after.observed_mask[:ix])
    assert np.array_equal(baseline.observed_target[:ix],after.observed_target[:ix],equal_nan=True)
    result=dict(issue_utc=issue.isoformat(),checked_hourly_rows=ix+1,changed_raw_rows=changed,
                causal_feature_tensor_through_issue_unchanged=True,earlier_imputed_target_unchanged=True,
                source_artifacts_written=False)
    p=V3/"verification/full_future_mutation.json";p.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))


if __name__=="__main__":main()
