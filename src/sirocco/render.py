import base64
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .config import (
    DEFAULT_LATITUDE,
    DEFAULT_LOCATION_NAME,
    DEFAULT_LONGITUDE,
    DEFAULT_THEME,
    DEFAULT_TIMEZONE,
    ICON_SETS,
    METEOCON_BASE,
    METEOCON_FILL_BASE,
    METEOCON_ICONS,
    MODEL_LABELS,
    MODEL_URLS,
    THEMES,
    WMO_CODES,
)

_POLLEN_SPECIES = [
    "alder_pollen",
    "birch_pollen",
    "grass_pollen",
    "mugwort_pollen",
    "ragweed_pollen",
]
_POLLEN_LABELS = ["Low", "Moderate", "High", "Very High"]
_POLLEN_SEVERITY_SUFFIXES = ["low", "moderate", "high", "very-high"]
_POLLEN_SPECIES_TYPE = {
    "grass_pollen": "grass",
    "alder_pollen": "tree",
    "birch_pollen": "tree",
    "mugwort_pollen": "tree",
    "ragweed_pollen": "tree",
}
_POLLEN_LINK = (
    "https://www.worc.ac.uk/about/academic-schools/school-of-science-and-the-environment"
    "/science-and-the-environment-research/national-pollen-and-aerobiology-research-unit"
    "/pollen-forecast.aspx"
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
    if t < -10:
        return "tc-0"
    if t < -5:
        return "tc-1"
    if t < 0:
        return "tc-2"
    if t < 5:
        return "tc-3"
    if t < 10:
        return "tc-4"
    if t < 15:
        return "tc-5"
    if t < 20:
        return "tc-6"
    if t < 25:
        return "tc-7"
    if t < 30:
        return "tc-8"
    if t < 35:
        return "tc-9"
    return "tc-10"


def precip_color(p: float | None) -> str | None:
    """Return a CSS class for precipitation probability, or None if negligible."""
    if p is None:
        return None
    if p < 10:
        return None
    if p < 30:
        return "pc-0"
    if p < 50:
        return "pc-1"
    if p < 70:
        return "pc-2"
    if p < 90:
        return "pc-3"
    return "pc-4"


def pollen_color(max_grains: float | None) -> str | None:
    """Return a CSS class for pollen severity, or None if negligible/absent."""
    if max_grains is None or max_grains < 1:
        return None
    if max_grains < 30:
        return "pollc-0"
    if max_grains < 50:
        return "pollc-1"
    if max_grains < 150:
        return "pollc-2"
    return "pollc-3"


def daily_pollen_max(pollen_data: dict, dates: list[str]) -> list[float | None]:
    """Return max pollen grains/m³ across all species for each date."""
    if not pollen_data or not pollen_data.get("time"):
        return [None] * len(dates)
    times = pollen_data["time"]
    result = []
    for date_str in dates:
        day_values = []
        for species in _POLLEN_SPECIES:
            species_vals = pollen_data.get(species, [])
            for j, t in enumerate(times):
                if t.startswith(date_str) and j < len(species_vals) and species_vals[j] is not None:
                    day_values.append(species_vals[j])
        result.append(max(day_values) if day_values else None)
    return result


def daily_pollen_dominant_type(pollen_data: dict, dates: list[str]) -> list[str]:
    """Return 'grass' or 'tree' for the dominant pollen species type each day."""
    if not pollen_data or not pollen_data.get("time"):
        return ["grass"] * len(dates)
    times = pollen_data["time"]
    result = []
    for date_str in dates:
        type_max: dict[str, float] = {}
        for species, species_type in _POLLEN_SPECIES_TYPE.items():
            vals = pollen_data.get(species, [])
            day_vals = [
                vals[j]
                for j, t in enumerate(times)
                if t.startswith(date_str) and j < len(vals) and vals[j] is not None
            ]
            if day_vals:
                type_max[species_type] = max(type_max.get(species_type, 0.0), max(day_vals))
        result.append(max(type_max, key=lambda k: type_max[k]) if type_max else "grass")
    return result


def uv_color(uv: float) -> str:
    """Return a CSS class name for the WHO UV index band."""
    if uv < 3:
        return "uvc-0"  # green
    if uv < 6:
        return "uvc-1"  # yellow
    if uv < 8:
        return "uvc-2"  # orange
    if uv < 11:
        return "uvc-3"  # red
    return "uvc-4"  # violet


def weather_icon_html(
    wmo_code: int,
    is_day: bool = True,
    size: int = 32,
    use_meteocons: bool = True,
    icon_base: str = METEOCON_BASE,
    icon_mapping: dict = METEOCON_ICONS,
) -> str:
    """Return an <img> tag for the active icon set, or emoji fallback."""
    _, emoji = wmo_description(wmo_code)
    if not use_meteocons:
        return emoji
    icons = icon_mapping.get(wmo_code)
    if not icons:
        return emoji
    name = icons[0] if is_day else icons[1]
    if "monochrome" in icon_base:
        svg_path = Path(icon_base) / f"{name}.svg"
        try:
            data = base64.b64encode(svg_path.read_bytes()).decode()
            uri = f"data:image/svg+xml;base64,{data}"
            return (
                f'<span class="weather-icon" aria-label="{emoji}" style="'
                f"display:block;width:{size}px;height:{size}px;"
                f"background-color:var(--icon-color);"
                f"-webkit-mask-image:url('{uri}');"
                f"mask-image:url('{uri}');"
                f'mask-size:contain;mask-repeat:no-repeat;mask-position:center;"></span>'
            )
        except OSError:
            return emoji
    return f'<img class="weather-icon" src="{icon_base}/{name}.svg" alt="{emoji}" width="{size}" height="{size}">'


def detail_icon(name: str, size: int = 24) -> str:
    """Return an inline <img> for a named Meteocons icon."""
    return f'<img src="{METEOCON_BASE}/{name}.svg" width="{size}" height="{size}" class="detail-icon" alt="">'


def wind_compass(degrees: float) -> str:
    dirs = [
        "N",
        "NNE",
        "NE",
        "ENE",
        "E",
        "ESE",
        "SE",
        "SSE",
        "S",
        "SSW",
        "SW",
        "WSW",
        "W",
        "WNW",
        "NW",
        "NNW",
    ]
    return dirs[round(degrees / 22.5) % 16]


def get_daytime_weather_code(
    hourly_codes: list,
    hourly_times: list,
    hourly_precip: list,
    sunrise_time: str,
    sunset_time: str,
) -> int | None:
    """Get representative daytime weather code.

    Returns the most common (modal) daytime code.
    """
    if not hourly_codes or not hourly_times:
        return None

    from collections import Counter

    # Filter to daytime hours
    daytime_codes = [
        code
        for code, time in zip(hourly_codes, hourly_times)
        if code is not None and sunrise_time <= time[11:16] <= sunset_time
    ]

    if not daytime_codes:
        return None

    # Return the most common (modal) daytime code
    code_counts = Counter(daytime_codes)
    return code_counts.most_common(1)[0][0]


def wind_arrow_char(speed: float | None) -> str:
    """Return an arrow character scaled to wind speed tier."""
    if speed is None:
        return "↑"
    speed = round(speed)
    if speed < 10:
        return "↑"  # calm/light — standard
    if speed < 20:
        return "⇑"  # moderate — double
    if speed < 30:
        return "⬆"  # fresh — heavy filled
    return "⬆⬆"  # strong — doubled heavy


def _themes_css() -> str:
    lines = []
    for key, vals in THEMES.items():
        props = "; ".join(f"{k}: {v}" for k, v in vals.items() if k.startswith("--"))
        lines.append(f'        [data-theme="{key}"] {{ {props} }}')
    return "\n".join(lines)


def _theme_options(default_theme: str) -> str:
    return "\n".join(
        f'            <option value="{key}"{" selected" if key == default_theme else ""}>'
        f"{vals['label']}</option>"
        for key, vals in THEMES.items()
    )


def build_html(
    data: dict,
    location_name: str = DEFAULT_LOCATION_NAME,
    model: str | None = None,
    wind_units: str = "kmh",
    lat: float = DEFAULT_LATITUDE,
    lon: float = DEFAULT_LONGITUDE,
    precip_model: str | None = None,
    icons: str = "meteocons",
    timezone: str = DEFAULT_TIMEZONE,
    theme: str = DEFAULT_THEME,
    per_day_step: list[int] | None = None,
    precip_model_note: str = "precip.",
    pollen_data: dict | None = None,
) -> str:
    daily = data["daily"]
    hourly = data.get("hourly", {})
    dates = daily["time"]
    n_days = len(dates)
    _now = datetime.now(ZoneInfo(timezone))
    generated_at = _now.strftime("%d %b %Y at %H:%M")

    # --- Summary panels (one per day) ---
    current_hour = _now.hour
    use_meteocons = icons != "emoji"
    icon_base, icon_mapping = ICON_SETS.get(icons, (METEOCON_BASE, METEOCON_ICONS))

    # Check if the first daily forecast date is today.
    today = _now.date()
    first_forecast_date = datetime.strptime(dates[0], "%Y-%m-%d").date()
    is_first_day_today = first_forecast_date == today

    pollen_daily = daily_pollen_max(pollen_data or {}, dates)
    pollen_types = daily_pollen_dominant_type(pollen_data or {}, dates)

    # Calculate the hour offset for hourly data slicing.
    # Open-Meteo API returns daily forecast starting from today or tomorrow,
    # and hourly data starting from the beginning of today (or sometimes the current hour).
    # We find where the first daily date appears in the hourly time array to align them.
    daily_to_hourly_offset = 0
    if "time" in hourly:
        try:
            # Match the first daily date to the first corresponding hourly entry.
            # Usually, dates[0] is either today or tomorrow.
            target = f"{dates[0]}T00:00"
            if target in hourly["time"]:
                daily_to_hourly_offset = hourly["time"].index(target)
            else:
                # Fallback: search for the first hour of that date
                for idx, t in enumerate(hourly["time"]):
                    if t.startswith(dates[0]):
                        daily_to_hourly_offset = idx
                        break
        except (ValueError, IndexError):
            # Fallback for manual/legacy offset calculation
            daily_to_hourly_offset = 0 if is_first_day_today else (24 - current_hour)
    else:
        # Fallback for manual/legacy offset calculation if hourly["time"] is missing
        daily_to_hourly_offset = 0 if is_first_day_today else (24 - current_hour)

    summary_panels = ""
    for i in range(n_days):
        code = daily["weather_code"][i]
        desc, _ = wmo_description(code)
        sunrise_hm = daily["sunrise"][i][11:16]
        sunset_hm = daily["sunset"][i][11:16]
        sunrise = format_time(daily["sunrise"][i])
        sunset = format_time(daily["sunset"][i])

        day_start = i * 24 + daily_to_hourly_offset
        # Show all 24 hours for each day; we'll mark the current hour visually
        h_slice = range(day_start, day_start + 24)

        if hourly.get("temperature_2m"):
            h_temps = [
                hourly["temperature_2m"][j]
                for j in h_slice
                if hourly["temperature_2m"][j] is not None
            ]
            h_gusts = [
                hourly["wind_gusts_10m"][j]
                for j in h_slice
                if hourly.get("wind_gusts_10m") and hourly["wind_gusts_10m"][j] is not None
            ]
            h_precip = [
                hourly["precipitation_probability"][j]
                for j in h_slice
                if hourly.get("precipitation_probability")
                and hourly["precipitation_probability"][j] is not None
            ]
            h_humidity = [
                hourly["relative_humidity_2m"][j]
                for j in h_slice
                if hourly.get("relative_humidity_2m")
                and hourly["relative_humidity_2m"][j] is not None
            ]
            tmax = max(h_temps) if h_temps else daily["temperature_2m_max"][i]
            tmin = min(h_temps) if h_temps else daily["temperature_2m_min"][i]
            # Only show UV if all daylight hours have data
            times = hourly.get("time", [])
            daylight_uv = [
                hourly["uv_index"][j]
                for j in h_slice
                if hourly.get("uv_index")
                and j < len(times)
                and sunrise_hm <= times[j][11:16] <= sunset_hm
            ]
            uv = (
                max(daylight_uv)
                if daylight_uv and all(v is not None for v in daylight_uv)
                else None
            )
            max_gust = max(h_gusts) if h_gusts else None
            max_precip = max(h_precip) if h_precip else None
            min_humidity = min(h_humidity) if h_humidity else None
        else:
            tmax = daily["temperature_2m_max"][i]
            tmin = daily["temperature_2m_min"][i]
            uv = daily["uv_index_max"][i]
            max_gust = None
            max_precip = None
            min_humidity = None

        p_max = pollen_daily[i] if i < len(pollen_daily) else None
        p_cls = pollen_color(p_max)
        if p_cls:
            idx = int(p_cls[-1])
            p_lbl = _POLLEN_LABELS[idx]
            p_type = pollen_types[i] if i < len(pollen_types) else "grass"
            icon_name = f"pollen-{p_type}-{_POLLEN_SEVERITY_SUFFIXES[idx]}"
            _picon = f'<img src="{METEOCON_FILL_BASE}/{icon_name}.svg" width="24" height="24" class="detail-icon" alt="">'
            pollen_html = (
                f"<span>"
                f'<a href="{_POLLEN_LINK}" target="_blank" style="text-decoration:none;color:inherit;">'
                f"{_picon} {p_lbl}"
                f"</a></span>"
            )
        else:
            pollen_html = ""

        active = "active" if i == 0 else ""
        summary_panels += f"""
    <div class="summary {active}" id="summary-{i}">
        <div class="summary-desc">{desc}</div>
        <div class="summary-details">
            <span>{detail_icon("sunrise")} {sunrise}</span>
            <span>{detail_icon("sunset")} {sunset}</span>
            {f"<span>{detail_icon('wind-beaufort-0')} {max_gust:.0f} {wind_units}</span>" if max_gust is not None else ""}
            {f"<span>{detail_icon('rain')} {max_precip:.0f}%</span>" if max_precip is not None else ""}
            {f"<span>{detail_icon('humidity')} {min_humidity:.0f}%</span>" if min_humidity is not None else ""}
            {f"<span>{detail_icon(f'uv-index-{max(1, min(int(uv), 11))}')} UV {uv:.0f}</span>" if uv is not None else ""}
            {pollen_html}
        </div>
    </div>"""

    # --- Daily strip ---
    day_cards = ""
    for i in range(n_days):
        weekday, short_date = format_date(dates[i])
        sunrise_hm = daily["sunrise"][i][11:16]
        sunset_hm = daily["sunset"][i][11:16]

        # Use modal daytime weather code, with precipitation weighting
        day_start = i * 24 + daily_to_hourly_offset
        h_times = hourly.get("time", [])[day_start : day_start + 24]
        h_codes = hourly.get("weather_code", [])[day_start : day_start + 24]
        h_precip = hourly.get("precipitation_probability", [])[day_start : day_start + 24]
        code = get_daytime_weather_code(h_codes, h_times, h_precip, sunrise_hm, sunset_hm)

        # Fallback to daily code if no daytime codes available
        if code is None:
            code = daily["weather_code"][i]

        day_icon = (
            weather_icon_html(
                code,
                is_day=True,
                size=36,
                use_meteocons=use_meteocons,
                icon_base=icon_base,
                icon_mapping=icon_mapping,
            )
            if code is not None
            else ""
        )
        tmax = daily["temperature_2m_max"][i]
        tmin = daily["temperature_2m_min"][i]
        active = "active" if i == 0 else ""
        short_weekday = weekday if weekday == "Today" else weekday[:3]
        day_cards += f"""
        <div class="day-card {active}" onclick="selectDay({i})">
            <div class="day-name"><span class="day-full">{weekday}</span><span class="day-short">{short_weekday}</span></div>
            <div class="day-date">{short_date}</div>
            <div class="day-emoji">{day_icon}</div>
            <div class="day-temps"><span class="tmax">{f"{tmax:.0f}°" if tmax is not None else "—"}</span><span class="tmin">{f"{tmin:.0f}°" if tmin is not None else "—"}</span></div>
        </div>"""

    # --- Hourly panels (one per day, pre-rendered) ---
    def _cell(v, fmt_str, suffix=""):
        return f"<td>{format(v, fmt_str)}{suffix}</td>" if v is not None else "<td>—</td>"

    def _lbl(full, short):
        return f'<td class="row-label"><span class="lbl-full">{full}</span><span class="lbl-short">{short}</span></td>'

    label_table = f"""<table class="hourly hourly-labels">
            <thead><tr><th class="row-label"></th></tr></thead>
            <tbody>
                <tr>{_lbl("Symbol", "Symbol")}</tr>
                <tr>{_lbl("Chance of precipitation", "Precipitation")}</tr>
                <tr>{_lbl("Temperature (°C)", "Temp (°C)")}</tr>
                <tr>{_lbl("Feels like (°C)", "Feels like")}</tr>
                <tr>{_lbl("Wind direction", "Direction")}</tr>
                <tr>{_lbl(f"Wind speed ({wind_units})", f"Wind ({wind_units})")}</tr>
                <tr>{_lbl(f"Wind gust ({wind_units})", f"Gusts ({wind_units})")}</tr>
                <tr>{_lbl("Humidity", "Humidity")}</tr>
                <tr>{_lbl("UV", "UV")}</tr>
            </tbody>
        </table>"""

    hourly_panels = ""
    for day_i in range(n_days):
        day_start = day_i * 24 + daily_to_hourly_offset
        step = (per_day_step[day_i] if per_day_step and day_i < len(per_day_step) else None) or 1
        slots = 24 // step
        indices = [day_start + j * step for j in range(slots)]
        all_times = hourly.get("time", [])
        indices = [k for k in indices if k < len(all_times)]
        h_times = [all_times[k] for k in indices]

        # Mark the current hour for visual separator (only for today)
        # For step>1, mark the slot whose time is nearest to the current hour.
        if day_i == 0 and is_first_day_today:
            current_hour_index = current_hour // step
        else:
            current_hour_index = None

        active = "active" if day_i == 0 else ""

        if not h_times:
            hourly_panels += f'<div class="hourly-panel {active}" id="day-{day_i}"></div>'
            continue

        sunrise_hm = daily["sunrise"][day_i][11:16]
        sunset_hm = daily["sunset"][day_i][11:16]

        def _pick(key):
            arr = hourly.get(key, [])
            return [arr[k] if k < len(arr) else None for k in indices]

        h_codes = _pick("weather_code")
        h_temps = _pick("temperature_2m")
        h_feels = _pick("apparent_temperature")
        h_precip = _pick("precipitation_probability")
        h_wind = _pick("wind_speed_10m")
        h_wdir = _pick("wind_direction_10m")
        h_gusts = _pick("wind_gusts_10m")
        h_humidity = _pick("relative_humidity_2m")
        h_uv = _pick("uv_index")

        time_cells = "".join(
            f"""<th{"" if current_hour_index is None or i != current_hour_index else ' class="now"'}>{t[11:16]}</th>"""
            for i, t in enumerate(h_times)
        )
        symbol_cells = "".join(
            (
                f"""<td{"" if current_hour_index is None or i != current_hour_index else ' class="now"'}>{weather_icon_html(c, is_day=sunrise_hm <= t[11:16] <= sunset_hm, size=20, use_meteocons=use_meteocons, icon_base=icon_base, icon_mapping=icon_mapping)}</td>"""
                if c is not None
                else f"""<td{"" if current_hour_index is None or i != current_hour_index else ' class="now"'}>—</td>"""
            )
            for i, (c, t) in enumerate(zip(h_codes, h_times))
        )

        def _cell_with_marker(v, fmt_str, suffix="", idx=None):
            now_class = (
                " now" if current_hour_index is not None and idx == current_hour_index else ""
            )
            return (
                f'<td class="{now_class}">{format(v, fmt_str)}{suffix}</td>'
                if v is not None
                else f'<td class="{now_class}">—</td>'
            )

        precip_cells = "".join(
            (
                f'<td class="{precip_color(p)}{" now" if current_hour_index is not None and i == current_hour_index else ""} tinted">{p:.0f}%</td>'
                if precip_color(p)
                else (
                    f"""<td{' class="now"' if current_hour_index is not None and i == current_hour_index else ""}>{format(p, ".0f")}%</td>"""
                    if p is not None
                    else f"""<td{' class="now"' if current_hour_index is not None and i == current_hour_index else ""}>—</td>"""
                )
            )
            for i, p in enumerate(h_precip)
        )
        temp_cells = "".join(
            (
                f'<td class="{temp_color(t)}{" now" if current_hour_index is not None and i == current_hour_index else ""} tinted">{t:.0f}°</td>'
                if t is not None
                else f"""<td{' class="now"' if current_hour_index is not None and i == current_hour_index else ""}>—</td>"""
            )
            for i, t in enumerate(h_temps)
        )
        feels_cells = "".join(
            (
                f'<td class="{temp_color(t)}{" now" if current_hour_index is not None and i == current_hour_index else ""} tinted">{t:.0f}°</td>'
                if t is not None
                else f"""<td{' class="now"' if current_hour_index is not None and i == current_hour_index else ""}>—</td>"""
            )
            for i, t in enumerate(h_feels)
        )
        wdir_cells = "".join(
            (
                f"""<td{' class="now"' if current_hour_index is not None and i == current_hour_index else ""}><div class="wind-arrow" style="transform:rotate({(d + 180) % 360:.0f}deg)">{wind_arrow_char(g)}</div><div class="wind-cmp">{wind_compass(d)}</div></td>"""
                if d is not None
                else f"""<td{' class="now"' if current_hour_index is not None and i == current_hour_index else ""}>—</td>"""
            )
            for i, (d, w, g) in enumerate(zip(h_wdir, h_wind, h_gusts))
        )
        wind_cells = "".join(
            (
                f"""<td{' class="now"' if current_hour_index is not None and i == current_hour_index else ""}>{format(w, ".0f")}</td>"""
                if w is not None
                else f"""<td{' class="now"' if current_hour_index is not None and i == current_hour_index else ""}>—</td>"""
            )
            for i, w in enumerate(h_wind)
        )
        gust_cells = "".join(
            (
                f"""<td{' class="now"' if current_hour_index is not None and i == current_hour_index else ""}>{format(g, ".0f")}</td>"""
                if g is not None
                else f"""<td{' class="now"' if current_hour_index is not None and i == current_hour_index else ""}>—</td>"""
            )
            for i, g in enumerate(h_gusts)
        )
        humidity_cells = "".join(
            (
                f"""<td{' class="now"' if current_hour_index is not None and i == current_hour_index else ""}>{format(h, ".0f")}%</td>"""
                if h is not None
                else f"""<td{' class="now"' if current_hour_index is not None and i == current_hour_index else ""}>—</td>"""
            )
            for i, h in enumerate(h_humidity)
        )
        uv_cells = "".join(
            (
                f'<td class="{uv_color(u)}{" now" if current_hour_index is not None and i == current_hour_index else ""} tinted">{u:.0f}</td>'
                if u is not None
                else f"""<td{' class="now"' if current_hour_index is not None and i == current_hour_index else ""}>—</td>"""
            )
            for i, u in enumerate(h_uv)
        )

        hourly_panels += f"""
        <div class="hourly-panel {active}" id="day-{day_i}">
            <div class="hourly-layout">
                {label_table}
                <div class="hourly-scroll">
                    <table class="hourly hourly-data">
                        <thead><tr>{time_cells}</tr></thead>
                        <tbody>
                            <tr>{symbol_cells}</tr>
                            <tr>{precip_cells}</tr>
                            <tr>{temp_cells}</tr>
                            <tr>{feels_cells}</tr>
                            <tr>{wdir_cells}</tr>
                            <tr>{wind_cells}</tr>
                            <tr>{gust_cells}</tr>
                            <tr>{humidity_cells}</tr>
                            <tr>{uv_cells}</tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>"""

    template = _env.get_template("forecast.html")
    primary_model_lbl = model_label(model)
    precip_model_lbl = model_label(precip_model) if precip_model else None

    if icons.startswith("meteocons"):
        icon_credit_html = (
            '<a href="https://meteocons.com/" target="_blank">Meteocons</a> (MIT License)'
        )
    elif icons == "makin-things":
        icon_credit_html = '<a href="https://github.com/Makin-Things/weather-icons" target="_blank">Makin-Things</a> (MIT License)'
    else:
        icon_credit_html = None

    return template.render(
        location_name=location_name,
        lat=lat,
        lon=lon,
        generated_at=generated_at,
        primary_model_label=primary_model_lbl,
        primary_model_url=MODEL_URLS.get(primary_model_lbl),
        precip_model_label=precip_model_lbl,
        precip_model_url=MODEL_URLS.get(precip_model_lbl) if precip_model_lbl else None,
        precip_model_note=precip_model_note,
        summary_panels=summary_panels,
        day_cards=day_cards,
        hourly_panels=hourly_panels,
        icon_credit_html=icon_credit_html,
        themes_css=_themes_css(),
        theme_options=_theme_options(theme),
        default_theme=theme,
        pollen_shown=any(v is not None for v in pollen_daily),
    )
