"""Create lightweight v2n reproducibility inventory without altering historical data."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CITY = ROOT / "final_blr_results/city_scale"
OUT = CITY / "reproducibility"
CRITICAL = [
    "data/graphs/bangalore_utm_nodes.parquet",
    "data/graphs/bangalore_utm_edges.parquet",
    "data/processed/graph/topology_graph.pt",
    "data/processed/graph/partitioned_manifold_64_clusters.pt",
    "results/data_v2j_arrays.npz",
    "results/data_v2j_fit.json",
    "results/loso_summary_v2j.csv",
    "results/loso_per_station_v2j.csv",
    "results/loso_decision_v2j.csv",
    "final_blr_results/baselines/v2m/data/data_v2m_arrays.npz",
    "final_blr_results/baselines/v2m/data/data_v2m_fit.json",
    "final_blr_results/research_backup_exports/research_backup_pretrain_v2m.zip",
    "final_blr_results/baselines/v2m/reproducibility/research_results_v2m.zip",
]
MISSING = ["corrected v2j ST-PIGNN/λ0/Laplacian neural checkpoints",
           "corrected W6 per-fold neural checkpoints", "independent road-node PM2.5 observations",
           "complete cutoff-aligned road-node dynamic feature tensor", "verified external USB copies"]


def sha(path):
    d = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(4 * 1024 * 1024), b""):
            d.update(b)
    return d.hexdigest()


def main():
    paths = [("critical_input", ROOT / rel) for rel in CRITICAL]
    for model in ("mlp", "tcn"):
        for h in (1, 3, 6, 12, 24):
            for seed in (11, 23, 37, 51, 79):
                paths.append(("v2m_checkpoint", ROOT / f"final_blr_results/baselines/v2m/{model}/h{h}/seed{seed}/checkpoint.pt"))
    excluded = {"artifact_manifest.json", "artifact_checksums.csv", "artifact_checksums.sha256",
                "research_results_v2n.zip", "V2N_ARCHIVE_VERIFICATION.json"}
    for path in sorted(CITY.rglob("*")):
        if path.is_file() and path.name not in excluded and "__pycache__" not in path.parts:
            paths.append(("v2n_output", path))
    seen = set()
    rows = []
    for role, path in paths:
        rel = path.relative_to(ROOT).as_posix()
        if rel in seen:
            continue
        seen.add(rel)
        rows.append(dict(role=role, path=rel, exists=path.exists(), bytes=path.stat().st_size if path.exists() else None,
                         sha256=sha(path) if path.exists() else None))
    with (OUT / "artifact_checksums.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["role", "path", "exists", "bytes", "sha256"])
        w.writeheader(); w.writerows(rows)
    (OUT / "artifact_checksums.sha256").write_text("".join(f"{r['sha256']}  {r['path']}\n" for r in rows if r["exists"]))
    manifest = dict(schema="v2n-artifact-manifest-1", starting_commit="6a50ace0afbd9895ccbd203da9d2c70b6db9861c",
                    frozen_protocol_commit="c6fb4e3", historical_source_commits={"v2j_training":"9a299f1bf01787f26750515cad8dff370e9c9aa0",
                    "v2k":"931bf09975dd17bfdca4f26259ede91046974f07", "v2l":"c931efc", "v2m_result":"5897065"},
                    graph_nodes=154902, raw_edge_rows=393089, processed_message_arcs=424550,
                    graph_crs="EPSG:32643", station_graph="15-station directed 4-nearest-neighbor distance graph",
                    feature_methods={"v2j":"centered corrected c-30/c+30 weather; 12x18 station inputs",
                                     "v2m":"cutoff-safe latest corrected record <= c; 12x18 station inputs"},
                    ig={"package":"captum.attr.IntegratedGradients", "steps":64,"method":"gausslegendre",
                        "internal_batch_size":16,"samples":45,"records":228,"baseline_primary":"training station channel mean",
                        "baseline_secondary":"zero standardized plus training calendar mean"},
                    city_inference="BLOCKED; zero nodes inferred", missing_artifacts=MISSING,
                    count=len(rows), artifacts=rows)
    (OUT / "artifact_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"{len(rows)} artifact rows; {len(MISSING)} missing classes")


if __name__ == "__main__":
    main()
