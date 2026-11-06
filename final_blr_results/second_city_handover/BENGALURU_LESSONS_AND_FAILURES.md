# Second-city research handover — independent replication candidate

This is a data/protocol handover only. London is a candidate, not approved. No second-city data eligibility gate is passed and no training is authorized. Bengaluru has repeatedly exposed test data, so independent replication is needed to determine whether forecasting/physics findings transfer beyond the development city. Do not select a city or protocol from expected scores.

## Lessons

1. Keep station and road graphs separate; topology does not provide road labels.
2. Enforce forecast-cutoff provenance for every feature; original notebook included target-hour pollutant input and copied station histories to roads.
3. Record v2j/v2m weather protocols separately; comparisons are cross-protocol.
4. Use independent spatial sites as inferential units; repeated timestamps do not create more sites. Four LOSO stations remained unscored.
5. Strong baselines matter; ridge, station mean and forecast-IDW were competitive or better.
6. A lower hinge violation score does not establish physical validity, source terms or conservation.
7. RGDR age gate did not solve sparse regularization exposure; do not relax post hoc.
8. No independent road truth or route effectiveness result exists.

Historical test exposure means Bengaluru is exploratory for any future design.
