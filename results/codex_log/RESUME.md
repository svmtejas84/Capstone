# Resume

- Step 4j fixed protocol committed/pushed at `27dd8ce`. Step 1 data fix built and temperature peak passed at 08:00 UTC. Step 1 source/results commit is pending; Step 2 benchmark, LOSO and lambda reruns have not started.
- Historical weather-dependent results are retained as shifted-weather results. New opt-in data builder: `python -m scripts.build_data_v2j`; outputs `results/data_v2j_arrays.npz` and `results/data_v2j_fit.json`. Original `build()` behavior remains default.
- No `scripts.*` process was running at initial check. Before any new work, check processes again. Continue with fixed v2g models/seeds and existing criteria, no tuning. Long jobs must use `scripts/run_supervised.sh` with per-seed/fold checkpoints. No London work.
