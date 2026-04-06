---
id: Wea-bt93
status: closed
deps: []
links: []
created: 2026-04-06T20:29:18Z
type: task
priority: 3
assignee: Giles Weaver
external-ref: Weather-8ry
---
# Move tests to tests/ directory

Move test_main.py to tests/ and split or rename appropriately (e.g. tests/test_render.py, tests/test_cli.py). Add testpaths = ['tests'] to pyproject.toml so pytest doesn't scan the whole repo.

