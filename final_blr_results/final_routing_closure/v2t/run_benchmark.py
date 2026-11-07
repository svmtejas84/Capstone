"""Frozen v2t CPU routing scenario benchmark; resumable per batch/scenario."""
from __future__ import annotations
import json, os, time, hashlib, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
import networkx as nx
import numpy as np
import pandas as pd
import osmnx as ox
from pyproj import Transformer

from matcher.commuter_model import Commuter, build_preference_list
from matcher.segment_model import Segment, build_preference_list as segment_prefs
from matcher.gale_shapley import batch_match
from matcher.edge_capacity_da import allocate_shared_edges
from matcher.road_capacity import route_capacity
from scripts.evaluate_routing_gs import load_graph, candidate_routes, route_stats, deferred_acceptance

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
GRAPH=ROOT/'data/processed/evaluations/routing_snapshot.graphml'
SEEDS=(11,23,37); DEMANDS=(12,24,48)
SCENARIOS=('original','uniform_125','spatial_sine','support_distance')
SPEED=15000.0; RMV=3.5

def save_atomic(frame,path):
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix('.tmp.parquet'); frame.to_parquet(tmp,index=False); os.replace(tmp,path)

def scenario_graph(base,name,station_xy):
    g=base.copy()
    for u,v,d in g.edges(data=True):
        c=float(d['predicted_pm25']); x=(g.nodes[u]['x']+g.nodes[v]['x'])/2; y=(g.nodes[u]['y']+g.nodes[v]['y'])/2
        if name=='uniform_125': c*=1.25
        elif name=='spatial_sine': c*=1+0.25*np.sin(x/1000)
        elif name=='support_distance':
            dist=np.sqrt(((station_xy-np.array([x,y]))**2).sum(axis=1)).min()
            c*=1+0.25*min(dist/5000,1)
        d['predicted_pm25']=max(0.,c); d['dose']=d['predicted_pm25']*RMV*d['length']/SPEED
    return g

def run_batch(base,raw_attrs,station_xy,seed,n,name):
    t0=time.perf_counter(); g=scenario_graph(base,name,station_xy)
    nodes=np.array(sorted(max(nx.strongly_connected_components(g),key=len)),dtype=np.int64)
    rng=np.random.default_rng(seed); od=[tuple(map(int,rng.choice(nodes,size=2,replace=False))) for _ in range(n)]
    routes={}; edges={}; prefs={}; ranks={}; route_caps={}; edge_caps={}; options=[]; refs=[]
    commuters=[Commuter(id=f'c{i:03d}',mode='cyclist',id_min=2.4,distance_tolerance_m=8000.) for i in range(n)]
    all_ids=[c.id for c in commuters]
    for i,(s,t) in enumerate(od):
        rs=candidate_routes(g,s,t,3)
        options.append(rs)
        shortest=route_stats(g,nx.astar_path(g,s,t,heuristic=lambda u,v: g.graph['astar_heuristic_scale']*np.hypot(g.nodes[u]['x']-g.nodes[v]['x'],g.nodes[u]['y']-g.nodes[v]['y']),weight='length'))
        min_dose=route_stats(g,nx.shortest_path(g,s,t,weight='dose'))
        refs.append((shortest,min_dose))
        ids=[]
        for j,r in enumerate(rs):
            rid=f'c{i:03d}_r{j}'; ids.append(rid); routes[rid]=r; edges[rid]=r['edges']
            attrs=[raw_attrs[e] for e in r['edges']]
            route_caps[rid]=route_capacity(attrs,travel_time_s=r['time_min']*60)
            ranks[rid]=segment_prefs(Segment(id=rid,cedge_mean=r['dose_ug'],capacity=route_caps[rid]),commuters)
            for e in r['edges']:
                if e not in edge_caps:
                    edge_caps[e]=route_capacity([raw_attrs[e]],travel_time_s=3600*g[e[0]][e[1]]['time_h'])
        prefs[all_ids[i]]=build_preference_list(commuters[i],ids,{r:routes[r]['dose_ug'] for r in ids},{r:routes[r]['distance_m'] for r in ids})
    original=batch_match(all_ids,list(routes),commuter_preferences=prefs,segment_preferences=ranks,segment_capacities=route_caps,max_iterations=n*len(routes))
    corrected=allocate_shared_edges(all_ids,prefs,edges,route_caps,edge_caps,ranks)
    offline=deferred_acceptance(options,edge_caps)
    allocations={'shortest':{all_ids[i]:refs[i][0] for i in range(n)},'fastest':{all_ids[i]:refs[i][0] for i in range(n)},
       'minimum_dose':{all_ids[i]:refs[i][1] for i in range(n)},
       'original_gs':{c:routes.get(original.get(c)) for c in all_ids},
       'corrected_da':{c:routes.get(corrected.get(c)) for c in all_ids},
       'offline_bundle':{all_ids[i]:offline.get(i) for i in range(n)}}
    rows=[]; runtime=time.perf_counter()-t0
    for method,assigned in allocations.items():
        occupancy={e:0 for e in edge_caps}
        for r in assigned.values():
            if r:
                for e in r['edges']: occupancy[e]+=1
        violations=sum(occupancy[e]>edge_caps[e] for e in occupancy)
        for i,c in enumerate(all_ids):
            r=assigned[c]
            rows.append(dict(seed=seed,demand=n,scenario=name,method=method,request_id=c,source=od[i][0],target=od[i][1],
                assigned=r is not None,route_id=(next((rid for rid,z in routes.items() if z is r),'') if r else ''),
                path=json.dumps(r['path']) if r else '[]',edges=json.dumps(r['edges']) if r else '[]',
                distance_m=r['distance_m'] if r else np.nan,time_min=r['time_min'] if r else np.nan,
                dose_ug=r['dose_ug'] if r else np.nan,edge_violations=violations,
                saturated_edges=sum(occupancy[e]==edge_caps[e] for e in occupancy),
                max_utilization=max((occupancy[e]/edge_caps[e] for e in occupancy if edge_caps[e]>0),default=0),
                batch_runtime_s=runtime))
    return pd.DataFrame(rows)

def main():
    assert hashlib.sha256(GRAPH.read_bytes()).hexdigest()=='38e2a46792e9209af57e9c71fb17f6768e0117016e978ebc280ba96241647810'
    base=load_graph(GRAPH,None); raw=ox.load_graphml(GRAPH)
    raw_attrs={(u,v):dict(raw[u][v][base[u][v]['key']]) for u,v in base.edges}
    st=pd.read_csv(ROOT/'results/stations_v2.csv'); transformer=Transformer.from_crs('EPSG:4326','EPSG:32643',always_xy=True)
    sx,sy=transformer.transform(st.longitude.to_numpy(),st.latitude.to_numpy()); station_xy=np.column_stack((sx,sy))
    parts=[]
    for name in SCENARIOS:
      for seed in SEEDS:
       for n in DEMANDS:
        path=OUT/'batches'/f'{name}_{seed}_{n}.parquet'
        if not path.exists(): save_atomic(run_batch(base,raw_attrs,station_xy,seed,n,name),path)
        parts.append(pd.read_parquet(path))
    all_rows=pd.concat(parts,ignore_index=True)
    save_atomic(all_rows,OUT/'ROUTING_PER_REQUEST_RESULTS.parquet')
    summary=all_rows.groupby(['scenario','seed','demand','method'],as_index=False).agg(
        requests=('request_id','size'),assigned=('assigned','sum'),mean_distance_m=('distance_m','mean'),median_distance_m=('distance_m','median'),
        mean_time_min=('time_min','mean'),median_time_min=('time_min','median'),mean_dose_ug=('dose_ug','mean'),median_dose_ug=('dose_ug','median'),
        edge_violations=('edge_violations','max'),saturated_edges=('saturated_edges','max'),max_utilization=('max_utilization','max'),
        runtime_s=('batch_runtime_s','max'),route_diversity=('path','nunique'))
    summary['unassigned']=summary.requests-summary.assigned; summary['success_rate']=summary.assigned/summary.requests
    summary.to_csv(OUT/'ROUTING_COMPARISON_RESULTS.csv',index=False)
    summary[['scenario','seed','demand','method','edge_violations','saturated_edges','max_utilization','assigned','unassigned']].to_csv(OUT/'ROUTING_CAPACITY_METRICS.csv',index=False)
    summary.loc[summary.scenario!='original'].to_csv(OUT/'ROUTING_SENSITIVITY_RESULTS.csv',index=False)
    (OUT/'COMPLETE').write_text(f'batches={len(parts)} rows={len(all_rows)}\n')
    print(f'batches={len(parts)} rows={len(all_rows)}')

if __name__=='__main__': main()
