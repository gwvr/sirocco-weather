---
id: Wea-jhvj
status: closed
deps: []
links: []
created: 2026-04-06T20:29:19Z
type: task
priority: 2
assignee: Giles Weaver
external-ref: Weather-kly
---
# Restructure as src-layout package

Move code from main.py into a src/sirocco/ package (src layout). Split into config.py, api.py, render.py, cli.py. Keep main.py as a thin entry point for uv run main.py compatibility. Move templates/ into src/sirocco/templates/. Update pyproject.toml build config and pytest coverage settings.

