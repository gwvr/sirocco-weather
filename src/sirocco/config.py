DEFAULT_LATITUDE = 51.5074
DEFAULT_LONGITUDE = -0.1278
DEFAULT_TIMEZONE = "Europe/London"
DEFAULT_LOCATION_NAME = "London, UK"

API_URL = "https://api.open-meteo.com/v1/forecast"

DEFAULT_THEME = "dark"

THEMES: dict[str, dict[str, str]] = {
    "light": {
        "label": "Light",
        "--bg": "#b8b8b8",
        "--surface": "#ffffff",
        "--surface-2": "#f5f7fa",
        "--text": "#222222",
        "--text-muted": "#999999",
        "--text-mid": "#555555",
        "--border": "#e8e8e8",
        "--border-strong": "#dddddd",
        "--accent": "#1a6faf",
        "--header": "#1a3c5e",
        "--link": "#1a6faf",
        "--icon-color": "#222222",
    },
    "dark": {
        "label": "Dark",
        "--bg": "#0f1923",
        "--surface": "#1a2535",
        "--surface-2": "#1e2d40",
        "--text": "#e0e0e0",
        "--text-muted": "#888888",
        "--text-mid": "#aaaaaa",
        "--border": "#2a3a4f",
        "--border-strong": "#3a4f6a",
        "--accent": "#2a86d4",
        "--header": "#cccccc",
        "--link": "#6ab0e0",
        "--icon-color": "#e0e0e0",
    },
    "tokyo-night": {
        "label": "Tokyo Night",
        "--bg": "#1a1b26",
        "--surface": "#16161e",
        "--surface-2": "#202330",
        "--text": "#a9b1d6",
        "--text-muted": "#787c99",
        "--text-mid": "#9aa5ce",
        "--border": "#222330",
        "--border-strong": "#29355a",
        "--accent": "#3d59a1",
        "--header": "#c0caf5",
        "--link": "#6183bb",
        "--icon-color": "#a9b1d6",
    },
    "tokyo-night-light": {
        "label": "Tokyo Night Light",
        "--bg": "#e6e7ed",
        "--surface": "#d6d8df",
        "--surface-2": "#dadce3",
        "--text": "#343b59",
        "--text-muted": "#707280",
        "--text-mid": "#545c7e",
        "--border": "#c1c2c7",
        "--border-strong": "#9da0ab",
        "--accent": "#2959aa",
        "--header": "#1a1f36",
        "--link": "#2959aa",
        "--icon-color": "#343b59",
    },
    # Moon variant from folke/tokyonight.nvim (not in the VSCode theme repo)
    "tokyo-night-moon": {
        "label": "Tokyo Night Moon",
        "--bg": "#222436",
        "--surface": "#1e2030",
        "--surface-2": "#2f334d",
        "--text": "#c8d3f5",
        "--text-muted": "#636da6",
        "--text-mid": "#828bb8",
        "--border": "#2f334d",
        "--border-strong": "#444a73",
        "--accent": "#82aaff",
        "--header": "#e0e5f5",
        "--link": "#65bcff",
        "--icon-color": "#c8d3f5",
    },
    "tokyo-night-storm": {
        "label": "Tokyo Night Storm",
        "--bg": "#24283b",
        "--surface": "#1f2335",
        "--surface-2": "#2c324a",
        "--text": "#a9b1d6",
        "--text-muted": "#8089b3",
        "--text-mid": "#9099c3",
        "--border": "#1b1e2e",
        "--border-strong": "#29355a",
        "--accent": "#3d59a1",
        "--header": "#c0caf5",
        "--link": "#668ac4",
        "--icon-color": "#a9b1d6",
    },
    "catppuccin-mocha": {
        "label": "Catppuccin Mocha",
        "--bg": "#1e1e2e",
        "--surface": "#313244",
        "--surface-2": "#181825",
        "--text": "#cdd6f4",
        "--text-muted": "#a6adc8",
        "--text-mid": "#bac2de",
        "--border": "#45475a",
        "--border-strong": "#585b70",
        "--accent": "#cba6f7",
        "--header": "#cdd6f4",
        "--link": "#89b4fa",
        "--icon-color": "#cdd6f4",
    },
    "catppuccin-macchiato": {
        "label": "Catppuccin Macchiato",
        "--bg": "#24273a",
        "--surface": "#363a4f",
        "--surface-2": "#1e2030",
        "--text": "#cad3f5",
        "--text-muted": "#a5adcb",
        "--text-mid": "#b8c0e0",
        "--border": "#494d64",
        "--border-strong": "#5b6078",
        "--accent": "#c6a0f6",
        "--header": "#cad3f5",
        "--link": "#8aadf4",
        "--icon-color": "#cad3f5",
    },
    "catppuccin-frappe": {
        "label": "Catppuccin Frappé",
        "--bg": "#303446",
        "--surface": "#414559",
        "--surface-2": "#292c3c",
        "--text": "#c6d0f5",
        "--text-muted": "#a5adce",
        "--text-mid": "#b5bfe2",
        "--border": "#51576d",
        "--border-strong": "#626880",
        "--accent": "#ca9ee6",
        "--header": "#c6d0f5",
        "--link": "#8caaee",
        "--icon-color": "#c6d0f5",
    },
    "catppuccin-latte": {
        "label": "Catppuccin Latte",
        "--bg": "#eff1f5",
        "--surface": "#e6e9ef",
        "--surface-2": "#ccd0da",
        "--text": "#4c4f69",
        "--text-muted": "#6c6f85",
        "--text-mid": "#5c5f77",
        "--border": "#bcc0cc",
        "--border-strong": "#acb0be",
        "--accent": "#8839ef",
        "--header": "#4c4f69",
        "--link": "#1e66f5",
        "--icon-color": "#4c4f69",
    },
    "gruvbox-dark": {
        "label": "Gruvbox Dark",
        "--bg": "#282828",
        "--surface": "#3c3836",
        "--surface-2": "#32302f",
        "--text": "#ebdbb2",
        "--text-muted": "#a89984",
        "--text-mid": "#bdae93",
        "--border": "#504945",
        "--border-strong": "#665c54",
        "--accent": "#d79921",
        "--header": "#ebdbb2",
        "--link": "#83a598",
        "--icon-color": "#ebdbb2",
    },
    "gruvbox-light": {
        "label": "Gruvbox Light",
        "--bg": "#fbf1c7",
        "--surface": "#ebdbb2",
        "--surface-2": "#f2e5bc",
        "--text": "#3c3836",
        "--text-muted": "#7c6f64",
        "--text-mid": "#665c54",
        "--border": "#d5c4a1",
        "--border-strong": "#bdae93",
        "--accent": "#b57614",
        "--header": "#3c3836",
        "--link": "#076678",
        "--icon-color": "#3c3836",
    },
    "dracula": {
        "label": "Dracula",
        "--bg": "#282a36",
        "--surface": "#44475a",
        "--surface-2": "#21222c",
        "--text": "#f8f8f2",
        "--text-muted": "#6272a4",
        "--text-mid": "#a0a8b8",
        "--border": "#44475a",
        "--border-strong": "#6272a4",
        "--accent": "#bd93f9",
        "--header": "#f8f8f2",
        "--link": "#8be9fd",
        "--icon-color": "#f8f8f2",
    },
}
DATAHUB_CODE_TO_WMO: dict[int, int] = {
    0: 0,  # Clear night → Clear sky
    1: 0,  # Sunny day → Clear sky
    2: 2,  # Partly cloudy (night) → Partly cloudy
    3: 2,  # Partly cloudy (day) → Partly cloudy
    4: 3,  # Not used → Overcast
    5: 45,  # Mist → Fog
    6: 45,  # Fog → Fog
    7: 2,  # Cloudy → Partly cloudy
    8: 3,  # Overcast → Overcast
    9: 80,  # Light rain shower (night) → Slight showers
    10: 80,  # Light rain shower (day) → Slight showers
    11: 51,  # Drizzle → Light drizzle
    12: 61,  # Light rain → Slight rain
    13: 81,  # Heavy rain shower (night) → Moderate showers
    14: 81,  # Heavy rain shower (day) → Moderate showers
    15: 65,  # Heavy rain → Heavy rain
    16: 85,  # Sleet shower (night) → Slight snow showers
    17: 85,  # Sleet shower (day) → Slight snow showers
    18: 67,  # Sleet → Heavy freezing rain
    19: 82,  # Hail shower (night) → Violent showers
    20: 82,  # Hail shower (day) → Violent showers
    21: 82,  # Hail → Violent showers
    22: 85,  # Light snow shower (night) → Slight snow showers
    23: 85,  # Light snow shower (day) → Slight snow showers
    24: 71,  # Light snow → Slight snow fall
    25: 86,  # Heavy snow shower (night) → Heavy snow showers
    26: 86,  # Heavy snow shower (day) → Heavy snow showers
    27: 75,  # Heavy snow → Heavy snow fall
    28: 95,  # Thunder shower (night) → Thunderstorm
    29: 95,  # Thunder shower (day) → Thunderstorm
    30: 95,  # Thunder → Thunderstorm
}

PROVIDERS: dict[str, dict] = {
    "ecmwf": {
        "label": "ECMWF",
        "open_meteo_model": "ecmwf_ifs025",
        "datahub": False,
    },
    "ukmo": {
        "label": "UK Met Office",
        "open_meteo_model": "ukmo_seamless",
        "datahub": True,
    },
}

METEOCON_BASE = "static/icons"
METEOCON_FILL_BASE = "static/icons-fill"
METEOCON_FLAT_BASE = "static/icons-flat"
METEOCON_MONOCHROME_BASE = "static/icons-monochrome"
MAKIN_THINGS_BASE = "static/icons-makin"

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

MAKIN_THINGS_ICONS = {
    0: ("clear-day", "clear-night"),
    1: ("cloudy-1-day", "cloudy-1-night"),
    2: ("cloudy-2-day", "cloudy-2-night"),
    3: ("cloudy-3-day", "cloudy-3-night"),
    45: ("fog-day", "fog-night"),
    48: ("fog-day", "fog-night"),
    51: ("rainy-1-day", "rainy-1-night"),
    53: ("rainy-1-day", "rainy-1-night"),
    55: ("rainy-2-day", "rainy-2-night"),
    56: ("rain-and-sleet-mix", "rain-and-sleet-mix"),
    57: ("rain-and-sleet-mix", "rain-and-sleet-mix"),
    61: ("rainy-1-day", "rainy-1-night"),
    63: ("rainy-2-day", "rainy-2-night"),
    65: ("rainy-3-day", "rainy-3-night"),
    66: ("rain-and-sleet-mix", "rain-and-sleet-mix"),
    67: ("rain-and-sleet-mix", "rain-and-sleet-mix"),
    71: ("snowy-1-day", "snowy-1-night"),
    73: ("snowy-2-day", "snowy-2-night"),
    75: ("snowy-3-day", "snowy-3-night"),
    77: ("snowy-1-day", "snowy-1-night"),
    80: ("rainy-1-day", "rainy-1-night"),
    81: ("rainy-2-day", "rainy-2-night"),
    82: ("rainy-3-day", "rainy-3-night"),
    85: ("snowy-1-day", "snowy-1-night"),
    86: ("snowy-3-day", "snowy-3-night"),
    95: ("scattered-thunderstorms-day", "scattered-thunderstorms-night"),
    96: ("severe-thunderstorm", "severe-thunderstorm"),
    99: ("severe-thunderstorm", "severe-thunderstorm"),
}

METEOCON_ICONS = {
    0: ("clear-day", "clear-night"),
    1: ("partly-cloudy-day", "partly-cloudy-night"),
    2: ("partly-cloudy-day", "partly-cloudy-night"),
    3: ("overcast-day", "overcast-night"),
    45: ("fog-day", "fog-night"),
    48: ("fog-day", "fog-night"),
    51: ("partly-cloudy-day-drizzle", "partly-cloudy-night-drizzle"),
    53: ("drizzle", "drizzle"),
    55: ("overcast-drizzle", "overcast-drizzle"),
    56: ("partly-cloudy-day-sleet", "partly-cloudy-night-sleet"),
    57: ("overcast-day-sleet", "overcast-night-sleet"),
    61: ("partly-cloudy-day-rain", "partly-cloudy-night-rain"),
    63: ("rain", "rain"),
    65: ("overcast-rain", "overcast-rain"),
    66: ("partly-cloudy-day-sleet", "partly-cloudy-night-sleet"),
    67: ("overcast-day-sleet", "overcast-night-sleet"),
    71: ("partly-cloudy-day-snow", "partly-cloudy-night-snow"),
    73: ("snow", "snow"),
    75: ("overcast-snow", "overcast-snow"),
    77: ("partly-cloudy-day-snow", "partly-cloudy-night-snow"),
    80: ("partly-cloudy-day-rain", "partly-cloudy-night-rain"),
    81: ("partly-cloudy-day-rain", "partly-cloudy-night-rain"),
    82: ("overcast-rain", "overcast-rain"),
    85: ("partly-cloudy-day-snow", "partly-cloudy-night-snow"),
    86: ("overcast-day-snow", "overcast-night-snow"),
    95: ("thunderstorms-day", "thunderstorms-night"),
    96: ("thunderstorms-day-rain", "thunderstorms-night-rain"),
    99: ("thunderstorms-day-overcast-rain", "thunderstorms-night-overcast-rain"),
}

ICON_SETS = {
    "meteocons": (METEOCON_BASE, METEOCON_ICONS),
    "meteocons-fill": (METEOCON_FILL_BASE, METEOCON_ICONS),
    "meteocons-flat": (METEOCON_FLAT_BASE, METEOCON_ICONS),
    "meteocons-monochrome": (METEOCON_MONOCHROME_BASE, METEOCON_ICONS),
    "makin-things": (MAKIN_THINGS_BASE, MAKIN_THINGS_ICONS),
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
    "ukmo_seamless": "UK Met Office",
    "ukmo_global": "UK Met Office",
    "ukmo_uk_deterministic": "UK Met Office",
    "ukmo_datahub": "Met Office DataHub",
    "ecmwf_ifs025": "ECMWF",
    "ecmwf_ifs04": "ECMWF",
    "ecmwf_aifs025": "ECMWF",
}

MODEL_URLS = {
    "UK Met Office": "https://open-meteo.com/en/docs/ukmo-api",
    "ECMWF": "https://open-meteo.com/en/docs/ecmwf-api",
    "Met Office DataHub": "https://datahub.metoffice.gov.uk",
}
