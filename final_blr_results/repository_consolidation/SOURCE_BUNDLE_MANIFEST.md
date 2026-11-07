# Git source-history bundle

Local path: `/home/jupyter-1nt23cb058/Capstone/final_blr_results/repository_consolidation/archive/ST_PIGNN_SOURCE_HISTORY_20261107.bundle`.

- Size: **203,652,339 bytes**.
- SHA-256: `8b9a0320967c1b25bb138eff336525772c28ad98309d160e0f7dc1a7bbcb9ff0`.
- Verification: `git bundle verify <path>` returned **“is okay”**, reported 15 refs and a complete history.
- Captured refs include `main`, `research/bengaluru-v2r-final`, `research/london`, older local research branches, origin tracking refs, and HEAD at the consolidated `ffce6d8...` commit.
- The bundle was created before the separate final-handoff documentation branch; it preserves the authoritative research/source baseline, not this later documentation-only branch.

This bundle contains Git objects and refs, including any binaries already tracked by Git. It does **not** contain ignored/raw datasets, untracked fold/checkpoint outputs, citywide prediction Parquets, Captum tensor files that are ignored, or the 16 local research ZIPs. Its presence on the same JupyterHub host is not an independent off-host backup. Previous archives were not deleted or modified.

Recovery checks:

```sh
sha256sum final_blr_results/repository_consolidation/archive/ST_PIGNN_SOURCE_HISTORY_20261107.bundle
git bundle verify final_blr_results/repository_consolidation/archive/ST_PIGNN_SOURCE_HISTORY_20261107.bundle
git bundle list-heads final_blr_results/repository_consolidation/archive/ST_PIGNN_SOURCE_HISTORY_20261107.bundle
```
