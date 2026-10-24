# Resume

- Last completed gate: Gate C LOSO. Predeclared verdict TIE; Gate C final log commit `68df3b0` was pushed to `origin/audit/canonical-notebook-20261023`. Gates A and B are also complete.
- Branch: `audit/canonical-notebook-20261023`.
- Latest commit: HEAD after the checkpoint commit named `Checkpoint: Gates A-C complete, S1-S4 queued`; run `git rev-parse HEAD` to obtain its hash. The preceding completed Gate C commit is `68df3b0`.
- Running job: none (PID: none; log path: none).
- NEXT: S1 diagnose; S2 residual formulation; S3 physics controls; S4 LOSO rerun. These were proposed but NOT RUN. The full S1-S4 prompt text is not in this handoff; ask the user to resend it before execution. Gate B/C results are final as precommitted.
- Continue command: `cd /home/jupyter-1nt23cb058/Capstone && cat results/codex_log/RESUME.md && git rev-parse HEAD && git status --short`.

## Completed results

- Gate A: cleaned training PM2.5 max 493 µg/m³; see `results/cleaning_compare_v2.json` and `results/cleaning_counts_v2.csv`.
- Gate B: cleaned h=1 comparison in `results/gate_v2b.csv` and `results/gate_v2b.md`. Persistence MAE/R² 8.116095/0.532089; IDW 22.698642/-0.205856; validation-selected corrected ST-PIGNN 20.613632/0.001594.
- Gate C: 15 folds considered, 11 scored, 14,583 observed test pairs per method. Pooled results in `results/loso_summary_v2.csv`; decision and bootstrap CI in `results/loso_decision_v2.json`; per-station scores in `results/loso_per_station_v2.csv`; raw predictions in `results/loso_predictions_v2.parquet`. Known-station ST-PIGNN versus ordinary kriging: MAE difference -0.305056 µg/m³, 95% paired UTC-day CI [-1.163714, 0.607623]; verdict TIE. Source commit `e90fd05`, config `configs/loso_v2.yaml`, seeds 11/23/37.
- `claude_paper.md` has appended factual Step 4b-A, Step 4b-B and Step 4b-C handoffs. Do not reread it in full.

## NOT RUN queue after S1-S4

1. D: cleaned h=6 and h=24 gate.
2. E: latency, synchronized, 50 warmup + 200 timed.
3. F: PVR and smoothness with matched lambda=0; Q blocked by absent traffic index.
4. G: ablation, including full model, lambda, cone and elevation controls.
5. H: calibration-fault test.
6. I: Integrated Gradients with named v2 channels.
7. J: routing after predicted-field range/correlation check, using the training feature builder.
8. K: figures, Makefile, MANIFEST, claim verdicts C1-C14.
9. L: citywide, conditional.
10. M: London, conditional.
