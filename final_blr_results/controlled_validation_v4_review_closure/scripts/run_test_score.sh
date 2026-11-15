#!/usr/bin/env bash
set -euo pipefail
run_dir=$1
PYTHONPATH=. python final_blr_results/controlled_validation_v4_review_closure/scripts/verify_and_score.py --stage score
touch "$run_dir/COMPLETE"
