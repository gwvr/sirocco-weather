import argparse
import httpx
import yaml
from datetime import datetime
from pathlib import Path

OUTPUT_FILE = "forecast.html"

# Defaults: Harpenden, UK
DEFAULT_LATITUDE = 51.81684
DEFAULT_LONGITUDE = -0.35706
DEFAULT_TIMEZONE = "Europe/London"
DEFAULT_LOCATION_NAME = "Harpenden, UK"

API_URL = "https://api.open-meteo.com/v1/forecast"

DAILY_VARIABLES = [
    "weather_code",
    "temperature_2m_max",
    "temperature_2m_min",
    "precipitation_sum",
    "precipitation_probability_max",
    "wind_speed_10m_max",
    "uv_index_max",
    "sunrise",
    "sunset",
]

HOURLY_VARIABLES = [
    "weather_code",
    "temperature_2m",
    "apparent_temperature",
    "precipitation_probability",
    "wind_speed_10m",
    "wind_direction_10m",
    "wind_gusts_10m",
    "relative_humidity_2m",
    "uv_index",
]

METEOCON_BASE = "https://bmcdn.nl/assets/weather-icons/v3.0/fill/svg"

# Maps WMO code -> (day icon name, night icon name) for Meteocons
METEOCON_ICONS = {
    0:  ("clear-day",                       "clear-night"),
    1:  ("partly-cloudy-day",               "partly-cloudy-night"),
    2:  ("partly-cloudy-day",               "partly-cloudy-night"),
    3:  ("overcast-day",                    "overcast-night"),
    45: ("fog-day",                         "fog-night"),
    48: ("fog-day",                         "fog-night"),
    51: ("partly-cloudy-day-drizzle",       "partly-cloudy-night-drizzle"),
    53: ("drizzle",                         "drizzle"),
    55: ("overcast-drizzle",                "overcast-drizzle"),
    56: ("partly-cloudy-day-sleet",         "partly-cloudy-night-sleet"),
    57: ("overcast-day-sleet",              "overcast-night-sleet"),
    61: ("partly-cloudy-day-rain",          "partly-cloudy-night-rain"),
    63: ("rain",                            "rain"),
    65: ("overcast-rain",                   "overcast-rain"),
    66: ("partly-cloudy-day-sleet",         "partly-cloudy-night-sleet"),
    67: ("overcast-day-sleet",              "overcast-night-sleet"),
    71: ("partly-cloudy-day-snow",          "partly-cloudy-night-snow"),
    73: ("snow",                            "snow"),
    75: ("overcast-snow",                   "overcast-snow"),
    77: ("partly-cloudy-day-snow",          "partly-cloudy-night-snow"),
    80: ("partly-cloudy-day-rain",          "partly-cloudy-night-rain"),
    81: ("partly-cloudy-day-rain",          "partly-cloudy-night-rain"),
    82: ("overcast-rain",                   "overcast-rain"),
    85: ("partly-cloudy-day-snow",          "partly-cloudy-night-snow"),
    86: ("overcast-day-snow",               "overcast-night-snow"),
    95: ("thunderstorms-day",               "thunderstorms-night"),
    96: ("thunderstorms-day-rain",          "thunderstorms-night-rain"),
    99: ("thunderstorms-day-overcast-rain", "thunderstorms-night-overcast-rain"),
}

WMO_CODES = {
    0: ("Clear Sky", "☀️"),
    1: ("Mainly Clear", "🌤️"),
    2: ("Partly Cloudy", "⛅"),
    3: ("Overcast", "☁️"),
    45: ("Fog", "🌫️"),
    48: ("Rime Fog", "🌫️"),
    51: ("Light Drizzle", "🌦️"),
    53: ("Moderate Drizzle", "🌦️"),
    55: ("Dense Drizzle", "🌧️"),
    56: ("Freezing Drizzle", "🌧️"),
    57: ("Heavy Freezing Drizzle", "🌧️"),
    61: ("Slight Rain", "🌧️"),
    63: ("Moderate Rain", "🌧️"),
    65: ("Heavy Rain", "🌧️"),
    66: ("Freezing Rain", "🌨️"),
    67: ("Heavy Freezing Rain", "🌨️"),
    71: ("Slight Snow", "❄️"),
    73: ("Moderate Snow", "❄️"),
    75: ("Heavy Snow", "❄️"),
    77: ("Snow Grains", "🌨️"),
    80: ("Slight Showers", "🌦️"),
    81: ("Moderate Showers", "🌧️"),
    82: ("Violent Showers", "⛈️"),
    85: ("Slight Snow Showers", "🌨️"),
    86: ("Heavy Snow Showers", "🌨️"),
    95: ("Thunderstorm", "⛈️"),
    96: ("Thunderstorm w/ Hail", "⛈️"),
    99: ("Thunderstorm w/ Heavy Hail", "⛈️"),
}


def fetch_precip_probability(latitude: float, longitude: float, timezone: str, model: str) -> list:
    """Fetch hourly precipitation_probability from a secondary model."""
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "timezone": timezone,
        "forecast_days": 7,
        "hourly": "precipitation_probability",
        "models": model,
    }
    response = httpx.get(API_URL, params=params, timeout=10)
    response.raise_for_status()
    return response.json()["hourly"]["precipitation_probability"]


def fetch_forecast(latitude: float, longitude: float, timezone: str, model: str | None = None, wind_units: str = "kmh") -> dict:
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "timezone": timezone,
        "forecast_days": 7,
        "daily": ",".join(DAILY_VARIABLES),
        "hourly": ",".join(HOURLY_VARIABLES),
        "wind_speed_unit": wind_units,
    }
    if model:
        params["models"] = model
    response = httpx.get(API_URL, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def format_time(iso_str: str) -> str:
    """Format ISO8601 datetime string to HH:MM."""
    dt = datetime.fromisoformat(iso_str)
    return dt.strftime("%H:%M")


def format_date(date_str: str) -> tuple[str, str]:
    """Return (weekday, short date) from a YYYY-MM-DD string."""
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    today = datetime.now().date()
    if dt.date() == today:
        label = "Today"
    elif (dt.date() - today).days == 1:
        label = "Tomorrow"
    else:
        label = dt.strftime("%A")
    return label, dt.strftime("%-d %b")


def wmo_description(code: int) -> tuple[str, str]:
    return WMO_CODES.get(code, ("Unknown", "🌡️"))


MODEL_LABELS = {
    "ukmo_seamless":           "UK Met Office",
    "ukmo_global":             "UK Met Office",
    "ukmo_uk_deterministic":   "UK Met Office",
    "ecmwf_ifs025":            "ECMWF",
    "ecmwf_ifs04":             "ECMWF",
    "ecmwf_aifs025":           "ECMWF",
}

def model_label(model: str | None) -> str:
    if model is None:
        return "ECMWF"
    return MODEL_LABELS.get(model, model)


def temp_color(t: float) -> str:
    if t < -10: return "#7f8db8"
    if t < -5:  return "#bbc2d9"
    if t < 0:   return "#eaedf3"
    if t < 5:   return "#fff1ca"
    if t < 10:  return "#ffeaac"
    if t < 15:  return "#ffd765"
    if t < 20:  return "#ffbd56"
    if t < 25:  return "#ffa447"
    if t < 30:  return "#ff8a39"
    if t < 35:  return "#f36233"
    return "#de2e33"


def uv_color(uv: float) -> str:
    """WHO UV index band colours, blended 50% with white to mute them."""
    if uv < 3:  base = (0x29, 0x95, 0x01)  # green
    elif uv < 6:  base = (0xF7, 0xE4, 0x00)  # yellow
    elif uv < 8:  base = (0xF1, 0x8B, 0x00)  # orange
    elif uv < 11: base = (0xE5, 0x32, 0x10)  # red
    else:         base = (0xB5, 0x67, 0xA4)  # violet
    r, g, b = ((c + 255 * 3) // 4 for c in base)
    return f"#{r:02x}{g:02x}{b:02x}"


def weather_icon_html(wmo_code: int, is_day: bool = True, size: int = 32, use_meteocons: bool = True) -> str:
    """Return an <img> tag for Meteocons, or emoji if use_meteocons is False / code is unknown."""
    _, emoji = wmo_description(wmo_code)
    if not use_meteocons:
        return emoji
    icons = METEOCON_ICONS.get(wmo_code)
    if not icons:
        return emoji
    name = icons[0] if is_day else icons[1]
    return f'<img class="weather-icon" src="{METEOCON_BASE}/{name}.svg" alt="{emoji}" width="{size}" height="{size}">'


def wind_compass(degrees: float) -> str:
    dirs = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
            "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    return dirs[round(degrees / 22.5) % 16]


def build_html(data: dict, location_name: str = DEFAULT_LOCATION_NAME, model: str | None = None, wind_units: str = "kmh", lat: float = DEFAULT_LATITUDE, lon: float = DEFAULT_LONGITUDE, precip_model: str | None = None, icons: str = "meteocons") -> str:
    daily = data["daily"]
    hourly = data.get("hourly", {})
    dates = daily["time"]
    n_days = len(dates)
    generated_at = datetime.now().strftime("%d %b %Y at %H:%M")

    # --- Summary panel (today, remaining hours only) ---
    current_hour = datetime.now().hour
    today_desc, _ = wmo_description(daily["weather_code"][0])
    today_sunrise = format_time(daily["sunrise"][0])
    today_sunset = format_time(daily["sunset"][0])
    use_meteocons = (icons == "meteocons")
    now_hm = datetime.now().strftime("%H:%M")
    is_day_now = daily["sunrise"][0][11:16] <= now_hm <= daily["sunset"][0][11:16]
    today_icon = weather_icon_html(daily["weather_code"][0], is_day=is_day_now, size=48, use_meteocons=use_meteocons)

    if hourly.get("temperature_2m"):
        remaining = range(current_hour, 24)
        h_temps = [hourly["temperature_2m"][j] for j in remaining if hourly["temperature_2m"][j] is not None]
        h_uv    = [hourly["uv_index"][j] for j in remaining if hourly.get("uv_index") and hourly["uv_index"][j] is not None]
        today_max = max(h_temps) if h_temps else daily["temperature_2m_max"][0]
        today_min = min(h_temps) if h_temps else daily["temperature_2m_min"][0]
        today_uv  = max(h_uv) if h_uv else daily["uv_index_max"][0]
    else:
        today_max = daily["temperature_2m_max"][0]
        today_min = daily["temperature_2m_min"][0]
        today_uv  = daily["uv_index_max"][0]

    summary_html = f"""
    <div class="summary">
        <div class="summary-main">
            <div class="summary-temp">{today_max:.0f}°<span class="summary-min">/{today_min:.0f}°C</span></div>
            <div class="summary-desc">{today_icon} {today_desc}</div>
        </div>
        <div class="summary-details">
            <span>🌅 {today_sunrise}</span>
            <span>🌇 {today_sunset}</span>
            <span>🕶️ UV {today_uv:.0f}</span>
        </div>
    </div>"""

    # --- Daily strip ---
    day_cards = ""
    for i in range(n_days):
        weekday, short_date = format_date(dates[i])
        day_icon = weather_icon_html(daily["weather_code"][i], is_day=True, size=36, use_meteocons=use_meteocons)
        tmax = daily["temperature_2m_max"][i]
        tmin = daily["temperature_2m_min"][i]
        active = "active" if i == 0 else ""
        day_cards += f"""
        <div class="day-card {active}" onclick="selectDay({i})">
            <div class="day-name">{weekday}</div>
            <div class="day-date">{short_date}</div>
            <div class="day-emoji">{day_icon}</div>
            <div class="day-temps"><span class="tmax">{f"{tmax:.0f}°" if tmax is not None else "—"}</span><span class="tmin">{f"{tmin:.0f}°" if tmin is not None else "—"}</span></div>
        </div>"""

    # --- Hourly panels (one per day, pre-rendered) ---
    hourly_panels = ""
    for day_i in range(n_days):
        start = day_i * 24
        end = start + 24
        h_times = hourly.get("time", [])[start:end]

        active = "active" if day_i == 0 else ""

        if not h_times:
            hourly_panels += f'<div class="hourly-panel {active}" id="day-{day_i}"></div>'
            continue

        sunrise_hm = daily["sunrise"][day_i][11:16]
        sunset_hm  = daily["sunset"][day_i][11:16]

        h_codes   = hourly.get("weather_code", [])[start:end]
        h_temps   = hourly.get("temperature_2m", [])[start:end]
        h_feels   = hourly.get("apparent_temperature", [])[start:end]
        h_precip  = hourly.get("precipitation_probability", [])[start:end]
        h_wind    = hourly.get("wind_speed_10m", [])[start:end]
        h_wdir    = hourly.get("wind_direction_10m", [])[start:end]
        h_gusts   = hourly.get("wind_gusts_10m", [])[start:end]
        h_humidity = hourly.get("relative_humidity_2m", [])[start:end]
        h_uv      = hourly.get("uv_index", [])[start:end]

        time_cells    = "".join(f"<th>{t[11:16]}</th>" for t in h_times)
        def _cell(v, fmt_str, suffix=""): return f"<td>{format(v, fmt_str)}{suffix}</td>" if v is not None else "<td>—</td>"

        symbol_cells   = "".join(
            f'<td>{weather_icon_html(c, is_day=sunrise_hm <= t[11:16] <= sunset_hm, size=24, use_meteocons=use_meteocons)}</td>'
            if c is not None else "<td>—</td>"
            for c, t in zip(h_codes, h_times)
        )
        precip_cells   = "".join(_cell(p, ".0f", "%") for p in h_precip)
        temp_cells     = "".join(f'<td style="background:{temp_color(t)};color:#222">{t:.0f}°</td>' if t is not None else "<td>—</td>" for t in h_temps)
        feels_cells    = "".join(f'<td style="background:{temp_color(t)};color:#222">{t:.0f}°</td>' if t is not None else "<td>—</td>" for t in h_feels)
        wdir_cells     = "".join(
            f'<td><div class="wind-arrow" style="transform:rotate({(d + 180) % 360:.0f}deg)">↑</div>'
            f'<div class="wind-cmp">{wind_compass(d)}</div></td>'
            if d is not None else "<td>—</td>"
            for d in h_wdir
        )
        wind_cells     = "".join(_cell(w, ".0f") for w in h_wind)
        gust_cells     = "".join(_cell(g, ".0f") for g in h_gusts)
        humidity_cells = "".join(_cell(h, ".0f", "%") for h in h_humidity)
        uv_cells       = "".join(f'<td style="background:{uv_color(u)};color:#222">{u:.0f}</td>' if u is not None else "<td>—</td>" for u in h_uv)

        hourly_panels += f"""
        <div class="hourly-panel {active}" id="day-{day_i}">
            <div class="hourly-scroll">
                <table class="hourly">
                    <thead><tr><th class="row-label"></th>{time_cells}</tr></thead>
                    <tbody>
                        <tr><td class="row-label">Symbol</td>{symbol_cells}</tr>
                        <tr><td class="row-label">Precip.</td>{precip_cells}</tr>
                        <tr><td class="row-label">Temp °C</td>{temp_cells}</tr>
                        <tr><td class="row-label">Feels like °C</td>{feels_cells}</tr>
                        <tr><td class="row-label">Wind direction</td>{wdir_cells}</tr>
                        <tr><td class="row-label">Wind speed ({wind_units})</td>{wind_cells}</tr>
                        <tr><td class="row-label">Wind gust ({wind_units})</td>{gust_cells}</tr>
                        <tr><td class="row-label">Humidity</td>{humidity_cells}</tr>
                        <tr><td class="row-label">UV</td>{uv_cells}</tr>
                    </tbody>
                </table>
            </div>
        </div>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>7-Day Forecast — {location_name}</title>
    <style>
        *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

        :root {{
            --bg:           #d8e2ed;
            --surface:      #ffffff;
            --surface-2:    #f5f7fa;
            --text:         #222222;
            --text-muted:   #999999;
            --text-mid:     #555555;
            --border:       #e8e8e8;
            --border-strong:#dddddd;
            --accent:       #1a6faf;
            --header:       #1a3c5e;
            --link:         #1a6faf;
        }}

        @media (prefers-color-scheme: dark) {{ :root {{ --bg:#0f1923; --surface:#1a2535; --surface-2:#1e2d40; --text:#e0e0e0; --text-muted:#7a8fa6; --text-mid:#a0b4c8; --border:#2a3a4f; --border-strong:#3a4f6a; --accent:#2a86d4; --header:#90c4e8; --link:#6ab0e0; }} }}
        [data-theme="dark"]  {{ --bg:#0f1923; --surface:#1a2535; --surface-2:#1e2d40; --text:#e0e0e0; --text-muted:#7a8fa6; --text-mid:#a0b4c8; --border:#2a3a4f; --border-strong:#3a4f6a; --accent:#2a86d4; --header:#90c4e8; --link:#6ab0e0; }}
        [data-theme="light"] {{ --bg:#b8b8b8; --surface:#ffffff; --surface-2:#f5f7fa; --text:#222222; --text-muted:#999999; --text-mid:#555555; --border:#e8e8e8; --border-strong:#dddddd; --accent:#1a6faf; --header:#1a3c5e; --link:#1a6faf; }}

        body {{
            font-family: Arial, Helvetica, sans-serif;
            background: var(--bg);
            color: var(--text);
            padding: 1.5rem 1rem;
            min-height: 100vh;
            max-width: 1200px;
            margin: 0 auto;
            transition: background 0.2s, color 0.2s;
        }}

        header {{ margin-bottom: 1rem; display: flex; justify-content: space-between; align-items: flex-start; }}
        header h1 {{ font-size: 1.4rem; font-weight: 700; color: var(--header); }}
        .generated {{ font-size: 0.75rem; color: var(--text-mid); margin-top: 0.2rem; }}
        .generated a {{ color: var(--link); text-decoration: none; }}
        .generated a:hover {{ text-decoration: underline; }}

        .theme-toggle {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 0.3rem 0.6rem;
            font-size: 0.8rem;
            color: var(--text-mid);
            cursor: pointer;
            white-space: nowrap;
            flex-shrink: 0;
        }}
        .theme-toggle:hover {{ border-color: var(--accent); color: var(--accent); }}

        /* Summary */
        .summary {{
            background: var(--surface);
            border-radius: 8px;
            padding: 1rem 1.5rem;
            margin-bottom: 0.75rem;
            display: flex;
            align-items: center;
            gap: 2rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        }}
        .summary-temp {{ font-size: 2.2rem; font-weight: 700; color: var(--header); }}
        .summary-min {{ font-size: 1.3rem; color: var(--text-muted); font-weight: 400; }}
        .summary-desc {{ font-size: 0.95rem; color: var(--text-mid); margin-top: 0.2rem; }}
        .summary-details {{ display: flex; gap: 1.5rem; font-size: 0.9rem; color: var(--text-mid); }}

        /* Daily strip */
        .daily-strip {{
            display: flex;
            background: var(--surface);
            border-radius: 8px;
            overflow: hidden;
            margin-bottom: 0.75rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        }}
        .day-card {{
            flex: 1;
            padding: 0.7rem 0.4rem;
            text-align: center;
            cursor: pointer;
            border-right: 1px solid var(--border);
            transition: background 0.1s;
            user-select: none;
        }}
        .day-card:last-child {{ border-right: none; }}
        .day-card:hover {{ background: var(--surface-2); }}
        .day-card.active {{ background: var(--accent); color: white; }}
        .day-card.active .day-date {{ color: rgba(255,255,255,0.75); }}
        .day-card.active .tmin {{ color: rgba(255,255,255,0.7); }}
        .day-name {{ font-weight: 700; font-size: 0.85rem; }}
        .day-date {{ font-size: 0.72rem; color: var(--text-muted); margin-bottom: 0.3rem; }}
        .day-emoji {{ font-size: 1.4rem; line-height: 1; margin: 0.25rem 0; }}
        .tmax {{ font-weight: 700; font-size: 0.85rem; }}
        .tmin {{ color: var(--text-muted); font-size: 0.85rem; margin-left: 0.2rem; }}

        /* Hourly panels */
        .hourly-panel {{ display: none; background: var(--surface); border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }}
        .hourly-panel.active {{ display: block; }}
        .hourly-scroll {{ overflow-x: auto; }}

        table.hourly {{ border-collapse: collapse; white-space: nowrap; }}
        table.hourly th,
        table.hourly td {{
            border: 1px solid var(--border);
            padding: 0.3rem 0.45rem;
            text-align: center;
            font-size: 0.78rem;
        }}
        table.hourly thead th {{
            background: var(--surface-2);
            color: var(--text-muted);
            font-weight: normal;
        }}
        td.row-label, th.row-label {{
            background: var(--surface-2);
            color: var(--text-mid);
            font-weight: 600;
            text-align: right;
            padding-right: 0.75rem;
            border-right: 2px solid var(--border-strong);
            position: sticky;
            left: 0;
            z-index: 1;
        }}
        th.row-label {{ z-index: 2; }}

        .weather-icon {{ display: block; margin: 0 auto; filter: drop-shadow(0 1px 4px rgba(0,0,0,0.4)); }}
        .summary-desc .weather-icon {{ display: inline; vertical-align: middle; }}

        .wind-arrow {{ font-size: 1rem; display: inline-block; line-height: 1; }}
        .wind-cmp {{ font-size: 0.65rem; color: var(--text-muted); margin-top: 0.1rem; }}

        a.map-link {{ text-decoration: none; color: inherit; }}
        a.map-link:hover {{ opacity: 0.7; }}

        footer {{
            text-align: center;
            margin-top: 1.5rem;
            font-size: 0.75rem;
            color: var(--text-muted);
        }}
    </style>
</head>
<body>
    <header>
        <div>
            <h1><a class="map-link" href="https://www.openstreetmap.org/?mlat={lat}&mlon={lon}&zoom=12" target="_blank">📍 {location_name}</a></h1>
            <p class="generated">Generated {generated_at} &mdash; Data from {model_label(model)}{f" &amp; {model_label(precip_model)} (precip.)" if precip_model else ""} via <a href="https://open-meteo.com/" target="_blank">Open-Meteo</a></p>
        </div>
        <button class="theme-toggle" onclick="toggleTheme()" id="theme-btn">Dark mode</button>
    </header>

    {summary_html}

    <div class="daily-strip">
        {day_cards}
    </div>

    {hourly_panels}

    <script>
    function selectDay(index) {{
        document.querySelectorAll('.day-card').forEach((c, i) => c.classList.toggle('active', i === index));
        document.querySelectorAll('.hourly-panel').forEach((p, i) => p.classList.toggle('active', i === index));
    }}

    (function() {{
        const saved = localStorage.getItem('theme');
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        const dark = saved ? saved === 'dark' : prefersDark;
        applyTheme(dark);
    }})();

    function applyTheme(dark) {{
        document.documentElement.setAttribute('data-theme', dark ? 'dark' : 'light');
        document.getElementById('theme-btn').textContent = dark ? 'Light mode' : 'Dark mode';
    }}

    function toggleTheme() {{
        const dark = document.documentElement.getAttribute('data-theme') !== 'dark';
        localStorage.setItem('theme', dark ? 'dark' : 'light');
        applyTheme(dark);
    }}
    </script>
</body>
</html>"""


def load_config(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f) or {}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch and display a 7-day weather forecast.")
    parser.add_argument("--config", metavar="FILE", help="YAML config file with named locations")
    parser.add_argument("--location", metavar="KEY", help="Location key from config file")
    parser.add_argument("--lat", type=float, metavar="LATITUDE")
    parser.add_argument("--lon", type=float, metavar="LONGITUDE")
    parser.add_argument("--timezone")
    parser.add_argument("--name", metavar="NAME", dest="location_name")
    parser.add_argument("--output", default=OUTPUT_FILE, metavar="FILE")
    parser.add_argument("--icons", default="meteocons", choices=["meteocons", "emoji"],
                        help="Icon set to use (default: meteocons)")
    return parser.parse_args()


def main():
    args = parse_args()

    config = load_config(args.config) if args.config else {}
    locations = config.get("locations", {})

    if locations:
        key = args.location or config.get("default") or next(iter(locations))
        if key not in locations:
            raise SystemExit(f"Unknown location '{key}'. Available: {', '.join(locations)}")
        loc = locations[key]
    else:
        loc = {}

    lat = args.lat or loc.get("lat", DEFAULT_LATITUDE)
    lon = args.lon or loc.get("lon", DEFAULT_LONGITUDE)
    timezone = args.timezone or loc.get("timezone", DEFAULT_TIMEZONE)
    location_name = args.location_name or loc.get("name", DEFAULT_LOCATION_NAME)
    model = loc.get("model")
    wind_units = loc.get("wind_units", "kmh")
    precip_model = loc.get("precip_model")

    print(f"Fetching 7-day forecast for {location_name}...")
    data = fetch_forecast(lat, lon, timezone, model, wind_units)

    if precip_model:
        print(f"Fetching precipitation probability from {precip_model}...")
        data["hourly"]["precipitation_probability"] = fetch_precip_probability(lat, lon, timezone, precip_model)

    icons = loc.get("icons", args.icons)
    html = build_html(data, location_name, model, wind_units, lat, lon, precip_model, icons)
    output_path = Path(args.output)
    output_path.write_text(html, encoding="utf-8")
    print(f"Forecast written to {output_path.resolve()}")


if __name__ == "__main__":
    main()
