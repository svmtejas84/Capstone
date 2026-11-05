"""Read-only forecast-origin audit for the corrected v2j weather input."""
from __future__ import annotations

import glob
import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent


def main():
    fit = json.loads((ROOT / "results/data_v2j_fit.json").read_text())
    assert fit["weather_half_hour_rule"] is True
    weather = []
    for name in sorted(glob.glob(str(ROOT / "data/raw/weather/*.parquet"))):
        frame = pd.read_parquet(name)
        if frame.index.tz is not None:
            raise AssertionError("Expected naive Asia/Kolkata raw labels")
        frame.index = (frame.index - pd.Timedelta(hours=5, minutes=30)).tz_localize("UTC")
        weather.append(frame)
    raw = pd.concat(weather).groupby(level=0).mean(numeric_only=True).sort_index()
    assert len(raw) == 37152 and (raw.index.minute == 30).all()
    rows = []
    for h in (1, 3, 6, 12, 24):
        path = ROOT / f"results/benchmark_predictions_h{h}_stpignn_original_seed11_v2j.parquet"
        pred = pd.read_parquet(path)
        target = pd.DatetimeIndex(pd.to_datetime(pred.target_time_utc, utc=True))
        cutoff = target - pd.Timedelta(hours=h)
        before = raw.reindex(cutoff - pd.Timedelta(minutes=30))
        after = raw.reindex(cutoff + pd.Timedelta(minutes=30))
        paired_temp = before.temperature_2m.notna().to_numpy() & after.temperature_2m.notna().to_numpy()
        paired_all = before.notna().all(axis=1).to_numpy() & after.notna().all(axis=1).to_numpy()
        exists = (cutoff + pd.Timedelta(minutes=30)).isin(raw.index)
        rows.append(dict(horizon_hours=h, target_pairs=len(pred), unique_target_hours=target.nunique(),
                         earliest_cutoff_utc=cutoff.min(), latest_cutoff_utc=cutoff.max(),
                         pairs_with_record_after_cutoff=int(exists.sum()),
                         pairs_with_future_temperature_used=int(paired_temp.sum()),
                         pairs_with_all_six_future_weather_values=int(paired_all.sum()),
                         future_temperature_fraction=float(paired_temp.mean()),
                         model_input_last_hour="cutoff", source="Open-Meteo Archive API; scripts/pull_weather.py"))
    table = pd.DataFrame(rows)
    table.to_csv(OUT / "weather_availability_audit.csv", index=False)
    example_cutoff=pd.Timestamp("2025-09-23T02:00:00Z")
    example_before=float(raw.loc[example_cutoff-pd.Timedelta(minutes=30),"temperature_2m"])
    example_after=float(raw.loc[example_cutoff+pd.Timedelta(minutes=30),"temperature_2m"])
    z=np.load(ROOT/"results/data_v2j_arrays.npz")
    model_times=pd.DatetimeIndex(pd.to_datetime(z["times_ns"],utc=True))
    example_index=model_times.get_loc(example_cutoff)
    feature_fit=fit["fit"]
    decoded=float(z["features"][example_index,0,7]*feature_fit["feature_stds"][7]+feature_fit["feature_means"][7])
    assert abs(example_before-example_after)>=1 and abs(decoded-(example_before+example_after)/2)<1e-4
    sample_target=pd.Timestamp("2025-09-23T00:00:00Z")
    sample_cutoff=sample_target-pd.Timedelta(hours=1)
    lines=["# Corrected v2j weather availability at forecast origin", "",
           "Read-only audit of `scripts/pull_weather.py`, `src/stpignn/data_v2.py`, `scripts/benchmark_v2j.py`, `results/data_v2j_fit.json`, five raw weather Parquets, and existing saved prediction keys. No model fitting or test-score selection. Source HEAD at audit start `b0c401b`.", "",
           "`scripts/pull_weather.py` obtains six **historical** variables from `https://archive-api.open-meteo.com/v1/archive` with `timezone=Asia/Kolkata`; it stores naive hourly local labels and no forecast issue/release time. `data_v2.py` subtracts 5h30m, producing actual :30 UTC record timestamps, then constructs each UTC hour `c` from records at `c−00:30` and `c+00:30`. `benchmark_v2j.py` sets forecast cutoff `c=target_time−h` and includes the feature row at `c` as the **last** of its 12 input hours. Therefore that last row incorporates the historical weather record timestamped **30 minutes after the forecast origin** whenever both records exist.", "",
           f"Example: target `{sample_target}` at h=1 has cutoff `{sample_cutoff}`; its weather feature averages `{sample_cutoff-pd.Timedelta(minutes=30)}` and `{sample_cutoff+pd.Timedelta(minutes=30)}`. The latter is future relative to issue time. The same weather channels are broadcast to the 15 station inputs. This is an availability problem for operational forecasting even though the target PM2.5 observation itself is withheld.", "",
           "| Horizon h | Existing test pairs | After-cutoff record present | Future temperature in mean | All six future values in mean |", "|---:|---:|---:|---:|---:|"]
    for row in rows:
        lines.append(f"| {row['horizon_hours']} | {row['target_pairs']} | {row['pairs_with_record_after_cutoff']} | {row['pairs_with_future_temperature_used']} | {row['pairs_with_all_six_future_weather_values']} |")
    lines += ["", f"Array-level check at a scored h=1 forecast cutoff `{example_cutoff}`: temperature records at `01:30` and `02:30` UTC are {example_before:.1f}°C and {example_after:.1f}°C. The stored standardized v2j temperature channel (index 7), decoded with train-fit mean/SD, is {decoded:.5f}°C, matching their {((example_before+example_after)/2):.2f}°C mean. Thus the later observed value actually enters the model input, beyond a code-path inference.", "",
              "All five horizons and all original target pairs were retained in this audit; no favorable subset was selected. The source is retrospective archive/reanalysis, not an archived operational weather forecast. The raw files lack issue times or release latencies, so even `c−00:30` cannot be certified operationally available; the `c+00:30` record is definitively after the origin by timestamp. The half-hour rule was deliberately fixed in v2j, and this audit does not alter it or historical predictions.", "",
              "**Methodological stop condition:** the original v2m assignment says not to permit an unavailable future observation in a forecasting input and to stop for supervisor review if temporal leakage is identified. The supervised backup exception does not waive this safeguard. Do not freeze or train the approved MLP/TCN on the unchanged v2j arrays as an operational forecast benchmark until the supervisor determines a new valid forecast-origin weather protocol. Such a change would require an explicit protocol revision and would invalidate direct input-equivalent comparison with existing v2j neural predictions unless those baselines are rerun under the new information set; no rerun is authorized here.", ""]
    (OUT / "weather_availability_audit.md").write_text("\n".join(lines))
    print(table.to_string(index=False))


if __name__ == "__main__":
    main()
