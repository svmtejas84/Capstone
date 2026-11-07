# Final Git handoff: Bengaluru baseline and London branch

## Verified branch state

At source synchronization, the following **local and remote** refs all resolved to `ffce6d8d32069d5262829b267cd374b2c021389b`:

| Ref | Purpose |
|---|---|
| `main` / `origin/main` | Authoritative completed Bengaluru code and evidence baseline |
| `research/bengaluru-v2r-final` / matching origin ref | Preserved research lineage and complete history |
| `research/london` / matching origin ref | Fresh branch created from verified main; no London research performed |

The merge method was `git merge --ff-only`; `origin/main` had zero unique commits, and all 159 pre-audit Bengaluru commits plus the audit commit were preserved in their original order. No conflict, cherry-pick, reset, force push, branch deletion, or source rewrite occurred. `origin/frontend_testing`, notebook-audit, v2o/v2p and v2q refs remain historical ancestors. A stale local tracking ref for already-deleted `origin/hitesh_testing` was removed only by requested `fetch --prune`.

The current final-handoff documentation and `verify_readonly.py` are on `research/repository-consolidation-handoff` for a pull request into `main`. They are documentation/tooling only and do not alter the verified source baseline. The final SHA of this handoff branch is obtained after its commit with `git rev-parse research/repository-consolidation-handoff`; it is intentionally not self-referenced in this file.

## Governance disclosure

The first and only direct main push succeeded, but GitHub reported a bypass of a rule requiring pull requests. This permission was not visible from local Git beforehand. No subsequent direct main push is used. Review/merge the handoff branch through the repository's normal PR process; do not bypass the rule again. Main already contains all completed Bengaluru research and v2u publication assets even before that documentation PR.

## Preservation and validation

The primary checkout remained on the Bengaluru branch to preserve local untracked v2j run controls, v2r fold outputs, graphs and archives. Main integration and focused tests ran in an isolated `/tmp` worktree. The test suite passed **28/28** with a dummy `AQICN_TOKEN` required solely for API import; the initial token-free run had one environment-related failure. Read-only validation passed 38 artifact hashes, seven same-host archive-member hashes, the saved monograph checks and 88 publication package hashes. See `VALIDATION_RESULTS.md`, `ARTIFACT_PRESERVATION_REPORT.md`, and the CSV manifests.

Sixteen local research ZIPs and the separate 203,652,339-byte source-history bundle remain on this host. Bundle SHA-256: `8b9a0320967c1b25bb138eff336525772c28ad98309d160e0f7dc1a7bbcb9ff0`. Git and the bundle do not back up ignored/raw data or local ZIPs; external USB copy remains unverified. No model was trained, no experiment rerun and no research result changed.

## London Codex entry

In a fresh clone/session, start from the dedicated branch and read the eligibility handover before any dataset work:

```sh
cd /home/jupyter-1nt23cb058/Capstone
git fetch origin
git switch research/london || git switch --track origin/research/london
git rev-parse HEAD
cat final_blr_results/second_city_handover/SECOND_CITY_NEXT_SESSION_PROMPT.md
```

London is a candidate study, not an approved training dataset. The branch is only a clean baseline; no London preprocessing or training has started.

## IEEE manuscript entry

Use the verified main ref and consult the research evidence; this does not authorize writing in the consolidation session:

```sh
cd /home/jupyter-1nt23cb058/Capstone
git fetch origin
git switch main
git merge --ff-only origin/main
cat final_blr_results/ieee_paper_evidence/FINAL_PAPER_EVIDENCE_HANDOFF.md
cat final_blr_results/ieee_publication_assets/FINAL_PUBLICATION_ASSET_HANDOFF.md
```

The rejected paper PDF and six complete review texts remain missing from the repository evidence record; do not reconstruct their exact quotations. Use `git show 22a0f5a:'draft paper.md'` only if the historical draft is specifically needed.
