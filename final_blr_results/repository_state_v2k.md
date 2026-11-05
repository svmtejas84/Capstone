# v2k repository state before changes

Inspected 2026-11-05T17:01:35Z. This record precedes v2k report generation.

- Branch: `audit/canonical-notebook-20261023`; HEAD and remote branch: `128dd0324deeb23310a93cb2aaa98f2032efb648`.
- The working tree contained only untracked run-control files and archived partial CPU benchmark CSVs under `results/codex_log/runs/`. No tracked file was modified. The untracked files are retained in place.
- Host process inspection found no `scripts.*` or `run_supervised` process. Existing v2j supervisor manifests and `COMPLETE` markers cover the GPU benchmark, LOSO, lambda, and DEM runs. The stopped CPU benchmark's stale PID file is historical and was not treated as an active job.
- The workspace filesystem is `/dev/sda2`, 879 GB total, 715 GB used, 120 GB available (86% used). `results/` occupies about 358 MB and `data/` about 2.1 GB.
- Existing corrected artifacts include `results/data_v2j_arrays.npz`, `data_v2j_fit.json`, `benchmark_v2j.csv`/`.md`, `loso_summary_v2j.csv`, `lambda_check_v2j.csv`, `dem_study_v2j.csv`, and `weather_fix_comparison_v2j.csv`; prediction caches also exist locally.
- The verified GitHub branch matches HEAD, so tracked lightweight artifacts are present in the remote Git repository. A 97 MB `/home/jupyter-1nt23cb058/Capstone.tar.gz` dated April 2026 is on the same local filesystem and predates v2j. No off-host archive destination for the full experiment cache was found. Home-directory persistence across JupyterHub recreation is unverified.
- No destructive reset, output removal, model training, paper edit, or citywide inference was performed during this inspection.
