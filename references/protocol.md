# FreshEye evidence protocol

This document defines the data exchanged among the orchestrator, runner, and judge.

## Design goals

- preserve the original behavior trace;
- keep observation separate from interpretation;
- make contamination visible;
- support independent re-judgment of the same evidence;
- support baseline/current regression comparisons;
- avoid dependence on one model's prose style.

## Manifest

The orchestrator creates `manifest.yaml` before testing.

Required fields:

```yaml
run_id: fe-20260730-001
mode: test
created_at: 2026-07-30T16:00:00+08:00
isolation_target: L3

target:
  kind: web
  entry_point: http://localhost:3000
  environment: local

persona:
  id: fresh-first-timer
  pack: core
  version: 0.1.0

task:
  instruction: Create a task for tomorrow at 3 PM.
  max_steps: 20
  max_duration_seconds: 180

runtime:
  viewport:
    width: 1440
    height: 900
  browser_state: fresh
  login_state: logged_out
  repetitions: 3

safety:
  forbidden_actions: []

evidence:
  screenshots: true
  trace: true
  video: false
```

Do not place developer-only success paths in the manifest.

## Runner result

Each runner returns one `result.json` matching `schemas/runner-result.schema.json`.

Example:

```json
{
  "schema_version": "0.1.0",
  "runner_id": "fresh-first-timer-r1",
  "persona_id": "fresh-first-timer",
  "status": "partial",
  "task_outcome": "A task was created, but no reminder time was confirmed.",
  "steps_taken": 7,
  "abandonment_reason": null,
  "tools_used": ["computer_use"],
  "forbidden_access_detected": false,
  "contamination_reason": null,
  "evidence_refs": [
    "evidence/step-003.png",
    "evidence/step-006.png"
  ],
  "uncertainties": [
    "The final screen did not visibly distinguish a deadline from a reminder."
  ]
}
```

The runner does not assign UX severity.

## Trace JSONL

Each line in `trace.jsonl` is an immutable event.

Example:

```json
{"step":1,"timestamp_or_order":"1","visible_clues":["Empty task list","Circular plus icon"],"expectation":"The plus icon will let me add something.","action":{"type":"click","target_description":"circular plus icon near the bottom"},"observed_result":"A text input appeared.","confidence_before":4,"confidence_after":5,"friction":null,"evidence_ref":"evidence/step-001.png"}
```

Required event fields:

- `step`: positive integer;
- `timestamp_or_order`: timestamp or deterministic ordinal;
- `visible_clues`: what was actually perceptible before acting;
- `expectation`: short expected outcome;
- `action.type`: click, type, scroll, navigate, wait, back, abandon, or other;
- `action.target_description`: human-visible description, never a selector;
- `observed_result`: visible product response;
- `confidence_before`: 1–5;
- `confidence_after`: 1–5;
- `friction`: null or concise user-level difficulty;
- `evidence_ref`: optional evidence path or tool artifact reference.

Optional event fields:

- `interpretation`: must be explicitly labeled and not phrased as observation;
- `recovery_attempt`: true/false;
- `error_type`: misunderstanding, slip, functional, environment, or unknown;
- `safety_stop`: true/false.

## Contamination record

`contamination.json` contains one entry per runner.

```json
{
  "schema_version": "0.1.0",
  "run_id": "fe-20260730-001",
  "runners": [
    {
      "runner_id": "fresh-first-timer-r1",
      "contaminated": false,
      "isolation_achieved": "L3",
      "checks": {
        "separate_thread": true,
        "sanitized_prompt": true,
        "fresh_browser_state": true,
        "runner_judge_separated": true,
        "forbidden_tool_use": false,
        "prior_results_exposed": false
      },
      "limitations": [
        "Subagent shared the parent working directory but did not use file tools."
      ]
    }
  ]
}
```

Unknown checks must not be recorded as true. Use `null` and downgrade the isolation level when needed.

## Judge result

The judge returns `judge-result.json` matching `schemas/judge-result.schema.json`.

A finding includes:

```json
{
  "id": "FE-001",
  "title": "Reminder state is not visibly confirmed",
  "status": "hypothesis",
  "evidence_status": "observed",
  "classification": "primary-persona",
  "severity": 3,
  "reproducibility": {
    "affected": 2,
    "valid_repetitions": 3
  },
  "persona_ids": ["fresh-first-timer"],
  "trace_refs": [
    "fresh-first-timer-r1:step-6",
    "fresh-first-timer-r3:step-5"
  ],
  "evidence_refs": [
    "runners/fresh-first-timer-r1/evidence/step-006.png"
  ],
  "observation": "Two runners could not tell whether 3 PM was a reminder or only a date value.",
  "user_impact": "The user may believe a reminder is configured when it is not.",
  "product_hypothesis": "Show a plain-language confirmation of date and reminder as separate states.",
  "uncertainty": "The third runner completed the task without expressing this concern."
}
```

## Evidence storage

Preferred evidence names:

```text
step-001-before.png
step-001-after.png
step-002-after.png
session.webm
```

Do not overwrite evidence from a previous runner or repetition.

If the Browser or Computer tool does not expose a portable file, record the tool artifact reference verbatim. Do not invent a path.

## Parent-thread responsibilities

The orchestrator may:

- write returned structured results to files;
- copy actual evidence artifacts into the run directory;
- validate JSON shape;
- perform contamination checks;
- spawn the judge;
- render the final Markdown report.

The orchestrator must not:

- reconstruct missing runner actions from memory;
- improve awkward or failed behavior traces;
- fill in evidence that was not captured;
- alter the Persona after seeing a result;
- discard valid unfavorable results.

## Regression protocol

Store the baseline run as immutable input. A current run uses a new directory and new runner threads.

The judge may compare:

- `baseline/manifest.yaml`;
- baseline valid runner results and evidence;
- `current/manifest.yaml`;
- current valid runner results and evidence.

The current runner must never receive baseline artifacts.

## Data hygiene

- redact credentials and personal information;
- use synthetic test data;
- do not store production secrets in manifests;
- do not capture unrelated user data visible in a shared browser;
- disclose when evidence is incomplete because of privacy redaction.
