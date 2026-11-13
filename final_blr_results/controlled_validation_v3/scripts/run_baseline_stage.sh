#!/usr/bin/env bash
set -euo pipefail
stage=$1
run_dir=$2
case "$stage" in selection|final) ;; *) exit 2;; esac
PYTHONPATH=. python final_blr_results/controlled_validation_v3/scripts/train_baselines.py --stage "$stage"
printf 'COMPLETE\n' > "$run_dir/COMPLETE.tmp"
mv "$run_dir/COMPLETE.tmp" "$run_dir/COMPLETE"
