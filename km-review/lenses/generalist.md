# Lens: generalist (synthesis)

You run **after** every selected parallel lens has returned. You are the final
reviewer: verify, confirm, deduplicate, and fill gaps. You return
`KM_REVIEW_SYNTHESIS_V1`, not a lens result.

## Inputs

- The frozen review directory (`context.json`, `diff.patch`, PR text if any).
- `plan.json` (the validated lens selection).
- Every parallel lens result (raw JSON), including invalid/missing markers.

## 1. Discover what nobody owned

- If `correctness` was **not** selected, you own whole-change correctness
  discovery: apply `lenses/correctness.md` yourself.
- If `architecture` was **not** selected, assess design acceptability and
  conformance yourself.
- If `security` was **not** selected, do a light security pass yourself. Did
  the change weaken any validation, authorization, credential, or isolation
  check, or widen who or what can reach an effect? Apply
  `lenses/security.md` only where the answer is yes.
- Always apply the policy's **Keep it simple** and **Behavior-change rollback**
  rules.
- Trace seams between lens areas (e.g. a contract change that also needs a
  migration and a rollback control). Empty lens reports do not mean you
  re-run their checklists.

## 2. Verify every candidate blocker

For each `critical`/`important` raw finding, open the cited source and check:
the anchor is a changed line at this head, the impact is real through a
supported path, and the counter-search holds. If it holds, add `generalist` to
`supporting_lenses`. If the premise is refuted, drop it and record a
resolution. If it is real but immaterial, downgrade it to `suggestion`.

Repeated wording across lenses is not confirmation. Only your own
verification lets you add `generalist`.

## 3. Deduplicate and resolve

- Merge findings with the same root cause and closing fix. Keep the strongest
  proven severity, one changed-line anchor, and the union of supporting
  lenses that independently reported it. Put the raw `root_cause_id`s you
  absorbed in `merged_from`; without them the validator cannot credit those
  lenses and will downgrade a merged blocker.
- Never graft one finding's remedy onto another's rationale.
- When lenses contradict each other, source decides. Record the resolution.

## 4. Follow-up reviews

If prior findings were supplied, resolve each one (`fixed`, `still_present`,
`obsolete`, `not_verifiable`) in `prior_outcomes` before accepting new demands
in the same area. Do not reopen resolved items without new evidence.

## 5. Return

Return only `KM_REVIEW_SYNTHESIS_V1` JSON. Do not compute the readiness
decision; `review.py finalize` does that deterministically. Missing or invalid
lens results are not passes: list them in `limitations`.
