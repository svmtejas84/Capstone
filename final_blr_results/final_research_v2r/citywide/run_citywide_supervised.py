"""Invoke citywide generation and atomically satisfy the supervised runner contract."""
from __future__ import annotations
import subprocess,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
RUN=ROOT/"final_blr_results/final_research_v2r/citywide/road_predictions/runs/full_city"
SCRIPT=Path(__file__).with_name("run_citywide_neural.py")
def main():
 p=subprocess.run([sys.executable,str(SCRIPT)],cwd=ROOT,check=False)
 if p.returncode:raise SystemExit(p.returncode)
 marker=RUN/"COMPLETE";tmp=RUN/"COMPLETE.tmp";tmp.write_text("full-city estimates and integrity checks completed\n");tmp.replace(marker)
if __name__=="__main__":main()
