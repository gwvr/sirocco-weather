from datetime import date
from unittest.mock import patch

from main import build_html, format_date, format_time, wmo_description


def test_format_time():
    assert format_time("2024-06-01T06:23:00") == "06:23"
    assert format_time("2024-06-01T20:05:00") == "20:05"


def test_format_date_today():
    today = date.today()
    with patch("main.datetime") as mock_dt:
        mock_dt.strptime.side_effect = lambda s, f: __import__("datetime").datetime.strptime(s, f)
        mock_dt.now.return_value = __import__("datetime").datetime(today.year, today.month, today.day)
        label, short = format_date(today.strftime("%Y-%m-%d"))
    assert label == "Today"


def test_format_date_tomorrow():
    from datetime import datetime, timedelta
    tomorrow = date.today() + timedelta(days=1)
    today_dt = datetime.today()
    with patch("main.datetime") as mock_dt:
        mock_dt.strptime.side_effect = lambda s, f: __import__("datetime").datetime.strptime(s, f)
        mock_dt.now.return_value = today_dt
        label, short = format_date(tomorrow.strftime("%Y-%m-%d"))
    assert label == "Tomorrow"


def test_format_date_weekday():
    from datetime import datetime, timedelta
    future = date.today() + timedelta(days=3)
    today_dt = datetime.today()
    with patch("main.datetime") as mock_dt:
        mock_dt.strptime.side_effect = lambda s, f: __import__("datetime").datetime.strptime(s, f)
        mock_dt.now.return_value = today_dt
        label, short = format_date(future.strftime("%Y-%m-%d"))
    assert label == future.strftime("%A")
    assert short == future.strftime("%-d %b")


def test_wmo_description_known():
    desc, emoji = wmo_description(0)
    assert desc == "Clear Sky"
    assert emoji == "☀️"


def test_wmo_description_unknown():
    desc, emoji = wmo_description(999)
    assert desc == "Unknown"
    assert emoji == "🌡️"


def _minimal_forecast():
    """Minimal API response shape for a single day."""
    return {
        "daily": {
            "time": ["2024-06-01"],
            "weather_code": [0],
            "temperature_2m_max": [22.5],
            "temperature_2m_min": [12.0],
            "precipitation_sum": [0.0],
            "precipitation_probability_max": [5.0],
            "wind_speed_10m_max": [15.0],
            "uv_index_max": [6.0],
            "sunrise": ["2024-06-01T04:48:00"],
            "sunset": ["2024-06-01T21:12:00"],
        }
    }


def test_build_html_contains_location():
    html = build_html(_minimal_forecast())
    assert "Harpenden, UK" in html


def test_build_html_contains_weather_description():
    html = build_html(_minimal_forecast())
    assert "Clear Sky" in html


def test_build_html_contains_temps():
    html = build_html(_minimal_forecast())
    assert "22°" in html  # 22.5 rounds to 22 (banker's rounding)
    assert "12°" in html


def test_build_html_is_valid_html():
    html = build_html(_minimal_forecast())
    assert html.startswith("<!DOCTYPE html>")
    assert "</html>" in html
