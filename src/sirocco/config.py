DEFAULT_LATITUDE = 51.81684
DEFAULT_LONGITUDE = -0.35706
DEFAULT_TIMEZONE = "Europe/London"
DEFAULT_LOCATION_NAME = "Harpenden, UK"

API_URL = "https://api.open-meteo.com/v1/forecast"
METEOCON_BASE = "https://bmcdn.nl/assets/weather-icons/v3.0/fill/svg"

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

MODEL_LABELS = {
    "ukmo_seamless":           "UK Met Office",
    "ukmo_global":             "UK Met Office",
    "ukmo_uk_deterministic":   "UK Met Office",
    "ecmwf_ifs025":            "ECMWF",
    "ecmwf_ifs04":             "ECMWF",
    "ecmwf_aifs025":           "ECMWF",
}

MODEL_URLS = {
    "UK Met Office": "https://open-meteo.com/en/docs/ukmo-api",
    "ECMWF":         "https://open-meteo.com/en/docs/ecmwf-api",
}
