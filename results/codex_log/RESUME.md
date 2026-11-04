# Resume

- 2026-11-04T14:35:45.839945+00:00 Deviation 6 W7 check and Part 2 protocol analysis complete and pushed.
- W4 sensor-density RUNNING under `scripts/run_w4_supervised_v2h.sh`, supervisor PID 3475905, `flock` + `setsid nohup` + `until` restart loop. Check `results/codex_log/runs/w4_v2h.log` and `results/sensor_density_v2h.csv`; completed model/draw rows are skipped on restart. Do not start another W4 copy.
- Next after W4: Part 3 conformal, Part 4 group-DRO, W3 DEM, W8 citywide precheck. Five-hour window ends near 2026-11-04 19:31 UTC. Preserve old outputs; append logs; new files `_v2h`.
