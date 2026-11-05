"""Short CPU-only recovery smoke test; never imports training data."""
import os
from pathlib import Path
import subprocess
import sys
import time

run=Path(sys.argv[1]); run.mkdir(parents=True,exist_ok=True)
marker=run/'dummy_first_failure'
if not marker.exists():
    marker.write_text('first attempt failed deliberately\n')
    print('intentional first failure',flush=True)
    sys.exit(23)
source=run/'dummy_progress.tmp'
start=0
if (run/'checkpoint.bin').exists():
    start=int((run/'checkpoint.bin').read_text())
for i in range(start,3):
    source.write_text(str(i+1))
    subprocess.check_call([str(Path(__file__).with_name('run_supervised.sh')),'checkpoint',str(run),str(source)])
    print('checkpoint',i+1,flush=True)
    time.sleep(float(os.getenv('DUMMY_SLEEP_SECONDS', '.4')))
(run/'COMPLETE.tmp').write_text('done\n')
os.replace(run/'COMPLETE.tmp',run/'COMPLETE')
