#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
ASSETS_DIR = SKILL_ROOT / "assets"


def run(command: list[str], cwd: Path) -> None:
    print(f"+ {subprocess.list2cmdline(command)}", flush=True)
    subprocess.run(command, cwd=cwd, check=True)


def normalize_module_name(name: str) -> str:
    module_name = re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_").lower()
    if not module_name:
        raise ValueError("Project name must contain at least one letter or digit.")
    if module_name[0].isdigit():
        raise ValueError("Project name cannot start with a digit after normalization.")
    return module_name


def build_gitignore() -> str:
    base_lines = (ASSETS_DIR / "Python.gitignore").read_text(encoding="utf-8").rstrip().splitlines()
    for extra_line in (".env", "config.json"):
        if extra_line not in base_lines:
            base_lines.append(extra_line)
    return "\n".join(base_lines) + "\n"


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def smoke_test_content(module_name: str) -> str:
    return (
        "import importlib\n\n\n"
        f"def test_package_imports() -> None:\n"
        f"    importlib.import_module(\"{module_name}\")\n"
    )


def bootstrap_repo(target_dir: Path, project_name: str) -> None:
    if target_dir.exists() and any(target_dir.iterdir()):
        raise SystemExit(f"Target directory must be empty: {target_dir}")

    normalize_module_name(project_name)
    target_dir.parent.mkdir(parents=True, exist_ok=True)

    run(
        [
            "uv",
            "init",
            "--package",
            "--vcs",
            "git",
            "--name",
            project_name,
            str(target_dir),
        ],
        cwd=target_dir.parent,
    )
    module_name = normalize_module_name(project_name)

    run(["uv", "add", "--dev", "ruff", "pyrefly", "pytest", "prek"], cwd=target_dir)
    run(
        ["uv", "run", "pyrefly", "init", "pyproject.toml", "--non-interactive"],
        cwd=target_dir,
    )

    write_file(target_dir / ".gitignore", build_gitignore())
    write_file(
        target_dir / ".pre-commit-config.yaml",
        (ASSETS_DIR / ".pre-commit-config.yaml").read_text(encoding="utf-8"),
    )
    write_file(target_dir / "AGENTS.md", (ASSETS_DIR / "AGENTS.md").read_text(encoding="utf-8"))
    write_file(target_dir / "tests" / "test_smoke.py", smoke_test_content(module_name))

    run(["uv", "run", "prek", "install"], cwd=target_dir)
    run(["uv", "run", "ruff", "check", ".", "--fix"], cwd=target_dir)
    run(["uv", "run", "pyrefly", "check", "."], cwd=target_dir)
    run(["uv", "run", "pytest"], cwd=target_dir)
    run(["uv", "run", "prek", "run", "--all-files"], cwd=target_dir)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Initialize a new uv-based Python repository with local quality gates.",
    )
    parser.add_argument("target_dir", help="Path to the new repository directory")
    parser.add_argument(
        "--name",
        help="Project name for uv init; defaults to the target directory name",
    )
    args = parser.parse_args()

    target_dir = Path(args.target_dir).resolve()
    project_name = args.name or target_dir.name

    try:
        bootstrap_repo(target_dir, project_name)
    except subprocess.CalledProcessError as exc:
        return exc.returncode
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 1

    print(f"Initialized repository at {target_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
