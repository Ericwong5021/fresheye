# FreshEye scoring

FreshEye prioritizes a small set of interpretable measures. Scores summarize evidence; they do not replace the trace.

## Task completion

| Score | Label | Definition |
|---:|---|---|
| 0 | Failed | The task was not completed, the persona abandoned it, or a blocker prevented completion. |
| 1 | Partial | Meaningful progress occurred, but the complete user goal or required final state was not achieved. |
| 2 | Completed | The user-level task was completed within the stated safety boundary. |

Do not award completion because the runner reached a technically related screen. Use the user's success definition.

## SEQ — Single Ease Question

After each task, the judge estimates task difficulty from the evidence:

| Score | Meaning |
|---:|---|
| 1 | Very difficult |
| 2 | Difficult |
| 3 | Somewhat difficult |
| 4 | Neither difficult nor easy |
| 5 | Somewhat easy |
| 6 | Easy |
| 7 | Very easy |

This is a synthetic estimate, not a response from a real participant. Report it as a hypothesis and explain evidence for extreme values.

## Confidence

Confidence represents how certain the Persona appears about the current action or product state.

| Score | Meaning |
|---:|---|
| 1 | Guessing or lost |
| 2 | Low confidence |
| 3 | Uncertain but able to proceed |
| 4 | Confident |
| 5 | Completely clear |

Runner trace events record confidence before and after each action. The judge may summarize median and end-state confidence.

## Trust

Trust captures whether the Persona believes the product will behave safely, preserve data, and respect its stated boundaries.

| Score | Meaning |
|---:|---|
| 1 | Actively distrusts the product |
| 2 | Serious unresolved concern |
| 3 | Neutral or mixed |
| 4 | Generally trusts the product |
| 5 | Clear evidence supports trust |

Do not infer trust from task completion alone.

## Severity

| Score | Label | User impact |
|---:|---|---|
| 0 | None | No usability problem supported by evidence. |
| 1 | Minor | Noticeable friction or cosmetic ambiguity with little task impact. |
| 2 | Moderate | Hesitation, error, or extra work; the Persona can usually recover. |
| 3 | Serious | Major confusion, repeated error, loss of confidence, or likely abandonment. |
| 4 | Blocker | The Persona cannot complete the primary task or faces unacceptable risk. |

Severity 2–4 findings require a trace step or evidence reference.

Severity depends on impact and Persona priority. A problem blocking the primary Persona must not be averaged down because expert users can recover.

## Reproducibility

Run the same Persona, task, and environment independently when the result matters.

| Repetitions showing issue | Interpretation |
|---:|---|
| 3/3 | Strong synthetic signal |
| 2/3 | Meaningful but variable signal |
| 1/3 | Candidate finding |
| 0/3 | Not reproduced |

A reproducibility count applies only to valid, uncontaminated runs.

Do not rerun until a preferred answer appears. Record the planned repetition count before testing.

## Finding classification

### Universal

Appears across materially different Personas and is supported by evidence.

### Primary persona

Materially harms the product's chosen primary Persona, even when other Personas do not experience it.

### Segment

Specific to a meaningful segment, context, or mental model.

### Edge case

Narrow but legitimate. Avoid prioritizing it above primary-persona blockers without a risk reason.

### Candidate

Appeared once, has weak evidence, or needs a targeted repeat.

### Non-issue

A mismatch not reasonably attributable to the interface or outside the declared product promise.

### Unverified

A plausible interpretation without enough observable evidence.

## Evidence status

Every finding uses one of:

- `observed`: directly visible in trace or screenshot;
- `inferred`: reasoned from multiple observed events;
- `unverified`: unsupported or dependent on missing evidence.

Every synthetic finding is also labeled:

- `[hypothesis]`: default FreshEye status;
- `[validated]`: allowed only when linked real-user evidence confirms it;
- `[contradicted]`: real-user evidence points in the opposite direction.

## Aggregation

Prefer distributions and counts over a single overall number.

Recommended summary:

```yaml
valid_repetitions: 3
task_completion:
  completed: 1
  partial: 1
  failed: 1
seq:
  median: 3
  range: [2, 5]
end_confidence:
  median: 2
trust:
  median: 3
```

Avoid combining completion, SEQ, confidence, trust, and severity into one opaque “UX score.” Different measures answer different questions.

## Regression comparison

Compare baseline and current runs on:

- valid completion ratio;
- median steps to completion or abandonment;
- median SEQ;
- end confidence and trust;
- error and recovery count;
- abandonment location;
- resolved, persistent, and newly introduced findings;
- isolation and contamination differences.

A regression conclusion is invalid when baseline and current controls materially differ.

## Recommended decision language

Use:

- “FreshEye found a reproducible blocker hypothesis for the primary Persona.”
- “The current build reduced median steps in three uncontaminated repeats.”
- “One runner experienced this issue; treat it as a candidate.”

Avoid:

- “Users will definitely fail.”
- “The interface is proven usable.”
- “Three AI Personas equal three real participants.”
