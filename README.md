# FreshEye

[简体中文](./README.zh-CN.md)

**Persona-driven blind usability testing for Codex.**

FreshEye asks a simple question traditional software testing often misses:

> Can a target user who knows nothing about the implementation understand the interface and complete the task?

FreshEye is an experimental Codex Skill that launches isolated subagents as synthetic users, drives the product only through visible UI interactions, records evidence, audits context contamination, and asks a separate judge subagent to score the experience.

## Why FreshEye

Functional tests verify that software behaves as designed. FreshEye evaluates whether people can discover how the software works without access to source code, product requirements, intended interaction paths, or developer context.

The core idea is **epistemic isolation**:

- the developer agent may know the code and design intent;
- the runner subagent receives only a persona, a user-level task, and the product entry point;
- the runner operates through Browser or Computer Use;
- a separate judge evaluates the recorded evidence;
- any forbidden implementation access marks the run as contaminated.

FreshEye does not claim synthetic users are equivalent to real users. Findings are hypotheses until validated with real-user research.

## V1 scope

FreshEye V1 supports:

- Codex CLI and Codex IDE workflows;
- custom runner and judge subagents;
- Browser / Computer Use interaction;
- persona packs for general users, AgentCompany, task apps, and Lumi;
- single-persona, panel, repeatability, and regression workflows;
- structured traces, contamination status, severity scoring, and Markdown reports;
- isolation levels from `L0` to `L3`.

FreshEye V1 does not yet provide:

- hard container isolation;
- a hosted testing service;
- native mobile-device automation;
- reliable child voice-conversation simulation;
- proof that synthetic findings generalize to real users.

## Architecture

```text
Developer Codex session
        |
        v
FreshEye Skill / Orchestrator
        |
        +--> fresheye_runner subagent A --> UI evidence
        +--> fresheye_runner subagent B --> UI evidence
        +--> fresheye_runner subagent C --> UI evidence
        |
        v
fresheye_judge subagent
        |
        v
.fresheye/runs/<run-id>/report.md
```

The runner and judge are deliberately separated. The runner acts as the persona and records what happened. The judge scores only the sanitized persona, task, and evidence.

## Installation

### Install with Codex

Ask Codex:

```text
Install this skill from https://github.com/Ericwong5021/fresheye
Then run its installer so the FreshEye custom subagents are copied into ~/.codex/agents.
```

### Manual installation

```bash
git clone https://github.com/Ericwong5021/fresheye.git
cd fresheye
python scripts/install.py --scope user
```

This installs:

```text
~/.agents/skills/fresheye/
~/.codex/agents/fresheye-runner.toml
~/.codex/agents/fresheye-judge.toml
```

Restart Codex if the Skill or custom agents do not appear immediately.

Run the diagnostic:

```bash
python ~/.agents/skills/fresheye/scripts/doctor.py
```

## Usage

Explicit invocation is recommended:

```text
$fresheye test http://localhost:3000
Persona: fresh-first-timer
Task: Create a task for tomorrow at 3 PM.
```

Panel test:

```text
$fresheye panel http://localhost:3000
Personas: fresh-first-timer, low-digital-literacy, impatient-goal-seeker
Task: Create a task for tomorrow at 3 PM.
Run each persona three times with a fresh browser state.
```

Regression test:

```text
$fresheye regress
Baseline: .fresheye/runs/20260730-before
Current target: http://localhost:3000
Reuse the same persona, task, viewport, account fixture, and repetition count.
```

## Isolation levels

| Level | Meaning |
|---|---|
| `L0` | Current development agent simulates a user. Not accepted by FreshEye. |
| `L1` | Separate subagent context, but browser or tool isolation is incomplete. |
| `L2` | Separate subagent and fresh browser state. |
| `L3` | Separate runner and judge, fresh browser state, sanitized inputs, restricted behavior, and contamination audit. FreshEye V1 target. |

A run must report the achieved level. It must never silently present degraded isolation as a valid blind test.

## Built-in persona packs

- `personas/core.yaml`
- `personas/agent-company.yaml`
- `personas/todolist.yaml`
- `personas/lumi.yaml`

Persona contracts describe goals, mental models, patience, exploration tendency, trust concerns, and abandonment conditions. They must never encode the intended solution path.

## Run artifacts

```text
.fresheye/runs/<run-id>/
├── manifest.yaml
├── persona.yaml
├── task.yaml
├── runners/
│   └── <runner-id>/
│       ├── trace.jsonl
│       ├── result.json
│       └── evidence/
├── judge-result.json
├── contamination.json
└── report.md
```

## Design principles

1. **Do not optimize for completion.** A real user may hesitate, misunderstand, fail, or leave.
2. **No implementation knowledge.** Source code, PRDs, diffs, selectors, internal APIs, and intended paths are forbidden to runners.
3. **Evidence before opinion.** Findings must point to an action step, visible clue, screenshot, or observable response.
4. **Separate action from judgment.** Runner and judge must use separate subagent threads.
5. **Expose uncertainty.** Synthetic findings are hypotheses; inconsistent findings stay inconsistent.
6. **Reproducibility over persona volume.** Three independent repeats of one primary persona are more useful than dozens of uncalibrated personas.

## Status

FreshEye is an early methodology prototype intended for validation in real projects. The immediate goal is to test whether isolated synthetic users find meaningful usability problems that development agents and conventional QA miss.

## License

MIT
