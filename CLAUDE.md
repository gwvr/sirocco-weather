# CLAUDE.md — Project Context for AI-Assisted Development

## 1. Project Overview

**Weather** is a work-in-progress Python application for fetching and displaying weather data.

- **Status:** Early development / work in progress
- **Entry point:** `main.py`
- **Package name:** `weather` (see `pyproject.toml`)
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
`uv run main.py`

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

## 5. API & Config Notes

> _To be filled in once external APIs or configuration are introduced._

- [ ] Weather API provider (e.g. OpenWeatherMap, Open-Meteo, etc.)
- [ ] API key management (environment variables, `.env` file, etc.)
- [ ] Config file format and location
- [ ] Any rate limits or usage notes
