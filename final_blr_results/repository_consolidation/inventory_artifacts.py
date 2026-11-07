"""Read-only artifact inventory for repository consolidation.

Writes only new audit CSVs under this directory. It does not open model weights,
run research code, or mutate existing artifacts.
"""
from __future__ import annotations
import csv, hashlib, subprocess, zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
KEYS=[
"notebooks/production/evaluated_wind_advection.ipynb",
"scripts/benchmark_v2j.py",
"src/stpignn/models_v2.py",
"src/stpignn/physics_v2.py",
"src/stpignn/rgdr.py",
"src/stpignn/rgdr_continuous.py",
"matcher/edge_capacity_da.py",
"router/api/routes.py",
"data/graphs/bangalore_utm_nodes.parquet",
"data/graphs/bangalore_utm_edges.parquet",
"data/processed/graph/partitioned_manifold_64_clusters.pt",
"results/checkpoints_v2c/final_stpignn_corrected_log1p_seed11.pt",
"final_blr_results/final_research_v2r/citywide/station_forecasts/folds/5607/outer/best_model.pt",
"final_blr_results/physics_audit/ensemble_analysis/ensemble_decomposition.csv",
"final_blr_results/final_three_pillars/captum/attribution_tensors.npz",
"final_blr_results/final_three_pillars/captum/v2r_heldout_h6/attribution_tensors.npz",
"final_blr_results/final_research_v2r/citywide/road_predictions/road_predictions_20251008T0700Z.parquet",
"final_blr_results/final_routing_closure/v2t/ROUTING_COMPARISON_RESULTS.csv",
"final_blr_results/ST_PIGNN_COMPLETE_RESEARCH_MONOGRAPH/ST_PIGNN_COMPLETE_RESEARCH_MONOGRAPH.md",
"final_blr_results/ieee_paper_evidence/FINAL_PAPER_EVIDENCE_HANDOFF.md",
"final_blr_results/ieee_publication_assets/FINAL_PUBLICATION_ASSET_HANDOFF.md",
"final_blr_results/second_city_handover/SECOND_CITY_NEXT_SESSION_PROMPT.md",
]

def git(*args):
    return subprocess.run(["git",*args],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL).returncode==0
def digest(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda:f.read(4*1024*1024),b""): h.update(chunk)
    return h.hexdigest()
def row(rel):
    p=ROOT/rel
    tracked=git("ls-files","--error-unmatch","--",rel)
    ignored=not tracked and git("check-ignore","-q","--",rel)
    state="TRACKED" if tracked else "IGNORED" if ignored else "UNTRACKED"
    return {"path":rel,"exists":p.is_file(),"git_state":state,"bytes":p.stat().st_size if p.is_file() else "",
            "sha256":digest(p) if p.is_file() else ""}
def write(name,rows):
    with (OUT/name).open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator="\n");w.writeheader();w.writerows(rows)

if __name__=="__main__":
    OUT.mkdir(exist_ok=True)
    write("KEY_ARTIFACT_HASHES.csv",[row(x) for x in KEYS])
    archives=sorted(p for p in ROOT.rglob("*.zip") if ".git" not in p.parts and ".venv" not in p.parts)
    write("LOCAL_ARCHIVE_HASHES.csv",[row(str(p.relative_to(ROOT))) for p in archives])
    archive_matches=[]
    for archive in archives:
        if not zipfile.is_zipfile(archive): continue
        with zipfile.ZipFile(archive) as z:
            names=z.namelist()
            for rel in KEYS:
                local=ROOT/rel
                if not local.is_file() or git("ls-files","--error-unmatch","--",rel): continue
                # Require a meaningful preserved suffix, not a generic basename.
                suffix=rel.split("final_blr_results/",1)[-1]
                candidates=[n for n in names if n.endswith(rel) or n.endswith(suffix)]
                for member in candidates:
                    h=hashlib.sha256()
                    with z.open(member) as f:
                        for b in iter(lambda:f.read(4*1024*1024),b""):h.update(b)
                    archive_matches.append({"local_path":rel,"archive_path":str(archive.relative_to(ROOT)),
                                            "member_path":member,"local_sha256":digest(local),
                                            "member_sha256":h.hexdigest(),"byte_identical":digest(local)==h.hexdigest()})
    if archive_matches:write("ARCHIVE_MEMBER_MATCHES.csv",archive_matches)
    weights=sorted(p for pat in ("*.pt","*.pth","*.ckpt","*.safetensors") for p in ROOT.rglob(pat)
                   if ".git" not in p.parts and ".venv" not in p.parts)
    states={"TRACKED":0,"UNTRACKED":0,"IGNORED":0}
    for p in weights:
        rel=str(p.relative_to(ROOT))
        state="TRACKED" if git("ls-files","--error-unmatch","--",rel) else "IGNORED" if git("check-ignore","-q","--",rel) else "UNTRACKED"
        states[state]+=1
    (OUT/"WEIGHT_SUMMARY.txt").write_text(f"Local weight-like files: {len(weights)}\n"+"".join(f"{k}: {v}\n" for k,v in states.items()))
    print("key",len(KEYS),"archives",len(archives),"weights",len(weights),states)
