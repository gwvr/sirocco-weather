import argparse
import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml
from dotenv import load_dotenv

from .api import (
    build_ukmo_hourly,
    fetch_datahub_hourly_all,
    fetch_datahub_threehourly,
    fetch_datahub_threehourly_all,
    fetch_forecast,
    fetch_pollen,
    fetch_precip_probability_datahub,
)
from .config import (
    DEFAULT_LATITUDE,
    DEFAULT_LOCATION_NAME,
    DEFAULT_LONGITUDE,
    DEFAULT_THEME,
    DEFAULT_TIMEZONE,
    PROVIDERS,
    THEMES,
)
from .render import build_html

OUTPUT_FILE = "forecast.html"


def _apply_datahub_precip(
    data: dict,
    datahub_hourly: dict,
    timezone: str,
    datahub_threehourly: dict | None = None,
) -> None:
    """Override hourly precipitation_probability with DataHub values where available.

    Priority: DataHub hourly (exact match) → DataHub three-hourly (nearest slot) → Open-Meteo fallback.
    """
    tz = ZoneInfo(timezone)
    utc_zone = ZoneInfo("UTC")
    hourly_times = data["hourly"].get("time", [])
    open_meteo_pp = data["hourly"].get("precipitation_probability", [])
    sorted_3h = sorted(datahub_threehourly or {})
    merged = []
    for i, t in enumerate(hourly_times):
        utc_dt = datetime.fromisoformat(t).replace(tzinfo=tz).astimezone(utc_zone)
        utc_key = utc_dt.strftime("%Y-%m-%dT%H:%MZ")
        val = datahub_hourly.get(utc_key)
        if val is None and sorted_3h:
            nearest = min(
                sorted_3h,
                key=lambda k: abs(
                    (
                        datetime.fromisoformat(k.rstrip("Z")).replace(tzinfo=utc_zone) - utc_dt
                    ).total_seconds()
                ),
            )
            val = datahub_threehourly[nearest]
        if val is None:
            val = open_meteo_pp[i] if i < len(open_meteo_pp) else None
        merged.append(val)
    data["hourly"]["precipitation_probability"] = merged


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
    parser.add_argument(
        "--icons",
        default="meteocons",
        choices=[
            "meteocons",
            "meteocons-fill",
            "meteocons-flat",
            "meteocons-monochrome",
            "makin-things",
            "emoji",
        ],
        help="Icon set to use (default: meteocons)",
    )
    parser.add_argument(
        "--theme",
        default=DEFAULT_THEME,
        choices=list(THEMES.keys()),
        help=f"UI theme (default: {DEFAULT_THEME})",
    )
    parser.add_argument(
        "--provider",
        choices=list(PROVIDERS.keys()),
        help="Data provider: 'ecmwf' (Open-Meteo/ECMWF) or 'ukmo' (Met Office DataHub)",
    )
    return parser.parse_args()


def main():
    load_dotenv()
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
    wind_units = loc.get("wind_units", "kmh")
    provider = loc.get("provider") or args.provider

    print(f"Fetching forecast for {location_name}...")

    per_day_step = None
    precip_model_note = "precip."

    if provider and PROVIDERS[provider]["datahub"]:
        # UKMO mode: Open-Meteo daily for day cards, DataHub for all display variables
        om_model = PROVIDERS[provider]["open_meteo_model"]
        data = fetch_forecast(lat, lon, timezone, om_model, wind_units)
        datahub_key = os.environ.get("MET_OFFICE_API_KEY")
        if datahub_key:
            print("Fetching all variables from Met Office DataHub...")
            dh_hourly_ts = fetch_datahub_hourly_all(lat, lon, datahub_key)
            dh_3h_ts = fetch_datahub_threehourly_all(lat, lon, datahub_key)
            hourly, per_day_step = build_ukmo_hourly(
                data["daily"]["time"],
                dh_hourly_ts,
                dh_3h_ts,
                timezone,
                wind_units,
                om_hourly=data.get("hourly"),
            )
            data["hourly"] = hourly
            # Primary label: DataHub (display data); secondary: Open-Meteo (daily)
            model = "ukmo_datahub"
            precip_model = om_model
            precip_model_note = "daily"
        else:
            print("Warning: provider=ukmo requires MET_OFFICE_API_KEY — hourly data unavailable")
            model = om_model
            precip_model = None
    elif provider:
        # ECMWF (or future non-DataHub providers)
        model = PROVIDERS[provider]["open_meteo_model"]
        data = fetch_forecast(lat, lon, timezone, model, wind_units)
        precip_model = None
    else:
        # Legacy path: model key + optional DataHub precip overlay
        model = loc.get("model")
        data = fetch_forecast(lat, lon, timezone, model, wind_units)
        datahub_key = os.environ.get("MET_OFFICE_API_KEY")
        precip_model = None
        if datahub_key:
            print("Fetching precipitation probability from Met Office DataHub...")
            datahub_pp = fetch_precip_probability_datahub(lat, lon, datahub_key)
            datahub_3h = fetch_datahub_threehourly(lat, lon, datahub_key)
            _apply_datahub_precip(data, datahub_pp, timezone, datahub_3h)
            precip_model = "ukmo_datahub"

    pollen_data = {}
    if loc.get("pollen", True):
        print("Fetching pollen data from Open-Meteo CAMS...")
        pollen_data = fetch_pollen(lat, lon, timezone)

    icons = loc.get("icons", args.icons)
    theme = loc.get("theme", args.theme)
    html = build_html(
        data,
        location_name,
        model,
        wind_units,
        lat,
        lon,
        precip_model,
        icons,
        timezone,
        theme,
        per_day_step=per_day_step,
        precip_model_note=precip_model_note,
        pollen_data=pollen_data,
    )
    output_path = Path(args.output)
    output_path.write_text(html, encoding="utf-8")
    print(f"Forecast written to {output_path.resolve()}")
