---
id: Wea-ut88
status: closed
deps: []
links: []
created: 2026-04-06T20:29:20Z
type: task
priority: 2
assignee: Giles Weaver
external-ref: Weather-wmz
---
# Add GitHub Actions workflow for deployment

Set up GitHub Actions to run uv run main.py on a schedule and deploy forecast.html to GitHub Pages. Should also run uv run pytest on push/PR. Jinja2 template is already committed so uv sync will pull everything needed.

