# Sirocco weather — it's a lot of hot air

A clean, fast, self-contained weather forecast page. No cookie banners. No upsells. No app. Just the forecast.

Built as a direct response to the creeping enshittification of the Met Office and BBC weather apps.

Vibe-coded with [Claude](https://claude.ai) and tracked with [Beads](https://beads.sh).

**[Live forecast →](https://gwvr.github.io/sirocco-weather/)**

---

## What it does

Fetches a 6-day forecast from [Open-Meteo](https://open-meteo.com/) and generates a single self-contained `forecast.html` file you can open in any browser. Deployed automatically to GitHub Pages every hour.

- Daily summary with weather icon, temperature range, sunrise/sunset, and UV index
- Hourly breakdown: symbol, precipitation probability, temperature, feels-like, wind direction/speed/gusts, humidity, UV
- Dark/light mode toggle (respects system preference)
- No JavaScript frameworks, no external dependencies at runtime

---

## Running locally

Requires Python 3.13+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/gwvr/sirocco-weather.git
cd sirocco-weather
uv run sirocco
```

Open `forecast.html` in your browser.

---

## Configuration

Create a `location.yaml` to set your location and preferred options:

```yaml
default: home

locations:
  home:
    name: Harpenden, UK
    lat: 51.81684
    lon: -0.35706
    timezone: Europe/London
    model: ukmo_seamless        # optional: weather model
    wind_units: mph             # optional: mph or kmh (default: kmh)
    precip_model: ecmwf_ifs025  # optional: secondary model for precipitation
```

Multiple locations are supported. Switch between them with `--location`:

```bash
uv run sirocco --location london
```

Or pass coordinates directly without a config file:

```bash
uv run sirocco --lat 51.5074 --lon -0.1278 --name "London, UK"
```

### Weather models

Open-Meteo supports several forecast models. Notable options:

| Model | Key |
|-------|-----|
| UK Met Office (default for UK) | `ukmo_seamless` |
| ECMWF IFS | `ecmwf_ifs025` |
| Default (ECMWF) | _(omit `model`)_ |

---

## Development

```bash
uv run pytest       # run tests
uv run sirocco      # regenerate forecast.html
```

After cloning, install the pre-commit hook to catch lint errors before commit:

```bash
uvx pre-commit install
```

---

## Credits

- **Weather data:** [Open-Meteo](https://open-meteo.com/) (free, open-source weather API)
- **Weather icons:** [Meteocons](https://meteocons.com/) by Bas Milius (MIT License)

