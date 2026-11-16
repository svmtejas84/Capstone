#!/usr/bin/env bash
# Resume-safe stage sequencing after the frozen graph study.
set -euo pipefail
root=final_blr_results/controlled_validation_v5

budget_gate() {
  python - "$root" <<'PY'
import json,sys
from pathlib import Path
p=Path(sys.argv[1])/"training"
rows=[json.loads(x.read_text()) for x in p.rglob("COMPLETE.json")]
hours=sum(float(r["elapsed_seconds"]) for r in rows)/3600
bytes_used=sum(x.stat().st_size for x in p.rglob("*") if x.is_file())
print(f"BUDGET_GATE cells={len(rows)} fit_hours={hours:.4f} checkpoint_bytes={bytes_used}",flush=True)
if hours>4 or bytes_used>4*1024**3:raise SystemExit("V5 frozen resource ceiling exceeded")
PY
}

wait_stage() {
  local name=$1 status
  while :; do
    status=$(bash scripts/run_supervised.sh status "$root/logs/$name" | head -1)
    case "$status" in
      COMPLETE) echo "STAGE_COMPLETE $name"; return 0 ;;
      RUNNING*) sleep 30 ;;
      *) echo "STAGE_STOPPED $name: $status" >&2; return 1 ;;
    esac
  done
}

launch_stage() {
  local name=$1
  if [[ ! -f "$root/logs/$name/command.nul" ]]; then
    bash scripts/run_supervised.sh launch "$root/logs/$name" -- bash "$root/scripts/run_stage.sh" "$name" "$root/logs/$name"
  fi
  wait_stage "$name"
  budget_gate
}

wait_stage lag
budget_gate
launch_stage cross
launch_stage fairness
touch "$root/logs/orchestrator/COMPLETE"
