# Data Sources

This document describes the APIs used to build Sirocco forecasts, which forecast components each provides, and why.

---

## Provider modes

The active provider is set via `provider:` in `location.yaml` or the `--provider` CLI flag. Three modes exist:

| Mode | Key | Requires |
|---|---|---|
| Met Office (DataHub) | `ukmo` | `MET_OFFICE_API_KEY` env var |
| ECMWF | `ecmwf` | — |
| Legacy | _(no provider key)_ | `model:` in `location.yaml` |

---

## 1. `ukmo` — Met Office DataHub + Open-Meteo

The primary production mode. Two APIs are combined: DataHub for display-quality hourly data, Open-Meteo for the daily structural frame.

### Met Office DataHub (site-specific endpoint)

**Endpoint:** `https://data.hub.api.metoffice.gov.uk/sitespecific/v0/point/`
**Model:** UK Deterministic (UKV), ~1.5 km resolution
**Coverage:** UK only

The site-specific endpoint returns point forecasts interpolated to the requested lat/lon from the UKV model — the same source used by the Met Office website.

Two sub-endpoints are used:

| Endpoint | Horizon | Step | Used for |
|---|---|---|---|
| `/hourly` | ~2 days | 1 h | Days 1–2 hourly display data |
| `/three-hourly` | ~7 days | 3 h | Days 3–7 display data |

**Provides (days 1–2, hourly):**
- Screen temperature (`screenTemperature`)
- Feels-like temperature (`feelsLikeTemperature`)
- Wind speed, direction, gusts
- Relative humidity
- UV index
- Precipitation probability
- Weather code (mapped from DataHub codes to WMO via `DATAHUB_CODE_TO_WMO`)

**Provides (days 3–7, three-hourly):**
- Temperature (averaged from `maxScreenAirTemp` / `minScreenAirTemp` per slot — see known limitation below)
- Feels-like temperature
- Wind speed, direction, gusts
- Precipitation probability
- Weather code

### Open-Meteo (ukmo_seamless)

**Endpoint:** `https://api.open-meteo.com/v1/forecast`
**Model:** `ukmo_seamless` — UKMO global seamless, ~10 km resolution
**Coverage:** Global

Used purely for the daily structural frame that drives the day cards. DataHub does not expose daily aggregates directly.

**Provides (all days):**
- Daily max/min temperature ⚠️ _(see known limitation below)_
- Daily precipitation sum
- Daily max precipitation probability
- Daily max wind speed
- Daily max UV index
- Sunrise / sunset times
- Daily weather code (for day-card icon)

### Known limitation — daily max/min temperatures (Wea-d6hm)

Daily high/low temperatures on the day cards currently come from Open-Meteo `ukmo_seamless` (global, ~10 km), **not** from DataHub UKV. This is why day-card temperatures can be slightly lower than the Met Office website, which derives its daily max/min from the UKV model.

The fix (tracked in `Wea-d6hm`) is to derive daily max/min directly from DataHub data:
- Days 1–2: `max/min(screenTemperature)` across the day's hourly DataHub entries
- Days 3–7: `maxScreenAirTemp` / `minScreenAirTemp` from the three-hourly entries

---

## 2. `ecmwf` — Open-Meteo / ECMWF IFS

A fully Open-Meteo path requiring no API key.

**Model:** `ecmwf_ifs025` — ECMWF IFS, ~25 km resolution
**Coverage:** Global

All forecast variables — both hourly and daily — come from a single Open-Meteo fetch.

**Provides:**
- All hourly display variables (temperature, feels-like, wind, humidity, UV, precipitation probability, weather code)
- All daily aggregates (max/min temperature, precipitation sum, wind max, UV max, sunrise/sunset, weather code)

No DataHub overlay is applied in this mode.

---

## 3. Legacy path (no provider key)

Used when `location.yaml` has a `model:` key but no `provider:` key. This pre-dates the named provider system and will be consolidated into the provider model in future.

**Model:** whatever `model:` is set to in `location.yaml` (e.g. `ukmo_seamless`, `ecmwf_ifs025`)
**Source:** Open-Meteo only

If `MET_OFFICE_API_KEY` is available, a DataHub precipitation probability overlay is applied on top of the Open-Meteo data (hourly for days 1–2, three-hourly for days 3–7). All other variables remain Open-Meteo sourced.

---

## Pollen (all modes)

**Source:** Open-Meteo CAMS (Copernicus Atmosphere Monitoring Service)
**Coverage:** Europe
**Species:** alder, birch, grass, mugwort, olive, ragweed

Fetched independently of the weather provider. Can be disabled per-location with `pollen: false` in `location.yaml`. Pollen data drives the daily pollen severity indicator in the summary panel.

---

## Summary table

| Forecast component | `ukmo` source | `ecmwf` source | Legacy source |
|---|---|---|---|
| Hourly temperature (days 1–2) | DataHub UKV `/hourly` | Open-Meteo ECMWF | Open-Meteo (model) |
| Hourly temperature (days 3–7) | DataHub UKV `/three-hourly` | Open-Meteo ECMWF | Open-Meteo (model) |
| Hourly wind / humidity / UV (days 1–2) | DataHub UKV `/hourly` | Open-Meteo ECMWF | Open-Meteo (model) |
| Hourly wind / humidity / UV (days 3–7) | DataHub UKV `/three-hourly` | Open-Meteo ECMWF | Open-Meteo (model) |
| Hourly precipitation probability (days 1–2) | DataHub UKV `/hourly` | Open-Meteo ECMWF | DataHub overlay (if key set) |
| Hourly precipitation probability (days 3–7) | DataHub UKV `/three-hourly` | Open-Meteo ECMWF | DataHub overlay (if key set) |
| Daily max/min temperature ⚠️ | Open-Meteo `ukmo_seamless` | Open-Meteo ECMWF | Open-Meteo (model) |
| Daily precipitation sum | Open-Meteo `ukmo_seamless` | Open-Meteo ECMWF | Open-Meteo (model) |
| Daily max wind / UV / precip prob | Open-Meteo `ukmo_seamless` | Open-Meteo ECMWF | Open-Meteo (model) |
| Sunrise / sunset | Open-Meteo `ukmo_seamless` | Open-Meteo ECMWF | Open-Meteo (model) |
| Pollen severity | Open-Meteo CAMS | Open-Meteo CAMS | Open-Meteo CAMS |

⚠️ Known limitation — see Wea-d6hm.
