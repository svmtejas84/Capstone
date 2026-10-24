# Quota and runtime

- 2026-10-24 15:17:38 UTC: user reports approximately 24% session quota remaining. Finish and push each started gate before beginning another. Long jobs use `nohup`; poll no more than once per five minutes.
- Gate A started 2026-10-24 15:17:38 UTC; analysis completed 2026-10-24 15:55 UTC. Stop after Gate A if remaining quota is insufficient to complete five-seed Gate B and its commit/push.
- 2026-10-24 15:58 UTC: stop after pushed Gate A; remaining session quota is insufficient to safely finish, commit and push the five-seed Gate B plus its longer runs. Gate B and C remain NOT RUN.
- Gate B started 2026-10-24 16:07:40 UTC. Preserve all Step 4 outputs; new cleaned results use `gate_v2b` names. Stop only after a complete Gate B commit/push if runtime or quota becomes tight.
- Gate B started 2026-10-24 16:07:40 UTC and analysis completed 2026-10-24 16:49 UTC. Five-seed short and longer runs finished within the fixed budget. Gate C begins only after Gate B push and a clean RESUME.md handoff.
