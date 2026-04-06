# CLAUDE.md — Project Context for AI-Assisted Development

## 1. Project Overview

**Sirocco** is a work-in-progress Python application for fetching and displaying weather data.

- **Status:** Early development / work in progress
- **Entry point:** `uv run sirocco` (console script)
- **Package name:** `sirocco-weather` (see `pyproject.toml`)
- **Version:** `0.1.0`

---

## 2. Environment & Editor

| Item        | Detail              |
|-------------|---------------------|
| OS          | Linux               |
| Editor      | Zed                 |
| Python      | 3.13                |
| Package mgr | `uv`                |

The Python version is pinned in `.python-version`. Dependencies are declared in `pyproject.toml` and managed exclusively with `uv` — do **not** use `pip` directly.

---

## 3. Common Commands

### Run the app
`uv run sirocco`

### Add a dependency
`uv add <package>`

### Remove a dependency
`uv remove <package>`

### Sync the environment (install all deps)
`uv sync`

### Run a one-off command in the project environment
`uv run <command>`

---

## 4. Coding Conventions

> _To be filled in as the project matures._

- [ ] Style guide / formatter (e.g. `ruff`, `black`)
- [ ] Linting rules
- [ ] Type annotation policy
- [ ] Naming conventions
- [ ] File/module structure

---

## 5. Git Workflow

This project uses a **branch-per-issue** workflow. Each tk ticket gets its own branch, merged back to `main` after visual approval of `forecast.html`.

### Branch naming

| Issue type | Prefix | Example |
|---|---|---|
| bug, chore | `fix/` | `fix/Wea-abc` |
| feature, task, epic | `feat/` | `feat/Wea-abc` |

The tk ticket ID is the branch slug.

### Starting work on an issue

```bash
git checkout -b fix/Wea-xyz   # create branch first
tk start Wea-xyz              # then mark in progress
```

### Commit message format

Include the tk ticket ID in parentheses at the end:

```
fix: short description of what changed (Wea-xyz)
```

### Signalling readiness for review

```bash
uv run pytest        # must pass
uv run sirocco       # regenerate forecast.html
```

Then tell the user to open `forecast.html` in their browser and **wait for approval** before merging.

### Merging after approval

```bash
git checkout main
git merge --no-ff fix/Wea-xyz -m "Merge fix/Wea-xyz: brief description of what was fixed and how"
git branch -d fix/Wea-xyz
tk close Wea-xyz
```

The merge message should summarise the issue and solution in 1–2 sentences, so `git log --oneline` is informative without digging into individual commits.

### If changes are requested after review

Switch back to the branch, fix, regenerate, and ask for re-review:

```bash
git checkout fix/Wea-xyz
# ... make changes ...
uv run sirocco && uv run pytest
git commit -m "fix: address feedback (Wea-xyz)"
# then signal for review again
```

---

## 6. Issue Tracking (tk)

@AGENTS.md

---

## 7. API & Config Notes

> _To be filled in once external APIs or configuration are introduced._

- [ ] Weather API provider (e.g. OpenWeatherMap, Open-Meteo, etc.)
- [ ] API key management (environment variables, `.env` file, etc.)
- [ ] Config file format and location
- [ ] Any rate limits or usage notes


## Issue Tracker (tk)

This project uses **tk** for issue tracking. Tickets are markdown files in `.tickets/`.

### Quick Reference

```bash
tk ready              # Find available work
tk show <id>          # View issue details
tk start <id>         # Claim/start work
tk close <id>         # Complete work
```

### Rules

- Use `tk` for ALL task tracking — do NOT use TodoWrite, TaskCreate, or markdown TODO lists
- Do NOT use beads (`bd`) — it has been retired
