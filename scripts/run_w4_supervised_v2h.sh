#!/bin/sh
set -eu
cd /home/jupyter-1nt23cb058/Capstone
exec 9>results/codex_log/runs/w4_v2h.lock
flock -n 9 || exit 0
until python -u -m scripts.lowdata_v2h >> results/codex_log/runs/w4_v2h.log 2>&1; do
  printf '%s W4 runner exited; restarting checkpointed rows\n' "$(date -u +%FT%TZ)" >> results/codex_log/runs/w4_v2h.log
  sleep 20
done
