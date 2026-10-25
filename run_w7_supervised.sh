#!/bin/bash
cd /home/jupyter-1nt23cb058/Capstone
exec 9>/tmp/w7.lock
flock -n 9 || { echo "already running"; exit 0; }
until python -u -m scripts.lambda_sweep_v2g >> results/codex_log/runs/w7_lambda_v2g.log 2>&1; do
  echo "restart $(date)" >> results/codex_log/runs/w7_supervisor.log
  sleep 30
done
echo "FINISHED $(date)" >> results/codex_log/runs/w7_supervisor.log
