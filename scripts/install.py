#!/usr/bin/env python3
"""Install FreshEye as a user- or project-scoped Codex Skill.

The script copies the Skill into Codex's .agents/skills location and installs
FreshEye's two custom subagent definitions into .codex/agents.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

SKILL_NAME = "fresheye"
AGENT_FILES = ("fresheye-runner.toml", "fresheye-judge.toml")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Install FreshEye for Codex")
    parser.add_argument(
        "--scope",
        choices=("user", "project"),
        default="user",
        help="Install globally for the user or into one project (default: user)",
    )
    parser.add_argument(
        "--project-dir",
        type=Path,
        help="Project root used with --scope project (default: current directory)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace an existing installation",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned operations without changing files",
    )
    return parser.parse_args()


def remove_existing(path: Path, *, force: bool, dry_run: bool) -> None:
    if not path.exists() and not path.is_symlink():
        return
    if not force:
        raise FileExistsError(
            f"Destination already exists: {path}. Re-run with --force to replace it."
        )
    print(f"replace: {path}")
    if dry_run:
        return
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    else:
        path.unlink()


def copy_skill(source: Path, destination: Path, *, force: bool, dry_run: bool) -> None:
    try:
        if source.resolve() == destination.resolve():
            print(f"skill already at destination: {destination}")
            return
    except FileNotFoundError:
        pass

    remove_existing(destination, force=force, dry_run=dry_run)
    print(f"copy skill: {source} -> {destination}")
    if dry_run:
        return

    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        source,
        destination,
        ignore=shutil.ignore_patterns(
            ".git",
            ".github",
            ".fresheye",
            "__pycache__",
            "*.pyc",
        ),
    )


def copy_agent(source: Path, destination: Path, *, force: bool, dry_run: bool) -> None:
    if destination.exists() and not force:
        raise FileExistsError(
            f"Agent already exists: {destination}. Re-run with --force to replace it."
        )
    print(f"copy agent: {source} -> {destination}")
    if dry_run:
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def main() -> int:
    args = parse_args()
    source_root = Path(__file__).resolve().parents[1]

    if not (source_root / "SKILL.md").is_file():
        print(f"error: SKILL.md not found under {source_root}", file=sys.stderr)
        return 2

    if args.scope == "user":
        skill_destination = Path.home() / ".agents" / "skills" / SKILL_NAME
        agent_directory = Path.home() / ".codex" / "agents"
    else:
        project_root = (args.project_dir or Path.cwd()).expanduser().resolve()
        skill_destination = project_root / ".agents" / "skills" / SKILL_NAME
        agent_directory = project_root / ".codex" / "agents"

    try:
        copy_skill(
            source_root,
            skill_destination,
            force=args.force,
            dry_run=args.dry_run,
        )
        for filename in AGENT_FILES:
            source = source_root / "codex-agents" / filename
            if not source.is_file():
                raise FileNotFoundError(f"Missing agent definition: {source}")
            copy_agent(
                source,
                agent_directory / filename,
                force=args.force,
                dry_run=args.dry_run,
            )
    except (FileExistsError, FileNotFoundError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print("\nFreshEye installation complete.")
    print(f"Skill:  {skill_destination}")
    print(f"Agents: {agent_directory}")
    print("Restart Codex if the Skill or custom agents are not detected immediately.")
    print(f"Then run: python {skill_destination / 'scripts' / 'doctor.py'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
