# Quota and runtime

- 2026-10-24 15:17:38 UTC: user reports approximately 24% session quota remaining. Finish and push each started gate before beginning another. Long jobs use `nohup`; poll no more than once per five minutes.
- Gate A started 2026-10-24 15:17:38 UTC; analysis completed 2026-10-24 15:55 UTC. Stop after Gate A if remaining quota is insufficient to complete five-seed Gate B and its commit/push.
- 2026-10-24 15:58 UTC: stop after pushed Gate A; remaining session quota is insufficient to safely finish, commit and push the five-seed Gate B plus its longer runs. Gate B and C remain NOT RUN.
- Gate B started 2026-10-24 16:07:40 UTC. Preserve all Step 4 outputs; new cleaned results use `gate_v2b` names. Stop only after a complete Gate B commit/push if runtime or quota becomes tight.
- Gate B started 2026-10-24 16:07:40 UTC and analysis completed 2026-10-24 16:49 UTC. Five-seed short and longer runs finished within the fixed budget. Gate C begins only after Gate B push and a clean RESUME.md handoff.
- Gate C started 2026-10-24 17:01:44 UTC. Five seeds remain the default; a reduction to three requires a logged quota decision before execution. Commit/push Gate C before any queued phase.
- Gate C source was committed at `e90fd05`; three fixed seeds were logged before scores. Persistent nohup run completed 2026-10-24 18:21:10 UTC in 3,284.709 seconds on CUDA. Four unscorable folds were recorded. Final commit/push is pending; no queued phase starts before it.
- Gate C result and handoff commits were pushed at 2026-10-24 18:30:14 UTC. Stop after Gate C; remaining D-K queue is NOT RUN.
- Checkpoint, 2026-10-25 UTC: approximately 13% quota remaining as reported by the user. Stop after commit/push; do not start S1-S4 or the later queue.
- S1 started 2026-10-25 02:38:26 UTC. Approximate session quota at prior checkpoint: 13%; finish and push S1 before considering S2.
- S1 analysis completed 2026-10-25 02:43:11 UTC, about five minutes after start. Final S1 commit/push is next; S2 remains NOT RUN.
- S2 started 2026-10-25 UTC after S1 commit `62132eb` was pushed. A long five-seed LR sweep may approach the five-hour limit; stop only at a clean checkpoint with logs, RESUME, commit and push.
