"""Independent scan of saved route continuity and shared-edge occupancy."""
from pathlib import Path
import json
import osmnx as ox
import pandas as pd
from matcher.road_capacity import route_capacity

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
raw=ox.load_graphml(ROOT/'data/processed/evaluations/routing_snapshot.graphml')
d=pd.read_parquet(OUT/'ROUTING_PER_REQUEST_RESULTS.parquet')
invalid=0; violations=0; groups=0
for _,part in d.groupby(['scenario','seed','demand','method']):
    groups+=1; occupied={}
    for row in part.itertuples(index=False):
        edges=[tuple(e) for e in json.loads(row.edges)]
        path=json.loads(row.path)
        if bool(row.assigned):
            if len(path)<2 or edges!=list(zip(path[:-1],path[1:])) or any(not raw.has_edge(u,v) for u,v in edges):
                invalid+=1
            for e in edges: occupied[e]=occupied.get(e,0)+1
        elif edges or path:
            invalid+=1
    for (u,v),count in occupied.items():
        edge_attrs=min(raw[u][v].values(),key=lambda a: float(a['length']))
        length=float(edge_attrs['length'])
        cap=route_capacity([edge_attrs],travel_time_s=length/15000*3600)
        violations+=int(count>cap)
assert invalid==0
assert violations==0
result={'saved_rows':len(d),'method_batch_scenario_groups':groups,
        'invalid_routes':invalid,'shared_directed_edge_capacity_violations':violations,
        'note':'Independent output scan; road-class capacity remains an assumed scenario constraint.'}
(OUT/'OUTPUT_INTEGRITY.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
