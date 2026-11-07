"""Recompute frozen paired and scenario summaries from saved per-request rows."""
from pathlib import Path
import pandas as pd
import numpy as np

ROOT=Path(__file__).resolve().parent
d=pd.read_parquet(ROOT/'ROUTING_PER_REQUEST_RESULTS.parquet')
keys=['scenario','seed','demand','request_id']
p=d.pivot(index=keys,columns='method',values=['assigned','dose_ug','time_min','distance_m','path'])
rows=[]
for (scenario,seed,n), frame in p.groupby(level=[0,1,2]):
    for candidate in ['original_gs','corrected_da','offline_bundle','minimum_dose','fastest']:
        for control in ['shortest','fastest','minimum_dose']:
            if candidate==control: continue
            common=frame[('assigned',candidate)].astype(bool)&frame[('assigned',control)].astype(bool)
            x=frame.loc[common]
            dose_delta=(x[('dose_ug',candidate)]-x[('dose_ug',control)]).astype(float)
            time_delta=(x[('time_min',candidate)]-x[('time_min',control)]).astype(float)
            ref_dose=x[('dose_ug',control)].astype(float).mean(); ref_time=x[('time_min',control)].astype(float).mean()
            rows.append(dict(scenario=scenario,seed=seed,demand=n,candidate=candidate,control=control,
                submitted=len(frame),common_admitted=int(common.sum()),
                mean_paired_dose_delta_ug=float(dose_delta.mean()),
                dose_delta_pct=float(100*dose_delta.mean()/ref_dose) if ref_dose else np.nan,
                mean_paired_time_delta_min=float(time_delta.mean()),
                time_overhead_pct=float(100*time_delta.mean()/ref_time) if ref_time else np.nan,
                same_path_fraction=float((x[('path',candidate)]==x[('path',control)]).mean())))
paired=pd.DataFrame(rows); paired.to_csv(ROOT/'PAIRED_COMPARISONS.csv',index=False)
sens=[]
base=d[d.scenario=='original'].set_index(['seed','demand','request_id','method'])
for scenario in sorted(set(d.scenario)-{'original'}):
    other=d[d.scenario==scenario].set_index(['seed','demand','request_id','method'])
    for method in sorted(d.method.unique()):
        b=base.xs(method,level='method'); o=other.xs(method,level='method')
        assert b.index.equals(o.index)
        sens.append(dict(scenario=scenario,method=method,requests=len(b),
            assignment_stability=float((b.assigned.values==o.assigned.values).mean()),
            route_stability=float((b.path.values==o.path.values).mean()),
            mean_dose_change_ug=float((o.dose_ug.values-b.dose_ug.values).mean()),
            mean_time_change_min=float((o.time_min.values-b.time_min.values).mean()),
            capacity_violations=int(o.edge_violations.max()),
            unassigned=int((~o.assigned.astype(bool)).sum())))
pd.DataFrame(sens).to_csv(ROOT/'SENSITIVITY_STABILITY.csv',index=False)
assert len(d)==6048 and len(paired)==36*5*2+36*3  # 5 candidates, three controls minus self
print('per request',len(d),'paired',len(paired),'sensitivity',len(sens))
