# Agent Instructions

This project uses **tk** for issue tracking. Tickets are markdown files in `.tickets/`.

## Quick Reference

```bash
tk ready              # Find available work
tk show <id>          # View issue details
tk start <id>         # Claim/start work
tk close <id>         # Complete work
```

## Non-Interactive Shell Commands

**ALWAYS use non-interactive flags** with file operations to avoid hanging on confirmation prompts.

Shell commands like `cp`, `mv`, and `rm` may be aliased to include `-i` (interactive) mode on some systems, causing the agent to hang indefinitely waiting for y/n input.

**Use these forms instead:**
```bash
# Force overwrite without prompting
cp -f source dest           # NOT: cp source dest
mv -f source dest           # NOT: mv source dest
rm -f file                  # NOT: rm file

# For recursive operations
rm -rf directory            # NOT: rm -r directory
cp -rf source dest          # NOT: cp -r source dest
```

**Other commands that may prompt:**
- `scp` - use `-o BatchMode=yes` for non-interactive
- `ssh` - use `-o BatchMode=yes` to fail instead of prompting
- `apt-get` - use `-y` flag
- `brew` - use `HOMEBREW_NO_AUTO_UPDATE=1` env var

## Issue Tracking with tk

**IMPORTANT**: This project uses **tk** for ALL issue tracking. Do NOT use markdown TODOs, task lists, or other tracking methods.

### Quick Start

**Check for ready work:**

```bash
tk ready
```

**Create new issues:**

```bash
tk create "Issue title" -t bug|feature|task|epic|chore -p 0-4 -d "Detailed context"
```

**Start and complete work:**

```bash
tk start <id>
tk close <id>
```

### Issue Types

- `bug` - Something broken
- `feature` - New functionality
- `task` - Work item (tests, docs, refactoring)
- `epic` - Large feature with subtasks
- `chore` - Maintenance (dependencies, tooling)

### Priorities

- `0` - Critical (security, data loss, broken builds)
- `1` - High (major features, important bugs)
- `2` - Medium (default, nice-to-have)
- `3` - Low (polish, optimization)
- `4` - Backlog (future ideas)

### Workflow for AI Agents

1. **Check ready work**: `tk ready` shows unblocked issues
2. **Create branch**: `git checkout -b fix/Wea-xyz` (use `feat/` for features/tasks)
3. **Start ticket**: `tk start Wea-xyz`
4. **Implement and test**: Make changes, run `uv run pytest`
5. **Discover new work?** Create a linked ticket before continuing
6. **Generate output**: `uv run sirocco` to produce `forecast.html`
7. **Signal for review**: Tell the user to open `forecast.html` in their browser and **wait for approval**
8. **After approval — merge and close**:
   ```bash
   git checkout main
   git merge --no-ff fix/Wea-xyz -m "Merge fix/Wea-xyz: brief description"
   git branch -d fix/Wea-xyz
   tk close Wea-xyz
   ```

### Important Rules

- ✅ Use tk for ALL task tracking
- ✅ Check `tk ready` before asking "what should I work on?"
- ✅ Create a ticket before starting any work item
- ❌ Do NOT create markdown TODO lists
- ❌ Do NOT use beads (`bd`) — it has been retired

## Landing the Plane (Session Completion)

**When ending a work session**, complete ALL steps below.

**MANDATORY WORKFLOW:**

1. **File issues for remaining work** — Create tk tickets for anything that needs follow-up
2. **Run quality gates** (if code changed):
   ```bash
   uv run pytest
   ```
3. **Commit all work** — Ensure the current branch is clean
4. **If mid-branch (not yet merged)**: Leave the branch in place; note the branch name and ticket ID in handoff
5. **Push to remote** (only if a remote is configured):
   ```bash
   git remote | grep -q . && git push || echo "No remote configured — skipping push"
   ```
6. **Hand off** — State current branch, ticket ID, and what still needs doing

**CRITICAL RULES:**
- NEVER merge without user approval of `forecast.html`
- NEVER fast-forward merge — always use `--no-ff`
- NEVER close a tk ticket before the branch is merged and deleted
- If mid-issue at session end, leave the branch intact — do not abandon work on `main`
