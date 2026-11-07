# Branch divergence and integration classification

The merge base of `origin/main` and `origin/research/bengaluru-v2r-final` is exactly `22a0f5ac5a0527bf173e97692e22c20a245bc6a7`, which is also the audited main tip. `git rev-list --left-right --count origin/main...origin/research/bengaluru-v2r-final` returned `0 159`; the reverse `git log source..origin/main` was empty. Main is a strict ancestor, so a fast-forward is available. No main-only commit or merge conflict needs reconciliation.

| Other ref versus Bengaluru | Other-only | Bengaluru-only | Decision |
|---|---:|---:|---|
| `origin/audit/canonical-notebook-20261023` | 0 | 32 | Already incorporated; preserve branch |
| `origin/research/bengaluru-v2o-v2p` | 0 | 28 | Already incorporated; preserve branch |
| `origin/research/bengaluru-v2q-recovery` | 0 | 25 | Already incorporated; preserve branch |
| `origin/frontend_testing` | 0 | 160 | Already incorporated through main; preserve remote branch |
| `origin/main` | 0 | 159 | Fast-forward destination |

The full main-to-Bengaluru tree diff has 1,621 paths: 1,613 additions, 7 modifications, and 1 deletion. The only deleted path is historical `draft paper.md`, deleted in commit `7d8e7d2`; its complete content remains recoverable from `origin/main`/Git history with `git show 22a0f5a:'draft paper.md'`. The production notebook was refactored in `2bbde3a` and remains present. The only modified serving code is the audited routing/inference change; no source-code path is deleted. `citywide_stpignn_best.pt` changed in the same historical workspace commit and remains in Git history; it is a historical checkpoint, not corrected-protocol evidence.

There is **no unique branch change requiring cherry-pick**, no intentionally excluded unique branch tip, and no unresolved branch divergence. Historical experimental code and results remain in reachable commits; their scientific status is governed by the research reports, not by branch recency.
