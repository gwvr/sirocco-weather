import tempfile
import os
from datetime import date
from unittest.mock import patch

from sirocco.render import (
    build_html,
    format_date,
    format_time,
    model_label,
    temp_color,
    uv_color,
    weather_icon_html,
    wind_compass,
    wmo_description,
)
from sirocco.cli import load_config


def test_format_time():
    assert format_time("2024-06-01T06:23:00") == "06:23"
    assert format_time("2024-06-01T20:05:00") == "20:05"


def test_format_date_today():
    today = date.today()
    with patch("sirocco.render.datetime") as mock_dt:
        mock_dt.strptime.side_effect = lambda s, f: __import__("datetime").datetime.strptime(s, f)
        mock_dt.now.return_value = __import__("datetime").datetime(today.year, today.month, today.day)
        label, short = format_date(today.strftime("%Y-%m-%d"))
    assert label == "Today"


def test_format_date_tomorrow():
    from datetime import datetime, timedelta
    tomorrow = date.today() + timedelta(days=1)
    today_dt = datetime.today()
    with patch("sirocco.render.datetime") as mock_dt:
        mock_dt.strptime.side_effect = lambda s, f: __import__("datetime").datetime.strptime(s, f)
        mock_dt.now.return_value = today_dt
        label, short = format_date(tomorrow.strftime("%Y-%m-%d"))
    assert label == tomorrow.strftime("%A")


def test_format_date_weekday():
    from datetime import datetime, timedelta
    future = date.today() + timedelta(days=3)
    today_dt = datetime.today()
    with patch("sirocco.render.datetime") as mock_dt:
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


# --- temp_color ---

def test_temp_color_cold():
    assert temp_color(-15) == "#7f8db8"
    assert temp_color(-7) == "#bbc2d9"
    assert temp_color(-2) == "#eaedf3"

def test_temp_color_mild():
    assert temp_color(3) == "#fff1ca"
    assert temp_color(7) == "#ffeaac"
    assert temp_color(12) == "#ffd765"

def test_temp_color_warm():
    assert temp_color(17) == "#ffbd56"
    assert temp_color(22) == "#ffa447"
    assert temp_color(27) == "#ff8a39"
    assert temp_color(32) == "#f36233"
    assert temp_color(36) == "#de2e33"


# --- uv_color ---

def test_uv_color_returns_hex():
    for uv in [0, 3, 6, 8, 11]:
        c = uv_color(uv)
        assert c.startswith("#") and len(c) == 7

def test_uv_color_low_is_greenish():
    c = uv_color(1)
    r = int(c[1:3], 16)
    g = int(c[3:5], 16)
    assert g > r  # green channel dominates for low UV

def test_uv_color_high_is_purplish():
    c = uv_color(12)
    r = int(c[1:3], 16)
    b = int(c[5:7], 16)
    assert r > 0 and b > 0  # violet band has both r and b


# --- wind_compass ---

def test_wind_compass_cardinals():
    assert wind_compass(0) == "N"
    assert wind_compass(90) == "E"
    assert wind_compass(180) == "S"
    assert wind_compass(270) == "W"

def test_wind_compass_intercardinals():
    assert wind_compass(45) == "NE"
    assert wind_compass(135) == "SE"
    assert wind_compass(225) == "SW"
    assert wind_compass(315) == "NW"

def test_wind_compass_wraps():
    assert wind_compass(360) == "N"


# --- model_label ---

def test_model_label_none():
    assert model_label(None) == "ECMWF"

def test_model_label_known():
    # Should return a human-readable label (not the raw model key)
    label = model_label("ecmwf_ifs025")
    assert isinstance(label, str) and len(label) > 0

def test_model_label_unknown():
    assert model_label("some_unknown_model") == "some_unknown_model"


# --- weather_icon_html ---

def test_weather_icon_html_no_meteocons_returns_emoji():
    result = weather_icon_html(0, use_meteocons=False)
    assert "<img" not in result

def test_weather_icon_html_with_meteocons_returns_img():
    result = weather_icon_html(0, use_meteocons=True)
    assert "<img" in result
    assert 'class="weather-icon"' in result

def test_weather_icon_html_unknown_code_falls_back_to_emoji():
    result = weather_icon_html(999, use_meteocons=True)
    assert "<img" not in result

def test_weather_icon_html_night():
    day = weather_icon_html(0, is_day=True, use_meteocons=True)
    night = weather_icon_html(0, is_day=False, use_meteocons=True)
    # Night icon filename differs from day icon filename
    assert day != night


# --- load_config ---

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


# --- build_html with hourly data ---

def _forecast_with_hourly():
    """Two-day forecast with minimal hourly data."""
    hours_day1 = [f"2024-06-01T{h:02d}:00" for h in range(24)]
    hours_day2 = [f"2024-06-02T{h:02d}:00" for h in range(24)]
    times = hours_day1 + hours_day2
    n = len(times)
    return {
        "daily": {
            "time": ["2024-06-01", "2024-06-02"],
            "weather_code": [0, 1],
            "temperature_2m_max": [22.5, 18.0],
            "temperature_2m_min": [12.0, 10.0],
            "precipitation_sum": [0.0, 1.2],
            "precipitation_probability_max": [5.0, 40.0],
            "wind_speed_10m_max": [15.0, 20.0],
            "uv_index_max": [6.0, 4.0],
            "sunrise": ["2024-06-01T04:48:00", "2024-06-02T04:49:00"],
            "sunset": ["2024-06-01T21:12:00", "2024-06-02T21:11:00"],
        },
        "hourly": {
            "time": times,
            "weather_code": [0] * n,
            "temperature_2m": [15.0] * n,
            "precipitation_probability": [10] * n,
            "wind_speed_10m": [12.0] * n,
            "wind_direction_10m": [180.0] * n,
            "is_day": [1] * n,
        },
    }

def test_build_html_with_hourly_renders_wind_compass():
    html = build_html(_forecast_with_hourly())
    assert "S" in html  # wind_compass(180) == "S"

def test_build_html_wind_units_mph():
    html = build_html(_forecast_with_hourly(), wind_units="mph")
    assert "mph" in html

def test_build_html_emoji_icons():
    html = build_html(_forecast_with_hourly(), icons="emoji")
    assert "<img" not in html
