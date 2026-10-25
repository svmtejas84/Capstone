# S3 residual physics controls

Source `scripts/physics_controls_v2c.py`, `configs/gate_v2c.yaml`, seeds [11, 23, 37, 51, 79], commit `107388bc8988d28c15a655046d2e1a51410f872d`, 2026-10-25T04:09:31.461222+00:00. Q absent (no measured traffic index).

| Model | MAE mean±SD (µg/m³) | PVR at zero mean±SD (%) | Mean edge gradient (µg/m³) | Dirichlet energy (µg²/m⁶) |
|---|---:|---:|---:|---:|
| stpignn_corrected | 8.259108±0.185399 | 46.031300±0.453204 | 23.660414 | 1289.694706 |
| stpignn_lambda0 | 8.160498±0.218007 | 45.924339±0.379431 | 24.124139 | 1361.782726 |
| stpignn_laplacian | 8.282859±0.242948 | 46.122834±0.557434 | 22.064324 | 1096.042120 |
Corrected minus stpignn_lambda0: MAE paired mean 0.098610, 95% seed-t CI [-0.016880927409557683, 0.21410145069762948]; PVR(0) paired mean 0.106961 percentage points, CI [-0.2357697079372732, 0.4496917840784524].
Corrected minus stpignn_laplacian: MAE paired mean -0.023751, 95% seed-t CI [-0.43079045968985985, 0.3832892422921912]; PVR(0) paired mean -0.091534 percentage points, CI [-1.2172217906980065, 1.034153860154119].

Physics penalty changes MAE or PVR(0) beyond five-seed paired noise under the predeclared 95% seed-t rule: NO.
source: results/physics_controls_v2c.csv and results/physics_controls_v2c.json; produced by scripts/physics_controls_v2c.py.
