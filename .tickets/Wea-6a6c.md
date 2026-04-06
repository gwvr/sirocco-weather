---
id: Wea-6a6c
status: closed
deps: []
links: []
created: 2026-04-06T20:29:19Z
type: task
priority: 3
assignee: Giles Weaver
external-ref: Weather-fho
---
# Move all hardcoded colours from Python into CSS

Currently colours live in three places in main.py: (1) temp_color() returns one of 11 hex values directly — could become CSS classes (e.g. .tc-0 through .tc-10); (2) uv_color() computes a blended RGB value from 5 base colours — pre-compute the blended values and use CSS classes instead; (3) inline color:#222 hardcoded in generated <td> style attributes (lines 313-314, 324) — could be a CSS class; (4) the entire CSS block is embedded in a Python f-string (lines 356-371) — could move to a static .css file. Goal: Python emits class names only, all colour values live in CSS.

