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


def fetch_forecast(latitude: float, longitude: float, timezone: str) -> dict:
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "timezone": timezone,
        "forecast_days": 7,
        "daily": ",".join(DAILY_VARIABLES),
    }
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


def build_html(data: dict, location_name: str = DEFAULT_LOCATION_NAME) -> str:
    daily = data["daily"]
    dates = daily["time"]
    codes = daily["weather_code"]
    temp_max = daily["temperature_2m_max"]
    temp_min = daily["temperature_2m_min"]
    precip = daily["precipitation_sum"]
    precip_prob = daily["precipitation_probability_max"]
    wind = daily["wind_speed_10m_max"]
    uv = daily["uv_index_max"]
    sunrises = daily["sunrise"]
    sunsets = daily["sunset"]

    generated_at = datetime.now().strftime("%d %b %Y at %H:%M")

    cards_html = ""
    for i in range(len(dates)):
        weekday, short_date = format_date(dates[i])
        desc, emoji = wmo_description(codes[i])
        is_today = weekday == "Today"
        card_class = "card today" if is_today else "card"

        cards_html += f"""
        <div class="{card_class}">
            <div class="card-header">
                <span class="weekday">{weekday}</span>
                <span class="date">{short_date}</span>
            </div>
            <div class="emoji">{emoji}</div>
            <div class="description">{desc}</div>
            <div class="temps">
                <span class="temp-max">{temp_max[i]:.0f}°</span>
                <span class="temp-min">{temp_min[i]:.0f}°</span>
            </div>
            <div class="details">
                <div class="detail">
                    <span class="detail-icon">🌧️</span>
                    <span class="detail-label">Rain</span>
                    <span class="detail-value">{precip[i]:.1f} mm</span>
                </div>
                <div class="detail">
                    <span class="detail-icon">💧</span>
                    <span class="detail-label">Prob.</span>
                    <span class="detail-value">{precip_prob[i]:.0f}%</span>
                </div>
                <div class="detail">
                    <span class="detail-icon">💨</span>
                    <span class="detail-label">Wind</span>
                    <span class="detail-value">{wind[i]:.0f} km/h</span>
                </div>
                <div class="detail">
                    <span class="detail-icon">🕶️</span>
                    <span class="detail-label">UV</span>
                    <span class="detail-value">{uv[i]:.0f}</span>
                </div>
                <div class="detail">
                    <span class="detail-icon">🌅</span>
                    <span class="detail-label">Rise</span>
                    <span class="detail-value">{format_time(sunrises[i])}</span>
                </div>
                <div class="detail">
                    <span class="detail-icon">🌇</span>
                    <span class="detail-label">Set</span>
                    <span class="detail-value">{format_time(sunsets[i])}</span>
                </div>
            </div>
        </div>
        """

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>7-Day Forecast — {location_name}</title>
    <style>
        *, *::before, *::after {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
            padding: 2rem 1rem;
            color: #e0e0e0;
        }}

        header {{
            text-align: center;
            margin-bottom: 2.5rem;
        }}

        header h1 {{
            font-size: 2rem;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 0.25rem;
        }}

        header p {{
            font-size: 0.9rem;
            color: #90a4c8;
        }}

        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            gap: 1rem;
            max-width: 1200px;
            margin: 0 auto;
        }}

        .card {{
            background: rgba(255, 255, 255, 0.07);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 1.25rem 1rem;
            backdrop-filter: blur(10px);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            text-align: center;
        }}

        .card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }}

        .card.today {{
            background: rgba(99, 179, 237, 0.2);
            border-color: rgba(99, 179, 237, 0.5);
            box-shadow: 0 0 20px rgba(99, 179, 237, 0.15);
        }}

        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            margin-bottom: 0.75rem;
        }}

        .weekday {{
            font-weight: 700;
            font-size: 1rem;
            color: #ffffff;
        }}

        .date {{
            font-size: 0.8rem;
            color: #90a4c8;
        }}

        .emoji {{
            font-size: 2.5rem;
            line-height: 1;
            margin: 0.5rem 0;
        }}

        .description {{
            font-size: 0.8rem;
            color: #b0c4de;
            margin-bottom: 0.75rem;
            min-height: 2em;
        }}

        .temps {{
            display: flex;
            justify-content: center;
            gap: 0.75rem;
            margin-bottom: 1rem;
        }}

        .temp-max {{
            font-size: 1.5rem;
            font-weight: 700;
            color: #ff9a76;
        }}

        .temp-min {{
            font-size: 1.5rem;
            font-weight: 400;
            color: #90a4c8;
        }}

        .details {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0.4rem 0.5rem;
            text-align: left;
        }}

        .detail {{
            display: flex;
            align-items: center;
            gap: 0.3rem;
            font-size: 0.75rem;
        }}

        .detail-icon {{
            font-size: 0.85rem;
        }}

        .detail-label {{
            color: #90a4c8;
            flex: 1;
        }}

        .detail-value {{
            color: #e0e0e0;
            font-weight: 600;
        }}

        footer {{
            text-align: center;
            margin-top: 2.5rem;
            font-size: 0.8rem;
            color: #5a7a9a;
        }}

        footer a {{
            color: #7aabcc;
            text-decoration: none;
        }}

        footer a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <header>
        <h1>📍 {location_name}</h1>
        <p>7-Day Weather Forecast</p>
    </header>

    <div class="grid">
        {cards_html}
    </div>

    <footer>
        <p>Generated on {generated_at} &mdash; Data from <a href="https://open-meteo.com/" target="_blank">Open-Meteo</a></p>
    </footer>
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

    print(f"Fetching 7-day forecast for {location_name}...")
    data = fetch_forecast(lat, lon, timezone)
    html = build_html(data, location_name)
    output_path = Path(args.output)
    output_path.write_text(html, encoding="utf-8")
    print(f"Forecast written to {output_path.resolve()}")


if __name__ == "__main__":
    main()
