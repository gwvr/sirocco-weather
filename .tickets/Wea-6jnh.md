---
id: Wea-6jnh
status: closed
deps: []
links: []
created: 2026-04-06T20:29:18Z
type: feature
priority: 2
assignee: Giles Weaver
external-ref: Weather-5wh
---
# Improve mobile layout responsiveness

Several layout issues on narrow screens: (1) Daily strip — 7 cards in a row become unreadable on phones, needs horizontal scroll or wrapping; (2) Summary panel — flex row doesn't stack on narrow screens, sunrise/sunset/UV details need to wrap; (3) Touch targets on day cards and theme toggle are too small. Hourly table already handles mobile well via overflow-x:auto. Needs media queries for ~480px and below.

