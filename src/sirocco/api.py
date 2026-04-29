import httpx

from .config import API_URL, DAILY_VARIABLES, HOURLY_VARIABLES


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


def fetch_precip_probability_datahub(latitude: float, longitude: float, api_key: str) -> dict:
    """Fetch hourly precipitation probability from Met Office DataHub.

    Returns a dict keyed by UTC time string (e.g. '2026-04-29T09:00Z') mapping
    to probability int, or an empty dict on any error.
    """
    url = "https://data.hub.api.metoffice.gov.uk/sitespecific/v0/point/hourly"
    try:
        response = httpx.get(
            url,
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


def fetch_forecast(
    latitude: float,
    longitude: float,
    timezone: str,
    model: str | None = None,
    wind_units: str = "kmh",
) -> dict:
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
