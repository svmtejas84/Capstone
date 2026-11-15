#!/usr/bin/env bash
set -euo pipefail
stage=$1
run_dir=$2
export PYTHONPATH=.
export MPLCONFIGDIR=/tmp/mpl_v5
case "$stage" in
  graph|lag) python final_blr_results/controlled_validation_v5/scripts/train_graph_lag.py --stage "$stage" ;;
  fairness) python final_blr_results/controlled_validation_v5/scripts/train_fairness.py --stage final ;;
  *) echo "unknown stage: $stage" >&2; exit 2 ;;
esac
touch "$run_dir/COMPLETE"
