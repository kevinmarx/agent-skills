# Result contract

All results are a single JSON object. Return JSON only — no prose, no fences.
`review.py` validates every result; malformed output counts as incomplete
coverage for that lens.

## Lens result: `KM_REVIEW_LENS_RESULT_V1`

```json
{
  "kind": "KM_REVIEW_LENS_RESULT_V1",
  "lens": "security",
  "reviewed_head": "<40-char head SHA from context.json>",
  "coverage": "complete",
  "disposition": "findings",
  "findings": [
    {
      "root_cause_id": "security:src/api/login.ts:42:token-logged",
      "origin": "semantic",
      "severity": "important",
      "path": "src/api/login.ts",
      "side": "RIGHT",
      "line": 42,
      "summary": "Why this blocks:\n...\n\nRequired change:\n...\n\nVerification:\n...",
      "counter_search": "Checked the log scrubber in src/log/redact.ts:10; it only redacts `password`.",
      "supporting_lenses": ["security"]
    }
  ],
  "prior_outcomes": [],
  "limitations": []
}
```

| `coverage` | `disposition` | Meaning |
| --- | --- | --- |
| `complete` | `pass` | Relevant scope reviewed; nothing remains. `findings` is empty. |
| `complete` | `not_applicable` | Diff does not touch this responsibility. `findings` is empty. |
| `complete` | `findings` | Relevant scope reviewed; at least one finding. |
| `incomplete` | `incomplete` | Could not review completely. Partial findings stay visible. |

Finding fields:

- `root_cause_id`: `<lens>:<path>:<line>:<slug>`; stable across follow-ups.
- `origin`: `semantic` (model judgment) or `deterministic` (an executable
  failure you were given); `deterministic` also requires `deterministic_check`.
  Interpreting prose rules is always `semantic`.
- `severity`: `critical`, `important`, or `suggestion`.
- `path`: a path from the changed-file manifest.
- `side` / `line`: `RIGHT` = new-file line, `LEFT` = removed old-file line.
  Blockers must anchor on a line the diff actually changed.
- `summary`: blockers use `Why this blocks:` / `Required change:` /
  `Verification:` in that order; suggestions begin with the exact prefix
  `Suggestion:` (the validator also tolerates `Suggestion (optional):`).
- `counter_search`: required for blockers; what could have refuted it.
- `supporting_lenses`: must include your own lens id.

`prior_outcomes` (follow-up only): `[{"root_cause_id": "...", "outcome":
"fixed|still_present|obsolete|not_verifiable", "evidence": "..."}]`.

`limitations`: missing evidence **required** to review your scope. CI status,
unexecuted tests, and optional context are not limitations.

## Synthesis result: `KM_REVIEW_SYNTHESIS_V1`

Returned only by the generalist.

```json
{
  "kind": "KM_REVIEW_SYNTHESIS_V1",
  "reviewed_head": "<head SHA>",
  "coverage": "complete",
  "consolidated_findings": [
    { "...same finding fields...": "", "supporting_lenses": ["security", "generalist"] }
  ],
  "resolutions": [
    { "root_cause_id": "...", "action": "dropped|merged|downgraded|confirmed", "reason": "..." }
  ],
  "prior_outcomes": [],
  "pr_intent": "One sentence: what the change is trying to achieve.",
  "limitations": []
}
```

- `consolidated_findings`: root-cause-deduplicated. Put `generalist` in
  `supporting_lenses` only for findings you independently verified. When you
  merge raw findings that used different ids, list the absorbed raw ids in
  `merged_from`; a lens counts as confirming only if its raw result contains
  the consolidated id or one of those ids.
- `resolutions`: every raw finding you dropped, merged, or downgraded, with
  the source-based reason. Nothing disappears silently.

## Aggregate: `KM_REVIEW_RESULT_V1` (written by `review.py finalize`)

The model never writes this. `finalize` computes it from the validated lens
results and the synthesis:

- **Confirmation:** a semantic blocker keeps its severity only when at least
  two distinct lenses support it, counting a lens only if its own valid raw
  result contains that `root_cause_id`, or it is `generalist`. Otherwise it is
  downgraded to `suggestion` and recorded in `downgrades`.
- **Citation:** a blocker anchored on a line the diff did not change is
  downgraded and recorded.
- **Status:** `stale` if HEAD moved or the worktree is dirty; otherwise
  `incomplete` if any selected lens or the synthesis is missing, malformed, or
  incomplete; otherwise `complete`.
- **Decision:** `ready` only when status is `complete` and no `critical` or
  `important` finding remains. Review readiness is not merge readiness: CI
  and human approvals remain independent.
