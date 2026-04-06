---
id: Wea-hx14
status: closed
deps: []
links: []
created: 2026-04-06T20:29:18Z
type: bug
priority: 1
assignee: Giles Weaver
external-ref: Weather-6g2
---
# Precipitation not shown in hourly panel — MET Office shows rain Mon 23 Mar

UKMO model doesn't provide hourly precipitation_probability. Fix: add optional precip_model field to location.yaml. When set, make a secondary Open-Meteo API call to fetch precipitation_probability from that model (e.g. ecmwf_ifs025) and display it in the hourly panel alongside UKMO data.

