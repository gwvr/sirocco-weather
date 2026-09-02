import os
import tempfile
from unittest.mock import MagicMock, patch

from sirocco.cli import load_config, main


def test_load_config_reads_yaml():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write("location: London\nlat: 51.5\n")
        path = f.name
    try:
        cfg = load_config(path)
        assert cfg["location"] == "London"
        assert cfg["lat"] == 51.5
    finally:
        os.unlink(path)


def test_load_config_empty_file_returns_empty_dict():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        path = f.name
    try:
        cfg = load_config(path)
        assert cfg == {}
    finally:
        os.unlink(path)


class TestUkmoDailyTempOverride:
    def _make_forecast_data(self):
        dates = ["2026-06-15", "2026-06-16", "2026-06-17"]
        return {
            "daily": {
                "time": dates,
                "temperature_2m_max": [20.0, 21.0, 22.0],
                "temperature_2m_min": [10.0, 11.0, 12.0],
                "weather_code": [1, 2, 3],
                "precipitation_sum": [0.0, 1.0, 2.0],
                "precipitation_probability_max": [10, 20, 30],
                "wind_speed_10m_max": [15.0, 16.0, 17.0],
                "uv_index_max": [5, 6, 7],
                "sunrise": ["06:00", "06:01", "06:02"],
                "sunset": ["21:00", "21:01", "21:02"],
            },
            "hourly": {
                "time": [],
                "temperature_2m": [],
                "weather_code": [],
                "apparent_temperature": [],
                "precipitation_probability": [],
                "wind_speed_10m": [],
                "wind_direction_10m": [],
                "wind_gusts_10m": [],
                "relative_humidity_2m": [],
                "uv_index": [],
            },
        }

    @patch("sirocco.cli.build_html", return_value="<html></html>")
    @patch("sirocco.cli.fetch_pollen", return_value={})
    @patch("sirocco.cli.fetch_datahub_daily")
    @patch("sirocco.cli.build_ukmo_hourly")
    @patch("sirocco.cli.fetch_datahub_threehourly_all", return_value=[])
    @patch("sirocco.cli.fetch_datahub_hourly_all", return_value=[])
    @patch("sirocco.cli.fetch_forecast")
    @patch("sirocco.cli.parse_args")
    @patch("sirocco.cli.load_dotenv")
    def test_daily_temps_overridden_from_datahub(
        self,
        _dotenv,
        mock_args,
        mock_forecast,
        _hourly,
        _3h,
        mock_build,
        mock_daily,
        _pollen,
        mock_html,
    ):
        mock_args.return_value = MagicMock(
            config=None,
            location=None,
            lat=51.5,
            lon=-0.1,
            timezone="Europe/London",
            location_name="Test",
            output="/dev/null",
            icons="meteocons",
            theme="dark",
            provider="ukmo",
        )
        data = self._make_forecast_data()
        mock_forecast.return_value = data
        mock_build.return_value = (data["hourly"], [1, 3, 3])
        # nightMinScreenTemperature is 6pm-6am: the low following the day.
        # Day N's displayed min uses the preceding day's nightMin.
        mock_daily.return_value = [
            {
                "time": "2026-06-14T00:00Z",
                "dayMaxScreenTemperature": 19.0,
                "nightMinScreenTemperature": 8.0,
            },
            {
                "time": "2026-06-15T00:00Z",
                "dayMaxScreenTemperature": 24.0,
                "nightMinScreenTemperature": 13.0,
            },
            {
                "time": "2026-06-16T00:00Z",
                "dayMaxScreenTemperature": 25.0,
                "nightMinScreenTemperature": None,
            },
            {
                "time": "2026-06-17T00:00Z",
                "dayMaxScreenTemperature": None,
                "nightMinScreenTemperature": 9.0,
            },
        ]

        with patch.dict(os.environ, {"MET_OFFICE_API_KEY": "test-key"}):
            main()

        # Jun 15 max=24 (from Jun 15), min=8 (nightMin from Jun 14)
        # Jun 16 max=25, min=13 (nightMin from Jun 15)
        # Jun 17 max=22 (no DataHub), min=None from Jun 16 → keeps OM 12.0
        assert data["daily"]["temperature_2m_max"] == [24.0, 25.0, 22.0]
        assert data["daily"]["temperature_2m_min"] == [8.0, 13.0, 12.0]

    @patch("sirocco.cli.build_html", return_value="<html></html>")
    @patch("sirocco.cli.fetch_pollen", return_value={})
    @patch("sirocco.cli.fetch_datahub_daily")
    @patch("sirocco.cli.build_ukmo_hourly")
    @patch("sirocco.cli.fetch_datahub_threehourly_all", return_value=[])
    @patch("sirocco.cli.fetch_datahub_hourly_all", return_value=[])
    @patch("sirocco.cli.fetch_forecast")
    @patch("sirocco.cli.parse_args")
    @patch("sirocco.cli.load_dotenv")
    def test_daily_temps_preserved_on_empty_datahub(
        self,
        _dotenv,
        mock_args,
        mock_forecast,
        _hourly,
        _3h,
        mock_build,
        mock_daily,
        _pollen,
        mock_html,
    ):
        mock_args.return_value = MagicMock(
            config=None,
            location=None,
            lat=51.5,
            lon=-0.1,
            timezone="Europe/London",
            location_name="Test",
            output="/dev/null",
            icons="meteocons",
            theme="dark",
            provider="ukmo",
        )
        data = self._make_forecast_data()
        mock_forecast.return_value = data
        mock_build.return_value = (data["hourly"], [1, 3, 3])
        mock_daily.return_value = []

        with patch.dict(os.environ, {"MET_OFFICE_API_KEY": "test-key"}):
            main()

        assert data["daily"]["temperature_2m_max"] == [20.0, 21.0, 22.0]
        assert data["daily"]["temperature_2m_min"] == [10.0, 11.0, 12.0]
