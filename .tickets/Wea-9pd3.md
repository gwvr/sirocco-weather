---
id: Wea-9pd3
status: closed
deps: []
links: []
created: 2026-04-06T20:29:19Z
type: task
priority: 3
assignee: Giles Weaver
external-ref: Weather-bro
---
# Improve test suite coverage

Many functions have zero test coverage: temp_color, uv_color, wind_compass, weather_icon_html, model_label, load_config. Also build_html is only tested with minimal 1-day data — no hourly data, no Meteocons, no wind_units variation. Priority areas: pure functions (easy/fast), then hourly HTML rendering, then fetch mocking.

