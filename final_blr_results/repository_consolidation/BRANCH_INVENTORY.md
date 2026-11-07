# Branch inventory at consolidation audit

Audit snapshot: 2026-11-07, after `git fetch origin --prune`, before any main update. Working branch and HEAD: `research/bengaluru-v2r-final` at `7cd1d8306e0433a48e5234ca2b065bb824e5fceb`. No uncommitted tracked modifications at audit start. Remote: `origin = https://github.com/svmtejas84/Capstone` for fetch and push.

| Local branch | Local tip | Upstream | Remote tip | Classification |
|---|---|---|---|---|
| `main` | `22a0f5ac5a0527bf173e97692e22c20a245bc6a7` | `origin/main` | same | Ancestor of Bengaluru; 159 commits behind at audit |
| `audit/canonical-notebook-20261023` | `c50f58f` | matching origin ref | same | Already incorporated into Bengaluru |
| `research/bengaluru-v2o-v2p` | `7356487` | matching origin ref | same | Already incorporated into Bengaluru |
| `research/bengaluru-v2q-recovery` | `062f4a1` | **no upstream configured** | matching origin ref | Already incorporated into Bengaluru |
| `research/bengaluru-v2r-final` | `7cd1d83` | matching origin ref | same | Authoritative completed Bengaluru source |

Remote-only `origin/frontend_testing` is `a73b497`, an ancestor of `origin/main` and thus already incorporated into the Bengaluru branch. `origin/hitesh_testing` was stale and `git fetch --prune` removed only the local remote-tracking ref; no remote branch was deleted by this audit. No London branch exists at audit. No Git tags were present. `git lfs` is not installed; no `.gitattributes`, LFS filter configuration, or LFS pointer text was found. This does not prove that no large binary is tracked directly: 138 local weight-like files are tracked.

The remote branch protection configuration could not be authenticated/read with the available Git CLI; actual push behavior must be observed. No branch was deleted or rewritten. The exact command/output lineage is summarized in `GIT_HISTORY_SUMMARY.md`.
