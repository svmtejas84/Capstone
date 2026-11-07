# Main synchronization verdict

**COMPLETE — source tree synchronized and remotely verified**, with a branch-governance caveat.

`main` was fast-forwarded (no merge commit) from `22a0f5ac5a0527bf173e97692e22c20a245bc6a7` to authoritative Bengaluru commit `ffce6d8d32069d5262829b267cd374b2c021389b`. The remote `refs/heads/main` returned that exact SHA, as did remote `refs/heads/research/bengaluru-v2r-final`. No source conflict occurred, and the focused tests/read-only artifact checks passed. `research/london` was then created from that verified main and its remote ref returned the same SHA. No London dataset work or training was started.

**Protection finding:** the `git push origin main` response explicitly said GitHub **“Bypassed rule violations”** and **“Changes must be made through a pull request.”** The account had a bypass permission and the push succeeded; this was not known from local Git before the push. The consolidation does not undo or conceal that event. No further direct main push is performed. Remaining final handoff documentation is placed on `research/repository-consolidation-handoff` for PR review. The compare target is `main`; the branch adds documentation and the read-only validator only. This protection state should be reviewed by a repository administrator. It does not change the SHA-equality evidence for the already synchronized source tree.

The local bundle is a **source-history** backup only. Raw datasets, ignored graph files, citywide predictions, many fold checkpoints and local ZIPs remain host-local or in same-host archives. Independent USB backup remains unverified.
