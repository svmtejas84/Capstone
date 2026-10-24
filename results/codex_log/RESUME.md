# Resume

- Last completed gate: Step 4 persistence gate (`02774aa`), before Gates A–C.
- Current gate: A CLEANING, STARTED 2026-10-24 15:17:38 UTC.
- Next gate: B CLEANED GATE, h=1 only, after A is committed and pushed.
- Branch: `audit/canonical-notebook-20261023`.
- Current code commit: `7484720` (`Implement audited per-row cleaning in data v2`).
- Running job: Gate A old-v2 comparison PID `2876953`, log `results/codex_log/runs/gate_a_compare.log`. Audit, rebuild and tests completed; their logs are in `results/codex_log/runs/gate_a_{audit_final,build_final,tests}.log`.
- Exact command to continue: `cd /home/jupyter-1nt23cb058/Capstone && cat results/codex_log/RESUME.md && ps -p 2876953 -o pid=,stat= && cat results/codex_log/runs/gate_a_compare.log && cat results/cleaning_compare_v2.json`.

## Remaining queue (NOT RUN)

1. D: h=6 and h=24 cleaned gate.
2. E: latency, synchronized, 50 warmup + 200 timed.
3. F: PVR and smoothness with matched lambda=0 and `figures/pvr_vs_gradient.pdf`; Q blocked by absent traffic index.
4. G: ablation with full model, lambda sweep, cone angles, SRTM/none/shuffled/northing/coordinates controls.
5. H: worst-station calibration-fault test.
6. I: Integrated Gradients with named v2 channels and `decay_definition.md`.
7. J: routing only after predicted-field range/correlation gate; use the training feature builder.
8. K: figures, Makefile, MANIFEST, and claim verdicts C1–C14 in `claude_paper.md` section 6.
