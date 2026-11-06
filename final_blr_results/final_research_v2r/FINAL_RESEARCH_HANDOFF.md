# Bengaluru v2r final research handoff

## Research status

v2r is complete with a negative spatial-decoder result and an RGDR feasibility stop. All evidence is exploratory: the Bengaluru dataset and test period have been exposed in previous rounds. No paper, other-city training, new architecture search or test-tuned selection was performed. Historical v2j–v2q results were preserved.

## Citywide forecasting

- **Source forecasts:** A corrected station-level GINE–GRU was fit in 15 outer station-isolated folds plus 15 time-block crossfit folds (30 total, seed 11). It uses the existing corrected architecture, 18 feature channels and 12 historical hours for h=6. Forecast input windows end at target−6h; target-hour features are excluded. No held-out station pollutant history, target, preprocessing or anchor data was used in its own fold. Per-fold models, manifests and forecast outputs are under `citywide/station_forecasts/`.
- **Decoder:** The existing frozen 1,249-parameter v2q compact decoder was trained from cross-fitted forecasts; validation selected epoch 3. Genuine LOSO validation scored 11 stations / 14,583 pairs; four stations had no eligible test observations. Pooled MAE: train-only spatial mean 20.634, forecast-IDW 20.154, decoder 27.360 µg/m³. Decoder-minus-IDW equal-site MAE difference was +5.101 (station-bootstrap 95% CI +1.815,+8.302). Decoder lost to each control at 9/11 scored sites. It does not improve the controls.
- **Full-city execution:** Completed for 154,902 road nodes at three frozen h=6 targets: 2025-10-08 13:00, 2026-02-10 07:00 and 2026-03-28 23:00 UTC. Road outputs are a combination of corrected GINE–GRU station forecasts and compact neural spatial decoder; IDW is retained as a comparator. They are **experimental neural-assisted estimates**, not observations or validated road-level predictions. All node outputs are finite and aligned; deterministic repeat inference matched exactly. The run took 56.44 seconds including decoder fit and maps; complete-node expansion was 1.12–1.30 seconds per timestamp, peak RSS 1.49 GB, GPU VRAM 0 for spatial expansion. Source GINE–GRU folds used up to 1.831 GB GPU memory per model.
- **Support:** Median nearest-station distance 3.315 km; 19.45% of road nodes exceed 5 km; 60.58% are outside the 15-station convex hull. These are support diagnostics, not calibrated prediction intervals. No independent road-side measurement exists, and held-out decoder results are unfavorable. Do not claim accurate citywide concentration or exposure mapping.

## RGDR

- `RGDR_BINARY_V1` is preserved unchanged, with prior 2.3% train edge-retention finding.
- `RGDR_CONTINUOUS_V2` is implemented as `q_i=exp(-age/4h)` for eligible observed pollutant values aged 0–24 hours; edge weight is `q_src q_dst`. It preserves the original directional mask, length factor, normalization, λ and warm-up. Age uses past observed values only.
- Existing physics tests plus continuous RGDR tests passed 13/13. The train-only h=6 diagnostic retained 2.48% directional edge mass and had 74.75% zero-penalty hours, failing frozen thresholds of ≥10% and <50%. The pilot stopped before model fitting. RGDR predictive effect is **NOT EVALUATED**, not zero. No claim of forecasting gain or physical conservation is supported. Prior-art review concluded novelty is not established.

## Claim assessment

| Claim | Status | Permitted conclusion |
|---|---|---|
| Issue-time-safe station h=6 forecasts can be generated | SUPPORTED as engineering | Corrected forecast code produced finite, cutoff-checked station predictions; Bengaluru results remain exploratory. |
| Learned decoder improves spatial generalization over controls | UNSUPPORTED | It performed worse than forecast-IDW and training-only mean on the 11 scored sites. |
| Full road network can be populated computationally | SUPPORTED as computational execution | Three 154,902-node arrays were generated and reproduced; this is not accuracy evidence. |
| Road-node concentration accuracy | NOT EVALUATED | No independent roadside targets exist. |
| RGDR implementation and mathematical checks | SUPPORTED as software correctness | Formula and tests pass; optimization feasibility fails. |
| RGDR predictive advantage, novelty or physical validity | NOT EVALUATED / NOT ESTABLISHED | No matched pilot ran; prior art is close and no conservation law is implemented. |
| Citywide exposure/routing benefit | NOT EVALUATED | No validated road concentration or route comparison is available. |

Earlier evidence remains binding context: v2m completed all 50 MLP/TCN cells; no ST-PIGNN-versus-TCN contrast survived reported Holm correction; v2l/v2p did not demonstrate physics specificity or mass conservation; previous LOSO favored weather/static ridge over ST-PIGNN (22.314 vs 20.624 µg/m³ on 11 sites); original notebook full-road input construction was historically target-leaking. The new v2r full-city demonstration does not overturn these limitations.

## Required next evidence

Further RGDR work requires a revised frozen reliability rule that passes training exposure without test-based tuning, then a matched controlled pilot and an independent dataset. A publishable citywide accuracy claim requires independent roadside PM2.5 measurements, calibrated uncertainty and spatial validation at genuinely independent locations. Any new large training campaign requires supervisor review. No further Bengaluru engineering is authorized after v2r without that review.

## Recovery and artifacts

See `EXPERIMENT_PROTOCOL.md`, `citywide/{methodology/CITYWIDE_METHODOLOGY.md,CITYWIDE_FINAL_VERDICT.md}`, `citywide/spatial_validation/SPATIAL_VALIDATION_VERDICT.md`, `rgdr/RGDR_FINAL_VERDICT.md`, `reproducibility/REPRODUCIBILITY.md`, `reproducibility/artifact_manifest.json`, and the v2r archive verification files. `results/codex_log/RESUME.md` records exact Git/push status and recovery commands.

Separate supplemental bundles are `archive/citywide_v2r.zip` and `archive/rgdr_v2r.zip`; their byte sizes, SHA-256 values, CRC results, and per-member hashes are recorded in `archive/archive_verification.json` and the two `archive/*_members.csv` files. The archive builder/verifier are `reproducibility/build_verify_archives.py` and `reproducibility/verify_archives.py`. Large data and checkpoint artifacts remain outside Git and are included in the citywide bundle; their source inputs are identified by hash in `reproducibility/artifact_manifest.json`.
