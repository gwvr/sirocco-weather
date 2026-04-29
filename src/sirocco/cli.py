import argparse
import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml
from dotenv import load_dotenv

from .api import fetch_forecast, fetch_precip_probability_datahub
from .config import (
    DEFAULT_LATITUDE,
    DEFAULT_LOCATION_NAME,
    DEFAULT_LONGITUDE,
    DEFAULT_TIMEZONE,
)
from .render import build_html

OUTPUT_FILE = "forecast.html"


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
        choices=["meteocons", "meteocons-fill", "meteocons-flat", "makin-things", "emoji"],
        help="Icon set to use (default: meteocons)",
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
    model = loc.get("model")
    wind_units = loc.get("wind_units", "kmh")

    print(f"Fetching forecast for {location_name}...")
    data = fetch_forecast(lat, lon, timezone, model, wind_units)

    datahub_key = os.environ.get("MET_OFFICE_API_KEY")
    if datahub_key:
        print("Fetching precipitation probability from Met Office DataHub...")
        datahub_pp = fetch_precip_probability_datahub(lat, lon, datahub_key)
        tz = ZoneInfo(timezone)
        utc = ZoneInfo("UTC")
        hourly_times = data["hourly"].get("time", [])
        data["hourly"]["precipitation_probability"] = [
            datahub_pp.get(
                datetime.fromisoformat(t)
                .replace(tzinfo=tz)
                .astimezone(utc)
                .strftime("%Y-%m-%dT%H:%MZ")
            )
            for t in hourly_times
        ]

    icons = loc.get("icons", args.icons)
    html = build_html(
        data,
        location_name,
        model,
        wind_units,
        lat,
        lon,
        "ukmo_datahub" if datahub_key else None,
        icons,
        timezone,
    )
    output_path = Path(args.output)
    output_path.write_text(html, encoding="utf-8")
    print(f"Forecast written to {output_path.resolve()}")
