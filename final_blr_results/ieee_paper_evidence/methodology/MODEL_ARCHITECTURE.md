# Model architecture evidence

Corrected ST-PIGNN is a station-graph GINE–GRU model with 18 channels, 12 input hours, log1p-compatible residual forecasting over causal persistence, and an observed-target objective. The production notebook's historical implementation is a separate 16-channel road-partition GINE–GRU pathway with a surviving historical checkpoint; the notebook input construction included target-hour leakage and other invalid assumptions. Do not present its weights as corrected-model evidence.

v2m MLP and TCN controls completed 50 cells (two model families, five horizons, five seeds each) under a different weather-information protocol from historical ST-PIGNN. The v2r spatial decoder is the existing compact 1,249-parameter model; it did not outperform its controls.

Source inventory: `results/research_audit_r1/architecture_inventory.md`, `final_blr_results/citywide_extension/v2q/ORIGINAL_MODEL_ARCHITECTURE.md`, and version-specific round reports.
