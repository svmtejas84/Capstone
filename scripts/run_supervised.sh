#!/usr/bin/env bash
# Detached, single-instance, bounded supervisor. No experiment is launched by this file itself.
set -euo pipefail

usage() { echo 'usage: run_supervised.sh {launch|resume|status|stop|checkpoint|verify} RUN_DIR [-- COMMAND ...|SOURCE_FILE]' >&2; exit 2; }
[[ $# -ge 2 ]] || usage
action=$1; run_dir=$2; shift 2
mkdir -p "$run_dir"
run_dir=$(cd "$run_dir" && pwd -P)
lock="$run_dir/supervisor.lock"
pidfile="$run_dir/supervisor.pid"

alive() {
  [[ -s "$pidfile" ]] || return 1
  local pid
  pid=$(cat "$pidfile")
  [[ "$pid" =~ ^[0-9]+$ ]] && kill -0 "$pid" 2>/dev/null
}

verify_checkpoint() {
  local file="$run_dir/checkpoint.bin" sum="$run_dir/checkpoint.bin.sha256"
  [[ ! -e "$file" && ! -e "$sum" ]] && return 0
  [[ -f "$file" && -f "$sum" ]] || return 1
  (cd "$run_dir" && sha256sum -c checkpoint.bin.sha256 >/dev/null)
}

start_worker() {
  if alive; then echo "RUNNING pid=$(cat "$pidfile")"; return 1; fi
  if ! (flock -n 9) 9>"$lock"; then echo 'RUNNING lock held'; return 1; fi
  verify_checkpoint || { echo 'INVALID checkpoint; preserve files and repair before resume' >&2; return 1; }
  if [[ -f "$run_dir/COMPLETE" ]]; then echo 'COMPLETE'; return 0; fi
  setsid nohup "$0" _worker "$run_dir" >>"$run_dir/supervisor.log" 2>&1 </dev/null &
  echo "STARTED pid=$!"
}

case "$action" in
  launch)
    [[ ${1:-} == -- && $# -ge 2 ]] || usage
    shift
    if [[ -e "$run_dir/command.nul" ]]; then echo 'Existing run; use resume' >&2; exit 2; fi
    printf '%s\0' "$@" >"$run_dir/command.nul.tmp"
    mv "$run_dir/command.nul.tmp" "$run_dir/command.nul"
    printf '%s\n' "${SUPERVISED_MAX_RESTARTS:-2}" >"$run_dir/max_restarts"
    python - "$run_dir" "$@" <<'PY'
import datetime,json,os,platform,subprocess,sys,tempfile
from pathlib import Path
p=Path(sys.argv[1]);cmd=sys.argv[2:]
def command(args):
 try:return subprocess.check_output(args,stderr=subprocess.DEVNULL,text=True,timeout=5).strip()
 except Exception:return None
try:
 import torch
 gpu=torch.cuda.get_device_name(0) if torch.cuda.is_available() else None
 torch_version=torch.__version__
except Exception:gpu=None;torch_version=None
d=dict(git_commit=command(['git','rev-parse','HEAD']),configuration=os.getenv('EXPERIMENT_CONFIG'),
 command=cmd,random_seeds=os.getenv('EXPERIMENT_SEEDS'),python=sys.version,
 python_executable=sys.executable,platform=platform.platform(),torch=torch_version,gpu=gpu,
 working_directory=os.getcwd(),
 start_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),output_directory=str(p),
 max_restarts=int((p/'max_restarts').read_text()),checkpoint_contract='checkpoint.bin plus checkpoint.bin.sha256; COMPLETE marker')
q=p/'execution_manifest.json.tmp';q.write_text(json.dumps(d,indent=2)+'\n');q.replace(p/'execution_manifest.json')
PY
    start_worker
    ;;
  resume) [[ -f "$run_dir/command.nul" ]] || usage; start_worker ;;
  status)
    if alive; then echo "RUNNING pid=$(cat "$pidfile")"; elif [[ -f "$run_dir/COMPLETE" ]]; then echo 'COMPLETE'; else echo 'STOPPED'; fi
    [[ -f "$run_dir/attempts.log" ]] && tail -3 "$run_dir/attempts.log" || true
    ;;
  stop)
    if alive; then pid=$(cat "$pidfile"); kill -TERM -- "-$pid" 2>/dev/null || kill -TERM "$pid"; echo "STOP_REQUESTED pid=$pid"; else echo 'NOT_RUNNING'; fi
    ;;
  checkpoint)
    [[ $# -eq 1 && -f "$1" ]] || usage
    cp "$1" "$run_dir/checkpoint.bin.tmp"
    (cd "$run_dir" && sha256sum checkpoint.bin.tmp | sed 's/checkpoint.bin.tmp/checkpoint.bin/' >checkpoint.bin.sha256.tmp)
    mv "$run_dir/checkpoint.bin.tmp" "$run_dir/checkpoint.bin"
    mv "$run_dir/checkpoint.bin.sha256.tmp" "$run_dir/checkpoint.bin.sha256"
    ;;
  verify) verify_checkpoint && echo 'CHECKPOINT_VALID' || { echo 'CHECKPOINT_INVALID'; exit 1; } ;;
  _worker)
    exec 9>"$lock"
    flock -n 9 || { echo 'duplicate worker blocked'; exit 75; }
    echo "$$" >"$pidfile"
    trap 'rm -f "$pidfile"' EXIT
    cd "$(python - "$run_dir/execution_manifest.json" <<'PY'
import json,sys
print(json.load(open(sys.argv[1]))['working_directory'])
PY
)"
    mapfile -d '' -t cmd <"$run_dir/command.nul"
    limit=$(cat "$run_dir/max_restarts")
    [[ "$limit" =~ ^[0-9]+$ ]] || exit 2
    for ((attempt=0; attempt<=limit; attempt++)); do
      verify_checkpoint || { echo 'checkpoint integrity failure' >>"$run_dir/attempts.log"; exit 74; }
      [[ -f "$run_dir/COMPLETE" ]] && exit 0
      stamp=$(date -u +%Y%m%dT%H%M%SZ)
      log="$run_dir/attempt_${attempt}_${stamp}.log"
      echo "$(date -u +%FT%TZ) START attempt=$attempt log=$log" >>"$run_dir/attempts.log"
      set +e
      "${cmd[@]}" >"$log" 2>&1
      code=$?
      set -e
      echo "$(date -u +%FT%TZ) EXIT attempt=$attempt code=$code" >>"$run_dir/attempts.log"
      if [[ $code -eq 0 && -f "$run_dir/COMPLETE" ]]; then exit 0; fi
      if [[ $code -eq 0 ]]; then echo 'missing COMPLETE marker' >>"$run_dir/attempts.log"; fi
    done
    echo 'RESTART_LIMIT_EXHAUSTED' >>"$run_dir/attempts.log"
    exit 1
    ;;
  *) usage ;;
esac
