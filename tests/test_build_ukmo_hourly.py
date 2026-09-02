import pytest

from sirocco.api import build_ukmo_hourly


def _hourly_entry(time_utc, **overrides):
    entry = {
        "time": time_utc,
        "screenTemperature": 15.0,
        "feelsLikeTemperature": 13.0,
        "significantWeatherCode": 1,
        "probOfPrecipitation": 10,
        "windSpeed10m": 5.0,
        "windDirectionFrom10m": 180,
        "windGustSpeed10m": 8.0,
        "screenRelativeHumidity": 70,
        "uvIndex": 3,
    }
    entry.update(overrides)
    return entry


def _threehourly_entry(time_utc, **overrides):
    entry = {
        "time": time_utc,
        "maxScreenAirTemp": 18.0,
        "minScreenAirTemp": 12.0,
        "feelsLikeTemp": 14.0,
        "significantWeatherCode": 3,
        "probOfPrecipitation": 20,
        "windSpeed10m": 6.0,
        "windDirectionFrom10m": 270,
        "windGustSpeed10m": 10.0,
        "screenRelativeHumidity": 80,
        "uvIndex": 2,
    }
    entry.update(overrides)
    return entry


def _utc_hourly_day(date="2026-06-15", **overrides):
    return [_hourly_entry(f"{date}T{h:02d}:00Z", **overrides) for h in range(24)]


def _utc_3h_day(date="2026-06-15", **overrides):
    return [_threehourly_entry(f"{date}T{h:02d}:00Z", **overrides) for h in range(0, 24, 3)]


class TestHourlyCoveredDay:
    def test_structure_and_values(self):
        entries = [
            _hourly_entry(f"2026-06-15T{h:02d}:00Z", screenTemperature=10.0 + h) for h in range(24)
        ]
        result, steps = build_ukmo_hourly(["2026-06-15"], entries, [], "UTC")

        assert steps == [1]
        assert len(result["time"]) == 24
        assert result["time"][0] == "2026-06-15T00:00"
        assert result["time"][-1] == "2026-06-15T23:00"
        assert result["temperature_2m"][0] == 10.0
        assert result["temperature_2m"][23] == 33.0
        assert all(code == 0 for code in result["weather_code"])
        assert result["wind_speed_10m"][0] == pytest.approx(18.0)
        assert result["wind_gusts_10m"][0] == pytest.approx(28.8)

    def test_none_screen_temperature(self):
        entries = _utc_hourly_day()
        entries[5]["screenTemperature"] = None
        entries[10]["screenTemperature"] = None
        result, _ = build_ukmo_hourly(["2026-06-15"], entries, [], "UTC")

        assert result["temperature_2m"][5] is None
        assert result["temperature_2m"][10] is None
        assert result["temperature_2m"][0] == 15.0


class TestThreeHourlyDay:
    def test_structure_and_values(self):
        dh_3h = [
            _threehourly_entry(
                f"2026-06-15T{h:02d}:00Z",
                maxScreenAirTemp=20.0,
                minScreenAirTemp=10.0,
            )
            for h in range(0, 24, 3)
        ]
        result, steps = build_ukmo_hourly(["2026-06-15"], [], dh_3h, "UTC")

        assert steps == [3]
        assert len(result["time"]) == 24
        for block in range(8):
            base = block * 3
            assert result["temperature_2m"][base] == 15.0
            assert result["temperature_2m"][base + 1] == 15.0
            assert result["temperature_2m"][base + 2] == 15.0
        assert all(code == 2 for code in result["weather_code"])

    def test_none_max_or_min_temp(self):
        dh_3h = [
            _threehourly_entry("2026-06-15T00:00Z", maxScreenAirTemp=None, minScreenAirTemp=10.0),
            _threehourly_entry("2026-06-15T03:00Z", maxScreenAirTemp=20.0, minScreenAirTemp=None),
            _threehourly_entry("2026-06-15T06:00Z", maxScreenAirTemp=None, minScreenAirTemp=None),
        ] + [_threehourly_entry(f"2026-06-15T{h:02d}:00Z") for h in range(9, 24, 3)]
        result, _ = build_ukmo_hourly(["2026-06-15"], [], dh_3h, "UTC")

        assert result["temperature_2m"][0] is None
        assert result["temperature_2m"][3] is None
        assert result["temperature_2m"][6] is None
        assert result["temperature_2m"][9] == 15.0


class TestEmptyDataHub:
    def test_all_none(self):
        result, steps = build_ukmo_hourly(["2026-06-15"], [], [], "UTC")

        assert steps == [3]
        assert len(result["time"]) == 24
        assert result["time"][0] == "2026-06-15T00:00"
        assert all(v is None for v in result["temperature_2m"])
        assert all(v is None for v in result["weather_code"])
        assert all(v is None for v in result["precipitation_probability"])
        assert all(v is None for v in result["wind_speed_10m"])


class TestTimezoneBoundary:
    def test_bst_maps_midnight_to_previous_utc_day(self):
        entries = []
        for h in range(24):
            utc_h = (h - 1) % 24
            utc_day = 14 if h == 0 else 15
            entries.append(
                _hourly_entry(
                    f"2026-06-{utc_day:02d}T{utc_h:02d}:00Z",
                    screenTemperature=99.0 if h == 0 else 15.0,
                )
            )
        result, _ = build_ukmo_hourly(["2026-06-15"], entries, [], "Europe/London")

        assert result["temperature_2m"][0] == 99.0

    def test_behind_utc_extends_into_next_day(self):
        entries = []
        for h in range(24):
            utc_h = (h + 4) % 24
            utc_day = 15 if utc_h >= 4 else 16
            entries.append(
                _hourly_entry(
                    f"2026-06-{utc_day:02d}T{utc_h:02d}:00Z",
                    screenTemperature=float(h),
                )
            )
        result, steps = build_ukmo_hourly(["2026-06-15"], entries, [], "America/New_York")

        assert steps == [1]
        assert result["temperature_2m"][0] == 0.0
        assert result["temperature_2m"][20] == 20.0

    def test_step_depends_on_timezone(self):
        dh_hourly = _utc_hourly_day("2026-06-15")
        dh_3h = _utc_3h_day("2026-06-16")

        _, steps_utc = build_ukmo_hourly(["2026-06-15"], dh_hourly, dh_3h, "UTC")
        _, steps_edt = build_ukmo_hourly(["2026-06-15"], dh_hourly, dh_3h, "America/New_York")

        assert steps_utc == [1]
        assert steps_edt == [3]


class TestOpenMeteoBackfill:
    def test_missing_hours_filled_from_om(self):
        dh_hourly = [
            _hourly_entry(f"2026-06-15T{h:02d}:00Z", screenTemperature=20.0) for h in range(6, 24)
        ]
        om_hourly = {
            "time": [f"2026-06-15T{h:02d}:00" for h in range(24)],
            "temperature_2m": [5.0 + h for h in range(24)],
            "weather_code": [2] * 24,
            "apparent_temperature": [4.0] * 24,
            "precipitation_probability": [50] * 24,
            "wind_speed_10m": [3.0] * 24,
            "wind_direction_10m": [90] * 24,
            "wind_gusts_10m": [6.0] * 24,
            "relative_humidity_2m": [60] * 24,
            "uv_index": [1] * 24,
        }
        result, _ = build_ukmo_hourly(["2026-06-15"], dh_hourly, [], "UTC", om_hourly=om_hourly)

        assert result["temperature_2m"][0] == 5.0
        assert result["temperature_2m"][5] == 10.0
        assert result["weather_code"][0] == 2
        assert result["temperature_2m"][6] == 20.0

    def test_om_precip_none_falls_back_to_3h(self):
        dh_hourly = [_hourly_entry(f"2026-06-15T{h:02d}:00Z") for h in range(6, 24)]
        dh_3h = _utc_3h_day("2026-06-15", probOfPrecipitation=75)
        om_hourly = {
            "time": [f"2026-06-15T{h:02d}:00" for h in range(6)],
            "temperature_2m": [10.0] * 6,
            "weather_code": [2] * 6,
            "apparent_temperature": [8.0] * 6,
            "precipitation_probability": [None] * 6,
            "wind_speed_10m": [3.0] * 6,
            "wind_direction_10m": [90] * 6,
            "wind_gusts_10m": [5.0] * 6,
            "relative_humidity_2m": [60] * 6,
            "uv_index": [1] * 6,
        }
        result, _ = build_ukmo_hourly(["2026-06-15"], dh_hourly, dh_3h, "UTC", om_hourly=om_hourly)

        assert result["precipitation_probability"][0] == 75
        assert result["precipitation_probability"][3] == 75


class TestMixedDays:
    def test_first_hourly_second_three_hourly(self):
        dh_hourly = _utc_hourly_day("2026-06-15")
        dh_3h = _utc_3h_day("2026-06-16")
        result, steps = build_ukmo_hourly(["2026-06-15", "2026-06-16"], dh_hourly, dh_3h, "UTC")

        assert steps == [1, 3]
        assert len(result["time"]) == 48
        assert result["time"][0] == "2026-06-15T00:00"
        assert result["time"][24] == "2026-06-16T00:00"
        assert result["time"][-1] == "2026-06-16T23:00"
