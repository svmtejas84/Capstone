#!/bin/sh
set -eu
cd /home/jupyter-1nt23cb058/Capstone
exec 9>results/codex_log/runs/dem_v2h.lock
flock -n 9 || exit 0
until python -u -m scripts.dem_study_v2h >> results/codex_log/runs/dem_v2h.log 2>&1; do
  printf '%s DEM runner exited; restarting cached horizon/variant/model/seed rows\n' "$(date -u +%FT%TZ)" >> results/codex_log/runs/dem_v2h.log
  sleep 20
done
