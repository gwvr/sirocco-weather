---
id: Wea-chcm
status: open
deps: []
links: []
created: 2026-04-06T20:29:17Z
type: bug
priority: 2
assignee: Giles Weaver
external-ref: Weather-1hb
---
# Investigate temperature discrepancy vs Met Office website

Temperatures shown (both summary panel and daily cards) are consistently lower than the Met Office website for Harpenden. Likely cause: Open-Meteo's ukmo_seamless is the UKMO global model (~10km resolution), whereas the Met Office website uses the high-resolution UKV model (~1.5km). Options to explore: (1) compare ECMWF IFS model output, (2) add a disclaimer about data source differences, (3) investigate whether any Open-Meteo model is closer to Met Office UKV output.

