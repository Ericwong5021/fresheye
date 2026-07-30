#!/usr/bin/env python3
"""Diagnose a FreshEye Codex installation using only the Python standard library."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any

REQUIRED_AGENT_FIELDS = ("name", "description", "developer_instructions")
AGENT_FILES = ("fresheye-runner.toml", "fresheye-judge.toml")

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:  # pragma: no cover - older Python
    tomllib = None  # type: ignore[assignment]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check FreshEye installation")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    parser.add_argument(
        "--project-dir",
        type=Path,
        default=Path.cwd(),
        help="Project directory to inspect for project-scoped installation",
    )
    return parser.parse_args()


def inspect_agent(path: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "path": str(path),
        "exists": path.is_file(),
        "valid": False,
        "missing_fields": [],
    }
    if not path.is_file():
        return result
    if tomllib is None:
        result["valid"] = None
        result["note"] = "Python < 3.11: TOML syntax not parsed"
        return result
    try:
        with path.open("rb") as handle:
            data = tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        result["error"] = str(exc)
        return result
    missing = [field for field in REQUIRED_AGENT_FIELDS if not data.get(field)]
    result["missing_fields"] = missing
    result["valid"] = not missing
    result["name"] = data.get("name")
    result["sandbox_mode"] = data.get("sandbox_mode")
    result["reasoning_effort"] = data.get("model_reasoning_effort")
    return result


def main() -> int:
    args = parse_args()
    project_root = args.project_dir.expanduser().resolve()
    source_root = Path(__file__).resolve().parents[1]

    user_skill = Path.home() / ".agents" / "skills" / "fresheye"
    project_skill = project_root / ".agents" / "skills" / "fresheye"
    user_agents = Path.home() / ".codex" / "agents"
    project_agents = project_root / ".codex" / "agents"

    skill_candidates = [source_root, user_skill, project_skill]
    discovered_skills = [
        {
            "path": str(path),
            "skill_md": (path / "SKILL.md").is_file(),
            "source_checkout": path == source_root,
        }
        for path in skill_candidates
        if path.exists()
    ]

    agent_results = []
    for directory, scope in ((user_agents, "user"), (project_agents, "project")):
        for filename in AGENT_FILES:
            result = inspect_agent(directory / filename)
            result["scope"] = scope
            result["file"] = filename
            agent_results.append(result)

    runner_found = any(
        item.get("exists") and item.get("file") == "fresheye-runner.toml"
        for item in agent_results
    )
    judge_found = any(
        item.get("exists") and item.get("file") == "fresheye-judge.toml"
        for item in agent_results
    )
    skill_found = any(item["skill_md"] for item in discovered_skills)

    status = {
        "python": {
            "version": sys.version.split()[0],
            "tomllib_available": tomllib is not None,
        },
        "codex_cli": {
            "path": shutil.which("codex"),
            "detected": shutil.which("codex") is not None,
        },
        "skills": discovered_skills,
        "agents": agent_results,
        "checks": {
            "skill_found": skill_found,
            "runner_found": runner_found,
            "judge_found": judge_found,
            "browser_or_computer_use": "must be verified inside the Codex host",
            "fresh_browser_profile": "must be verified for each live run",
        },
        "maximum_confirmed_isolation": "L1" if skill_found and runner_found and judge_found else "L0",
        "note": (
            "Doctor can verify local files, not runtime tool availability or fresh browser state. "
            "A live run may reach L2 or L3 only after those controls are verified."
        ),
    }

    success = skill_found and runner_found and judge_found

    if args.json:
        print(json.dumps(status, indent=2, ensure_ascii=False))
    else:
        print("FreshEye doctor")
        print("================")
        print(f"Python:      {status['python']['version']}")
        print(f"Codex CLI:   {status['codex_cli']['path'] or 'not detected'}")
        print(f"Skill:       {'ok' if skill_found else 'missing'}")
        print(f"Runner:      {'ok' if runner_found else 'missing'}")
        print(f"Judge:       {'ok' if judge_found else 'missing'}")
        print(f"Confirmed:   {status['maximum_confirmed_isolation']}")
        print("Browser:     verify Browser or Computer Use inside Codex")
        print("Fresh state: verify a new browser profile/context for each repetition")
        if not success:
            print("\nRun scripts/install.py --scope user --force from the FreshEye checkout.")

    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
