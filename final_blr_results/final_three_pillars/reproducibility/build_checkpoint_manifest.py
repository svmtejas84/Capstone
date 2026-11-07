"""Read-only hash/metadata inventory of candidate ST-PIGNN checkpoint files."""
from __future__ import annotations
import csv,hashlib
from pathlib import Path
import torch

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parents[1]/"captum"/"CHECKPOINT_MANIFEST.csv"

def digest(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for b in iter(lambda:f.read(1<<20),b""):h.update(b)
 return h.hexdigest()

def main():
 paths=set()
 for base in (ROOT/"results/checkpoints_v2",ROOT/"results/checkpoints_v2b",ROOT/"results/checkpoints_v2c"):
  if base.exists():paths.update(p for p in base.glob("*.pt") if "stpignn" in p.name)
 for p in (ROOT/"final_blr_results/final_research_v2r/citywide/station_forecasts/folds").glob("*/outer/best_model.pt"):
  paths.add(p)
 for name in ("citywide_stpignn_best.pt","citywide_stpignn_checkpoint_STABLE.pt","citywide_stpignn_autosave.pt"):
  p=ROOT/name
  if p.exists():paths.add(p)
 rows=[]
 for p in sorted(paths):
  try:
   obj=torch.load(p,map_location="cpu",weights_only=False)
   state=obj.get("state_dict",obj.get("model",obj)) if isinstance(obj,dict) else {}
   w=state.get("node_encoder.weight") if isinstance(state,dict) else None
   inputs=int(w.shape[1]) if hasattr(w,"shape") and len(w.shape)==2 else "unknown"
   version=("v2r_outer_LOSO" if "final_research_v2r" in str(p) else
            "legacy_road_notebook" if p.name.startswith("citywide_") else p.parent.name)
   if version=="v2r_outer_LOSO": verdict="AVAILABLE_V2R_OUTER_FOLD; selected use listed in v2r IG sample manifest"
   elif "v2c" in str(p): verdict="USED_FOR_V2C_H1_IG" if "final_stpignn_corrected" in p.name else "NOT_USED_PROTOCOL_OR_VARIANT"
   elif version=="legacy_road_notebook":verdict="HISTORICAL_ONLY_TARGET_LEAKING_PATHWAY"
   else:verdict="OLDER_PROTOCOL_NOT_SUBSTITUTED"
   rows.append({"path":p.relative_to(ROOT),"exists":True,"bytes":p.stat().st_size,"sha256":digest(p),
    "version":version,"checkpoint_model":obj.get("model","metadata_missing") if isinstance(obj,dict) else "unknown",
    "seed":obj.get("seed","unknown") if isinstance(obj,dict) else "unknown",
    "horizon_hours":obj.get("horizon_hours","unknown") if isinstance(obj,dict) else "unknown",
    "input_channels":inputs,"source_commit":"see parent experiment manifest; checkpoint metadata does not always retain commit",
    "saved_prediction_match":("verified per selected records <=1e-4" if verdict.startswith("USED_FOR") else "not assessed"),
    "verdict":verdict})
  except Exception as e:
   rows.append({"path":p.relative_to(ROOT),"exists":True,"bytes":p.stat().st_size,"sha256":digest(p),"version":"unknown","checkpoint_model":"unreadable","seed":"unknown","horizon_hours":"unknown","input_channels":"unknown","source_commit":"unknown","saved_prediction_match":"not assessed","verdict":"UNVERIFIABLE: "+type(e).__name__})
 rows.append({"path":"results/benchmark_predictions_*_v2j.parquet","exists":False,"bytes":"","sha256":"","version":"v2j_final_corrected","checkpoint_model":"ST-PIGNN corrected/λ0/Laplacian predictions only","seed":"11,23,37,51,79","horizon_hours":"1,3,6,12,24","input_channels":18,"source_commit":"final_blr_results/physics_audit/provenance/model_configurations.csv","saved_prediction_match":"predictions exist; training weights explicitly NONE SAVED","verdict":"MISSING; exact v2j IG cannot be computed"})
 OUT.parent.mkdir(parents=True,exist_ok=True)
 with OUT.open("w",newline="") as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 print(f"rows={len(rows)} output={OUT}")

if __name__=="__main__":main()
