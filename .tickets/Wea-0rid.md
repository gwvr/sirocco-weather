---
id: Wea-0rid
status: open
deps: []
links: []
created: 2026-04-06T20:29:18Z
type: bug
priority: 2
assignee: Giles Weaver
external-ref: Weather-3hz
---
# Daily weather symbol too pessimistic vs Met Office

Open-Meteo's daily weather_code is the most severe condition across the full 24 hours (e.g. 3am fog counts). The Met Office website shows a representative daytime symbol. Fix: derive the daily card symbol from daytime hourly weather_code values (between sunrise and sunset) instead of using Open-Meteo's daily weather_code directly.

