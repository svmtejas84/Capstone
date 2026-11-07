# Consolidated main validation

Fast-forward ran in isolated worktree `/tmp/stpignn-main-consolidation-20261107`: `git merge --ff-only research/bengaluru-v2r-final` moved `main` from `22a0f5ac5a0527bf173e97692e22c20a245bc6a7` to `ffce6d8d32069d5262829b267cd374b2c021389b`. No merge commit or conflict occurred. `git diff --quiet main research/bengaluru-v2r-final`, `git status --short`, and `git diff --check` all returned success immediately after the fast-forward. The primary checkout and its untracked artifacts were not switched or cleaned.

The focused CPU test command was:

```sh
AQICN_TOKEN=unit_test_token python -m pytest -q \
  tests/test_physics_v2.py tests/test_rgdr.py \
  tests/test_rgdr_continuous_v2r.py tests/test_edge_capacity_da_v2t.py
```

**28/28 passed.** The initial attempt without a test-only token had 27 passes and one import failure: `router.api.dependencies` instantiates settings that require `AQICN_TOKEN` even for a disconnected-path unit test. The isolated worktree had no `.env`; no real credential was copied or exposed. Rerunning with a dummy token passed. This is a test-environment dependency, not a change to routing logic. No GPU, model fitting, or research result regeneration occurred.

The new read-only validator (`verify_readonly.py`) was run with `--artifact-root /home/jupyter-1nt23cb058/Capstone`: **PASS**. It verified 12 required tracked paths, SHA-256 of 38 key/local archive artifacts, seven byte-identical archive members, the saved monograph 16-volume/15-appendix zero-mismatch report, ten publication figures, ten tables, and 88 package member hashes. It intentionally did not run the older monograph/publication verifiers because those scripts rewrite their reports and archives. The verification did not claim external USB backup.

After pushing main, `git fetch origin` and `git ls-remote` showed `main`, `research/bengaluru-v2r-final`, and newly created `research/london` all at `ffce6d8d32069d5262829b267cd374b2c021389b`. The authoritative Bengaluru commit is an ancestor of main (indeed the same commit at this stage). Original notebook, corrected source, final routing implementation, reports, monograph, publication figures/tables and the local archives remain present. Only one historical paper draft is absent from the final tree, explicitly preserved in Git history.
