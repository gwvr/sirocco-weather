---
id: Wea-xpfi
status: closed
deps: []
links: []
created: 2026-04-06T20:29:20Z
type: bug
priority: 3
assignee: Giles Weaver
external-ref: Weather-nbk
---
# Hourly table content peeks left of sticky row labels when scrolled

When scrolling the hourly forecast panel to the end of the day, a sliver of content is visible to the left of the sticky row label column. Fix: add overflow: hidden to .hourly-panel and increase z-index on sticky cells.

