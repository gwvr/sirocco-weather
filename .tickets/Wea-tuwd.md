---
id: Wea-tuwd
status: closed
deps: []
links: []
created: 2026-04-06T20:29:20Z
type: task
priority: 3
assignee: Giles Weaver
external-ref: Weather-kxp
---
# Replace main.py entry point with console script

Now that pyproject.toml has a [project.scripts] sirocco entry point, update GitHub Actions workflows and CLAUDE.md to use 'uv run sirocco' instead of 'uv run main.py', then delete main.py.

