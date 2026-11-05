#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../../.."
export MPLCONFIGDIR="${TMPDIR:-/tmp}/v2l-matplotlib"
mkdir -p "$MPLCONFIGDIR"
python -m final_blr_results.physics_audit.reproducibility.run_physics_audit
python -m final_blr_results.physics_audit.physical_diagnostics.compute_physical_diagnostics
