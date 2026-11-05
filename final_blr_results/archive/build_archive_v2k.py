"""Inventory local research artifacts without copying or changing them."""
from __future__ import annotations

import csv
import datetime as dt
import fnmatch
import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


DEFINITIONS = [
    ("legacy_notebook", "Was the original full-road graph notebook benchmark valid?", "UNVERIFIABLE", ["notebooks/production/evaluated_wind_advection.ipynb", "results/legacy*", "results/replay*", "citywide_stpignn_best.pt", "complete_64_cluster_performance_report.csv"], "legacy weather and mixed/zero-filled targets", "historical notebook index split", [42], "same-pair trained baseline and persistence predictions unavailable; untrained comparison", "replay only; exact old benchmark cannot be reconstructed"),
    ("phase_a_canonical", "Can the notebook path be replayed and audited?", "VERIFIED", ["results/audit*", "results/full_replay*", "results/stations.csv", "results/legacy_canonical_notebook.ipynb"], "legacy graph", "canonical replay", [42], "replay fidelity does not establish predictive validity", "python -m scripts.audit_canonical (writes historical results; use read-only audit for verification)"),
    ("gate_a_cleaning", "Does observed-only cleaning remove invalid target inputs?", "VERIFIED", ["results/cleaning*", "results/old_filtering*", "results/data_v2*", "results/splits_v2.json", "results/imputation*"], "data_v2 raw station/weather", "configs/data_v2.yaml", [42], "pre-v2j weather is shifted; later corrected v2j is separate", "python -m scripts.build_data_v2 (would overwrite historical files; do not run here)"),
    ("gate_b", "Do trained baselines pass the original gate?", "PROVISIONAL", ["results/gate_v2b*", "results/baselines_v2b*", "results/neural*_v2b*", "results/checkpoints_v2b/*"], "shifted weather", "configs/gate_v2b.yaml", [11,23,37,51,79], "shifted-weather input", "requires original runner and frozen config"),
    ("gate_c", "Do residual/input corrections improve the gate?", "PROVISIONAL", ["results/gate_v2c*", "results/neural*_v2c*", "results/checkpoints_v2c/*", "results/diagnosis*"], "shifted weather", "configs/gate_v2c.yaml", [11,23,37,51,79], "shifted-weather input and repeated test exposure", "requires original runner and frozen config"),
    ("w1_input", "What lag, alignment, and input defects existed?", "VERIFIED", ["results/input*", "results/data_v2g_arrays.npz", "results/old_vs_raw*"], "data_v2g shifted weather", "configs/data_v2.yaml", [42], "weather timestamps shifted until v2j", "python -m scripts.input_fix_v2g (historical output; do not rerun here)"),
    ("s2_s3_residual", "Did residual/physics variants improve prediction?", "PROVISIONAL", ["results/physics*", "results/pvr*", "results/neural*", "results/checkpoints_v2/*"], "pre-v2j shifted weather", "configs/gate_v2.yaml", [11,23,37,51,79], "original physics null trends; shifted weather", "saved predictions where present; otherwise retraining"),
    ("s4_spatial", "Did spatial source/graph variants transfer?", "INCONCLUSIVE", ["results/loso*", "results/stations_v2.csv", "ST_PIGNN_additional_eval_23oct2026.md"], "station subset shifted weather", "LOSO", [11,23,37], "station versus road-node distribution mismatch", "saved LOSO predictions where present"),
    ("w2_w5_horizons_shifted", "Which model wins each forecast horizon with shifted weather?", "SUPERSEDED", ["results/benchmark*_v2g*", "results/horizon_curve_v2g.csv"], "data_v2g shifted weather", "configs/data_v2.yaml and benchmark_v2g.yaml", [11,23,37,51,79], "Asia/Kolkata raw weather labelled UTC", "python -m scripts.summarize_benchmark_v2g (metric-only)"),
    ("w6_loso_shifted", "Does the shifted-weather station graph transfer to unseen stations?", "SUPERSEDED", ["results/loso*_v2g*", "results/loso*_v2c*"], "shifted weather", "W6 fixed fold protocol", [11,23,37], "zero-target folds retained; weather shift", "saved predictions; metric-only extraction required"),
    ("w7_lambda_shifted", "Does the original physics coefficient help on shifted-weather data?", "SUPERSEDED", ["results/lambda*_v2g*", "results/lambda_predictions_v2g/*"], "shifted weather", "configs/benchmark_v2g.yaml", [11,23,37,51,79], "mostly null/negative lambda trend; weather shift", "summarize saved lambda predictions only"),
    ("w3_dem_shifted", "Does SRTM help under the fixed controls?", "SUPERSEDED", ["results/dem*_v2h*", "results/dem_midpoint_v2g.npy"], "shifted weather", "W3 fixed h=1/24", [11,23,37,51,79], "h=24 null; h=1 changed after v2j weather correction", "saved local DEM predictions where available"),
    ("w4_sensor_density", "How does reduced sensor density affect predictions?", "INCONCLUSIVE", ["results/sensor*", "results/w4*"], "data_v2g shifted weather", "W4 fixed draws", [11,23,37,51,79], "held-out target populations differ; per-pair predictions absent", "requires retraining for pairwise comparison"),
    ("w8_citywide", "Are citywide temporal inputs ready?", "BLOCKED", ["results/citywide*", "data/processed/model_input/model_input_node_hourly_features.parquet"], "one raw weather source", "W8 precheck", [], "single source projected to duplicate 100% of citywide weather; only 22 nodes have temporal rows", "python -m scripts.citywide_precheck_v2h (data-only; historical output path)"),
    ("p1_protocol_inflation", "How much did historical protocol choices inflate scores?", "PROVISIONAL", ["results/protocol*", "results/legacy_checkpoint_v2_metrics.csv"], "mixed historical datasets", "P0–P4 protocol ladder", [11,23,37,51,79], "six post-hoc deviations and repeated test exposure", "python -m scripts.audit_r1_recompute for saved cells"),
    ("p2_conformal", "Did uncertainty intervals cover held-out targets?", "FAILED", ["results/conformal*"], "shifted weather", "P2 rolling protocol", [11,23,37,51,79], "undercoverage; possible future-to-origin label use at h>1", "python -m scripts.audit_r1_recompute (saved predictions)"),
    ("p3_group_dro", "Did Group-DRO improve LOSO?", "FAILED", ["results/loso_groupdro*", "results/codex_log/runs/groupdro*"], "shifted weather", "W6 LOSO", [11,23,37,51,79], "pooled LOSO loss versus fixed baseline", "python -m scripts.audit_r1_recompute (saved predictions)"),
    ("r1_audit", "Are old claims and artifacts reproducible?", "VERIFIED", ["results/research_audit_r1/*", "docs/EXPERIMENT_RECOVERY.md"], "historical mixed", "R1 audit", [], "audit identifies unresolved methodological defects", "read-only audit scripts only"),
    ("weather_timestamp", "Are raw weather labels shifted?", "VERIFIED", ["results/weather_timestamp_check_v2i.md", "data/raw/weather/*"], "raw Asia/Kolkata naive timestamps", "2022-2026", [], "+5.5 h label defect in pre-v2j data", "python -m scripts.weather_timestamp_check_v2i if available; read-only inspection"),
    ("v2j_benchmark", "What wins with corrected weather?", "VERIFIED", ["results/benchmark*_v2j*", "results/horizon_curve_v2j.csv", "results/data_v2j*", "results/codex_log/runs/benchmark_gpu_v2j/*"], "data_v2j corrected weather", "configs/data_v2.yaml and benchmark_v2g.yaml", [11,23,37,51,79], "repeated Bengaluru test exposure remains; no trained model checkpoints saved", "python -m scripts.summarize_benchmark_v2j (saved predictions)"),
    ("v2j_loso", "Does the corrected station graph transfer?", "VERIFIED", ["results/loso*_v2j*", "results/codex_log/runs/loso_v2j/*"], "data_v2j corrected weather fold rebuilds", "W6 fixed folds", [11,23,37], "no neural WIN; four zero-target folds", "metric-only extraction from saved LOSO predictions required"),
    ("v2j_lambda", "Does physics help after weather correction?", "VERIFIED", ["results/lambda*_v2j*", "results/lambda_predictions_v2j/*", "results/codex_log/runs/lambda_v2j/*"], "data_v2j corrected weather", "h=1/24 fixed grid", [11,23,37,51,79], "h=24 null; h=1 positive only at lambda=0.06", "scripts.lambda_check_v2j.summarize from saved predictions"),
    ("v2j_dem", "Does corrected-weather SRTM beat all controls?", "VERIFIED", ["results/dem*_v2j*", "results/codex_log/runs/dem_v2j/*"], "data_v2j corrected weather", "W3 fixed h=1/24", [11,23,37,51,79], "all-control criterion null at both horizons", "saved local DEM predictions; summary extraction required"),
    ("london_copenhagen_feasibility", "Are second-city data gates met?", "BLOCKED", ["results/second_city*", "results/london*", "results/research_audit_r1/gate_m0*"], "external metadata only", "fixed >=30 hourly station gate", [], "eligible station counts unknown; no training authorization", "metadata-only lookup"),
    ("routing_validation", "Was route guidance validated?", "FAILED", ["results/*routing*", "data/processed/evaluations/routing_snapshot.graphml", "notebooks/*route*"], "legacy graph and predicted data", "historical route audit", [], "old routing validation failed; no street-level accuracy", "no validated regeneration path"),
    ("gapfill_and_preprocessing", "What station gap-filling and graph preprocessing was performed?", "PROVISIONAL", ["data/processed/gapfill/*", "data/processed/graph/*", "data/graphs/*", "results/imputation*"], "raw stations and OSM/SRTM", "historical preprocessing", [], "legacy imputation is not observed truth", "source scripts exist; outputs should not be overwritten"),
]


def main():
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    head = git("rev-parse", "HEAD")
    remote = subprocess.check_output(["git", "ls-remote", "origin", "refs/heads/audit/canonical-notebook-20261023"],
                                     cwd=ROOT, text=True).split()[0]
    tracked = set(git("ls-files", "-z").split("\x00"))
    historical = set()
    for line in git("rev-list", "--objects", "--all").splitlines():
        if " " in line:
            historical.add(line.split(" ", 1)[1])
    tar_listing_path = Path("/tmp/capstone_tar_listing_v2k.txt")
    tar_paths = set(tar_listing_path.read_text().splitlines()) if tar_listing_path.exists() else set()
    roots = ["results", "data", "figures", "notebooks", "configs", "scripts", "docs"]
    paths = [p for root in roots for p in (ROOT / root).rglob("*") if p.is_file()]
    paths += [p for p in ROOT.iterdir() if p.is_file() and p.suffix in {".csv", ".pt", ".md", ".parquet"}]
    paths = sorted(set(paths))
    rows = []
    for path in paths:
        rel = path.relative_to(ROOT).as_posix()
        size = path.stat().st_size
        in_git = rel in tracked
        rows.append({"path": rel, "size_bytes": size, "sha256": sha256(path),
                     "exists_workspace": True, "git_current": in_git,
                     "git_history": in_git or rel in historical,
                     "github_current_commit_verified": bool(in_git and remote == head),
                     "local_april_tar_path_listed": f"Capstone/{rel}" in tar_paths,
                     "verified_independent_durable_backup": False,
                     "backup_note": "GitHub current commit for tracked file only" if in_git and remote == head
                                    else "No verified off-host copy; local workspace only"})
    with (OUT / "archive_integrity.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    experiments = []
    matched = set()
    for name, question, status, patterns, dataset, split, seeds, defects, command in DEFINITIONS:
        files = [row["path"] for row in rows if any(fnmatch.fnmatch(row["path"], pattern) for pattern in patterns)]
        matched.update(files)
        result_files = [path for path in files if path.startswith("results/")]
        checkpoints = [path for path in files if "checkpoint" in path or path.endswith(".pt")]
        predictions = [path for path in files if "prediction" in path and path.endswith(".parquet")]
        metrics = [path for path in result_files if path.endswith((".csv", ".md", ".json")) and "prediction" not in path]
        logs = [path for path in files if path.endswith(".log")]
        manifests = [path for path in files if path.endswith("execution_manifest.json")]
        manifest_data = []
        for path in manifests:
            try: manifest_data.append(json.loads((ROOT / path).read_text()))
            except (OSError, ValueError): pass
        reproducibility = ("recomputable_from_saved_predictions" if predictions else
                           "regenerable_from_checkpoints" if checkpoints else
                           "reproducible_only_through_retraining" if "training" in command or "retraining" in command else
                           "unrecoverable_or_data_only")
        experiments.append({"experiment_id": name, "research_question": question, "status": status,
                            "source_code_commit": manifest_data[-1].get("git_commit") if manifest_data else None,
                            "source_commit_evidence": manifests[-1] if manifests else "not recorded in matched manifest",
                            "configuration": [path for path in files if path.startswith("configs/")] or split,
                            "dataset_version": dataset, "data_provenance": dataset,
                            "split_identifier": split, "training_seeds": seeds,
                            "checkpoint_paths": checkpoints, "prediction_paths": predictions,
                            "metric_files": metrics, "statistical_evaluation_files": [p for p in metrics if any(t in p for t in ("ci", "bootstrap", "decision", "summary", "verdict"))],
                            "execution_logs": logs, "execution_manifests": manifests,
                            "hardware": sorted({str(d.get("gpu") or "CPU/unknown") for d in manifest_data}) or ["not recorded"],
                            "start_timestamps_utc": [d.get("start_utc") for d in manifest_data if d.get("start_utc")],
                            "completion_timestamps_utc": [], "known_defects": defects,
                            "methodological_deviations": ["see results/research_audit_r1/protocol_readiness.md and historical_results_register.md"],
                            "regeneration_command": command,
                            "recovery_requirements": "Use saved predictions if present; checkpoint weights alone lack optimizer/RNG state for exact epoch recovery.",
                            "reproducibility_class": reproducibility,
                            "artifact_paths": files,
                            "artifact_count": len(files),
                            "github_tracked_artifact_count": sum(p in tracked for p in files),
                            "verified_independent_durable_backup_count": 0})
    unmatched = [row["path"] for row in rows if row["path"].startswith("results/") and row["path"] not in matched]
    experiments.append({"experiment_id": "other_discovered_results", "research_question": "Additional result artifacts not mapped to a named family",
                        "status": "INCONCLUSIVE", "source_code_commit": None, "configuration": None,
                        "dataset_version": "mixed", "data_provenance": "mixed", "split_identifier": None,
                        "training_seeds": [], "checkpoint_paths": [], "prediction_paths": [],
                        "metric_files": unmatched, "statistical_evaluation_files": [], "execution_logs": [],
                        "hardware": ["not recorded"], "start_timestamps_utc": [], "completion_timestamps_utc": [],
                        "known_defects": "not classified; retain for supervisor review", "methodological_deviations": [],
                        "regeneration_command": None, "recovery_requirements": "inspect source and provenance before use",
                        "reproducibility_class": "unverified", "artifact_paths": unmatched,
                        "artifact_count": len(unmatched), "github_tracked_artifact_count": sum(p in tracked for p in unmatched),
                        "verified_independent_durable_backup_count": 0})
    manifest = {"schema_version": "v2k-1", "generated_utc": now, "repository_commit": head,
                "remote_commit": remote, "tracked_remote_commit_matches": remote == head,
                "artifact_count": len(rows), "experiment_count": len(experiments),
                "unmatched_result_count": len(unmatched), "integrity_register": "final_blr_results/archive/archive_integrity.csv",
                "backup_policy": "Tracked lightweight files have a verified GitHub current-commit copy; no independent durable full-archive backup was identified or verified.",
                "experiments": experiments}
    (OUT / "experiment_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({k: manifest[k] for k in ("artifact_count", "experiment_count", "unmatched_result_count")}, indent=2))


if __name__ == "__main__":
    main()
