import pandas as pd

from src.stpignn.data_v2 import weather_utc_half_hours


def test_local_weather_shift_is_exactly_five_and_a_half_hours():
    local = pd.date_range("2022-01-01 00:00", periods=3, freq="h")
    utc = weather_utc_half_hours(local)
    assert list(utc) == list((local - pd.Timedelta(hours=5, minutes=30)).tz_localize("UTC"))
    assert (utc == pd.DatetimeIndex(["2021-12-31 18:30Z", "2021-12-31 19:30Z",
                                    "2021-12-31 20:30Z"])).all()
