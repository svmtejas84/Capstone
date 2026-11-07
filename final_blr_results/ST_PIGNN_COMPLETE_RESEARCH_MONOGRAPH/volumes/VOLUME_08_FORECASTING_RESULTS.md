# Volume 8 — Forecasting benchmarks, controls and statistical inference

<a id="volume-08"></a>

## Editorial reconstruction and evidentiary boundary

Evaluation populations and weather protocols are part of every result. The v2l physics comparison uses 14,583 matched observed station-hour pairs over 177 UTC days at each horizon and five seeds; paired statistics were clustered by day, with exploratory Holm families and seven-day block sensitivity. A negative MAE difference favors the first model. At h=6 the physics-minus-λ0 ensemble difference is −0.410 µg/m³; h=24 is +0.145. The v2m 50-cell MLP/TCN study found two ST-PIGNN-versus-MLP Holm-surviving contrasts at 6 and 12 hours, none versus TCN, under differing weather protocols. Strong statistical baselines and negative R² values remain part of the record. Repeated test exposure prevents confirmatory interpretation. [EVIDENCE: v2l verdict | final_blr_results/physics_audit/FINAL_PHYSICS_VERDICT.md | snapshot 1c46a4b]

## Full round-specific source exhibits

The exhibits reproduce the cited local reports as source evidence. Their original round-specific conclusions may be narrower than later findings; read the editorial reconstruction and final synthesis before treating one exhibit as the final verdict.

## Source exhibit 1: `results/benchmark_v2j.md`

[EVIDENCE: `results/benchmark_v2j.md` | SHA-256 `cc0ad8792dbae97607364937dd35234a474738ee96909bf75ed94a1dbcd29a42` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Benchmark v2g

Source `scripts/summarize_benchmark_v2j.py`, `configs/benchmark_v2g.yaml`, seeds [11,23,37,51,79], commit `94e09d8b3b7578309dfc6a022e3ec3e899d4c0e5`, 2026-11-05T16:08:43.502072+00:00.

| h (hours) | Model | Test pairs | MAE (µg/m³) | R² |
|---:|---|---:|---:|---:|
| 1 | adaptive_graph_st | 14583 | 7.946646 | 0.589726 |
| 1 | adaptive_graph_st_fixed_knn | 14583 | 8.133109 | 0.583399 |
| 1 | climatology_hod_dow | 14583 | 21.468647 | -0.092450 |
| 1 | gine_gru_wind | 14583 | 7.983870 | 0.576905 |
| 1 | gru_only | 14583 | 7.991347 | 0.577336 |
| 1 | persistence | 14583 | 8.116095 | 0.532089 |
| 1 | ridge_lag_calendar_weather | 14583 | 8.706329 | 0.569749 |
| 1 | same_hour_yesterday | 14583 | 14.130312 | 0.283173 |
| 1 | st_gru_gcn | 14583 | 8.219692 | 0.546568 |
| 1 | station_train_mean | 14583 | 20.964647 | -0.014396 |
| 1 | stpignn_lambda0 | 14583 | 8.052157 | 0.577463 |
| 1 | stpignn_laplacian | 14583 | 8.098208 | 0.584650 |
| 1 | stpignn_original | 14583 | 8.025685 | 0.584580 |
| 1 | stpignn_v2 | 14583 | 9.529689 | 0.525801 |
| 1 | stpignn_v2_source_removed | 14583 | 9.520366 | 0.521431 |
| 1 | stpignn_v2_transport_removed | 14583 | 8.071176 | 0.571929 |
| 1 | vanilla_gcn | 14583 | 8.255069 | 0.539090 |
| 3 | adaptive_graph_st | 14583 | 13.052213 | 0.129641 |
| 3 | adaptive_graph_st_fixed_knn | 14583 | 12.648611 | 0.268449 |
| 3 | climatology_hod_dow | 14583 | 21.468647 | -0.092450 |
| 3 | gine_gru_wind | 14583 | 12.744374 | 0.280456 |
| 3 | gru_only | 14583 | 12.654972 | 0.259475 |
| 3 | persistence | 14583 | 13.244358 | 0.100938 |
| 3 | ridge_lag_calendar_weather | 14583 | 13.356836 | 0.313913 |
| 3 | same_hour_yesterday | 14583 | 14.130312 | 0.283173 |
| 3 | st_gru_gcn | 14583 | 13.172390 | 0.146772 |
| 3 | station_train_mean | 14583 | 20.964647 | -0.014396 |
| 3 | stpignn_lambda0 | 14583 | 12.471519 | 0.278184 |
| 3 | stpignn_laplacian | 14583 | 12.164030 | 0.312659 |
| 3 | stpignn_original | 14583 | 12.341537 | 0.304991 |
| 3 | stpignn_v2 | 14583 | 13.321236 | 0.225775 |
| 3 | stpignn_v2_source_removed | 14583 | 13.542488 | 0.207820 |
| 3 | stpignn_v2_transport_removed | 14583 | 13.181196 | 0.274787 |
| 3 | vanilla_gcn | 14583 | 13.230824 | 0.135705 |
| 6 | adaptive_graph_st | 14583 | 15.171126 | 0.097414 |
| 6 | adaptive_graph_st_fixed_knn | 14583 | 15.955085 | 0.068961 |
| 6 | climatology_hod_dow | 14583 | 21.468647 | -0.092450 |
| 6 | gine_gru_wind | 14583 | 16.025676 | 0.121780 |
| 6 | gru_only | 14583 | 15.162159 | 0.110641 |
| 6 | persistence | 14583 | 16.606891 | -0.161368 |
| 6 | ridge_lag_calendar_weather | 14583 | 16.106333 | 0.171015 |
| 6 | same_hour_yesterday | 14583 | 14.130312 | 0.283173 |
| 6 | st_gru_gcn | 14583 | 16.467860 | -0.103882 |
| 6 | station_train_mean | 14583 | 20.964647 | -0.014396 |
| 6 | stpignn_lambda0 | 14583 | 15.116481 | 0.142052 |
| 6 | stpignn_laplacian | 14583 | 14.835915 | 0.171044 |
| 6 | stpignn_original | 14583 | 14.706262 | 0.181031 |
| 6 | stpignn_v2 | 14583 | 15.855576 | 0.095351 |
| 6 | stpignn_v2_source_removed | 14583 | 16.025538 | 0.063317 |
| 6 | stpignn_v2_transport_removed | 14583 | 15.878058 | 0.126021 |
| 6 | vanilla_gcn | 14583 | 16.611604 | -0.113498 |
| 12 | adaptive_graph_st | 14583 | 16.926308 | -0.007270 |
| 12 | adaptive_graph_st_fixed_knn | 14583 | 17.601434 | -0.059712 |
| 12 | climatology_hod_dow | 14583 | 21.468647 | -0.092450 |
| 12 | gine_gru_wind | 14583 | 16.876650 | 0.080042 |
| 12 | gru_only | 14583 | 16.388554 | 0.068118 |
| 12 | persistence | 14583 | 19.105561 | -0.456901 |
| 12 | ridge_lag_calendar_weather | 14583 | 17.389648 | 0.084610 |
| 12 | same_hour_yesterday | 14583 | 14.130312 | 0.283173 |
| 12 | st_gru_gcn | 14583 | 19.540140 | -0.328535 |
| 12 | station_train_mean | 14583 | 20.964647 | -0.014396 |
| 12 | stpignn_lambda0 | 14583 | 15.771677 | 0.104603 |
| 12 | stpignn_laplacian | 14583 | 15.506682 | 0.179835 |
| 12 | stpignn_original | 14583 | 15.509281 | 0.142016 |
| 12 | stpignn_v2 | 14583 | 17.663727 | -0.000258 |
| 12 | stpignn_v2_source_removed | 14583 | 18.237435 | -0.107369 |
| 12 | stpignn_v2_transport_removed | 14583 | 17.490540 | 0.035421 |
| 12 | vanilla_gcn | 14583 | 19.054571 | -0.417399 |
| 24 | adaptive_graph_st | 14583 | 13.744016 | 0.396024 |
| 24 | adaptive_graph_st_fixed_knn | 14583 | 15.171014 | 0.353674 |
| 24 | climatology_hod_dow | 14583 | 21.468647 | -0.092450 |
| 24 | gine_gru_wind | 14583 | 14.188251 | 0.390879 |
| 24 | gru_only | 14583 | 14.106813 | 0.372422 |
| 24 | persistence | 14583 | 14.130312 | 0.283173 |
| 24 | ridge_lag_calendar_weather | 14583 | 15.005095 | 0.357805 |
| 24 | same_hour_yesterday | 14583 | 14.130312 | 0.283173 |
| 24 | st_gru_gcn | 14583 | 13.896435 | 0.329070 |
| 24 | station_train_mean | 14583 | 20.964647 | -0.014396 |
| 24 | stpignn_lambda0 | 14583 | 13.756937 | 0.379094 |
| 24 | stpignn_laplacian | 14583 | 14.004429 | 0.380395 |
| 24 | stpignn_original | 14583 | 13.901807 | 0.377261 |
| 24 | stpignn_v2 | 14583 | 14.708729 | 0.344348 |
| 24 | stpignn_v2_source_removed | 14583 | 14.677748 | 0.343028 |
| 24 | stpignn_v2_transport_removed | 14583 | 14.044759 | 0.384829 |
| 24 | vanilla_gcn | 14583 | 14.028811 | 0.329959 |

#### Fixed criteria

h=1, gine_gru_wind: met; persistence ΔMAE -0.132225 CI [-0.216927,-0.052045]; same_hour_yesterday ΔMAE -6.146442 CI [-6.900165,-5.419064].
h=1, adaptive_graph_st: met; persistence ΔMAE -0.169449 CI [-0.284212,-0.053512]; same_hour_yesterday ΔMAE -6.183665 CI [-6.925528,-5.438952].
h=1, adaptive_graph_st_fixed_knn: not met; persistence ΔMAE +0.017014 CI [-0.103356,+0.138057]; same_hour_yesterday ΔMAE -5.997203 CI [-6.747396,-5.252284].
h=1, stpignn_v2: not met; persistence ΔMAE +1.413594 CI [+1.145301,+1.694451]; same_hour_yesterday ΔMAE -4.600623 CI [-5.403371,-3.830316].
h=1, stpignn_v2_source_removed: not met; persistence ΔMAE +1.404270 CI [+1.127552,+1.689757]; same_hour_yesterday ΔMAE -4.609946 CI [-5.419543,-3.838364].
h=1, stpignn_v2_transport_removed: not met; persistence ΔMAE -0.044919 CI [-0.135443,+0.042624]; same_hour_yesterday ΔMAE -6.059135 CI [-6.817997,-5.325371].
h=1, gru_only: met; persistence ΔMAE -0.124748 CI [-0.211269,-0.041825]; same_hour_yesterday ΔMAE -6.138964 CI [-6.891419,-5.400934].
h=1, vanilla_gcn: not met; persistence ΔMAE +0.138973 CI [+0.097528,+0.183047]; same_hour_yesterday ΔMAE -5.875243 CI [-6.655790,-5.108555].
h=1, st_gru_gcn: not met; persistence ΔMAE +0.103597 CI [+0.061070,+0.146453]; same_hour_yesterday ΔMAE -5.910619 CI [-6.676339,-5.157949].
h=1, stpignn_original: not met; persistence ΔMAE -0.090410 CI [-0.189909,+0.002105]; same_hour_yesterday ΔMAE -6.104627 CI [-6.863391,-5.357383].
h=1, stpignn_lambda0: not met; persistence ΔMAE -0.063938 CI [-0.144829,+0.018536]; same_hour_yesterday ΔMAE -6.078155 CI [-6.839228,-5.336821].
h=1, stpignn_laplacian: not met; persistence ΔMAE -0.017887 CI [-0.122860,+0.086231]; same_hour_yesterday ΔMAE -6.032104 CI [-6.788533,-5.292411].
h=3, gine_gru_wind: met; persistence ΔMAE -0.499984 CI [-0.825387,-0.200345]; same_hour_yesterday ΔMAE -1.385938 CI [-2.230282,-0.596680].
h=3, adaptive_graph_st: met; persistence ΔMAE -0.192145 CI [-0.231856,-0.156555]; same_hour_yesterday ΔMAE -1.078098 CI [-1.984434,-0.212886].
h=3, adaptive_graph_st_fixed_knn: met; persistence ΔMAE -0.595747 CI [-0.910680,-0.289615]; same_hour_yesterday ΔMAE -1.481701 CI [-2.313348,-0.685956].
h=3, stpignn_v2: not met; persistence ΔMAE +0.076878 CI [-0.281714,+0.444019]; same_hour_yesterday ΔMAE -0.809076 CI [-1.731380,+0.063590].
h=3, stpignn_v2_source_removed: not met; persistence ΔMAE +0.298130 CI [-0.025239,+0.634577]; same_hour_yesterday ΔMAE -0.587824 CI [-1.532187,+0.311045].
h=3, stpignn_v2_transport_removed: not met; persistence ΔMAE -0.063163 CI [-0.408680,+0.280036]; same_hour_yesterday ΔMAE -0.949116 CI [-1.803652,-0.161251].
h=3, gru_only: met; persistence ΔMAE -0.589387 CI [-0.924661,-0.271241]; same_hour_yesterday ΔMAE -1.475340 CI [-2.314517,-0.660370].
h=3, vanilla_gcn: not met; persistence ΔMAE -0.013534 CI [-0.106315,+0.080217]; same_hour_yesterday ΔMAE -0.899488 CI [-1.825080,-0.027127].
h=3, st_gru_gcn: not met; persistence ΔMAE -0.071968 CI [-0.150420,+0.004393]; same_hour_yesterday ΔMAE -0.957922 CI [-1.883724,-0.093732].
h=3, stpignn_original: met; persistence ΔMAE -0.902821 CI [-1.217034,-0.595843]; same_hour_yesterday ΔMAE -1.788775 CI [-2.629511,-1.007196].
h=3, stpignn_lambda0: met; persistence ΔMAE -0.772839 CI [-1.112657,-0.448616]; same_hour_yesterday ΔMAE -1.658792 CI [-2.495622,-0.861187].
h=3, stpignn_laplacian: met; persistence ΔMAE -1.080328 CI [-1.383569,-0.798276]; same_hour_yesterday ΔMAE -1.966281 CI [-2.791331,-1.185205].
h=6, gine_gru_wind: not met; persistence ΔMAE -0.581216 CI [-1.059127,-0.113383]; same_hour_yesterday ΔMAE +1.895364 CI [+1.082542,+2.734533].
h=6, adaptive_graph_st: not met; persistence ΔMAE -1.435765 CI [-1.857324,-0.975265]; same_hour_yesterday ΔMAE +1.040814 CI [+0.210452,+1.903569].
h=6, adaptive_graph_st_fixed_knn: not met; persistence ΔMAE -0.651806 CI [-1.096844,-0.207865]; same_hour_yesterday ΔMAE +1.824774 CI [+0.957738,+2.694820].
h=6, stpignn_v2: not met; persistence ΔMAE -0.751315 CI [-1.256808,-0.271716]; same_hour_yesterday ΔMAE +1.725264 CI [+0.833057,+2.640829].
h=6, stpignn_v2_source_removed: not met; persistence ΔMAE -0.581354 CI [-0.985350,-0.188730]; same_hour_yesterday ΔMAE +1.895226 CI [+0.990012,+2.813658].
h=6, stpignn_v2_transport_removed: not met; persistence ΔMAE -0.728833 CI [-1.210679,-0.252709]; same_hour_yesterday ΔMAE +1.747746 CI [+0.936035,+2.575977].
h=6, gru_only: not met; persistence ΔMAE -1.444732 CI [-1.880504,-1.003683]; same_hour_yesterday ΔMAE +1.031848 CI [+0.219547,+1.876354].
h=6, vanilla_gcn: not met; persistence ΔMAE +0.004713 CI [-0.148699,+0.165737]; same_hour_yesterday ΔMAE +2.481292 CI [+1.525441,+3.455021].
h=6, st_gru_gcn: not met; persistence ΔMAE -0.139031 CI [-0.266578,-0.012351]; same_hour_yesterday ΔMAE +2.337548 CI [+1.381642,+3.301297].
h=6, stpignn_original: not met; persistence ΔMAE -1.900629 CI [-2.343760,-1.441736]; same_hour_yesterday ΔMAE +0.575950 CI [-0.212747,+1.373650].
h=6, stpignn_lambda0: not met; persistence ΔMAE -1.490410 CI [-1.963357,-0.987453]; same_hour_yesterday ΔMAE +0.986169 CI [+0.167854,+1.814027].
h=6, stpignn_laplacian: not met; persistence ΔMAE -1.770976 CI [-2.232748,-1.298909]; same_hour_yesterday ΔMAE +0.705604 CI [-0.085667,+1.510486].
h=12, gine_gru_wind: not met; persistence ΔMAE -2.228911 CI [-2.953846,-1.469566]; same_hour_yesterday ΔMAE +2.746339 CI [+1.885032,+3.606532].
h=12, adaptive_graph_st: not met; persistence ΔMAE -2.179253 CI [-2.646397,-1.679069]; same_hour_yesterday ΔMAE +2.795997 CI [+1.896454,+3.743806].
h=12, adaptive_graph_st_fixed_knn: not met; persistence ΔMAE -1.504128 CI [-1.935881,-1.050168]; same_hour_yesterday ΔMAE +3.471122 CI [+2.554979,+4.463626].
h=12, stpignn_v2: not met; persistence ΔMAE -1.441834 CI [-2.017083,-0.852254]; same_hour_yesterday ΔMAE +3.533416 CI [+2.621618,+4.496355].
h=12, stpignn_v2_source_removed: not met; persistence ΔMAE -0.868127 CI [-1.340201,-0.392048]; same_hour_yesterday ΔMAE +4.107123 CI [+3.129469,+5.161717].
h=12, stpignn_v2_transport_removed: not met; persistence ΔMAE -1.615021 CI [-2.242399,-0.958637]; same_hour_yesterday ΔMAE +3.360228 CI [+2.478345,+4.245695].
h=12, gru_only: not met; persistence ΔMAE -2.717007 CI [-3.286969,-2.114294]; same_hour_yesterday ΔMAE +2.258242 CI [+1.409834,+3.126648].
h=12, vanilla_gcn: not met; persistence ΔMAE -0.050990 CI [-0.235234,+0.139631]; same_hour_yesterday ΔMAE +4.924260 CI [+3.755909,+6.212725].
h=12, st_gru_gcn: not met; persistence ΔMAE +0.434579 CI [+0.058790,+0.797067]; same_hour_yesterday ΔMAE +5.409829 CI [+4.190404,+6.669702].
h=12, stpignn_original: not met; persistence ΔMAE -3.596280 CI [-4.300959,-2.858951]; same_hour_yesterday ΔMAE +1.378969 CI [+0.590573,+2.155164].
h=12, stpignn_lambda0: not met; persistence ΔMAE -3.333884 CI [-4.061435,-2.570646]; same_hour_yesterday ΔMAE +1.641366 CI [+0.806613,+2.476607].
h=12, stpignn_laplacian: not met; persistence ΔMAE -3.598879 CI [-4.404913,-2.805783]; same_hour_yesterday ΔMAE +1.376370 CI [+0.595384,+2.133770].
h=24, gine_gru_wind: not met; persistence ΔMAE +0.057939 CI [-0.307619,+0.409348]; same_hour_yesterday ΔMAE +0.057939 CI [-0.307619,+0.409348].
h=24, adaptive_graph_st: met; persistence ΔMAE -0.386295 CI [-0.723199,-0.079855]; same_hour_yesterday ΔMAE -0.386295 CI [-0.723199,-0.079855].
h=24, adaptive_graph_st_fixed_knn: not met; persistence ΔMAE +1.040702 CI [+0.460728,+1.588534]; same_hour_yesterday ΔMAE +1.040702 CI [+0.460728,+1.588534].
h=24, stpignn_v2: not met; persistence ΔMAE +0.578417 CI [+0.081838,+1.048287]; same_hour_yesterday ΔMAE +0.578417 CI [+0.081838,+1.048287].
h=24, stpignn_v2_source_removed: not met; persistence ΔMAE +0.547436 CI [+0.073396,+1.002773]; same_hour_yesterday ΔMAE +0.547436 CI [+0.073396,+1.002773].
h=24, stpignn_v2_transport_removed: not met; persistence ΔMAE -0.085553 CI [-0.409155,+0.232846]; same_hour_yesterday ΔMAE -0.085553 CI [-0.409155,+0.232846].
h=24, gru_only: not met; persistence ΔMAE -0.023499 CI [-0.466097,+0.410028]; same_hour_yesterday ΔMAE -0.023499 CI [-0.466097,+0.410028].
h=24, vanilla_gcn: not met; persistence ΔMAE -0.101501 CI [-0.271530,+0.062929]; same_hour_yesterday ΔMAE -0.101501 CI [-0.271530,+0.062929].
h=24, st_gru_gcn: met; persistence ΔMAE -0.233876 CI [-0.349351,-0.123223]; same_hour_yesterday ΔMAE -0.233876 CI [-0.349351,-0.123223].
h=24, stpignn_original: not met; persistence ΔMAE -0.228504 CI [-0.710430,+0.239909]; same_hour_yesterday ΔMAE -0.228504 CI [-0.710430,+0.239909].
h=24, stpignn_lambda0: not met; persistence ΔMAE -0.373374 CI [-0.793311,+0.021527]; same_hour_yesterday ΔMAE -0.373374 CI [-0.793311,+0.021527].
h=24, stpignn_laplacian: not met; persistence ΔMAE -0.125883 CI [-0.618065,+0.353246]; same_hour_yesterday ΔMAE -0.125883 CI [-0.618065,+0.353246].

Any-model win: met.
Physics criterion: see fixed lambda check h=1 and h=24.
DEM criterion: not met.

## Source exhibit 2: `final_blr_results/baselines/v2m/FINAL_BASELINE_VERDICT.md`

[EVIDENCE: `final_blr_results/baselines/v2m/FINAL_BASELINE_VERDICT.md` | SHA-256 `e055392bdf4c5d3655fe0285d4fec0588cefff0cdffc0d5912e3ba5864944e82` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Final v2m Bengaluru baseline verdict

All 50/50 final cells completed on the V100, with five checkpoints and prediction files per model/horizon, each guarded by SHA-256 completion markers. This is an exploratory analysis on an exposed test set. Historical ST-PIGNN and other controls used centered v2j weather, whereas MLP/TCN used the corrected cutoff-safe v2m weather input. The comparisons below have exact matched targets and timestamps but are **cross-protocol**, not identical-input architectural ablations.

#### Five-seed ensemble metrics

| Horizon | MLP MAE / RMSE / R² | TCN MAE / RMSE / R² | Historical ST-PIGNN MAE | Strongest historical statistical baseline |
|---:|---:|---:|---:|---|
| 1 | 8.016 / 24.631 / 0.559 | 8.080 / 25.098 / 0.542 | 8.026 | persistence 8.116 |
| 3 | 12.543 / 32.209 / 0.245 | 12.268 / 31.571 / 0.275 | 12.342 | persistence 13.244 |
| 6 | 15.513 / 36.678 / 0.021 | 14.868 / 34.724 / 0.123 | 14.706 | same_hour_yesterday 14.130 |
| 12 | 16.026 / 35.090 / 0.104 | 15.278 / 34.235 / 0.147 | 15.509 | same_hour_yesterday 14.130 |
| 24 | 13.840 / 29.340 / 0.374 | 13.894 / 29.265 / 0.377 | 13.902 | persistence 14.130 |

#### Prespecified ten paired comparisons

Difference is ST-PIGNN MAE minus new baseline MAE; negative favors ST-PIGNN. CIs are nominal paired UTC-day bootstrap intervals; p-values are two-sided day-level sign-flip Monte Carlo values with Holm adjustment across all ten tests.

| h | Baseline | Difference | Nominal 95% CI | Raw p | Holm p | Holm verdict |
|---:|---|---:|---:|---:|---:|---|
| 1 | mlp | +0.009 | [-0.048, +0.063] | 0.7396 | 1.0000 | no ST-PIGNN advantage |
| 1 | tcn | -0.054 | [-0.133, +0.029] | 0.2094 | 1.0000 | no ST-PIGNN advantage |
| 3 | mlp | -0.202 | [-0.370, -0.047] | 0.0105 | 0.0840 | no ST-PIGNN advantage |
| 3 | tcn | +0.073 | [-0.080, +0.215] | 0.3283 | 1.0000 | no ST-PIGNN advantage |
| 6 | mlp | -0.807 | [-1.082, -0.519] | 0.0005 | 0.0050 | ST-PIGNN lower |
| 6 | tcn | -0.161 | [-0.373, +0.054] | 0.1584 | 0.9505 | no ST-PIGNN advantage |
| 12 | mlp | -0.517 | [-0.796, -0.256] | 0.0010 | 0.0090 | ST-PIGNN lower |
| 12 | tcn | +0.231 | [+0.024, +0.433] | 0.0300 | 0.2099 | no ST-PIGNN advantage |
| 24 | mlp | +0.062 | [-0.229, +0.372] | 0.6737 | 1.0000 | no ST-PIGNN advantage |
| 24 | tcn | +0.007 | [-0.265, +0.278] | 0.9620 | 1.0000 | no ST-PIGNN advantage |

ST-PIGNN has lower MAE than MLP at h=6 and h=12 after exploratory Holm adjustment. No ST-PIGNN versus TCN contrast survives adjustment. At h=3 versus MLP, the nominal interval excludes zero but Holm p=0.084. At h=12 TCN has lower MAE than historical ST-PIGNN with a nominal interval excluding zero, but Holm p=0.210. These are matched-target, different-weather-input comparisons and cannot isolate architecture.

#### Individual seeds, ensembles, and training

| Model | h | Mean individual MAE | Five-seed ensemble MAE | Selected LR |
|---|---:|---:|---:|---:|
| mlp | 1 | 8.154 | 8.016 | 0.0003 |
| mlp | 3 | 12.856 | 12.543 | 0.003 |
| mlp | 6 | 15.908 | 15.513 | 0.0003 |
| mlp | 12 | 16.340 | 16.026 | 0.001 |
| mlp | 24 | 14.025 | 13.840 | 0.001 |
| tcn | 1 | 8.190 | 8.080 | 0.0001 |
| tcn | 3 | 12.561 | 12.268 | 0.003 |
| tcn | 6 | 15.388 | 14.868 | 0.003 |
| tcn | 12 | 15.648 | 15.278 | 0.003 |
| tcn | 24 | 14.240 | 13.894 | 0.003 |

All ten ensembles improve on the mean individual-seed MAE. The individual-seed spread and complete per-seed MAE/RMSE/R² are in `comparisons/individual_seed_metrics.csv`; no missing seeds were substituted. MLP has 18,113 parameters; TCN has 16,641. The sum of final-cell training times is 84.8 s; the full supervised all-groups run (selection plus final fits) took about 166 s. Peak PyTorch allocated GPU memory was 125,483,008 bytes (about 120 MiB). The earlier MLP h=1 group ran separately. Four LR candidates had the same seed-11 validation-selection opportunity per model/horizon; selected TCN LR is at the upper grid boundary for h=3,6,12,24. No test-selected config or silently skipped seed was found. Per-epoch loss/validation histories were not recorded by the inherited fit function and are unavailable; saved final validation metrics and best epochs remain in per-cell metrics and group selection files.

#### Relation to established baselines

Both new models have lower MAE than historical persistence at every horizon. They are below historical same-hour-yesterday at h=1,3,24 and above it at h=6,12. At h=6 and h=12, same-hour-yesterday remains the strongest historical statistical baseline, and neither new neural model beats it. TCN is below MLP in MAE at h=3,6,12, while MLP is below TCN at h=1,24. Historical GRU-only is below both new models at h=1 and h=6, while TCN is below GRU-only at h=3 and h=12; MLP is below GRU-only at h=24. See `comparisons/secondary_comparisons.csv` for all matched-pair descriptive values. These facts do not justify a general claim that graph/physics complexity improves forecasting under the cutoff-safe information set.

#### Scientific limits and archive status

The weather correction changes inputs but not targets or evaluation masks. Historical neural checkpoints were not retrained; all cross-protocol contrasts are descriptive. The test set was repeatedly examined, there were six prior post-hoc deviations, and the 500 µg/m³ ceiling and sparse stations limit generalization. There is no validated full-road or street-level accuracy, measured emissions Q, or external replication. The pre-training local ZIP was checksum verified; its independent external copy is pending under the supervisor exception. The separate supplementary ZIP is `reproducibility/research_results_v2m.zip` (15,762,253 bytes, SHA-256 `f669952674bcc24a15fe6f5a5c492d3b6492f2e625d2179954aee6f51b6fef3b`); 275 members passed ZIP CRC and per-member SHA-256 verification. Its external copy is also pending. The descriptive plot is `figures/mae_by_horizon_v2m.png`.

## Source exhibit 3: `final_blr_results/physics_audit/FINAL_PHYSICS_VERDICT.md`

[EVIDENCE: `final_blr_results/physics_audit/FINAL_PHYSICS_VERDICT.md` | SHA-256 `7bddfc1776c8d23123c6ad0400cc1c0c98434db6c2e7bc4017565506d0f724fe` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Final physics attribution verdict — v2l

**Scope:** post-hoc reanalysis of existing corrected v2j Bengaluru predictions. Source training commit `9a299f1bf01787f26750515cad8dff370e9c9aa0`; v2k comparison commit `931bf09975dd17bfdca4f26259ede91046974f07`; v2l decision commit `2b2ab47`. No training, test-time selection, manuscript edit or citywide inference occurred. Complete methods: `methodology/PHYSICS_ATTRIBUTION_METHODOLOGY.md`.

#### 1. Predictive contribution and multiplicity

The table uses matched five-seed mean predictions on the same 14,583 observed station-hour targets (177 UTC days) at every horizon. Negative Δ favors physics. The original 35-test Holm results are preserved; the five-horizon family is a separately labelled retrospective sensitivity analysis.

| h | Physics−λ0 ensemble ΔMAE (µg/m³) | Nominal 95% UTC-day CI | Original 35-test Holm p | Retrospective five-test Holm p |
|---:|---:|---:|---:|---:|
| 1 | −0.026 | [−0.050,−0.001] | 0.4453 | 0.0840 |
| 3 | −0.130 | [−0.210,−0.055] | 0.0175 | 0.0025 |
| 6 | −0.410 | [−0.550,−0.274] | 0.0175 | 0.0025 |
| 12 | −0.262 | [−0.381,−0.139] | 0.0175 | 0.0025 |
| 24 | +0.145 | [−0.013,+0.314] | 0.6357 | 0.0840 |

There is exploratory evidence of better ensemble prediction at h=3,6,12 under both adjusted families. The h=1 nominal interval excludes zero, as did the separate fixed h=1 lambda check, but its 35-test Holm result does not; the h=24 ensemble is worse by point estimate. No historical success criterion is revised.

#### 2. Seed stability and ensemble dependence

| h | Seeds favoring physics | Mean individual-seed ΔMAE | Ensemble ΔMAE | Extra physics ensemble gain |
|---:|---:|---:|---:|---:|
| 1 | 1/5 | +0.009 | −0.026 | +0.036 |
| 3 | 3/5 | −0.005 | −0.130 | +0.125 |
| 6 | 5/5 | −0.566 | −0.410 | −0.156 |
| 12 | 4/5 | −0.254 | −0.262 | +0.008 |
| 24 | 3/5 | +0.155 | +0.145 | +0.011 |

At h=1 the ensemble gain reverses the average individual-model direction; at h=3 it accounts for nearly all the benefit. At h=6/12 individual models also improve, although h=12 is not universal across seeds. Seed counts are descriptive training variability on one test population, not independent replications. Full per-seed intervals and spread are in `seed_analysis/`.

#### 3. Model-selection validity

The three models share the exact 43,393-parameter backbone, corrected input arrays, graph/edge features, target transformation and observed test mask. Their source loss branches differ by upwind hinge, zero penalty or Laplacian gradient penalty. Each had four LR trials with seed-11 validation MAE, the same 30-epoch/patience-five budget, and five complete final seeds. No test-based selection is visible. Selected LRs differ at h=1,6,12,24, and best epochs differ, so this is a fair **validation-selected procedural ablation** but not a common-LR/common-epoch causal estimate of the penalty alone. No corrected v2j checkpoint exists for weight-level audit. Details: `selection_audit/model_selection_review.md`.

#### 4. Statistical and temporal robustness

The original 2,000-replicate UTC-day bootstrap and sign-flip values reproduce to rounding. Resampling is paired by day and observation-weighted; day-level sign symmetry and independence remain assumptions. Seven-consecutive-calendar-day moving-block CIs are [−0.068,+0.015], [−0.252,−0.042], [−0.632,−0.209], [−0.451,−0.076], [−0.064,+0.342] for h=1,3,6,12,24. Thus h=3/6/12 remain negative in this dependence sensitivity, h=1 does not. Months favor physics in 4/7, 6/7, 6/7, 6/7 and 1/7 respectively; unfavorable months were retained. The five largest absolute day sums account for 13–20% of absolute day effect depending on horizon. See `statistical_robustness/`.

#### 5. Physics versus Laplacian and physical behavior

Physics−Laplacian ensemble ΔMAE is −0.073, +0.178, −0.130, +0.003 and −0.103 µg/m³ across h=1,3,6,12,24. In the original 35-test family, physics has adjusted favorable evidence at h=1 and h=6; Laplacian is better at h=3; h=12 is indistinguishable and h=24 only nominally favors physics. The wind-cone PVR>0 of physics is lower than λ0 at h=1/12 but **higher** at h=3/6/24. Spatial gradients, variance and near-constant output rates do not show a unique transport-consistency signature. The same sparse observed station edges provide a descriptive reference, not street-level truth. The upwind hinge has no measured emissions Q and does not enforce mass conservation. Lower PVR or hinge magnitude cannot prove atmospheric validity. Details: `physical_diagnostics/`.

#### 6. Historical reconciliation and limits

Shifted-weather W7 found a weak λ=0.06 benefit only at h=6 among five horizons and generally harmful larger λ. Corrected v2j shifted h=1 into a small favorable fixed-check cell and retained no h=24 benefit. v2k's broader benchmark additionally found h=3/6/12 ensemble contrasts, but different weather, selection and aggregation prevent pooling old and new experiments as independent replication. Earlier physics-null findings and negative Laplacian/λ cells remain in `reconciliation/historical_physics_evidence.md`. The Bengaluru test set has been repeatedly exposed, horizons share observations, only 11 stations provide test targets, and no compatible citywide checkpoint or validated street-level ground truth exists.

#### Separate classifications

| Question | Classification | Reason |
|---|---|---|
| Predictive effect | **MIXED** | Exploratory adjusted benefit at h=3/6/12; h=1 fragile and h=24 absent. |
| Seed robustness | **MIXED** | Stronger at h=6/12, weak/inconsistent at h=1/3/24. |
| Ensemble dependence | **PRESENT** | Dominant at h=1/3; not the principal source at h=6/12. |
| Physics specificity | **UNSUPPORTED** | Laplacian and transport-proxy comparisons are inconsistent; no conservation/Q evidence. |
| Independent confirmation | **NOT AVAILABLE** | Same repeatedly examined Bengaluru test set; no external holdout. |

These classifications separate statistical predictive association from causal architectural attribution. A physical mechanism cannot be established from these saved outputs alone. Required local prediction caches have no verified independent durable backup; `reproducibility/` lists paths, checksums and the no-training regeneration command.

## Source exhibit 4: `final_blr_results/ieee_paper_evidence/results/RESULTS_VERIFICATION.md`

[EVIDENCE: `final_blr_results/ieee_paper_evidence/results/RESULTS_VERIFICATION.md` | SHA-256 `a09b90c9c197c7447eba5eae13ac66a80bf2b903f93e0a975522b76cf56a384d` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Results verification ledger

#### Verification performed

Values in this package are traced to round-specific saved reports and machine-readable summary tables. The v2m ZIP archive contains all 50 individual MLP/TCN prediction parquet files. Independently recomputed 50 individual cells, 10 five-seed ensembles, and the 10 frozen ST-PIGNN-versus-MLP/TCN paired MAE deltas from the archived arrays. All 240 individual/ensemble metric checks match within 5e-6 (pair counts exact; maximum absolute difference 3.82e-6), and paired MAE deltas match the saved frozen table within 2.81e-8 on all 14,583 pairs. Raw predictions are retained in the existing archive; they were read in-memory, not extracted or modified. v2l per-seed and comparison CSVs are included without changing frozen families. v2r decoder metrics were recomputed from its 14,583-pair LOSO parquet; all three pooled methods match the saved summary within floating-point precision (maximum absolute difference < 8×10⁻¹⁵ for RMSE/MAE; R² < 6×10⁻¹⁷).

Recomputed v2m paired MAE contrasts across the predeclared ten family from archived five-seed predictions: all 10 deltas match the saved table within 2.81×10⁻⁸ µg/m³, relative improvements within 2.16×10⁻⁷ percentage points, with exact 14,583-pair counts. The archive members were read in-memory. The frozen confidence intervals, sign-flip p-values and Holm corrections remain sourced from the saved primary comparison table; they were not recalculated under a new family.

No discrepancy was repaired silently. If manuscript source PDFs/reviews or source-level data are transferred later, the matrices and bibliographic audit require a versioned supplement. Negative R² and unscored stations are retained.

#### Interpretation limits

MAE/RMSE/R² describe the stated observed-monitor populations only. Repeated station-time rows do not increase independent spatial-site count. Retrospective interpolation, forecasting, road graph structure, citywide execution, explainability, and routing software are distinct evidence types.

## Source exhibit 5: `final_blr_results/ieee_paper_evidence/methodology/TRAINING_AND_EVALUATION.md`

[EVIDENCE: `final_blr_results/ieee_paper_evidence/methodology/TRAINING_AND_EVALUATION.md` | SHA-256 `64c4cd69e3c2cf5e6f03319b4e68e08f00c55b0bf8b04dea4706b8dac26ee935` | snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`]

### Training and evaluation

Keep each round's split, features, model selection, and test population separate. The v2l frozen comparisons use 14,583 matched station-hour pairs over 177 UTC days at each horizon, 11 scored sites. v2m contains all 50 MLP/TCN model-seed-horizon cells and ten frozen primary comparisons; its weather protocol differs from historical ST-PIGNN. Bengaluru's test set has repeated exposure and is exploratory, not independent confirmation.

No experiments were run to create this evidence package. v2m archived individual predictions were used to recompute 50 individual model-seed cells, ten five-seed ensemble metrics and the ten frozen paired ST-PIGNN contrasts; v2r LOSO paired predictions were used to independently recalculate pooled and site metrics. `results/RESULTS_VERIFICATION.md` labels provenance. Statistical comparisons are within their original frozen family; do not create new favorable multiplicity families.
