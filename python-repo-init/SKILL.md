---
name: python-repo-init
description: Initialize or standardize a Python repository around uv. Use when Codex needs to create a new Python repo with `uv init`, add Ruff, Pyrefly, pytest, and prek, install pre-commit hooks, copy the GitHub Python `.gitignore` sample plus `config.json`, and add an `AGENTS.md` policy that requires `uv run ruff check . --fix`, `uv run pyrefly check .`, and `uv run pytest` before source-file changes are considered complete.
---

# Python Repo Init

## Overview

Create a fresh uv-based Python repository with consistent local quality gates.
Use the bootstrap script for new repos. For existing repos, apply the same files and commands manually instead of re-running `uv init`.

## Quick Start

Run `scripts/bootstrap_repo.py <target-dir>` for a fresh repo.

Example:

```powershell
python scripts\bootstrap_repo.py D:\Projects\example-repo
```

The script:

1. Runs `uv init --package --vcs git`
2. Adds `ruff`, `pyrefly`, `pytest`, and `prek` as dev dependencies with uv
3. Runs `uv run pyrefly init pyproject.toml --non-interactive`
4. Writes `.gitignore`, `.pre-commit-config.yaml`, `AGENTS.md`, and a smoke test
5. Installs prek hooks
6. Verifies `uv run ruff check . --fix`, `uv run pyrefly check .`, `uv run pytest`, and `uv run prek run --all-files`

## Workflow

### Fresh Repo

Use `scripts/bootstrap_repo.py`.
Pass `--name <project-name>` when the package name should not come from the directory name.

### Existing Repo

Do not run the bootstrap script against a non-empty repo.
Instead:

1. Ensure the project already uses uv or migrate it first.
2. Run `uv add --dev ruff pyrefly pytest prek`.
3. Run `uv run pyrefly init pyproject.toml --non-interactive`.
4. Replace `.gitignore` with the bundled GitHub Python template plus `config.json`.
5. Add `AGENTS.md` and `.pre-commit-config.yaml` from `assets/`.
6. Run `uv run prek install`.
7. Verify `uv run ruff check . --fix`, `uv run pyrefly check .`, `uv run pytest`, and `uv run prek run --all-files`.

## Assets

Read `assets/Python.gitignore` when regenerating `.gitignore`.
Copy `assets/AGENTS.md` and `assets/.pre-commit-config.yaml` into the target repo unless the user asks for a different policy.

## Notes

Keep tool execution behind `uv run ...`.
Keep the repo package-oriented by using `uv init --package` unless the user explicitly asks for a script-only project.
