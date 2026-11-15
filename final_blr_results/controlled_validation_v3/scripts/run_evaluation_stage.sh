#!/usr/bin/env bash
# Frozen one-time exposed-test scoring; each Python evaluator atomically caches
# completed per-seed predictions so interrupted runs do not rescore them.
set -euo pipefail
[[ $# -eq 2 ]] || { echo 'usage: run_evaluation_stage.sh {controls|baselines} RUN_DIR' >&2; exit 2; }
stage=$1
run_dir=$2
case "$stage" in
  controls)
    PYTHONPATH=. python final_blr_results/controlled_validation_v3/scripts/evaluate_controls.py
    ;;
  baselines)
    PYTHONPATH=. python final_blr_results/controlled_validation_v3/scripts/evaluate_baselines.py
    ;;
  *) echo "unknown stage: $stage" >&2; exit 2;;
esac
touch "$run_dir/COMPLETE"
