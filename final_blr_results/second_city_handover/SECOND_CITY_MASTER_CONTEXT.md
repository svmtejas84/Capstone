# Second-city research handover — independent replication candidate

This is a data/protocol handover only. London is a candidate, not approved. No second-city data eligibility gate is passed and no training is authorized. Bengaluru has repeatedly exposed test data, so independent replication is needed to determine whether forecasting/physics findings transfer beyond the development city. Do not select a city or protocol from expected scores.

## Bengaluru conclusions

Corrected ST-PIGNN was evaluated on 15 monitoring stations, not directly on the 154,902-node road graph. v2l found mixed horizon effects for weak directional regularization; no mass conservation or full advection–diffusion equation was implemented. v2m completed 50 MLP/TCN cells under a different weather-information protocol; no ST-PIGNN–TCN comparison survived Holm. Corrected W6 LOSO lost to weather/static ridge (MAE 22.314 vs 20.624 µg/m³; 11 scored stations, four unscored). v2r compact decoder lost to forecast-IDW/train mean; three all-city arrays are experimental estimates only. RGDR implemented/tests passed but failed frozen exposure and had no model pilot; novelty and predictive value are unestablished. Captum only covered v2m MLP/TCN; ST-PIGNN IG unavailable. Routing effectiveness is not evaluated.

## Reusable repository

`src/stpignn/`, `scripts/build_data_v2.py`, `scripts/benchmark_v2g.py`, `final_blr_results/baselines/v2m/reproducibility/`, `final_blr_results/physics_audit/reproducibility/`, and `final_blr_results/final_research_v2r/` contain versioned code/protocols. Pin source commit and re-audit feature availability before reuse.
