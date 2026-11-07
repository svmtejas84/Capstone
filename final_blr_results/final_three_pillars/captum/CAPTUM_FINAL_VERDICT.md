# Captum final verdict

**Classification: MIXED.** Captum Integrated Gradients ran on compatible saved corrected ST-PIGNN checkpoints from two distinct protocol versions. Numerical wrapper parity and completeness diagnostics are strong for the selected examples. This is post-hoc, baseline-relative attribution on previously examined Bengaluru observations; it is not independent confirmation, causal evidence, or physical validation.

## Coverage

- v2c historical corrected h=1: 5 checkpoints/seeds, 9 deterministic examples, two baselines, 54 records. Maximum prediction-wrapper discrepancy was `4.58e-5 µg/m³`; maximum absolute completeness delta `2.15e-5 µg/m³`; 0 flagged and 0 nonfinite records.
- v2r outer-LOSO corrected h=6: 3 fold checkpoints for held-out stations 5607, 3409385, 6206921; 3 fixed target times per station; two baselines; 18 records. Maximum wrapper discrepancy was `7.63e-6 µg/m³`; maximum absolute completeness delta `7.81e-6 µg/m³`; 0 flagged and 0 nonfinite records.
- The root `IG_RESULTS.csv` combines both versions with an `analysis_version` column. Version-specific result files and full attribution tensors are retained in their subdirectories.

These versions differ in feature schema, horizon, data split and model lineage; their attribution magnitudes must not be compared as a controlled horizon or version effect. v2c and v2r example counts are not spatially representative. Neighbor-station attribution is input attribution through the station graph, not edge attribution. No λ=0 matched checkpoint was recovered for the final corrected protocol; no physics-versus-λ comparison is available. v2j final corrected checkpoints were not saved. The v2n MLP/TCN attribution results remain separate and do not explain ST-PIGNN.

Use the attribution results only to describe how these model outputs change relative to the fixed reference inputs. They do not establish causal influence, atmospheric transport, conservation, true road-level pollution importance, or intervention effects.
