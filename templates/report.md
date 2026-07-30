# FreshEye usability report

> FreshEye synthetic usability test  
> Status: **hypothesis, not real-user validation**  
> Isolation achieved: **{{ isolation_achieved }}**  
> Valid repetitions: **{{ valid_repetitions }}/{{ total_repetitions }}**  
> Contaminated repetitions: **{{ contaminated_repetitions }}**

## Test contract

| Field | Value |
|---|---|
| Run | `{{ run_id }}` |
| Target | {{ target }} |
| Environment | {{ environment }} |
| Task | {{ task }} |
| Persona | {{ persona_name }} (`{{ persona_id }}`) |
| Viewport/context | {{ runtime_context }} |
| Planned repetitions | {{ total_repetitions }} |

## Outcome

| Measure | Result |
|---|---|
| Completed | {{ completed }} |
| Partial | {{ partial }} |
| Failed/abandoned | {{ failed }} |
| Median SEQ | {{ seq_median }}/7 |
| Median end confidence | {{ confidence_median }}/5 |
| Median trust | {{ trust_median }}/5 |

## Behavior summary

{{ behavior_summary }}

## Findings

### FE-001 — {{ finding_title }}

- **Status:** `[hypothesis]`
- **Severity:** {{ severity }}/4
- **Classification:** {{ classification }}
- **Reproduced:** {{ affected }}/{{ valid_repetitions }} valid repetitions
- **Evidence status:** {{ evidence_status }}
- **Observation:** {{ observation }}
- **User impact:** {{ user_impact }}
- **Trace/evidence:** {{ evidence_refs }}
- **Product hypothesis:** {{ product_hypothesis }}
- **Uncertainty:** {{ uncertainty }}

Repeat this section for each finding, ordered by severity and reproducibility.

## Disagreements

{{ disagreements }}

Do not erase disagreement by averaging. State which Personas or repetitions behaved differently.

## Contamination audit

{{ contamination_summary }}

| Runner | Valid | Isolation | Limitation or contamination reason |
|---|---:|---|---|
| {{ runner_id }} | {{ valid }} | {{ runner_isolation }} | {{ limitation }} |

## Isolation limitations

{{ limitations }}

## Product hypotheses

{{ product_hypotheses }}

Keep these at product and interaction level. Do not prescribe source-code changes unless a separate implementation task is requested after the blind test.

## Real-user validation questions

{{ real_user_validation_questions }}

## Appendix: run artifacts

- Manifest: `manifest.yaml`
- Persona: `persona.yaml`
- Task: `task.yaml`
- Runner results: `runners/*/result.json`
- Traces: `runners/*/trace.jsonl`
- Evidence: `runners/*/evidence/`
- Contamination audit: `contamination.json`
- Structured judgment: `judge-result.json`
