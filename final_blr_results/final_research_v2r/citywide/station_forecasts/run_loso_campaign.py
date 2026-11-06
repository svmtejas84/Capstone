"""Serial, restartable 15-fold × two-block station forecast campaign."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[4]
BASE=Path(__file__).resolve().parent


def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument("--run-dir",required=True)
    ap.add_argument("--limit-folds",type=int,default=15)
    args=ap.parse_args()
    run=Path(args.run_dir).resolve();run.mkdir(parents=True,exist_ok=True)
    ids=np.load(ROOT/"results/data_v2j_arrays.npz")["station_ids"].astype(int).tolist()
    assert len(ids)==15
    started=time.monotonic();done=[]
    for sid in ids[:args.limit_folds]:
        for part in ("inner","outer"):
            fold=BASE/"folds"/str(sid)/part
            fold.mkdir(parents=True,exist_ok=True)
            if (fold/"COMPLETE").exists():
                assert (fold/"best_model.pt").exists() and (fold/"station_forecasts.parquet").exists()
                print(f"SKIP COMPLETE sid={sid} part={part}",flush=True)
            else:
                cmd=[sys.executable,str(BASE/"train_loso_fold.py"),"--run-dir",str(fold),
                     "--exclude-station",str(sid)]
                if part=="inner":cmd.append("--inner")
                with (fold/"worker.log").open("a") as log:
                    subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
                assert (fold/"COMPLETE").exists()
            if part=="outer" and not (fold/"station_forecasts_all.parquet").exists():
                subprocess.run([sys.executable,str(BASE/"export_outer_all.py"),"--station",str(sid)],
                               cwd=ROOT,check=True)
            done.append({"station_id":sid,"part":part,"summary":str((fold/"summary.json").relative_to(ROOT))})
            (run/"progress.json.tmp").write_text(json.dumps(done,indent=2)+"\n")
            (run/"progress.json.tmp").replace(run/"progress.json")
            print(f"DONE sid={sid} part={part} elapsed={time.monotonic()-started:.1f}s",flush=True)
            if time.monotonic()-started>3600:
                raise TimeoutError("one-hour fold-campaign budget reached; preserve completed fold markers")
    (run/"COMPLETE.tmp").write_text(f"{len(done)} fold cells complete\n")
    (run/"COMPLETE.tmp").replace(run/"COMPLETE")


if __name__=="__main__":main()
