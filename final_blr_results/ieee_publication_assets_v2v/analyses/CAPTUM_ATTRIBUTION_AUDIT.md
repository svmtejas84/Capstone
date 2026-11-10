# Captum attribution tensor audit

Raw saved Captum tensors were loaded directly; summary percentages were not used as a substitute. Primary records use the fixed training-mean baseline repeated over the twelve input lags. Feature summaries are mean per-record sums of signed or absolute attribution over the station-node and lag dimensions; temporal summaries sum over feature and station dimensions; feature-by-lag heatmaps sum over station nodes and average over records.

| Variant | Saved checkpoint records | Primary attribution records | Input channels | Maximum absolute completeness delta | Maximum wrapper absolute error |
|---|---:|---:|---:|---:|---:|
| One-hour ST-PIGNN variant | 54 records from 5 checkpoint/seed cells | 45 | 13 | 2.146e−5 µg/m³ | 4.578e−5 µg/m³ |
| Six-hour station-isolated ST-PIGNN variant | 18 records from 3 outer-LOSO checkpoints | 9 | 18 | 7.808e−6 µg/m³ | 7.629e−6 µg/m³ |

## Major feature summaries from raw arrays

The one-hour variant has lagged-PM2.5 mean absolute summed IG 4.91785. The six-hour variant has 5.42877e−6. Six-hour values are 2.64720 for temperature, 2.40596 for surface pressure, 0.98925 for wind speed, 0.99771 for hour sine, 0.57784 for wind-direction sine, and 0.31929 for wind-direction cosine. The raw values are in `source_data/F06_feature_attribution_summary.csv`; the compact comparison is `tables/T06b_major_feature_attributions.csv`.

These numbers are not directly comparable between horizons: one-hour uses a 13-channel earlier corrected model variant, while six-hour outer-LOSO uses 18 channels including missingness and calendar features. Different target/horizon wrappers and checkpoint selection also affect output scale. The near-zero lagged-pollutant attribution in the six-hour model is recorded as an observed attribution property, not explained as a causal mechanism.

The analyses use 64 Gauss–Legendre integration steps, CPU float32, evaluation mode, one thread, and internal batch size 1. The six-hour primary baseline is training-period mean per station/channel, with a zero-environment sensitivity baseline; missingness/calendar channels are preserved for that sensitivity path. These variants do not cover every corrected forecast checkpoint; corrected v2j benchmark checkpoint-specific IG remains unavailable.
