#!/usr/bin/env python3
"""Validate the FreshEye repository without third-party dependencies."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None  # type: ignore[assignment]

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "README.md",
    "SKILL.md",
    "LICENSE",
    "agents/openai.yaml",
    "codex-agents/fresheye-runner.toml",
    "codex-agents/fresheye-judge.toml",
    "personas/core.yaml",
    "personas/agent-company.yaml",
    "personas/todolist.yaml",
    "personas/lumi.yaml",
    "references/isolation.md",
    "references/scoring.md",
    "references/protocol.md",
    "schemas/manifest.schema.json",
    "schemas/runner-result.schema.json",
    "schemas/judge-result.schema.json",
    "templates/report.md",
    "examples/todolist-create-task.yaml",
    "examples/agent-company-delegate.yaml",
    "examples/lumi-purchase-decision.yaml",
)


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def validate_skill(errors: list[str]) -> None:
    path = ROOT / "SKILL.md"
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        fail(errors, "SKILL.md must start with YAML frontmatter")
        return
    try:
        _, frontmatter, body = text.split("---", 2)
    except ValueError:
        fail(errors, "SKILL.md frontmatter is not closed")
        return
    if not re.search(r"^name:\s*fresheye\s*$", frontmatter, re.MULTILINE):
        fail(errors, "SKILL.md frontmatter must define name: fresheye")
    if not re.search(r"^description:\s*\S", frontmatter, re.MULTILINE):
        fail(errors, "SKILL.md frontmatter must define a description")
    if len(body.strip()) < 500:
        fail(errors, "SKILL.md body appears unexpectedly short")


def validate_agents(errors: list[str]) -> None:
    if tomllib is None:
        fail(errors, "Python 3.11+ is required to validate TOML agent files")
        return
    expected_names = {
        "fresheye-runner.toml": "fresheye_runner",
        "fresheye-judge.toml": "fresheye_judge",
    }
    for filename, expected_name in expected_names.items():
        path = ROOT / "codex-agents" / filename
        try:
            with path.open("rb") as handle:
                data = tomllib.load(handle)
        except (OSError, tomllib.TOMLDecodeError) as exc:
            fail(errors, f"Invalid TOML {path}: {exc}")
            continue
        for field in ("name", "description", "developer_instructions"):
            if not data.get(field):
                fail(errors, f"{path} is missing {field}")
        if data.get("name") != expected_name:
            fail(errors, f"{path} name must be {expected_name}")
        if data.get("sandbox_mode") != "read-only":
            fail(errors, f"{path} must default to read-only sandbox mode")


def validate_schemas(errors: list[str]) -> None:
    for path in sorted((ROOT / "schemas").glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            fail(errors, f"Invalid JSON schema {path}: {exc}")
            continue
        if data.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            fail(errors, f"{path} must use JSON Schema draft 2020-12")
        if data.get("type") != "object":
            fail(errors, f"{path} root type must be object")


def validate_personas(errors: list[str]) -> None:
    ids: dict[str, Path] = {}
    id_pattern = re.compile(r"^\s{2}- id:\s*([a-z0-9-]+)\s*$", re.MULTILINE)
    for path in sorted((ROOT / "personas").glob("*.yaml")):
        text = path.read_text(encoding="utf-8")
        found = id_pattern.findall(text)
        if not found:
            fail(errors, f"No persona IDs found in {path}")
        for persona_id in found:
            if persona_id in ids:
                fail(errors, f"Duplicate persona id {persona_id} in {path} and {ids[persona_id]}")
            ids[persona_id] = path
    if len(ids) < 10:
        fail(errors, f"Expected at least 10 personas, found {len(ids)}")


def main() -> int:
    errors: list[str] = []

    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            fail(errors, f"Missing required file: {relative}")

    if not errors:
        validate_skill(errors)
        validate_agents(errors)
        validate_schemas(errors)
        validate_personas(errors)

    if errors:
        print("FreshEye lint failed:", file=sys.stderr)
        for item in errors:
            print(f"- {item}", file=sys.stderr)
        return 1

    print("FreshEye lint passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
