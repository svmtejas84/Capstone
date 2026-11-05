# Corrected v2j weather availability at forecast origin

Read-only audit of `scripts/pull_weather.py`, `src/stpignn/data_v2.py`, `scripts/benchmark_v2j.py`, `results/data_v2j_fit.json`, five raw weather Parquets, and existing saved prediction keys. No model fitting or test-score selection. Source HEAD at audit start `b0c401b`.

`scripts/pull_weather.py` obtains six **historical** variables from `https://archive-api.open-meteo.com/v1/archive` with `timezone=Asia/Kolkata`; it stores naive hourly local labels and no forecast issue/release time. `data_v2.py` subtracts 5h30m, producing actual :30 UTC record timestamps, then constructs each UTC hour `c` from records at `c−00:30` and `c+00:30`. `benchmark_v2j.py` sets forecast cutoff `c=target_time−h` and includes the feature row at `c` as the **last** of its 12 input hours. Therefore that last row incorporates the historical weather record timestamped **30 minutes after the forecast origin** whenever both records exist.

Example: target `2025-09-23 00:00:00+00:00` at h=1 has cutoff `2025-09-22 23:00:00+00:00`; its weather feature averages `2025-09-22 22:30:00+00:00` and `2025-09-22 23:30:00+00:00`. The latter is future relative to issue time. The same weather channels are broadcast to the 15 station inputs. This is an availability problem for operational forecasting even though the target PM2.5 observation itself is withheld.

| Horizon h | Existing test pairs | After-cutoff record present | Future temperature in mean | All six future values in mean |
|---:|---:|---:|---:|---:|
| 1 | 14583 | 14563 | 14563 | 14563 |
| 3 | 14583 | 14571 | 14571 | 14571 |
| 6 | 14583 | 14583 | 14583 | 14583 |
| 12 | 14583 | 14583 | 14583 | 14583 |
| 24 | 14583 | 14583 | 14583 | 14583 |

Array-level check at a scored h=1 forecast cutoff `2025-09-23 02:00:00+00:00`: temperature records at `01:30` and `02:30` UTC are 20.7°C and 22.2°C. The stored standardized v2j temperature channel (index 7), decoded with train-fit mean/SD, is 21.45000°C, matching their 21.45°C mean. Thus the later observed value actually enters the model input, beyond a code-path inference.

All five horizons and all original target pairs were retained in this audit; no favorable subset was selected. The source is retrospective archive/reanalysis, not an archived operational weather forecast. The raw files lack issue times or release latencies, so even `c−00:30` cannot be certified operationally available; the `c+00:30` record is definitively after the origin by timestamp. The half-hour rule was deliberately fixed in v2j, and this audit does not alter it or historical predictions.

**Methodological stop condition:** the original v2m assignment says not to permit an unavailable future observation in a forecasting input and to stop for supervisor review if temporal leakage is identified. The supervised backup exception does not waive this safeguard. Do not freeze or train the approved MLP/TCN on the unchanged v2j arrays as an operational forecast benchmark until the supervisor determines a new valid forecast-origin weather protocol. Such a change would require an explicit protocol revision and would invalidate direct input-equivalent comparison with existing v2j neural predictions unless those baselines are rerun under the new information set; no rerun is authorized here.
