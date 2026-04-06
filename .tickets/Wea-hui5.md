---
id: Wea-hui5
status: closed
deps: []
links: []
created: 2026-04-06T20:29:18Z
type: bug
priority: 2
assignee: Giles Weaver
external-ref: Weather-6ft
---
# Handle None/unknown WMO weather codes in daily strip

The last day of the forecast sometimes has a None or unrecognised WMO weather code, causing the fallback thermometer emoji/icon to appear in the daily strip. Should investigate what code the API returns and handle None gracefully (skip icon, show placeholder, or omit the card).

