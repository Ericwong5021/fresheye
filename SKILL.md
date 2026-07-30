---
name: fresheye
description: Run persona-driven blind usability tests in Codex using isolated runner and judge subagents plus Browser or Computer Use. Use for first-time-user testing, cognitive walkthroughs, UI flow validation, multi-persona panels, and UX regression tests. Do not use for source-code review, implementation debugging, or as a replacement for real-user research.
---

# FreshEye

FreshEye tests whether a target user can understand and use a product without access to developer knowledge.

The skill is an orchestrator. It must not simulate the user in the current development thread. It delegates UI use to a `fresheye_runner` subagent and evaluation to a separate `fresheye_judge` subagent.

## Core rule

The development agent may know the implementation. The synthetic user must not.

Never send the runner:

- source code or repository files;
- git history, diffs, issue discussions, or review comments;
- PRDs, architecture documents, developer conversations, or design rationale;
- expected interaction paths, button locations, selectors, component names, or internal terminology;
- API, database, console, DOM, accessibility-tree, or network-inspection output;
- information about what changed in the current version;
- other runners' traces, findings, or scores.

The runner may receive only:

- the selected Persona Contract;
- a user-level task instruction;
- the public product entry point;
- explicit environment facts a real participant would be told;
- runtime constraints such as viewport, account state, time limit, and maximum steps.

## Supported commands

Interpret the first token after `$fresheye` as the mode.

| Mode | Purpose |
|---|---|
| `test` | One persona, one task, one or more independent repetitions. Default. |
| `panel` | Several personas test the same task independently. |
| `regress` | Repeat a baseline manifest against a new build and compare behavior. |
| `inspect` | Evaluate screenshots or a non-interactive mock when live UI access is unavailable. Mark isolation at most `L1`. |
| `personas` | List built-in persona IDs and their intended use. |
| `doctor` | Check Skill installation, custom-agent files, and runtime prerequisites. |

If no mode is given, use `test`.

## Required inputs

Minimum:

1. product entry point: URL, desktop app, or attached UI artifact;
2. user-level task;
3. persona ID or an explicit Persona Contract.

Reasonable defaults:

- repetitions: `3` for a primary decision, otherwise `1`;
- max steps: `20`;
- max duration: `180 seconds`;
- viewport: infer from persona context, otherwise desktop;
- fresh state: required;
- login: logged out unless task requires an account;
- isolation target: `L3`.

Do not ask for implementation details. Do not request the correct path. If account credentials or destructive-action boundaries are genuinely required, ask only for those operational facts.

## Preflight

Before a live run:

1. Verify that subagents are enabled.
2. Verify that `fresheye_runner` and `fresheye_judge` are available.
3. Verify Browser or Computer Use is available for the runner.
4. Establish whether a fresh browser context/profile can be created.
5. Identify the target environment: local, preview, staging, or production.
6. Define forbidden actions, especially purchase, deletion, publication, external messaging, or production mutation.
7. Determine the maximum achievable isolation level before testing.

If custom agents are missing, a generic new subagent may be used with the complete runner or judge contract copied into its task. Mark the run no higher than `L1` unless all other `L2/L3` controls are independently verified.

Never run FreshEye in the current development thread. That is `L0` and invalid.

## Run directory

Create:

```text
.fresheye/runs/<YYYYMMDD-HHMMSS>-<task-slug>/
```

Populate:

```text
manifest.yaml
persona.yaml
task.yaml
runners/<runner-id>/result.json
runners/<runner-id>/trace.jsonl
runners/<runner-id>/evidence/
contamination.json
judge-result.json
report.md
```

The parent/orchestrator writes files. A read-only runner may return structured content to the parent instead of writing inside the repository.

## Phase 1: Build a sanitized manifest

The manifest must contain only participant-visible or experiment-operational information.

Required structure:

```yaml
run_id: fe-20260730-001
mode: test
isolation_target: L3

target:
  kind: web
  entry_point: http://localhost:3000
  environment: local

persona:
  id: fresh-first-timer
  source: personas/core.yaml

task:
  instruction: Create a task for tomorrow at 3 PM.
  max_steps: 20
  max_duration_seconds: 180

runtime:
  viewport: desktop
  browser_state: fresh
  login_state: logged_out
  repetitions: 3

safety:
  forbidden_actions:
    - make a real purchase
    - delete production data
    - send external messages

evidence:
  screenshots: true
  trace: true
  video: optional
```

Before spawning a runner, perform a sanitization pass:

- remove causal hints such as “the new button” or “verify the redesigned date picker”;
- remove implementation nouns the user would not know;
- convert feature validation into a neutral user goal;
- remove success paths and expected click sequences;
- remove comparison language that reveals the tested variable;
- verify that Persona fields describe behavior, not a solution.

Bad task:

> Verify that the redesigned floating plus button makes task creation easier.

Sanitized task:

> Create a task for tomorrow at 3 PM.

## Phase 2: Select or construct the Persona Contract

Read only the persona pack containing the selected ID.

A valid Persona Contract should cover:

- identity and real-world situation;
- primary goal and success definition;
- prior knowledge and mental model;
- digital confidence;
- reading patience;
- exploration tendency;
- risk tolerance and trust concerns;
- device, network, attention, and interruption context;
- error-recovery behavior;
- abandonment conditions.

Persona contracts must not contain:

- UI element names specific to the target;
- instructions to look in a location;
- the expected workflow;
- hidden product concepts;
- forced confusion or predetermined findings.

## Phase 3: Spawn runner subagents

Use one new `fresheye_runner` subagent per persona per repetition.

Never reuse a runner thread across repetitions. Never allow runners to communicate. Never show one runner another runner's result.

For each runner, send exactly:

```text
FRESHEYE BLIND RUN

Isolation target: <level>
Runner ID: <id>
Target: <entry point>
Persona Contract:
<sanitized persona>

Task:
<neutral task instruction>

Runtime:
<viewport, fresh state, login state, limits, safety constraints>

Use only visible UI through Browser or Computer Use.
Return a Runner Result matching references/protocol.md.
If forbidden implementation information is accessed or revealed, stop and mark the run CONTAMINATED.
```

### Runner behavioral discipline

The runner must:

- act from the persona's knowledge and habits;
- use only visible interface clues;
- state a short expectation before each action;
- take one user-level action at a time;
- record visible response and confidence after each action;
- allow hesitation, misinterpretation, recovery, and abandonment;
- avoid superhuman exhaustive exploration;
- stop when the persona's abandonment conditions are reached;
- distinguish observed facts from interpretations;
- declare every tool it used.

The runner must not:

- optimize for completing the task at any cost;
- inspect files, source, git, terminal, console, DOM, accessibility tree, selectors, network, API, or database;
- use keyboard shortcuts or hidden commands the persona would not know;
- infer intended behavior from developer conventions unavailable to the user;
- continue indefinitely after realistic abandonment;
- score the product or recommend code changes.

### Browser state

A repetition should start with:

- fresh browser profile/context;
- cleared cookies and local/session storage;
- no autofill or remembered credentials;
- task-specific test account or fixture where needed;
- no onboarding state inherited from another run.

If fresh state cannot be verified, reduce the isolation level and disclose it.

## Phase 4: Collect Runner Results

Each runner returns:

- run status: completed, partial, abandoned, blocked, or contaminated;
- task outcome without UX scoring;
- ordered trace entries;
- evidence references;
- tools used;
- forbidden-access declaration;
- contamination self-check;
- unresolved uncertainties.

Do not rewrite the trace to make it cleaner. Preserve failures and contradictions.

The trace must be JSONL with one event per line. Follow `references/protocol.md` and `schemas/runner-result.schema.json`.

## Phase 5: Contamination audit

The orchestrator audits each runner before judging usability.

Mark `contaminated: true` if any of the following occurred:

- runner read project or repository files;
- runner used shell, git, file search, code search, or implementation documentation;
- runner inspected DOM, selectors, console, network, API, or database;
- runner received developer rationale, intended path, tested-variable hints, or previous results;
- browser state was inherited but presented as fresh;
- runner and judge were the same thread;
- trace was materially reconstructed after the run.

A contaminated repetition is excluded from usability aggregation. Report it separately; do not silently rerun until a favorable result appears.

## Phase 6: Spawn the judge

After all runner threads finish, spawn one new `fresheye_judge` subagent.

The judge receives only:

- sanitized manifest;
- Persona Contract;
- neutral task;
- runner results and traces;
- evidence captured from the visible UI;
- contamination audit.

The judge must not receive source code, PRD, diffs, developer conversation, intended path, or current implementation goals.

Judge task:

```text
FRESHEYE EVIDENCE JUDGMENT

Evaluate only the supplied blind-test evidence.
Do not infer implementation details or excuse friction based on design intent.
Exclude contaminated repetitions.
Apply references/scoring.md.
Classify every claim as observed, inferred, or unverified.
Preserve disagreement across repetitions and personas.
Return JSON matching schemas/judge-result.schema.json plus a concise Markdown report.
```

## Phase 7: Score and aggregate

Default metrics:

- task completion: `0 failed`, `1 partial`, `2 completed`;
- SEQ task difficulty: `1 very difficult` to `7 very easy`;
- confidence: `1` to `5`;
- trust: `1` to `5`;
- issue severity: `0` to `4`;
- reproducibility: number of valid repetitions showing the same friction.

Finding classes:

- `universal`: appears across materially different personas;
- `primary-persona`: blocks or seriously harms the primary persona;
- `segment`: specific to a meaningful user segment;
- `edge-case`: narrow but legitimate condition;
- `candidate`: appeared once or lacks enough evidence;
- `non-issue`: expectation mismatch not attributable to the interface;
- `unverified`: interpretation without adequate evidence.

Synthetic findings must be labeled `[hypothesis]`. Only real-user calibration may promote them to `[validated]`.

## Mode behavior

### `test`

Run one persona independently. Use three repetitions when the result will drive an important decision.

### `panel`

Run each persona independently. Parallel execution is allowed only when browser profiles, accounts, and data fixtures cannot affect each other. Otherwise run sequentially.

Aggregate commonality only after all independent runs complete.

### `regress`

Read the baseline manifest and preserve:

- persona version;
- task wording;
- viewport and device context;
- browser/account state;
- time and step limits;
- repetition count;
- safety constraints.

Compare behavior, not screenshots alone:

- completion rate;
- median steps;
- abandonment point;
- error and recovery count;
- confidence and trust;
- SEQ;
- reproduced, resolved, and newly introduced findings.

Do not tell current runners what changed or which baseline finding is expected to improve.

### `inspect`

Use when only screenshots, mockups, or static designs exist.

The persona may assess visible hierarchy, language, affordance, trust, and expected next action. It cannot claim task completion. Mark findings as `candidate` and isolation no higher than `L1` unless execution is independently available.

### `personas`

Return a compact table from the persona packs. Do not load all Persona Contracts into the active context unless requested.

### `doctor`

Run `scripts/doctor.py` when available. Report:

- Skill path;
- runner and judge agent files;
- whether subagent configuration appears installed;
- whether Codex restart may be required;
- Browser/Computer availability as observed in the current host;
- maximum plausible isolation level.

## Report requirements

`report.md` must begin with:

```text
FreshEye synthetic usability test
Status: hypothesis, not real-user validation
Isolation achieved: L0/L1/L2/L3
Valid repetitions: X/Y
Contaminated repetitions: N
```

Then include:

1. target, task, Persona, and environment;
2. outcome and score summary;
3. behavior timeline;
4. findings ordered by severity and reproducibility;
5. cross-run or cross-persona disagreements;
6. contamination and isolation limitations;
7. recommended product hypotheses, not implementation prescriptions;
8. suggested real-user validation questions.

Every severity `2–4` finding requires an evidence reference or trace step.

## Safety

Do not perform irreversible or consequential real-world actions during a test unless the user has explicitly authorized the exact action.

Prefer test, local, preview, or staging environments. In production:

- stop before final purchase, publication, deletion, message sending, or account changes;
- use dedicated test accounts and synthetic data;
- do not bypass authentication, CAPTCHA, rate limits, or access controls;
- do not expose credentials in artifacts.

## Boundaries

FreshEye is for behavioral usability hypotheses. Route elsewhere when the primary task is:

- source-code correctness or security review;
- functional API testing without a user interface;
- visual pixel-diff regression;
- accessibility standards certification;
- performance benchmarking;
- production incident debugging;
- real-user recruiting or moderated research.

FreshEye may complement these methods but must not relabel them as persona-driven blind testing.
