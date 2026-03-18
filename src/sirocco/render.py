from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .config import (
    DEFAULT_LATITUDE,
    DEFAULT_LOCATION_NAME,
    DEFAULT_LONGITUDE,
    METEOCON_BASE,
    METEOCON_ICONS,
    MODEL_LABELS,
    WMO_CODES,
)

_env = Environment(
    loader=FileSystemLoader(Path(__file__).parent / "templates"),
    variable_start_string="[[",
    variable_end_string="]]",
    block_start_string="[%",
    block_end_string="%]",
    autoescape=select_autoescape(["html"]),
)


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


def model_label(model: str | None) -> str:
    if model is None:
        return "ECMWF"
    return MODEL_LABELS.get(model, model)


def temp_color(t: float) -> str:
    """Return a CSS class name for the temperature band."""
    if t < -10: return "tc-0"
    if t < -5:  return "tc-1"
    if t < 0:   return "tc-2"
    if t < 5:   return "tc-3"
    if t < 10:  return "tc-4"
    if t < 15:  return "tc-5"
    if t < 20:  return "tc-6"
    if t < 25:  return "tc-7"
    if t < 30:  return "tc-8"
    if t < 35:  return "tc-9"
    return "tc-10"


def uv_color(uv: float) -> str:
    """Return a CSS class name for the WHO UV index band."""
    if uv < 3:  return "uvc-0"   # green
    if uv < 6:  return "uvc-1"   # yellow
    if uv < 8:  return "uvc-2"   # orange
    if uv < 11: return "uvc-3"   # red
    return "uvc-4"                # violet


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
        temp_cells     = "".join(f'<td class="{temp_color(t)} tinted">{t:.0f}°</td>' if t is not None else "<td>—</td>" for t in h_temps)
        feels_cells    = "".join(f'<td class="{temp_color(t)} tinted">{t:.0f}°</td>' if t is not None else "<td>—</td>" for t in h_feels)
        wdir_cells     = "".join(
            f'<td><div class="wind-arrow" style="transform:rotate({(d + 180) % 360:.0f}deg)">↑</div>'
            f'<div class="wind-cmp">{wind_compass(d)}</div></td>'
            if d is not None else "<td>—</td>"
            for d in h_wdir
        )
        wind_cells     = "".join(_cell(w, ".0f") for w in h_wind)
        gust_cells     = "".join(_cell(g, ".0f") for g in h_gusts)
        humidity_cells = "".join(_cell(h, ".0f", "%") for h in h_humidity)
        uv_cells       = "".join(f'<td class="{uv_color(u)} tinted">{u:.0f}</td>' if u is not None else "<td>—</td>" for u in h_uv)

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
