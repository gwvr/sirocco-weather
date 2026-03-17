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
    "precipitation_probability",
    "wind_speed_10m",
    "wind_direction_10m",
    "wind_gusts_10m",
    "relative_humidity_2m",
    "uv_index",
]

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
    if t < 0:  return "#aed6f1"
    if t < 5:  return "#d6eaf8"
    if t < 10: return "#a9dfbf"
    if t < 15: return "#fef9e7"
    if t < 20: return "#fdebd0"
    if t < 25: return "#fad7a0"
    return "#f1948a"


def wind_compass(degrees: float) -> str:
    dirs = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
            "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    return dirs[round(degrees / 22.5) % 16]


def build_html(data: dict, location_name: str = DEFAULT_LOCATION_NAME, model: str | None = None, wind_units: str = "kmh") -> str:
    daily = data["daily"]
    hourly = data.get("hourly", {})
    dates = daily["time"]
    n_days = len(dates)
    generated_at = datetime.now().strftime("%d %b %Y at %H:%M")

    # --- Summary panel (today) ---
    today_desc, today_emoji = wmo_description(daily["weather_code"][0])
    today_max = daily["temperature_2m_max"][0]
    today_min = daily["temperature_2m_min"][0]
    today_sunrise = format_time(daily["sunrise"][0])
    today_sunset = format_time(daily["sunset"][0])
    today_uv = daily["uv_index_max"][0]

    summary_html = f"""
    <div class="summary">
        <div class="summary-main">
            <div class="summary-temp">{today_max:.0f}°<span class="summary-min">/{today_min:.0f}°C</span></div>
            <div class="summary-desc">{today_emoji} {today_desc}</div>
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
        _, emoji = wmo_description(daily["weather_code"][i])
        tmax = daily["temperature_2m_max"][i]
        tmin = daily["temperature_2m_min"][i]
        active = "active" if i == 0 else ""
        day_cards += f"""
        <div class="day-card {active}" onclick="selectDay({i})">
            <div class="day-name">{weekday}</div>
            <div class="day-date">{short_date}</div>
            <div class="day-emoji">{emoji}</div>
            <div class="day-temps"><span class="tmax">{tmax:.0f}°</span><span class="tmin">{tmin:.0f}°</span></div>
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

        h_codes   = hourly.get("weather_code", [])[start:end]
        h_temps   = hourly.get("temperature_2m", [])[start:end]
        h_precip  = hourly.get("precipitation_probability", [])[start:end]
        h_wind    = hourly.get("wind_speed_10m", [])[start:end]
        h_wdir    = hourly.get("wind_direction_10m", [])[start:end]
        h_gusts   = hourly.get("wind_gusts_10m", [])[start:end]
        h_humidity = hourly.get("relative_humidity_2m", [])[start:end]
        h_uv      = hourly.get("uv_index", [])[start:end]

        time_cells    = "".join(f"<th>{t[11:16]}</th>" for t in h_times)
        def _cell(v, fmt_str, suffix=""): return f"<td>{format(v, fmt_str)}{suffix}</td>" if v is not None else "<td>—</td>"

        symbol_cells   = "".join(f"<td>{wmo_description(c)[1]}</td>" if c is not None else "<td>—</td>" for c in h_codes)
        precip_cells   = "".join(_cell(p, ".0f", "%") for p in h_precip)
        temp_cells     = "".join(f'<td style="background:{temp_color(t)}">{t:.0f}°</td>' if t is not None else "<td>—</td>" for t in h_temps)
        wdir_cells     = "".join(
            f'<td><div class="wind-arrow" style="transform:rotate({(d + 180) % 360:.0f}deg)">↑</div>'
            f'<div class="wind-cmp">{wind_compass(d)}</div></td>'
            if d is not None else "<td>—</td>"
            for d in h_wdir
        )
        wind_cells     = "".join(_cell(w, ".0f") for w in h_wind)
        gust_cells     = "".join(_cell(g, ".0f") for g in h_gusts)
        humidity_cells = "".join(_cell(h, ".0f", "%") for h in h_humidity)
        uv_cells       = "".join(_cell(u, ".0f") for u in h_uv)

        hourly_panels += f"""
        <div class="hourly-panel {active}" id="day-{day_i}">
            <div class="hourly-scroll">
                <table class="hourly">
                    <thead><tr><th class="row-label"></th>{time_cells}</tr></thead>
                    <tbody>
                        <tr><td class="row-label">Symbol</td>{symbol_cells}</tr>
                        <tr><td class="row-label">Precip.</td>{precip_cells}</tr>
                        <tr><td class="row-label">Temp °C</td>{temp_cells}</tr>
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

        body {{
            font-family: Arial, Helvetica, sans-serif;
            background: #eef2f7;
            color: #222;
            padding: 1.5rem 1rem;
            min-height: 100vh;
            max-width: 1200px;
            margin: 0 auto;
        }}

        header {{ margin-bottom: 1rem; }}
        header h1 {{ font-size: 1.4rem; font-weight: 700; color: #1a3c5e; }}
        .generated {{ font-size: 0.75rem; color: #999; margin-top: 0.2rem; }}
        .generated a {{ color: #1a6faf; text-decoration: none; }}
        .generated a:hover {{ text-decoration: underline; }}

        /* Summary */
        .summary {{
            background: white;
            border-radius: 8px;
            padding: 1rem 1.5rem;
            margin-bottom: 0.75rem;
            display: flex;
            align-items: center;
            gap: 2rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        }}
        .summary-temp {{ font-size: 2.2rem; font-weight: 700; color: #1a3c5e; }}
        .summary-min {{ font-size: 1.3rem; color: #999; font-weight: 400; }}
        .summary-desc {{ font-size: 0.95rem; color: #555; margin-top: 0.2rem; }}
        .summary-details {{ display: flex; gap: 1.5rem; font-size: 0.9rem; color: #555; }}

        /* Daily strip */
        .daily-strip {{
            display: flex;
            background: white;
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
            border-right: 1px solid #e8e8e8;
            transition: background 0.1s;
            user-select: none;
        }}
        .day-card:last-child {{ border-right: none; }}
        .day-card:hover {{ background: #f0f4ff; }}
        .day-card.active {{ background: #1a6faf; color: white; }}
        .day-card.active .day-date {{ color: rgba(255,255,255,0.75); }}
        .day-card.active .tmin {{ color: rgba(255,255,255,0.7); }}
        .day-name {{ font-weight: 700; font-size: 0.85rem; }}
        .day-date {{ font-size: 0.72rem; color: #999; margin-bottom: 0.3rem; }}
        .day-emoji {{ font-size: 1.4rem; line-height: 1; margin: 0.25rem 0; }}
        .tmax {{ font-weight: 700; font-size: 0.85rem; }}
        .tmin {{ color: #999; font-size: 0.85rem; margin-left: 0.2rem; }}

        /* Hourly panels */
        .hourly-panel {{ display: none; background: white; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }}
        .hourly-panel.active {{ display: block; }}
        .hourly-scroll {{ overflow-x: auto; }}

        table.hourly {{ border-collapse: collapse; white-space: nowrap; }}
        table.hourly th,
        table.hourly td {{
            border: 1px solid #e8e8e8;
            padding: 0.3rem 0.45rem;
            text-align: center;
            font-size: 0.78rem;
        }}
        table.hourly thead th {{
            background: #f5f7fa;
            color: #666;
            font-weight: normal;
        }}
        td.row-label, th.row-label {{
            background: #f5f7fa;
            color: #555;
            font-weight: 600;
            text-align: right;
            padding-right: 0.75rem;
            border-right: 2px solid #ddd;
            position: sticky;
            left: 0;
            z-index: 1;
        }}
        th.row-label {{ z-index: 2; }}

        .wind-arrow {{ font-size: 1rem; display: inline-block; line-height: 1; }}
        .wind-cmp {{ font-size: 0.65rem; color: #777; margin-top: 0.1rem; }}

        footer {{
            text-align: center;
            margin-top: 1.5rem;
            font-size: 0.75rem;
            color: #999;
        }}
    </style>
</head>
<body>
    <header>
        <h1>📍 {location_name}</h1>
        <p class="generated">Generated {generated_at} &mdash; Data from {model_label(model)} via <a href="https://open-meteo.com/" target="_blank">Open-Meteo</a></p>
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

    print(f"Fetching 7-day forecast for {location_name}...")
    data = fetch_forecast(lat, lon, timezone, model, wind_units)
    html = build_html(data, location_name, model, wind_units)
    output_path = Path(args.output)
    output_path.write_text(html, encoding="utf-8")
    print(f"Forecast written to {output_path.resolve()}")


if __name__ == "__main__":
    main()
