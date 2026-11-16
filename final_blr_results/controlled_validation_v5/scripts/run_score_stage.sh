#!/usr/bin/env bash
set -euo pipefail
run_dir=$1
export PYTHONPATH=.
export MPLCONFIGDIR=/tmp/mpl_v5
test -f final_blr_results/controlled_validation_v5/verification/training_verified.json
python final_blr_results/controlled_validation_v5/scripts/verify_and_score.py --stage score
touch "$run_dir/COMPLETE"
