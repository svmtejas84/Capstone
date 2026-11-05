# Research backup export — local ZIP verified, external copy pending

Created/verified UTC: 2026-11-05T19:19:12.757610+00:00.

- Archive: `/home/jupyter-1nt23cb058/Capstone/final_blr_results/research_backup_exports/research_backup_pretrain_v2m.zip`
- Size: 348,597,625 bytes.
- SHA-256: `13d4e04ead4cb6027b1fb81010bc5f57bdebaf3a859085b41aa20d84158a1905`.
- Source list: `/home/jupyter-1nt23cb058/Capstone/final_blr_results/baselines/v2m/backup_manifest.csv`; export manifest: `/home/jupyter-1nt23cb058/Capstone/final_blr_results/research_backup_exports/RESEARCH_BACKUP_MANIFEST.csv` (also embedded in the ZIP).
- Included: 1104 of the 1,110 previously local-only files, including all 305 corrected v2j benchmark prediction files. All included members had CRC and SHA-256 verified against the **current** source manifest. 4 source paths changed since the earlier backup-gate snapshot; both old and current hashes are in the export manifest: results/codex_log/ACTIONS.md, results/codex_log/DECISIONS.md, results/codex_log/QUOTA.md, results/codex_log/RESUME.md. Excluded transient controls: 6 files, listed with reasons in the manifest: results/codex_log/runs/benchmark_gpu_v2j/supervisor.lock, results/codex_log/runs/benchmark_v2j/supervisor.lock, results/codex_log/runs/benchmark_v2j/supervisor.pid, results/codex_log/runs/dem_v2j/supervisor.lock, results/codex_log/runs/lambda_v2j/supervisor.lock, results/codex_log/runs/loso_v2j/supervisor.lock.
- Git-backed research reports, code, methodology, configurations and existing tracked data are independently recoverable from GitHub branch `audit/canonical-notebook-20261023` at commit `a0d87aa7d16ba7d202f2b6e833d57f489741ab7d` (later v2m documentation commits add this report). The three historical classes in `backup_verification.md` remain MISSING AT SOURCE.

## Download and external transfer

In JupyterLab's file browser, navigate to `Capstone/final_blr_results/research_backup_exports/` and download `research_backup_pretrain_v2m.zip`, `RESEARCH_BACKUP_MANIFEST.csv`, this instruction file and `RESEARCH_BACKUP_SHA256.txt`. Save all four to a persistent external drive. On the destination computer, verify the ZIP hash using `sha256sum -c RESEARCH_BACKUP_SHA256.txt` from the directory containing the ZIP, then run `unzip -t research_backup_pretrain_v2m.zip`. To restore, extract into an empty directory, preserving member relative paths. Compare extracted SHA-256s with `source_sha256` for rows marked INCLUDED in the manifest. Obtain Git-backed files from the cited commit separately. Do not overwrite an active workspace during restore.

**Status: LOCAL ARCHIVE VERIFIED — EXTERNAL COPY PENDING.** The ZIP currently shares the JupyterHub filesystem with the source; it is not a verified pen-drive/off-host backup. JupyterHub loss before the owner downloads and verifies the archive could destroy local-only artifacts. Do not delete local sources or this archive before external verification.
