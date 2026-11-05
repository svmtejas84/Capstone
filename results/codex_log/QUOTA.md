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
- S2 analysis completed 2026-10-25 04:03:07 UTC, about 1 hour 18 minutes after its start. The five-hour limit is not yet near; commit/push S2 before S3.
- S3 started 2026-10-25 UTC after S2 push. About 1 hour 25 minutes elapsed since S1 start; five-hour limit not near. Commit/push S3 before S4.
- S3 analysis completed 2026-10-25 04:10:26 UTC, about 7 minutes after start. Commit/push S3 before S4; five-hour limit not near.
- S4 started 2026-10-25 UTC after S3 push. Roughly 1 hour 35 minutes elapsed since S1 start; allow the long LOSO run, then append Step 4c, commit/push and stop. Do not start D-M.
- 2026-10-25 08:27 UTC: new W1–W8 round begins with an approximately five-hour ceiling. S4 is already pushed. W1 ended at 08:29 UTC with the user-specified AR stop condition, well before the time ceiling. No W2–W8 job was launched.
- 2026-10-25 08:50 UTC: X1–X5 diagnostic completed about 23 minutes after the new round began. Commit/push the diagnostic and stop; W2 is explicitly excluded from this step.
- 2026-10-25 09:13 UTC: W2 source implemented and all 12 neural methods passed a forward/backward smoke check on CUDA. The 08:27 UTC five-hour window has about 4 hours 14 minutes left. Commit/push the source before long training; train priority horizons 1, 6, 24 first and checkpoint results after each complete horizon.
- 2026-10-25 09:30 UTC: priority h=1 fully completed, including corrected references and 2,000 paired-day W5 checks. About 3 hours 57 minutes remain. Source/result commits and pushes precede h=6; W3/W4/W6/W7/W8 runners are prepared but not yet run.
- 2026-10-25 09:51 UTC: h=6 complete, about 3 hours 36 minutes remain until 13:27 UTC. Commit/push h=6 and then run priority h=24. W3/W4/W6/W7/W8 still not run.
- 2026-10-25 10:07 UTC: all priority W2 horizons h=1/6/24 complete with W5 partial criteria; about 3 hours 20 minutes remain. Commit/push h=24, then start W6 before h=3/12 per user priority. W3/W4/W7/W8 remain unrun.
- 2026-10-25 12:52 UTC: five-hour window ends near 13:27 UTC; about 35 minutes remain. W2 h=3 complete, W6 at fold 12/15, h=12 still queued. Stop cleanly before limit if remaining steps cannot finish.
- 2026-10-25 13:30 UTC: five-hour limit passed. W6 completed at 13:14 and h=12 completed; commit and push completed results, leave W3/W4/W7/W8 queued, start no further study run.
- 2026-10-25 13:30 UTC: W6 pushed as `2ce644a`; h=12 final artifact commit/push is the last action in this time window. W3/W4/W7/W8 remain queued.
- 2026-10-25 13:37 UTC: user continuation starts a new five-hour work window ending near 18:35 UTC. W7 runs first, followed by W3, W4, W8. Reserve time to checkpoint and push before the limit.
- 2026-10-25 13:40 UTC: about 4 hours 55 minutes remain; W7 at h=1 original lambda=0 final seeds. W3/W4/report source prepared while W7 trains.

- 2026-11-04T14:33:46.874842+00:00 DONE deviation 6 Part 2: protocol-inflation analysis from stored result files only, no retraining. P0 baseline/persistence gains cannot be reconstructed on its 308 pairs; P1/P2/P3/P4 strongest-baseline MAE gains are -9.323752/-12.607068/-0.143013/+0.097270 ug/m3. Sources `scripts/protocol_inflation_v2h.py`, `results/protocol_inflation_v2h.csv`, `figures/protocol_inflation.pdf`; fixed h=1 and existing selected seeds.

- 2026-11-04T14:35:45.839945+00:00 START W4 supervised sensor-density run, PID 3475905, source commit `01a87a0`, log `runs/w4_v2h.log`; restart skips completed model/draw rows.

- 2026-11-04T14:45:39.233265+00:00 DONE W4 sensor-density: 100 scored rows (h=1/24, 3/5 stations, five draws, five methods), 50 ten-station rows BLOCKED because only eight stations have observed-lag train pairs. All scored pooled R2 means are negative. Three-station draw means happened to have lower MAE than five-station means; draws differ, so do not interpret as density improvement or physics robustness. Source `scripts/lowdata_v2h.py`, config `configs/benchmark_v2g.yaml`, seeds/draws [11,23,37,51,79], source commit `01a87a0`, `results/sensor_density_v2h.csv`, `results/sensor_density_summary_v2h.csv`, `figures/sensor_density.pdf`, raw `runs/w4_v2h.log`.

- 2026-11-04T14:46:01.869365+00:00 START Part 3 supervised conformal run, PID 3478053, source commit `37531f7`, log `runs/conformal_v2h.log`; checkpoint per horizon/calibration/model.

- 2026-11-04T14:51:11.392312+00:00 DONE Part 3 conformal: 288 horizon/pooled × calibration × nominal × fixed/rolling × model rows; per-station/per-month coverage in `results/conformal_station_month_v2h.csv`. No model meets the fixed interval-score-vs-persistence-and-ridge plus ±5-point coverage criterion; 80% train-tail fixed coverage is below nominal at every horizon for all six models. Source `scripts/conformal_v2h.py`, fixed seed 11, LR 3e-4, 10 epochs, config `configs/benchmark_v2g.yaml`, source commit `37531f7`, raw `runs/conformal_v2h.log`; predictions checkpointed per horizon/calibration/model. Validation-calibration results exploratory due A/B architecture ranking on validation.

- 2026-11-04T14:51:38.202128+00:00 START Part 4 group-DRO supervised run, PID 3479087, source commit `8815516`, log `runs/groupdro_v2h.log`; fold/method/seed checkpoint.

- 2026-11-04T14:56:08.651690+00:00 Part 4 supervisor PID 3479087 restarted after child termination to load five-seed source; completed fold/method/seed rows retained.

- 2026-11-04T15:13:42.360229+00:00 DONE Part 4 five-seed attribute-embedded LOSO. Validation selected eta=0.01. Group-DRO pooled MAE/R2 21.356246/-0.147737 vs best fixed ridge_weather_static 20.593676/0.072518; paired UTC-day MAE CI for group-DRO minus baseline [+0.209967,+1.324329], LOSS. Matched ERM 21.319738/-0.134574, also LOSS. All 15 folds retained; 11 scored, four zero-test-target folds [5547,5548,6975,2498781] reported. Per-station table includes five baselines. Source `scripts/loso_groupdro_v2h.py`, config `configs/data_v2.yaml` and `configs/benchmark_v2g.yaml`, seeds [11,23,37,51,79], source commit `8448e30`, 2,000 paired UTC-day bootstrap draws; raw `runs/groupdro_v2h.log`, resummary `runs/groupdro_v2h_resummary.log`.

- 2026-11-04T15:14:13.958291+00:00 START W3 DEM supervised run, PID 3483121, source commit `212cbcd`, log `runs/dem_v2h.log`; checkpoint per horizon/variant/model/seed.

- 2026-11-04T15:25:41.375357+00:00 DONE W3 DEM: 160 fixed horizon/variant/model/seed fits, 32 variant rows and 32 paired UTC-day bootstrap comparisons. Validation-best A/B/C is adaptive_graph_st at h=1 and 24. SRTM h=1 criterion MET: versus no-terrain ΔMAE -0.014685 ug/m3, 95% CI [-0.019364,-0.009846]; all fixed northing/shuffle controls also favor SRTM. h=24 criterion NOT MET: SRTM minus none +0.048087, CI [-0.010084,+0.104894], and northing performs better. Per-station SRTM values verified against graph elevations; correlation with northing 0.367851. Source `scripts/dem_study_v2h.py`, config `configs/benchmark_v2g.yaml`, model seeds [11,23,37,51,79], shuffle seeds [4201..4205], 2,000 UTC-day draws, source commits `212cbcd` and atomic-write `2319df6`, raw `runs/dem_v2h.log`.

- 2026-11-04T15:27:36.887378+00:00 DONE W8 no-training citywide precheck: 154,902 topology nodes, one raw weather source, 22 nodes with stored hourly model-input rows, 154,880 without stored temporal rows, all nodes with SRTM elevation. Stored-node exact duplicate weather series 5/22 (22.727%); broadcasting sole raw source citywide gives 100% identical series, so fixed >50% rule BLOCKS citywide training. Source `scripts/citywide_precheck_v2h.py`, source commit `dd94737`, no seed, raw `runs/w8_citywide_v2h.log`. No citywide training.

- 2026-11-04T15:30:23.170886+00:00 DONE deviation 6 Step 4h: appended one 169-line paper section from finalized outputs, then corrected W8 projected-duplicate line and table spacing; verified P0-P4 rows, 150 W4 rows, 288 conformal rows, five-seed LOSO tables, 64 DEM rows, W7 all horizons, W8 BLOCKED, and no running study jobs. Paper source `scripts/append_step4h_v2h.py`, generation commit `62f0df1`, run log `runs/step4h_paper_v2h.log`. All requested bounded work complete; stop before routing, IG, citywide training or second city.
2026-11-05 R1 engineering audit: no GPU training and no new Bengaluru/London/Copenhagen experiment. Only saved-prediction recomputation, documentation, web source checks, lightweight existing tests, and synthetic CPU recovery tests were run. No active supervisor process remains.
2026-11-05 Step 4i-1: zero GPU training; local weather timestamp measurement only, 37,152 stored hourly rows. No active experiment jobs.
2026-11-05 Step 4i-2: zero GPU training; 188 small LAQN annual-report metadata requests plus one station/species metadata request, no hourly observation-series download. Delhi lookup used source pages only. No active experiment job.
2026-11-05 Step 4i-3: paper tables/source lines only; zero GPU training; no new job.
2026-11-05 Step 4j-1: CPU-only data rebuild and one shift test; zero GPU training. No experiment job running at this checkpoint.
2026-11-05 Step 4j-2: one sequential supervised benchmark job active; per-seed CSV and prediction Parquet checkpoints. LOSO, lambda and DEM jobs have not started.
2026-11-05T12:56Z Step 4j-2 resource correction: GPU unavailable (`gpu: null` in execution manifest; torch CUDA false). Benchmark is CPU-only, 230/300 neural seed fits saved. Remaining full Step 2 may require many more CPU hours.
2026-11-05 Step 4j GPU correction: CPU job stopped. Host V100 is available outside sandbox; CPU-only partial outputs archived and excluded. GPU neural rerun pending; zero active jobs after stop.
2026-11-05T13:01:58Z Step 4j GPU benchmark active: one host V100 neural job; no CPU neural job and no concurrent experiment.
2026-11-05T14:00:57Z Step 4j GPU benchmark complete: about 59 minutes on Tesla V100, all five horizons. No active benchmark job; LOSO/lambda/DEM pending.
2026-11-05T15:07:54Z Step 4j LOSO complete: about 63 minutes on Tesla V100, all fixed folds and both anchors. Lambda and DEM pending.
