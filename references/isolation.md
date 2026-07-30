# FreshEye isolation model

FreshEye's product hypothesis depends on epistemic isolation: the synthetic participant should know only what a real target user could know at the beginning of the session.

Subagents reduce context pollution, but they are not a hard security boundary. FreshEye V1 therefore treats isolation as a measured property rather than a binary claim.

## Isolation levels

### L0 — invalid

The current development agent changes role and pretends to be a user.

Typical problems:

- it knows the source code, intended path, and recent changes;
- it can reinterpret confusing UI using design intent;
- it is motivated to complete the task;
- action and judgment happen in the same context.

FreshEye must not publish an L0 run as a blind usability test.

### L1 — separate context

A new subagent thread receives a sanitized Persona Contract and task.

Requirements:

- new runner thread;
- no deliberate developer context in the prompt;
- no sharing of previous runner results;
- contamination self-declaration.

Limitations:

- working directory or tools may still be inherited;
- browser state may not be fresh;
- runner and judge separation may be incomplete.

### L2 — context plus user-state isolation

L1 plus:

- fresh browser context or profile;
- cleared cookie, cache, local storage, and session state;
- independent test account or fixture when needed;
- no onboarding or data inherited from another repetition;
- runtime device and viewport match the Persona context.

### L3 — FreshEye V1 target

L2 plus:

- dedicated `fresheye_runner` custom subagent;
- separate `fresheye_judge` subagent;
- neutral task sanitization;
- runner tool-use declaration;
- explicit forbidden-information contract;
- contamination audit before aggregation;
- structured evidence and preserved traces;
- degraded controls disclosed in the report.

L3 is still soft isolation. It is appropriate for methodology validation, not a claim of adversarial containment.

### Future L4 and L5

Not implemented by this Skill:

- `L4`: separate Codex process in an empty working directory with explicit tool allowlist;
- `L5`: isolated container or remote runner, disposable browser, separate credentials, immutable evidence store, and server-enforced policy.

## Contamination classes

### Knowledge contamination

The runner learns implementation or intended-path information.

Examples:

- “We moved the create button to the bottom-right.”
- source code, PRD, git diff, issue, or developer chat is visible;
- task wording names the control being evaluated.

### Tool contamination

The runner uses a tool unavailable to the represented user.

Examples:

- shell, filesystem, git, code search;
- DOM, selector, accessibility-tree, console, or network inspection;
- direct API or database access.

Normal browser accessibility features used by a Persona with assistive technology require a separate explicit protocol. They must not be silently used as implementation inspection.

### State contamination

The starting product state contains knowledge or progress from another session.

Examples:

- logged-in cookies from the developer;
- onboarding already completed;
- previous runner-created records;
- autofill or remembered search history;
- feature flags that do not match the stated environment.

### Evaluation contamination

The action and scoring contexts influence each other.

Examples:

- runner knows the hypothesis or expected improvement;
- runner judges its own behavior;
- judge receives developer rationale;
- current runner sees baseline findings during a regression test.

### Persona contamination

The Persona Contract encodes the answer or forces a desired finding.

Bad:

```yaml
behavior:
  - looks for the plus button in the lower-right corner
  - becomes confused by the project field
```

Good:

```yaml
behavior:
  exploration_tendency: low
  icon_preference: distrusts unfamiliar icons without labels
  abandonment_conditions:
    - required fields are ambiguous after one attempt
```

## Sanitization checklist

Before spawning a runner, ask:

1. Does the task describe a human goal rather than a feature under test?
2. Does any wording reveal what changed?
3. Does the Persona mention target-specific controls or concepts?
4. Does the runner receive the expected path or completion mechanism?
5. Are developer terms converted into ordinary user language?
6. Can account and environment facts be provided without revealing the hypothesis?
7. Is the test safe without allowing irreversible actions?

## Tool-use audit

Each runner must return `tools_used` and `forbidden_access_detected`.

The orchestrator should compare the declaration with visible subagent activity when available. Any unexplained tool use should be treated conservatively.

Suggested audit record:

```json
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
    "Subagent inherited the parent working directory, but no file tools were used."
  ]
}
```

## Handling contamination

- preserve the contaminated trace;
- exclude it from score aggregation;
- state the reason in the report;
- do not rewrite the trace;
- do not rerun repeatedly until a preferred outcome appears;
- rerun once with corrected controls when a valid result is still needed;
- keep both attempts in the run record.

## Regression blinding

During a regression test, the current runner receives the same neutral task and Persona as the baseline runner. It must not receive:

- baseline findings;
- baseline screenshots;
- the changed code or design;
- the expected direction of improvement;
- the name of the changed component.

Only the judge sees baseline and current evidence after both sets of runs are complete.
