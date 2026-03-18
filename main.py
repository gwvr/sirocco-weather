import argparse
import httpx
import yaml
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

_env = Environment(
    loader=FileSystemLoader(Path(__file__).parent / "templates"),
    variable_start_string="[[",
    variable_end_string="]]",
    block_start_string="[%",
    block_end_string="%]",
    autoescape=select_autoescape(["html"]),
)

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
        "forecast_days": 6,
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
        "forecast_days": 6,
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
    today_code = daily["weather_code"][0]
    today_icon = weather_icon_html(today_code, is_day=is_day_now, size=64, use_meteocons=use_meteocons) if today_code is not None else ""

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
        <div class="summary-left">
            <div class="summary-icon">{today_icon}</div>
            <div class="summary-desc">{today_desc}</div>
        </div>
        <div class="summary-temp">{today_max:.0f}°<span class="summary-min">/{today_min:.0f}°C</span></div>
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
        code = daily["weather_code"][i]
        day_icon = weather_icon_html(code, is_day=True, size=36, use_meteocons=use_meteocons) if code is not None else ""
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
    def _cell(v, fmt_str, suffix=""): return f"<td>{format(v, fmt_str)}{suffix}</td>" if v is not None else "<td>—</td>"

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
        symbol_cells   = "".join(
            f'<td>{weather_icon_html(c, is_day=sunrise_hm <= t[11:16] <= sunset_hm, size=20, use_meteocons=use_meteocons)}</td>'
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
                        <tr><td class="row-label">Chance of precipitation</td>{precip_cells}</tr>
                        <tr><td class="row-label">Temperature (°C)</td>{temp_cells}</tr>
                        <tr><td class="row-label">Feels like (°C)</td>{feels_cells}</tr>
                        <tr><td class="row-label">Wind direction</td>{wdir_cells}</tr>
                        <tr><td class="row-label">Wind speed ({wind_units})</td>{wind_cells}</tr>
                        <tr><td class="row-label">Wind gust ({wind_units})</td>{gust_cells}</tr>
                        <tr><td class="row-label">Humidity</td>{humidity_cells}</tr>
                        <tr><td class="row-label">UV</td>{uv_cells}</tr>
                    </tbody>
                </table>
            </div>
        </div>"""

    template = _env.get_template("forecast.html")
    return template.render(
        location_name=location_name,
        lat=lat,
        lon=lon,
        generated_at=generated_at,
        primary_model_label=model_label(model),
        precip_model_label=model_label(precip_model) if precip_model else None,
        summary_html=summary_html,
        day_cards=day_cards,
        hourly_panels=hourly_panels,
    )


def load_config(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f) or {}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch and display a weather forecast.")
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

    config_path = args.config or ("location.yaml" if Path("location.yaml").exists() else None)
    config = load_config(config_path) if config_path else {}
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

    print(f"Fetching forecast for {location_name}...")
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
