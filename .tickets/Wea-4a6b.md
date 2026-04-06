---
id: Wea-4a6b
status: closed
deps: []
links: []
created: 2026-04-06T20:29:20Z
type: bug
priority: 3
assignee: Giles Weaver
external-ref: Weather-wbv
---
# Daily strip overflows viewport width on mobile

The day selector strip scrolls left and right slightly on mobile due to min-width on day cards pushing total width over the viewport. Fix: remove min-width and let flex: 1 fill naturally.

