# Untracked and ignored local artifact audit

At audit start, tracked files were clean. `git status --short` listed pre-existing untracked archives, v2r fold/run outputs, v2j run-control files, and benchmark files. No such item was removed, staged, or treated as an authoritative Git file. `git status --short --ignored` also showed ignored raw/processed data, graph tensors, model-input directories, prediction Parquets, checkpoint caches, the local publication ZIP and the derived 13 MB F07 node CSV. The ignored `.env` was not read or copied.

The inventory script counted 272 local weight-like files (`.pt`, `.pth`, `.ckpt`, `.safetensors`): **138 tracked**, **74 untracked**, **60 ignored**. The key local-only examples are the 154,902-node road graph files, 64-partition tensor, v2r fold weights, citywide prediction Parquets and Captum attribution tensors. Their exact paths, sizes, SHA-256 values and Git state are in `KEY_ARTIFACT_HASHES.csv`. All 16 local ZIP files and SHA-256 values are in `LOCAL_ARCHIVE_HASHES.csv`; eight are untracked and eight ignored. Seven important local files were confirmed byte-identical to members in on-host ZIP archives (`ARCHIVE_MEMBER_MATCHES.csv`).

The ZIP matches are **same-host copies**, not verified independent backups. The external USB copy remains pending/unverified. A Git push preserves only tracked objects and does not back up untracked/ignored graph data, v2r fold outputs, attribution tensors, citywide predictions, or local ZIPs. No new large artifact is staged or committed by the consolidation.

The worktree operation is planned in a separate temporary worktree to protect all these local files. The primary checkout remains on the Bengaluru branch until the branch integration is complete.
