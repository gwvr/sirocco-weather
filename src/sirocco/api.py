from datetime import datetime
from zoneinfo import ZoneInfo

import httpx

from .config import API_URL, DAILY_VARIABLES, DATAHUB_CODE_TO_WMO, HOURLY_VARIABLES

_DATAHUB_BASE = "https://data.hub.api.metoffice.gov.uk/sitespecific/v0/point"

_MS_TO_MPH = 2.23694
_MS_TO_KMH = 3.6
_MS_TO_KNOTS = 1.94384


def _wind_convert(ms_value: float | None, wind_units: str) -> float | None:
    if ms_value is None:
        return None
    if wind_units == "mph":
        return ms_value * _MS_TO_MPH
    if wind_units == "kn":
        return ms_value * _MS_TO_KNOTS
    return ms_value * _MS_TO_KMH


# --- DataHub precip-only fetches (used by legacy path and _apply_datahub_precip) ---


def fetch_precip_probability_datahub(latitude: float, longitude: float, api_key: str) -> dict:
    """Fetch hourly precipitation probability from Met Office DataHub (~2-day horizon).

    Returns a dict keyed by UTC time string (e.g. '2026-04-29T09:00Z') mapping
    to probability int, or an empty dict on any error.
    """
    try:
        response = httpx.get(
            f"{_DATAHUB_BASE}/hourly",
            params={"latitude": latitude, "longitude": longitude},
            headers={"apikey": api_key},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        time_series = data["features"][0]["properties"]["timeSeries"]
        return {entry["time"]: entry.get("probOfPrecipitation") for entry in time_series}
    except Exception as e:
        print(f"DataHub fetch failed: {e} — precipitation will be blank")
        return {}


def fetch_datahub_threehourly(latitude: float, longitude: float, api_key: str) -> dict:
    """Fetch three-hourly probOfPrecipitation from Met Office DataHub (7-day horizon).

    Returns a dict keyed by UTC time string mapping to probability int.
    """
    try:
        response = httpx.get(
            f"{_DATAHUB_BASE}/three-hourly",
            params={"latitude": latitude, "longitude": longitude},
            headers={"apikey": api_key},
            timeout=10,
        )
        response.raise_for_status()
        time_series = response.json()["features"][0]["properties"]["timeSeries"]
        return {entry["time"]: entry.get("probOfPrecipitation") for entry in time_series}
    except Exception as e:
        print(f"DataHub three-hourly fetch failed: {e} — extended precipitation will be blank")
        return {}


# --- DataHub full-variable fetches (used by UKMO provider) ---


def fetch_datahub_hourly_all(latitude: float, longitude: float, api_key: str) -> list:
    """Fetch the full hourly time series from Met Office DataHub (~2-day horizon).

    Returns the raw list of time series entry dicts, or [] on error.
    """
    try:
        response = httpx.get(
            f"{_DATAHUB_BASE}/hourly",
            params={"latitude": latitude, "longitude": longitude},
            headers={"apikey": api_key},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()["features"][0]["properties"]["timeSeries"]
    except Exception as e:
        print(f"DataHub hourly (all vars) fetch failed: {e}")
        return []


def fetch_datahub_threehourly_all(latitude: float, longitude: float, api_key: str) -> list:
    """Fetch the full three-hourly time series from Met Office DataHub (7-day horizon).

    Returns the raw list of time series entry dicts, or [] on error.
    """
    try:
        response = httpx.get(
            f"{_DATAHUB_BASE}/three-hourly",
            params={"latitude": latitude, "longitude": longitude},
            headers={"apikey": api_key},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()["features"][0]["properties"]["timeSeries"]
    except Exception as e:
        print(f"DataHub three-hourly (all vars) fetch failed: {e}")
        return []


def build_ukmo_hourly(
    dates: list[str],
    dh_hourly_ts: list,
    dh_3h_ts: list,
    timezone: str,
    wind_units: str = "kmh",
    om_hourly: dict | None = None,
) -> tuple[dict, list[int]]:
    """Build a combined hourly data dict from DataHub time series.

    Days within DataHub hourly coverage use step=1 (hourly columns).
    Days beyond use DataHub three-hourly values, expanded to 24 slots/day,
    with step=3 so the renderer shows 8 columns.

    Returns (hourly_dict, per_day_step).
    """
    tz_local = ZoneInfo(timezone)
    tz_utc = ZoneInfo("UTC")

    dh_hourly = {e["time"]: e for e in dh_hourly_ts}
    dh_3h = {e["time"]: e for e in dh_3h_ts}
    sorted_3h_keys = sorted(dh_3h.keys())
    dh_hourly_end = max(dh_hourly.keys()) if dh_hourly else ""

    # Build Open-Meteo hourly lookup keyed by local time string for backfill
    om_lookup: dict[str, dict[str, object]] = {}
    if om_hourly and om_hourly.get("time"):
        om_keys = [
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
        for idx, t in enumerate(om_hourly["time"]):
            om_lookup[t] = {
                k: (om_hourly.get(k) or [None])[idx]
                if om_hourly.get(k) and idx < len(om_hourly[k])
                else None
                for k in om_keys
            }

    times: list[str] = []
    weather_code: list = []
    temperature_2m: list = []
    apparent_temperature: list = []
    precipitation_probability: list = []
    wind_speed_10m: list = []
    wind_direction_10m: list = []
    wind_gusts_10m: list = []
    relative_humidity_2m: list = []
    uv_index: list = []
    per_day_step: list[int] = []

    for date_str in dates:
        date = datetime.strptime(date_str, "%Y-%m-%d").date()

        # A day uses hourly data if its end-of-day UTC is within DataHub hourly coverage.
        day_end_local = datetime(date.year, date.month, date.day, 23, 0, tzinfo=tz_local)
        day_end_utc = day_end_local.astimezone(tz_utc).strftime("%Y-%m-%dT%H:%MZ")
        step = 1 if (dh_hourly and day_end_utc <= dh_hourly_end) else 3
        per_day_step.append(step)

        if step == 1:
            for h in range(24):
                local_dt = datetime(date.year, date.month, date.day, h, 0, tzinfo=tz_local)
                utc_key = local_dt.astimezone(tz_utc).strftime("%Y-%m-%dT%H:%MZ")
                times.append(local_dt.strftime("%Y-%m-%dT%H:%M"))
                e = dh_hourly.get(utc_key)
                local_key = local_dt.strftime("%Y-%m-%dT%H:%M")
                om = om_lookup.get(local_key, {}) if not e else {}
                if e:
                    weather_code.append(
                        DATAHUB_CODE_TO_WMO.get(
                            e.get("significantWeatherCode"), e.get("significantWeatherCode")
                        )
                    )
                    temperature_2m.append(e.get("screenTemperature"))
                    apparent_temperature.append(e.get("feelsLikeTemperature"))
                    precipitation_probability.append(e.get("probOfPrecipitation"))
                    wind_speed_10m.append(_wind_convert(e.get("windSpeed10m"), wind_units))
                    wind_direction_10m.append(e.get("windDirectionFrom10m"))
                    wind_gusts_10m.append(_wind_convert(e.get("windGustSpeed10m"), wind_units))
                    relative_humidity_2m.append(e.get("screenRelativeHumidity"))
                    uv_index.append(e.get("uvIndex"))
                else:
                    # Backfill past hours from Open-Meteo; supplement precip from 3-hourly DataHub
                    pp = om.get("precipitation_probability")
                    if pp is None and sorted_3h_keys:
                        nearest_3h = min(
                            sorted_3h_keys,
                            key=lambda k: abs(
                                (
                                    datetime.fromisoformat(k.rstrip("Z")).replace(tzinfo=tz_utc)
                                    - local_dt.astimezone(tz_utc)
                                ).total_seconds()
                            ),
                        )
                        pp = dh_3h[nearest_3h].get("probOfPrecipitation")
                    weather_code.append(om.get("weather_code"))
                    temperature_2m.append(om.get("temperature_2m"))
                    apparent_temperature.append(om.get("apparent_temperature"))
                    precipitation_probability.append(pp)
                    wind_speed_10m.append(om.get("wind_speed_10m"))
                    wind_direction_10m.append(om.get("wind_direction_10m"))
                    wind_gusts_10m.append(om.get("wind_gusts_10m"))
                    relative_humidity_2m.append(om.get("relative_humidity_2m"))
                    uv_index.append(om.get("uv_index"))
        else:
            for block in range(8):
                local_dt = datetime(date.year, date.month, date.day, block * 3, 0, tzinfo=tz_local)
                utc_dt = local_dt.astimezone(tz_utc)

                if sorted_3h_keys:
                    nearest_key = min(
                        sorted_3h_keys,
                        key=lambda k: abs(
                            (
                                datetime.fromisoformat(k.rstrip("Z")).replace(tzinfo=tz_utc)
                                - utc_dt
                            ).total_seconds()
                        ),
                    )
                    e3 = dh_3h[nearest_key]
                else:
                    e3 = {}

                t_max = e3.get("maxScreenAirTemp")
                t_min = e3.get("minScreenAirTemp")
                temp = (t_max + t_min) / 2 if t_max is not None and t_min is not None else None

                for h_off in range(3):
                    slot = datetime(
                        date.year, date.month, date.day, block * 3 + h_off, 0, tzinfo=tz_local
                    )
                    times.append(slot.strftime("%Y-%m-%dT%H:%M"))
                    weather_code.append(
                        DATAHUB_CODE_TO_WMO.get(
                            e3.get("significantWeatherCode"), e3.get("significantWeatherCode")
                        )
                    )
                    temperature_2m.append(temp)
                    apparent_temperature.append(e3.get("feelsLikeTemp"))
                    precipitation_probability.append(e3.get("probOfPrecipitation"))
                    wind_speed_10m.append(_wind_convert(e3.get("windSpeed10m"), wind_units))
                    wind_direction_10m.append(e3.get("windDirectionFrom10m"))
                    wind_gusts_10m.append(_wind_convert(e3.get("windGustSpeed10m"), wind_units))
                    relative_humidity_2m.append(e3.get("screenRelativeHumidity"))
                    uv_index.append(e3.get("uvIndex"))

    return {
        "time": times,
        "weather_code": weather_code,
        "temperature_2m": temperature_2m,
        "apparent_temperature": apparent_temperature,
        "precipitation_probability": precipitation_probability,
        "wind_speed_10m": wind_speed_10m,
        "wind_direction_10m": wind_direction_10m,
        "wind_gusts_10m": wind_gusts_10m,
        "relative_humidity_2m": relative_humidity_2m,
        "uv_index": uv_index,
    }, per_day_step


_POLLEN_SPECIES = [
    "alder_pollen",
    "birch_pollen",
    "grass_pollen",
    "mugwort_pollen",
    "ragweed_pollen",
]


def fetch_pollen(latitude: float, longitude: float, timezone: str) -> dict:
    """Fetch hourly pollen from Open-Meteo CAMS air quality API (~5-day horizon, Europe only).

    Returns {"time": [...], "alder_pollen": [...], ...} or {} on error.
    """
    try:
        response = httpx.get(
            "https://air-quality-api.open-meteo.com/v1/air-quality",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "timezone": timezone,
                "hourly": ",".join(_POLLEN_SPECIES),
            },
            timeout=10,
        )
        response.raise_for_status()
        return response.json().get("hourly", {})
    except Exception as e:
        print(f"Pollen fetch failed: {e} — pollen will be blank")
        return {}


# --- Open-Meteo fetches ---


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


def fetch_forecast(
    latitude: float,
    longitude: float,
    timezone: str,
    model: str | None = None,
    wind_units: str = "kmh",
    daily_only: bool = False,
) -> dict:
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "timezone": timezone,
        "forecast_days": 6,
        "daily": ",".join(DAILY_VARIABLES),
        "wind_speed_unit": wind_units,
    }
    if not daily_only:
        params["hourly"] = ",".join(HOURLY_VARIABLES)
    if model:
        params["models"] = model
    response = httpx.get(API_URL, params=params, timeout=10)
    response.raise_for_status()
    return response.json()
