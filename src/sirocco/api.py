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
