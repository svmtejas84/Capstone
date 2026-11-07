"""Read-only checks for the Git-integrated source and host-local artifacts."""
from __future__ import annotations
import argparse, csv, hashlib, json, subprocess
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
REQUIRED=[
    "notebooks/production/evaluated_wind_advection.ipynb",
    "src/stpignn/models_v2.py", "src/stpignn/physics_v2.py",
    "src/stpignn/rgdr.py", "src/stpignn/rgdr_continuous.py",
    "matcher/edge_capacity_da.py", "router/api/routes.py",
    "final_blr_results/final_routing_closure/v2t/ROUTING_FINAL_VERDICT.md",
    "final_blr_results/ST_PIGNN_COMPLETE_RESEARCH_MONOGRAPH/ST_PIGNN_COMPLETE_RESEARCH_MONOGRAPH.md",
    "final_blr_results/ieee_paper_evidence/FINAL_PAPER_EVIDENCE_HANDOFF.md",
    "final_blr_results/ieee_publication_assets/FINAL_PUBLICATION_ASSET_HANDOFF.md",
    "final_blr_results/second_city_handover/SECOND_CITY_NEXT_SESSION_PROMPT.md",
]
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return h.hexdigest()
def rows(name):
    with (HERE/name).open(newline='') as f:return list(csv.DictReader(f))
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--artifact-root',type=Path,default=ROOT)
    args=ap.parse_args(); artifact_root=args.artifact_root.resolve()
    absent=[p for p in REQUIRED if not (ROOT/p).is_file()]
    if absent:raise AssertionError(f'Missing tracked paths: {absent}')
    checked=0
    for name in ('KEY_ARTIFACT_HASHES.csv','LOCAL_ARCHIVE_HASHES.csv'):
        for row in rows(name):
            p=artifact_root/row['path']
            if row['exists']=='True':
                if not p.is_file() or sha(p)!=row['sha256']:raise AssertionError(f'Artifact changed: {p}')
                checked+=1
    for row in rows('ARCHIVE_MEMBER_MATCHES.csv'):
        if row['byte_identical']!='True' or row['local_sha256']!=row['member_sha256']:
            raise AssertionError(f'Archive member mismatch: {row}')
    mon=json.loads((ROOT/'final_blr_results/ST_PIGNN_COMPLETE_RESEARCH_MONOGRAPH/reproducibility/verification.json').read_text())
    for key in ('source_hash_mismatches','appendix_source_mismatches','table_hash_mismatches','figure_hash_mismatches','broken_authored_links'):
        if mon[key] not in (0, []):raise AssertionError(f'Monograph {key}={mon[key]}')
    if mon['volumes']!=16 or mon['appendices']!=15:raise AssertionError('Monograph volume count')
    pub=ROOT/'final_blr_results/ieee_publication_assets'
    fig=json.loads((pub/'source_data/figure_manifest.json').read_text())
    with (pub/'tables/table_manifest.csv').open(newline='') as f: tab=list(csv.DictReader(f))
    if len(fig)!=10 or len(tab)!=10:raise AssertionError('Publication asset count')
    for x in fig:
        for ext in ('png','pdf','svg'):
            if not (pub/x[ext]).is_file():raise AssertionError(f'Missing figure {x[ext]}')
    checked_pub=0
    for row in csv.DictReader((pub/'verification/CHECKSUMS.csv').open(newline='')):
        p=artifact_root/'final_blr_results/ieee_publication_assets'/row['path']
        if not p.exists():
            if row['path']=='source_data/F07_snapshot_node_data.csv':continue
            raise AssertionError(f'Missing publication copy {p}')
        if sha(p)!=row['sha256']:raise AssertionError(f'Publication file changed {p}')
        checked_pub+=1
    print(json.dumps({'status':'PASS','required_tracked_paths':len(REQUIRED),
        'artifact_sha256_checked':checked,'archive_member_matches':len(rows('ARCHIVE_MEMBER_MATCHES.csv')),
        'monograph_volumes':16,'monograph_appendices':15,'publication_figures':len(fig),
        'publication_tables':len(tab),'publication_files_hashed':checked_pub},indent=2))
if __name__=='__main__':main()
